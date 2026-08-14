# Blind Human Pair Review App Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build one offline HTML app that supports blind, independent human evaluation of 30 balanced Full/Sharded generation pairs.

**Architecture:** A Node build script reads the final generations and active score pool solely to select a balanced hidden sample, then emits two artifacts: a reviewer-facing HTML file containing only anonymized A/B case content and a separate join manifest. Browser JavaScript renders the rubric and form, autosaves local annotations, and supports JSON export/import without any network call.

**Tech Stack:** Node.js built-ins, static HTML/CSS/JavaScript, browser `localStorage`, and Node's built-in test runner.

**Spec:** `docs/superpowers/specs/2026-08-14-blind-human-review-app-design.md`

## Global Constraints

- Produce exactly 30 pairs / 60 outputs, with five pairs per each of six models and six genres.
- Use score data only for hidden sample stratification; do not place automated scores, reasons, source, model, condition, record IDs, or sampling stratum in the reviewer HTML or its export payload.
- Show each pair only as randomized `Response A` and `Response B`.
- Require atomic-constraint scores and reasons; quality comments remain optional.
- Persist `started_at`, `completed_at`, and elapsed review time per case locally.
- Write the hidden manifest outside the reviewer artifact with the exact schema in the spec.
- Do not commit: the user has not authorized a git commit.

---

### Task 1: Build and test the hidden balanced-sample selector

**Files:**
- Create: `evaluations/build_human_blind_review.mjs`
- Create: `evaluations/test_build_human_blind_review.mjs`
- Create: `evaluations/tmp_human_blind_review_manifest.json`

**Interfaces:**
- Consumes: `runs/results/all_results.jsonl`, `evaluations/constraints.jsonl`, `runs/benchmark_data.json`, the active score sources, and `evaluations/native_judge_repair_batches/manifest.json`.
- Produces: `selectCases()` returning `{cases, manifest}` and a JSON manifest with `case_id`, `story_id`, `model`, `genre`, `A_condition`, `B_condition`, `full_record_id`, `sharded_record_id`, and `sampling_stratum`.

- [ ] **Step 1: Write failing selection tests**

```javascript
import test from "node:test";
import assert from "node:assert/strict";
import { selectCases } from "./build_human_blind_review.mjs";

test("selectCases returns a 30-pair, 60-output balanced blind sample", () => {
  const { cases, manifest } = selectCases({ seed: "human-review-v1" });
  assert.equal(cases.length, 30);
  assert.equal(manifest.length, 30);
  assert.deepEqual(countBy(manifest, "model"), {
    "google/gemma-4-12b-qat": 5,
    "ibm/granite-4-h-tiny": 5,
    "llama-3.1-8b-instruct": 5,
    "mistralai/mistral-7b-instruct-v0.3": 5,
    "openai/gpt-oss-20b": 5,
    "qwen/qwen3.5-9b": 5,
  });
  assert.deepEqual(countBy(manifest, "genre"), {
    comedy: 5, fantasy: 5, historical_fiction: 5,
    mystery: 5, romance: 5, science_fiction: 5,
  });
});

test("reviewer cases omit automated and provenance fields", () => {
  const { cases } = selectCases({ seed: "human-review-v1" });
  for (const item of cases) {
    assert.deepEqual(Object.keys(item).sort(), ["case_id", "constraints", "full_instruction", "response_a", "response_b"]);
    assert.equal("model" in item, false);
    assert.equal("condition" in item, false);
    assert.equal("record_id" in item, false);
    assert.equal("score" in item, false);
  }
});
```

- [ ] **Step 2: Run the tests to verify failure**

Run: `node --test evaluations/test_build_human_blind_review.mjs`

Expected: FAIL because `build_human_blind_review.mjs` and `selectCases` do not exist.

- [ ] **Step 3: Implement deterministic, hidden selection and manifest generation**

```javascript
export function selectCases({ seed }) {
  // Load final Full/Sharded pairs and active scores.
  // Compute hidden strata from adherence/quality deltas.
  // Use seeded backtracking to satisfy five-per-model, five-per-genre,
  // and mixed-stratum targets without selecting duplicate pairs.
  // Randomly map each selected pair to A/B and return only anonymized content.
}
```

The loader must compose 781 non-overlap auto rows, valid native and long rows
excluding repaired IDs, and 12 repair rows. It may use those values for
selection only; omit them from returned reviewer cases. Add an explicit
assertion that each selected pair has all expected atomic constraints.

- [ ] **Step 4: Run selector tests and build the hidden manifest**

