---
language:
  - en
license: cc-by-4.0
task_categories:
  - text-generation
tags:
  - creative-writing
  - instruction-following
  - text-generation
  - llm-as-judge
---

# The Effects of Incremental Instruction Delivery on Language-Model Creative Writing — Study Dataset

*Consolidated dataset card. Six independent configs, one repo to cite. This
repo supersedes the narrower `sister-benchmark` /
`sister-benchmark-generations` split for anyone citing the full study going
forward; those two repos remain published as legacy for existing citations.*

## Summary

Everything needed to reproduce the paper's tables from generation through
judging: the 160-task benchmark, six baseline models' raw outputs on it
(full-instruction vs. sharded/incremental delivery), pointwise judge scores,
two independent pairwise evaluator-validation passes, and the human pairwise
annotation sample used to validate them. See the paired GitHub repo
(`incremental-instruction-creative-writing`) for the generation/judging code.

## Configs

Load any config with `datasets.load_dataset(repo_id, config_name=...)`.

| Config | Splits | Rows | What it is |
|---|---|---|---|
| `benchmark` | `tasks` | 160 | The task specifications themselves. |
| `generations` | one per model (6) | 1,156 each | Raw outputs, full + sharded conditions, one baseline model per split. |
| `pointwise_scores` | `scores` | 1,920 | Per-constraint adherence + 5-dimension creative-quality scores, one row per final generation record. `source` field distinguishes the judging pass that produced each row. |
| `pairwise_validation` | `primary`, `reversed` | 30 each | A/B preference judgments over a fixed 30-case blind sample, in original and swapped response order (position-bias check). |
| `evidence_first_validation` | `primary`, `reversed` | 30 each | An independent, evidence-first pairwise evaluator over the same 30 cases: per-constraint satisfied/partial/violated audit + evidence before a final preference. |
| `human_eval_sample` | `sample` | 30 | The blind 30-case sample itself (task, constraints, both responses). |
| `human_eval_annotations` | `annotations` | 11 | Human-validation annotations against the sample above (a separate config, not a split of `human_eval_sample` -- the two have different schemas). |

## Plain repo files (not dataset splits)

- `benchmark/constraints.jsonl`, `benchmark/constraint_schema.json` — atomic
  constraints extracted from every task, one record per `story_id`, and
  their taxonomy/extraction provenance.
- `evaluations/judge_config.json` — the judging rubric: adherence scale
  (0/0.5/1), the six quality dimensions with anchored 1–5 definitions, and
  the blinding contract (judges never see model identity or condition).
- `generations/generations_index.json` — run provenance: model/quant
  identity, seeds, context-length segments and retries, per-model progress
  and integrity hashes.
- `methodology/` — both evaluator-validation methodology reports, and the
  position-consistency / constraint-stability / dimension-stability
  statistics behind them (e.g. 86.7% constraint-status stability across 496
  audited decisions in the evidence-first pass).
- `ARTIFACT_MANIFEST.json` — SHA-256 + row count for every file above, so a
  download can be checked against what's cited.

## Join keys

- `story_id` = `{domain}_{item_id zero-padded to 3 digits}` (e.g.
  `fantasy_001`) — joins `benchmark`, `constraints.jsonl`, and any score row.
- `record_id` — unique per generation attempt; joins `generations` rows to
  `pointwise_scores` rows.
- `case_id` (`case-01`..`case-30`) — joins `human_eval_sample`,
  `human_eval_annotations`, `pairwise_validation`, and
  `evidence_first_validation` rows for the same fixed sample.

## Provenance

Built from the `SISTER` development repository; see `ARTIFACT_MANIFEST.json`
and the GitHub repo's README for the exact source commit this push
corresponds to.

## License

Creative Commons Attribution 4.0 International (CC BY 4.0).
