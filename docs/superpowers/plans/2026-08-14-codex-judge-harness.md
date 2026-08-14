# Codex Judge Harness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a durable, blinded, resumable derived-score harness for the creative-writing judge workflow.

**Architecture:** `evaluations/run_judge_harness.py` is a standard-library module that validates one blinded batch and one structured judge response, derives `evaluation_id` and `I_i`, and atomically writes raw response and score artifacts. A separate join operation reads provenance only after all worker judgments are stored; Codex worker orchestration stays outside Python and gives each fresh Terra-high worker one eight-record batch.

**Tech Stack:** Python 3.10+ standard library (`argparse`, `hashlib`, `json`, `pathlib`, `tempfile`, `os`); `unittest`; JSON/JSONL.

**Spec:** `docs/superpowers/specs/2026-08-14-codex-judge-harness-design.md`

## Global Constraints

- Never modify `runs/benchmark_data.json`, `runs/results/*.jsonl`, or any other raw generation evidence.
- Every JSON/JSONL rewrite is atomic: temporary file in the destination directory, `fsync`, then `os.replace`.
- A judge worker receives one blinded eight-record batch only; it never receives provenance, model identity, condition, seed, or generation settings.
- `evaluation_id` is exactly `sha256(record_id + judge_prompt_version)`.
- `I_i` is the arithmetic mean of that record's per-constraint scores.
- `scores.jsonl` has at most one row per `record_id`; resume skips already-scored rows rather than overwriting them.
- Use only Python standard library modules and `unittest`.

---

### Task 1: Specify and test pure judge-response validation

**Files:**
- Create: `evaluations/test_run_judge_harness.py`
- Create: `evaluations/run_judge_harness.py`

**Interfaces:**
- Consumes: a blinded batch `list[dict]` and structured raw response `{"evaluations": list[dict]}`.
- Produces: `validate_response(batch: list[dict], response: dict, judge_prompt_version: str) -> list[dict]`, whose rows include `record_id`, `evaluation_id`, `adherence`, `I_i`, and `quality`.
- Errors: `ValueError` for invalid batch or response contracts.

- [ ] **Step 1: Write failing tests for a valid response and derived values**

```python
def test_validate_response_adds_stable_id_and_instruction_mean(self):
    rows = harness.validate_response(BATCH, VALID_RESPONSE, "v1")
    self.assertEqual(rows[0]["evaluation_id"], hashlib.sha256(b"record-1v1").hexdigest())
    self.assertEqual(rows[0]["I_i"], 0.75)
    self.assertEqual(rows[0]["quality"]["characterization"], 3)
```

- [ ] **Step 2: Run the test and verify it fails because `validate_response` does not exist**

Run: `python -m unittest discover -s evaluations -p test_run_judge_harness.py -v`

Expected: FAIL with an `AttributeError` for missing `validate_response`.

- [ ] **Step 3: Write failing tests for contract violations**

```python
def test_validate_response_rejects_missing_constraint_score(self):
    invalid = copy.deepcopy(VALID_RESPONSE)
    invalid["evaluations"][0]["adherence"].pop()
    with self.assertRaisesRegex(ValueError, "constraint"):
        harness.validate_response(BATCH, invalid, "v1")

def test_validate_response_rejects_inconsistent_nullable_characterization(self):
    invalid = copy.deepcopy(VALID_RESPONSE)
    invalid["evaluations"][0]["quality"]["characterization"] = None
    invalid["evaluations"][0]["quality"]["characterization_na"] = False
    with self.assertRaisesRegex(ValueError, "characterization"):
        harness.validate_response(BATCH, invalid, "v1")
```

- [ ] **Step 4: Run the tests and verify each fails for the absent implementation**

Run: `python -m unittest discover -s evaluations -p test_run_judge_harness.py -v`

Expected: FAIL only because `validate_response` is absent.

- [ ] **Step 5: Implement the minimal pure validation API**

```python
def evaluation_id(record_id, judge_prompt_version):
    return hashlib.sha256(f"{record_id}{judge_prompt_version}".encode("utf-8")).hexdigest()

def validate_response(batch, response, judge_prompt_version):
    # Validate batch record IDs, exact response record coverage, exact
    # constraint coverage, scales, non-empty reasons, and quality shape.
    # Return normalized score rows with evaluation_id and I_i.
```

- [ ] **Step 6: Run the test module and verify it passes**

Run: `python -m unittest discover -s evaluations -p test_run_judge_harness.py -v`

Expected: PASS.

- [ ] **Step 7: Commit the isolated validation slice**

```bash
git add evaluations/run_judge_harness.py evaluations/test_run_judge_harness.py
git commit -m "feat: validate blinded judge responses"
```

