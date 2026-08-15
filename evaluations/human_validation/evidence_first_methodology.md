# Evidence-First Pairwise Judge Validation

## Procedure

The judge completed a compact structured evidence audit before each final preference: per-constraint satisfied/partial/violated status for both responses, then eight grounded creative dimensions. These are inspectable evidence-based intermediate judgments, not hidden chain-of-thought.
Both primary and A/B-reversed passes were judged in fresh contexts using only sanitized cases and the rubric. Neither pass received human annotations, prior pairwise outputs, pointwise scores, provenance, or position-consistency results.

## Final-preference robustness

- Constraint following: exact 46.7%; directional 70.0%; opposite-direction reversals 2/30.
- Creative quality: exact 70.0%; directional 80.0%; opposite-direction reversals 5/30.

## Evidence-level robustness

- Constraint status decisions stable after restoring orientation: 430/496 (86.7%).
- prose_and_craft: 83.3% dimension-winner consistency.
- coherence_and_progression: 83.3% dimension-winner consistency.
- originality_of_execution: 66.7% dimension-winner consistency.
- natural_constraint_integration: 70.0% dimension-winner consistency.
- characterization: 73.3% dimension-winner consistency.
- atmosphere_and_effect: 60.0% dimension-winner consistency.
- narrative_payoff: 76.7% dimension-winner consistency.
- genre_effectiveness: 80.0% dimension-winner consistency.

## Interpretation and limitations

A changed final preference can arise from changed evidence decisions or from changed final aggregation despite stable evidence decisions; `evidence_first_position_consistency.json` separates these cases. This study measures order robustness and inspectability on the fixed N=30 sample, not agreement with humans or the full 1,920-output dataset. No human comparison has been performed for the evidence-first evaluator.

