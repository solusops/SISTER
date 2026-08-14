# Codex Judge Harness Design

## Purpose

Build a durable, Codex-native derived-evaluation harness for the 1,920
blinded creative-writing generations. The harness implements the committed
constraint-adherence and quality-rubric contract without modifying immutable
generation evidence under `runs/results/`.

## Scope

The harness prepares and validates a single blinded batch, accepts a
schema-conforming judge response, calculates derived fields, and atomically
persists resumable score artifacts. Codex orchestrates fresh
`gpt-5.6-terra` high-reasoning judge workers externally, one worker per
eight-record batch. The Python module does not call a model API itself.

The existing Claude workflow remains an unmodified reference for the prompt
and schema contract.

## Components

### Judge contract

`evaluations/judge_prompt.md` will state the immutable blinded-worker
instructions. A worker receives only one JSON batch containing
`record_id`, `story_id`, `full_instruction`, `constraints`, and `text`, plus
the prompt and `evaluations/judge_config.json`. It returns exactly one
evaluation for each input record:

- one `{constraint_id, score, reason}` result for every supplied constraint;
- five independent quality fields;
- `characterization=null` and `characterization_na=true` only when the
  rubric's stated condition applies.

The worker receives no provenance file, model metadata, condition, seed, or
generation settings and must not speculate about them.

### Harness module

`evaluations/run_judge_harness.py` will use only the Python standard library.
It will expose small functions for:

- loading and validating a blinded batch;
- computing `evaluation_id = sha256(record_id + judge_prompt_version)`;
- parsing and validating a structured raw judge response against its batch;
- requiring exactly one result per record and exactly one scored result per
  input constraint;
- requiring adherence scores in `{0, 0.5, 1}`, quality scores in `1..5`, and
  a consistent nullable-characterization pair;
- calculating `I_i` as the arithmetic mean of all adherence scores;
- atomically storing raw judge output and derived score rows;
- resuming by omitting record IDs already represented in `scores.jsonl`; and
- joining provenance only after scoring, keyed by `record_id`.

The CLI will support validation and persistence of a supplied raw response,
and separate joining of a supplied provenance map. It will accept input paths
explicitly, so the current temporary Claude scratchpad can be used without
copying its blinded batches into the repository. The provenance path is never
an argument to or otherwise exposed in the worker prompt.

### Derived artifacts

- `evaluations/scores.jsonl`: one durable row per `record_id`, including
  `evaluation_id`, scored `adherence`, `I_i`, `quality`, judge-run metadata,
  and (only after the join step) provenance fields.
- `evaluations/judge_raw/<batch-stem>.json`: exact structured response
  received for that batch, retained before parsing-derived data.
- `evaluations/score_schema.json`: schema and provenance/validation contract
  for these derived artifacts.

Every rewrite of a JSON or JSONL artifact is via a temporary file in the
target directory, `fsync`, and `os.replace`. Existing raw generation files
are never written.

## Data Flow

```text
blinded batch -> fresh Terra-high worker -> raw structured response
     -> validate against the same batch -> calculate I_i/evaluation_id
     -> raw response + scores.jsonl (atomic, resumable)

scores.jsonl + provenance map -> post-judging join -> updated scores.jsonl
```

The provenance map is absent from every left-hand step.

## Error Handling

Malformed JSON, missing/extra record IDs, missing/extra constraint IDs,
invalid scales, duplicate score rows, and inconsistent characterization
values fail before any score artifact is changed. A batch whose records are
already all present in `scores.jsonl` is skipped. A partial prior run resumes
only the missing records; it never overwrites existing score rows.

## Testing

`evaluations/test_run_judge_harness.py` will use `unittest` and temporary
directories. Tests will first establish the desired API, then cover
evaluation ID and `I_i` calculation, valid response persistence,
batch/constraint mismatch rejection, nullable characterization rules,
deduplication/resume, and deferred provenance joining. Tests will assert that
failed validation leaves score artifacts unchanged.

## Documentation

`evaluations/README.md`, `.mex/ROUTER.md`, `.mex/context/evaluation.md`, and
`.mex/patterns/derived-evaluation.md` will describe the implemented derived
score contract and preserve the distinction between blinded judging and the
post-judging provenance join.