Run: `node --test evaluations/test_build_human_blind_review.mjs && node evaluations/build_human_blind_review.mjs`

Expected: PASS; `tmp_human_blind_review_manifest.json` contains 30 records
with the specified join fields and balanced model/genre counts.

### Task 2: Build and test the offline blinded review app

**Files:**
- Modify: `evaluations/build_human_blind_review.mjs`
- Modify: `evaluations/test_build_human_blind_review.mjs`
- Create: `evaluations/tmp_human_blind_review.html`

**Interfaces:**
- Consumes: anonymized `cases` returned by `selectCases()`.
- Produces: one browser-openable HTML file with `window.HUMAN_REVIEW_CASES`,
  `saveCase(caseId, annotation)`, `exportAnnotations()`, and
  `importAnnotations(file)`.

- [ ] **Step 1: Extend tests with browser-artifact assertions**

```javascript
test("build emits an offline reviewer app with no hidden metadata", () => {
  buildReviewApp({ seed: "human-review-v1" });
  const html = readFileSync("evaluations/tmp_human_blind_review.html", "utf8");
  assert.match(html, /Response A/);
  assert.match(html, /Response B/);
  assert.match(html, /A clearly better/);
  assert.match(html, /started_at/);
  assert.doesNotMatch(html, /codex_native_terra_medium|auto_judge_sonnet_medium_effort/);
  assert.doesNotMatch(html, /full_record_id|sharded_record_id|sampling_stratum/);
});
```

- [ ] **Step 2: Run the extended tests to verify failure**

Run: `node --test evaluations/test_build_human_blind_review.mjs`

Expected: FAIL because the builder does not yet emit the reviewer artifact.

- [ ] **Step 3: Implement the self-contained HTML application**

```javascript
function emptyAnnotation() {
  return {
    started_at: null,
    completed_at: null,
    elapsed_seconds: 0,
    response_a: { adherence: {}, quality: {}, quality_comments: {} },
    response_b: { adherence: {}, quality: {}, quality_comments: {} },
    pair_preference: null,
    notes: "",
  };
}
```

Render full instruction, atomic constraints, and response prose; provide
0/.5/1 controls and required short reasons for every response/constraint;
provide 1–5 quality controls, nullable characterization, optional quality
comments, optional structured preference, optional notes, navigation, review
progress, a collapsible exact-rubric panel, local save, import, export, and
reset confirmation. The app must not render hidden fields in DOM data or export.

- [ ] **Step 4: Run tests and open the built artifact for a smoke check**

Run: `node --test evaluations/test_build_human_blind_review.mjs && node evaluations/build_human_blind_review.mjs`

Expected: PASS; opening `evaluations/tmp_human_blind_review.html` shows 30
anonymized cases, randomized A/B response order, and no automatic score data.

### Task 3: Verify selection, reviewer payload, and artifact safety

**Files:**
- Modify: `evaluations/test_build_human_blind_review.mjs`
- Modify: `evaluations/README.md`

**Interfaces:**
- Consumes: built app and hidden manifest.
- Produces: a verified audit trail and brief use instructions.

- [ ] **Step 1: Add export-schema and rubric tests**

```javascript
test("annotation schema preserves independent human data only", () => {
  const annotation = normalizeAnnotation({ case_id: "case-001" });
  assert.deepEqual(Object.keys(annotation).sort(), [
    "case_id", "completed_at", "elapsed_seconds", "notes",
    "pair_preference", "response_a", "response_b", "started_at",
  ]);
  assert.equal(JSON.stringify(annotation).includes("model"), false);
  assert.equal(JSON.stringify(annotation).includes("condition"), false);
  assert.equal(JSON.stringify(annotation).includes("score"), false);
});
```

- [ ] **Step 2: Run tests to verify failure**

Run: `node --test evaluations/test_build_human_blind_review.mjs`

Expected: FAIL until the exporter normalizes exactly the independent-human
schema and the app includes all five quality-dimension anchors.

- [ ] **Step 3: Implement export normalization and concise reviewer instructions**

Add `normalizeAnnotation()` to the builder. Document opening the HTML locally,
autosave behavior, JSON export/import, reset, and the location/access rule for
the hidden manifest in `evaluations/README.md`.

- [ ] **Step 4: Run the complete verification suite**

Run: `node --test evaluations/test_build_human_blind_review.mjs && git diff --check`

Expected: PASS with no whitespace errors. Confirm separately that
`git diff --name-only -- runs/benchmark_data.json runs/results` is empty.
