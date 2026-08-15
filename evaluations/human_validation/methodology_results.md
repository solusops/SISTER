# Matched Human–Model Pairwise Validation

## Raw observations

- The fixed blind sample contains 30 matched response pairs (60 responses).
- The primary pass preserves the app's existing Response A/Response B assignment.
- The reversed pass swaps the same two responses within every case; instruction and atomic constraints are unchanged.
- Both model passes were validated and frozen before any human annotations were loaded.

## Computed statistics

### Position consistency

- Constraint following: directional 76.7%; exact five-level 50.0% (N=30).
- Creative-writing quality: directional 83.3%; exact five-level 53.3% (N=30).
- Combined across both decisions: directional 80.0%; exact five-level 51.7% (N=60).
- Directional preference changes after swapping: 12. See `position_consistency_summary.json` for the complete list.

### Human–model agreement

Completed human cases: 11. Primary-order model judgments are compared with the same A/B assignment.
- Constraint following: exact 36.4%; directional 54.5%; quadratic weighted kappa 0.421; collapsed kappa 0.127; mean absolute disagreement 1.182; severe disagreement 18.2%.
- Creative-writing quality: exact 54.5%; directional 54.5%; quadratic weighted kappa 0.480; collapsed kappa 0.214; mean absolute disagreement 1.000; severe disagreement 27.3%.
See `human_model_agreement_summary.json` and `human_model_disagreements.md` for the completed-case data and diagnostic table.

## Interpretation

Position consistency describes whether the model's comparative direction is stable under a pure A/B label swap. It does not establish agreement with human reviewers and must not be interpreted as validity evidence by itself.

## Limitations

- The sample is N=30 and is a matched evaluator-validation study, not a rerun of the 1,920-output pointwise evaluation.
- The supplied human export contains 11 completed cases; all human-model statistics are based on N=11, not the full 30-case sample.
- The repository's hidden manifest records selection strata, but it does not identify a recoverable development/pilot versus held-out boundary. This report therefore does not claim that all 30 cases were untouched held-out validation data.
- Categorical labels remain authoritative; the -2 to +2 representation in `ordinal_model_judgments.jsonl` is for analysis only.

