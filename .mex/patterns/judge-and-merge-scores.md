---
name: judge-and-merge-scores
description: Run further blinded LLM judging, or merge automated and manual score exports into one canonical evaluations/scores.jsonl.
triggers:
  - "judge harness"
  - "score the generations"
  - "merge scores"
  - "manual scoring"
edges:
  - target: context/evaluation.md
    condition: for the full rubric, blinding contract, and current scoring state this pattern assumes
  - target: patterns/derived-evaluation.md
    condition: for the constraint-record conventions (story_id, constraint_id) that judge records must stay consistent with
  - target: patterns/debug-evaluation-run.md
    condition: if a *generation* run (not judging) is what's stuck
grounds_to: []
last_updated: "2026-08-14"
---

# Judge and Merge Scores

## Context

Judging this dataset (1,920 final generation records) is split across two
paths right now, neither of which has produced the canonical
`evaluations/scores.jsonl` yet:

1. **`evaluations/scores_auto.jsonl`** — 784 records scored by an ad hoc
   Claude Code Workflow. Mechanically validated (0 errors: exact
   constraint-ID coverage, valid score ranges, consistent
   `characterization`/`characterization_na`), never independently
   LLM-verified (that stage was designed but never completed in the run that
   produced this file).
2. **Native candidate scores** — 1,093 non-long Terra rows and 46 long
   Sol-high rows have now been structurally checked. Twelve invalid candidates
   were replaced by isolated one-record repairs; the active, non-canonical
   pool is 1,920 unique rows (781 legacy auto rows after removing three
   auto/long overlaps, 1,085 retained native rows, 42 retained long rows, and
   12 repairs). See `context/evaluation.md` for the current artifact paths.
3. **A published manual-scoring web tool** — for the 1,093 records that ad
   hoc run never reached, plus 46 records excluded from automated judging as
   outliers (>10,000 chars, mostly `qwen/qwen3.5-9b` sharded). URL is in
   `.mex/ROUTER.md`'s "Current Project State". Its HTML source lives only in
   a past session's temp scratchpad — not recoverable from this repo.

A prior attempt at a reusable persistence/validation module
(`evaluations/run_judge_harness.py` + `test_run_judge_harness.py`) was
removed as failed work on 2026-08-14. There is no persistence-layer code to
build on — if one is wanted, write it fresh; don't go looking for it.

Read `context/evaluation.md`'s "Judging" section for the rubric and blinding
contract before touching any of this.

## Steps — running further automated judging

Only do this if API/agent budget allows — the first attempt ran out of
budget partway through, which is why the manual tool exists at all.

1. Build blinded input batches: `{record_id, story_id, full_instruction,
   constraints[], text}` per record, joined from `runs/results/all_results.jsonl`
   (filter `is_final: true`) and `evaluations/constraints.jsonl` by
   `story_id = domain + "_" + item_id` zero-padded to 3 digits. Strip
   `model_id`, `model_name`, `condition`, `quant_file`, seed — the judge must
   never see them.
2. Exclude anything already in the active score pool (currently represented
   by `scores_auto_nonoverlap.jsonl`, valid native/long candidates, and
   repairs) or a completed manual
   export, and anything in `excluded_for_manual_annotation.jsonl` (already
   routed to manual scoring) or over the same ~10,000-character threshold if
   extending that exclusion policy further.
3. Score in small batches (8 records/agent was the working size — larger
   batches risk within-batch drift on subjective quality judgments, smaller
   costs more agent spawns per record).
4. Validate every response before trusting it: exact constraint-ID coverage
   against `evaluations/constraints.jsonl` for that record's `story_id`, all
   adherence scores in `{0, 0.5, 1}`, all quality scores integers 1–5, and
   `characterization`/`characterization_na` mutually consistent (null iff
   `na: true`). Write this check in whatever script drives the run — don't
   skip it and don't assume a prior implementation exists to import.
5. Persist append-only, keyed by `record_id`, so a partial/interrupted run
   can resume without re-scoring or duplicating records already saved.

## Steps — merging manual-tool exports

The manual tool's export panel produces JSONL per person, each line shaped
`{record_id, story_id, adherence[], quality, source: "manual_human_annotation"}`.

1. Collect every export file from every annotator.
2. For each `record_id`, if it appears in more than one export: **do not
   silently pick one.** Compare the `adherence`/`quality` payloads; if
   identical, dedupe silently; if they differ, list the conflict (record_id,
   which exports, what differs) for the user to resolve — this usually means
   two people worked outside their assigned index range.
3. Validate each surviving row the same structural checks described above — a
   human can make the same structural mistakes an LLM judge can (missing a
   constraint, an out-of-range score).
4. Merge validated manual rows with `scores_auto.jsonl` into
   `evaluations/scores.jsonl`, tagging each row's `source`
   (`auto_judge_sonnet_medium_effort` vs. `manual_human_annotation`) so
   Phase 8-style sensitivity analysis can split on it later if manual vs.
   automated scores turn out to disagree systematically.

## Gotchas

- `story_id`, not `item_id`, is the join key everywhere — see
  `patterns/derived-evaluation.md`'s gotcha on this; it applies identically
  to score records.
- Never show raw shard text to a judge, automated or human — full
  instruction + constraint list only. This was a deliberate blinding choice,
  not an oversight, and applies to any future manual-scoring UI too.
- The 46-record outlier exclusion threshold (~10,000 characters) was chosen
  to keep ~97.6% of data in automated judging while dropping only the
  genuine long tail — don't silently tighten or loosen it without recording
  the new threshold and reasoning here.
- If you build a new persistence/validation module, don't reuse the name
  `run_judge_harness.py` in a way that implies continuity with the removed
  attempt — that file's history (a red, uncommitted TDD state its author
   abandoned) is gone; starting over cleanly is the point.
- Batch completion messages are not validation. The prior Terra defects all
  omitted the final supplied constraint, and early long workers used an
  ambiguous quality-key name. Enforce exact coverage and the canonical six
  quality keys before an output enters the active pool; repair failures in
  blinded one-record contexts rather than editing a judge's substantive score.

## Verify

- [ ] `evaluations/scores.jsonl` (once it exists) has exactly one row per
      `record_id`, and every `record_id` traces to a real final generation
      record in `runs/results/all_results.jsonl`.
- [ ] Every row's constraint-ID set matches `evaluations/constraints.jsonl`
      for that `story_id` exactly (no missing, no invented).
- [ ] Every row's `source` field distinguishes automated vs. manual origin.
- [ ] No conflicting duplicate `record_id` was silently resolved without
      being surfaced to the user first.
- [ ] `runs/results/*.jsonl` and `runs/benchmark_data.json` were not touched.

## Update Scaffold

- [ ] Update `.mex/ROUTER.md` "Current Project State" once
      `evaluations/scores.jsonl` exists, or once manual scoring completes.
- [ ] Update `.mex/context/evaluation.md` "Metrics and Results" once paired
      statistics are implemented over the merged scores.
- [ ] Record any new merge-conflict pattern encountered here, so the next
      merge doesn't have to rediscover it.