### Task 2: Add atomic raw-score persistence and resume behavior

**Files:**
- Modify: `evaluations/run_judge_harness.py`
- Modify: `evaluations/test_run_judge_harness.py`

**Interfaces:**
- Consumes: normalized score rows, raw structured response, an input batch path, and an evaluation output directory.
- Produces: `persist_batch(output_dir: Path, batch_path: Path, raw_text: str, rows: list[dict]) -> int` and `read_scores(path: Path) -> list[dict]`.
- Behavior: stores `judge_raw/<batch-stem>.json`, atomically replaces `scores.jsonl`, and returns the number of newly appended rows; duplicate record IDs are skipped only when their existing row has the same `evaluation_id`.

- [ ] **Step 1: Write a failing test for atomic persistence of raw and parsed artifacts**

```python
def test_persist_batch_writes_raw_response_and_one_score_row(self):
    with tempfile.TemporaryDirectory() as temporary:
        output = Path(temporary)
        added = harness.persist_batch(output, Path("judge_batch_001.json"), RAW_RESPONSE, ROWS)
        self.assertEqual(added, 1)
        self.assertEqual(json.loads((output / "judge_raw" / "judge_batch_001.json").read_text()), VALID_RESPONSE)
        self.assertEqual(harness.read_scores(output / "scores.jsonl"), ROWS)
```

- [ ] **Step 2: Run the persistence test and verify it fails because `persist_batch` does not exist**

Run: `python -m unittest discover -s evaluations -p test_run_judge_harness.py -v`

Expected: FAIL with an `AttributeError` for missing `persist_batch`.

- [ ] **Step 3: Write failing tests for resume and duplicate conflict protection**

```python
def test_persist_batch_skips_existing_matching_evaluation_id(self):
    # Persist once, persist the same normalized row again, then assert 0 added
    # and exactly one retained score row.

def test_persist_batch_rejects_existing_record_with_different_evaluation_id(self):
    # Seed scores.jsonl with record-1 under another prompt version; assert
    # ValueError and byte-for-byte unchanged scores.jsonl after the call.
```

- [ ] **Step 4: Run the tests and verify the failures identify missing persistence behavior**

Run: `python -m unittest discover -s evaluations -p test_run_judge_harness.py -v`

Expected: FAIL only for the missing persistence functions.

- [ ] **Step 5: Implement atomic write and resume helpers**

```python
def atomic_write_json(path, document):
    # Write JSON to mkstemp(dir=path.parent), fsync, then os.replace.

def atomic_write_jsonl(path, rows):
    # Serialize canonical one-row-per-line JSON, fsync, then os.replace.

def persist_batch(output_dir, batch_path, raw_text, rows):
    # Validate existing rows before writing either artifact, atomically retain
    # raw response, then atomically replace the deduplicated score dataset.
```

- [ ] **Step 6: Run the test module and verify it passes**

Run: `python -m unittest discover -s evaluations -p test_run_judge_harness.py -v`

Expected: PASS.

- [ ] **Step 7: Commit the persistence slice**

```bash
git add evaluations/run_judge_harness.py evaluations/test_run_judge_harness.py
git commit -m "feat: persist resumable judge scores"
```

### Task 3: Add deferred provenance joining and the command-line interface

**Files:**
- Modify: `evaluations/run_judge_harness.py`
- Modify: `evaluations/test_run_judge_harness.py`

**Interfaces:**
- Consumes: `scores.jsonl`, a provenance JSON object keyed by `record_id`, and CLI arguments.
- Produces: `join_provenance(scores_path: Path, provenance_path: Path) -> int` plus `main()` subcommands:
  - `score --batch PATH --response PATH --output DIR --judge-prompt-version VERSION --judge-model MODEL --judge-settings JSON`
  - `join-provenance --scores PATH --provenance PATH`
- Behavior: joins only exact record IDs, rejects missing/extra provenance IDs, and never sends provenance to score validation or worker prompts.

- [ ] **Step 1: Write a failing test for deferred provenance joining**

```python
def test_join_provenance_adds_only_matching_record_metadata(self):
    with tempfile.TemporaryDirectory() as temporary:
        scores_path = Path(temporary) / "scores.jsonl"
        harness.atomic_write_jsonl(scores_path, ROWS)
        provenance_path = Path(temporary) / "provenance.json"
        provenance_path.write_text(json.dumps({"record-1": {"model_id": "hidden-model"}}))
        self.assertEqual(harness.join_provenance(scores_path, provenance_path), 1)
        self.assertEqual(harness.read_scores(scores_path)[0]["model_id"], "hidden-model")
```

