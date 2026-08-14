# Blind Human Pair Review App — Design

## Goal

Create a temporary, self-contained browser app for a first high-quality human
evaluation pass over exactly 30 matched generation pairs (60 outputs). The
reviewer must not see model identity, Full/Sharded condition, automated scores,
score sources, record IDs, or preselected outcome categories.

## Sample construction

- Select exactly 30 `(model, story)` pairs, each containing one Full and one
  Sharded final output.
- Balance the set at five pairs per each of the six models and five pairs per
  each of the six genres.
- Stratify selection behind the scenes across clear Full wins, clear Sharded
  wins, near-ties, and unusual adherence/quality relationships. Existing score
  data may be used only to construct this hidden sample; it must not be
  embedded in the app or any human-annotation export.
- Randomly assign each condition to visible `Response A` or `Response B` per
  pair. Store only the resulting A/B texts in the app; omit condition labels,
  model names, score values, score rationales, and provenance entirely.
- Human scoring is fully independent: do not prefill a rationale, aggregate,
  warning, comparison signal, or any other field from automated scoring.

## Review flow

1. The reviewer sees a neutral case number, full instruction, and atomic
   constraint list, followed by Response A and Response B in randomized order.
2. For each response, the reviewer scores every supplied constraint using the
   existing adherence interpretation: `0` = violated/absent, `0.5` = partially
   satisfied, `1` = clearly satisfied, with a short evidence-based rationale.
3. For each response, the reviewer scores the five existing quality dimensions
   (`craft`, `structure_coherence`, `originality`, `genre_effectiveness`, and
   `characterization`) on the existing 1–5 anchored scale, with the same
   nullable characterization rule. Quality comments are optional, so the
   required written workload remains limited to atomic adherence reasons.
4. The reviewer records one structured, optional pair preference: `A clearly
   better`, `A slightly better`, `Tie`, `B slightly better`, or `B clearly
   better`, plus optional overall notes. This preference is supplementary and
   does not replace the two independent rubric scores.
5. Navigation supports previous/next case, a completion indicator, and a
   case list showing only completion state.

## Rubric display

The app includes a collapsible reference panel containing the exact adherence
definitions and all 1–5 anchors from `evaluations/judge_config.json`. It does
not display any automated decisions, aggregates, labels, or reasons.

## Persistence and export

- Save work automatically in browser `localStorage` after each input change.
  Track `started_at`, `completed_at`, and elapsed review time per case, without
  associating those values with model or condition in the reviewer-visible app.
- Support manual JSON import of a prior export and JSON download of current
  annotations. The export contains only case ID, anonymized A/B responses'
  human ratings/reasons, structured preference, optional notes, and completion
  metadata.
- Provide a reset action with confirmation. No server, network call, or
  external dependency is required.

## Artifact and verification

- Deliver one offline-openable HTML file under `evaluations/` with all 30
  selected pairs embedded.
- Retain a separate hidden manifest outside the app and reviewer export with
  `case_id`, `story_id`, `model`, `genre`, `A_condition`, `B_condition`,
  `full_record_id`, `sharded_record_id`, and `sampling_stratum`. It is the
  sole post-hoc join path from human annotations to automated results.
- Verify: exactly 30 cases; 60 outputs; five cases for each model and genre in
  the hidden selection manifest; neither visible UI nor export schema contains
  model/condition/provenance/automated-score data; A/B assignment is mixed;
  all cases carry every expected constraint; rubric fields persist across a
  browser reload; export/import round-trips; per-case timing persists; and
  the app contains no prefilled or score-derived reviewer guidance.
