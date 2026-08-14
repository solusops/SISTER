---
name: pairwise-evaluator-validation
description: Reproduce the matched 30-pair model evaluation, reversed-order robustness pass, or post-freeze human comparison.
last_updated: "2026-08-15"
---

# Pairwise Evaluator Validation

## Context

This is a fixed matched evaluator-validation study, not a full-generation
evaluation. Its only source sample is the ignored local blind-review app:
`evaluations/.tmp_human_review/blind_case_pack.js`, checked against its hidden
30-row manifest. Its publishable derived artifacts are under
`evaluations/human_validation/`.

## Steps

1. Run `node evaluations/human_validation/validate_pairwise_validation.mjs prepare`.
   It writes exactly 30 sanitized primary cases and 30 A/B-swapped reversed
   cases, each with 60 response slots; only case ID, instruction, atomic
   constraints, Response A, and Response B are allowed.
2. Give a fresh judge context only one sanitized case file plus the pairwise
   rubric. Never expose the hidden manifest, human export, pointwise scores,
   model/condition metadata, or the other model pass. Freeze the candidate
   with `freeze primary|reversed <candidate.jsonl>`.
3. Only after both freeze receipts exist, run `report` to generate ordinal
   analysis-only data and position consistency. Reversed decisions are
   translated back into original A/B orientation before comparison.
4. Only if a human export is supplied, run `analyze-human <export.jsonl>`.
   It uses only completed human cases, validates the scale, and reports exact
   and directional agreement, quadratic weighted kappa, collapsed kappa, mean
   absolute ordinal disagreement, severe opposite-direction rate, and a
   per-case diagnostic table. It never tunes the judge against human labels.

## Verify

- Both sanitized files have 30 unique case IDs and 60 responses.
- Both frozen judgment files have exactly one valid five-level choice and
  concise reason per dimension for every case.
- The primary input preserves existing A/B positions; the reversed input swaps
  only the two response fields.
- No human export is read before both freezes. If it is unavailable, report
  that limitation and do not claim human-model agreement or held-out status.
