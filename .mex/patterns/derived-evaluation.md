---
name: derived-evaluation
description: Add or edit derived annotation/scoring records under evaluations/ (e.g. constraint extraction) without touching raw generation or benchmark data.
triggers:
  - "constraint extraction"
  - "derived evaluation"
  - "score the generations"
  - "evaluations/constraints"
edges:
  - target: context/evaluation.md
    condition: when checking the dataset/protocol contract a derived record must stay consistent with
  - target: context/architecture.md
    condition: when the relationship between evaluations/, runs/results/, and benchmark_data.json is unclear
  - target: patterns/judge-and-merge-scores.md
    condition: when the derived record in question is a judge score rather than an extracted constraint
  - target: patterns/update-paper-results.md
    condition: once a derived score is verified and ready to cite in the manuscript
grounds_to: []
last_updated: "2026-08-15"
---

# Derived Evaluation

## Context

`evaluations/` holds derived annotation and scoring artifacts, kept strictly separate from the immutable generation evidence in `runs/results/` and the benchmark definition in `runs/benchmark_data.json`. `constraints.jsonl` (atomic constraints extracted from all 160 tasks) and `constraint_schema.json` (its taxonomy, extraction method, and validation status) are complete — see `evaluations/README.md`. Judge scoring is partially run — see `patterns/judge-and-merge-scores.md` for the current split between `scores_auto.jsonl` (784 records scored ad hoc) and a manual-scoring tool for the remainder. There is no reusable persistence/validation module; a prior parallel attempt was removed as failed work. Pairwise blind evaluation and the statistics/analysis layer are not yet built.

### Current correction (2026-08-15)

A distinct matched 30-pair evaluator-validation workflow now lives under
`evaluations/human_validation/`; follow
`patterns/pairwise-evaluator-validation.md` for its blinding, freeze, and
post-freeze human-comparison contract. The earlier sentence refers only to
the former project state and must not be used as current guidance.

## Steps

1. Read `evaluations/constraint_schema.json`'s `"provenance"` and `"validation"` fields before adding to or trusting `constraints.jsonl` — they record extraction method, spot-check coverage, and any known systematic issues (e.g. the romance_011-020 batch-boundary fix already applied and documented there).
2. Key every record by `story_id` = `domain + "_" + item_id` zero-padded to 3 digits (e.g. `fantasy_001`) — `item_id` alone repeats across domains (comedy runs 1–60, all other domains 1–20), so it is not a safe join key on its own.
3. Any new derived-evaluation record must reference generation `record_id`s or benchmark `story_id`s, never duplicate or restate their text as a new source of truth.
4. Never write to `runs/benchmark_data.json` or `runs/results/*.jsonl` to produce a derived artifact — regenerate the derived file from source if it needs to change.
5. If you add a new derived artifact (e.g. a judge-score file), document it in `evaluations/README.md`'s "Contents" list and give it its own schema file following `constraint_schema.json`'s shape (`$schema`, `description` stating it's derived and never-hand-edit-the-source, `provenance`, `validation`).

## Gotchas

- `story_id` is the stable global join key, not `item_id` — a query or script that groups only by `item_id` will silently merge unrelated tasks across domains.
- `constraint_id` is `story_id + "_c" + running integer starting at 1, in source order` — don't renumber existing IDs when appending; only renumber within a record you are actively re-extracting (as the schema's provenance note describes doing for `romance_011-020`).
- Extraction is LLM-derived, not ground truth: the schema's `human_spot_check` covered only 36/160 stories (6 per genre, seed 42). Treat the remaining 124 as validated only by the mechanical checks (story_id match, taxonomy membership, `introduced_at_shard` bounds, ID uniqueness) unless you've spot-checked further.
- A compound requirement (e.g. "a short, deliberately cheesy romance story") should split into separate atomic constraints (genre/tone/length) — the schema's provenance note documents this exact failure mode from one extraction batch and how it was caught and fixed.

## Verify

- [ ] Every new/edited record's `story_id` matches `domain_ItemIdZeroPadded3` and exists in `runs/benchmark_data.json`.
- [ ] `constraint_id`s within a record are unique and sequential from 1 in source order.
- [ ] Every `type` value is one of the enumerated taxonomy values in `constraint_schema.json`.
- [ ] Every `introduced_at_shard` is within bounds of that task's `shards[]` array.
- [ ] `runs/benchmark_data.json` and `runs/results/*.jsonl` were not modified.
- [ ] `constraint_schema.json`'s `provenance`/`validation` fields are updated if the extraction method, coverage, or known issues changed.

## Debug

If a derived record looks wrong against the source task, re-read the task's `full_instruction` and `shards` directly from `runs/benchmark_data.json` rather than trusting a prior extraction — the schema's own provenance notes show extraction batches can drift, and the fix was caught only by manual spot-check, not by the mechanical validators.

## Update Scaffold

- [ ] Update `.mex/ROUTER.md` "Current Project State" when `evaluations/scores.jsonl` is created, or pairwise/stats work starts.
- [ ] Update `.mex/context/evaluation.md` "Metrics and Results" once paired statistics are implemented over the merged scores.
- [ ] Update this pattern if a new derived-artifact type is added beyond constraints and scores, or split it further if that type's workflow diverges significantly.
