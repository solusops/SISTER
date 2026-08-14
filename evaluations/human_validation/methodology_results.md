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

No human annotation export is present in this repository, so exact agreement, directional agreement, weighted Cohen's kappa, collapsed Cohen's kappa, mean absolute disagreement, severe-disagreement rate, and the per-case disagreement table have not been computed. This is a data-availability limitation, not an exclusion of cases.

## Interpretation

Position consistency describes whether the model's comparative direction is stable under a pure A/B label swap. It does not establish agreement with human reviewers and must not be interpreted as validity evidence by itself.

## Limitations

- The sample is N=30 and is a matched evaluator-validation study, not a rerun of the 1,920-output pointwise evaluation.
- The repository does not contain the human export, so no human–model estimate can yet be reported.
- The repository's hidden manifest records selection strata, but it does not identify a recoverable development/pilot versus held-out boundary. This report therefore does not claim that all 30 cases were untouched held-out validation data.
- Categorical labels remain authoritative; the -2 to +2 representation in `ordinal_model_judgments.jsonl` is for analysis only.