- [ ] **Step 2: Run the join test and verify it fails because `join_provenance` does not exist**

Run: `python -m unittest discover -s evaluations -p test_run_judge_harness.py -v`

Expected: FAIL with an `AttributeError` for missing `join_provenance`.

- [ ] **Step 3: Write failing tests for provenance coverage and CLI scoring**

```python
def test_join_provenance_rejects_missing_record_without_changing_scores(self):
    # Supply a provenance map missing record-1 and assert ValueError plus
    # unchanged scores.jsonl contents.

def test_score_cli_persists_validated_batch_with_judge_metadata(self):
    # Patch sys.argv with the score subcommand and assert the score row records
    # judge_prompt_version, judge_model, and parsed judge_settings.
```

- [ ] **Step 4: Run the tests and verify they fail because the join/CLI implementation is absent**

Run: `python -m unittest discover -s evaluations -p test_run_judge_harness.py -v`

Expected: FAIL only for missing `join_provenance` or `main` behavior.

- [ ] **Step 5: Implement the separate join and CLI boundary**

```python
def join_provenance(scores_path, provenance_path):
    # Require score and provenance record-ID sets to match exactly, merge the
    # mapping values into copied score rows, then atomically replace scores.

def main():
    # Parse `score` and `join-provenance`; validate arguments before reading
    # and never load provenance in the `score` subcommand.
```

- [ ] **Step 6: Run the test module and verify it passes**

Run: `python -m unittest discover -s evaluations -p test_run_judge_harness.py -v`

Expected: PASS.

- [ ] **Step 7: Commit the CLI and join slice**

```bash
git add evaluations/run_judge_harness.py evaluations/test_run_judge_harness.py
git commit -m "feat: add judge provenance join CLI"
```

### Task 4: Document the durable score contract and worker prompt

**Files:**
- Create: `evaluations/judge_prompt.md`
- Create: `evaluations/score_schema.json`
- Modify: `evaluations/README.md`
- Modify: `.mex/ROUTER.md`
- Modify: `.mex/context/evaluation.md`
- Modify: `.mex/patterns/derived-evaluation.md`

**Interfaces:**
- Consumes: the committed `judge_config.json` rubric and the module's exact CLI/artifact behavior.
- Produces: an externally usable blinded-worker instruction, a score schema, and updated project navigation/scaffold state.

- [ ] **Step 1: Write a failing documentation-contract test**

```python
def test_score_schema_lists_required_score_and_reproducibility_fields(self):
    schema = json.loads((Path(__file__).parent / "score_schema.json").read_text())
    required = set(schema["required"])
    self.assertTrue({"record_id", "evaluation_id", "adherence", "I_i", "quality", "judge"} <= required)
```

- [ ] **Step 2: Run the test and verify it fails because `score_schema.json` does not exist**

Run: `python -m unittest discover -s evaluations -p test_run_judge_harness.py -v`

Expected: FAIL with `FileNotFoundError`.

- [ ] **Step 3: Add the score schema, worker prompt, and documentation updates**

`judge_prompt.md` must reproduce the committed anchors, require every input
record and constraint to be returned, stress component independence, prohibit
provenance speculation, and enforce the nullable-characterization rule.
`score_schema.json` must state that it is derived data, list every score row's
required fields, document deferred provenance fields, and name the atomic,
resumable artifact contract. The README and `.mex` files must state that the
harness now exists but no score run is evidence until it is executed and
verified.

- [ ] **Step 4: Run the full test module and verify it passes**

Run: `python -m unittest discover -s evaluations -p test_run_judge_harness.py -v`

Expected: PASS.

- [ ] **Step 5: Run source and artifact integrity checks**

Run: `git diff --check -- evaluations .mex`

Expected: no output.

Run: `git diff --name-only -- runs/benchmark_data.json runs/results`

Expected: no output.

- [ ] **Step 6: Commit the documented harness contract**

```bash
git add evaluations .mex/ROUTER.md .mex/context/evaluation.md .mex/patterns/derived-evaluation.md docs/superpowers
git commit -m "docs: document blinded judge score workflow"
```

## Plan Self-Review

- Spec coverage: Tasks 1–3 cover the judge response, raw retention, stable IDs, `I_i`, resume, and post-judgment provenance join. Task 4 covers the durable artifact and worker contracts plus scaffold updates.
- Placeholder scan: no `TBD`, `TODO`, deferred implementation markers, or unspecified interfaces remain.
- Type consistency: all tasks use the same `list[dict]` batch/row interfaces, `evaluation_id(record_id, judge_prompt_version)`, `scores.jsonl`, and separate `join_provenance` boundary.
