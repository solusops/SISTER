---
name: router
description: Session bootstrap and navigation hub. Read at the start of every session before any task. Contains project state, routing table, and behavioural contract.
edges:
  - target: context/architecture.md
    condition: when working on system design, integrations, or understanding how evaluation and paper components connect
  - target: context/stack.md
    condition: when working with Python, LaTeX, evaluation libraries, or making technology decisions
  - target: context/conventions.md
    condition: when writing or reviewing Python or LaTeX changes
  - target: context/decisions.md
    condition: when making an architectural or technology choice, or understanding why one was made
  - target: context/setup.md
    condition: when setting up the environment, compiling the paper, or running project commands
  - target: context/evaluation.md
    condition: when working on datasets, models, multi-turn protocols, metrics, or result artifacts
  - target: patterns/INDEX.md
    condition: when starting any task and looking for a repeatable workflow
  - target: patterns/judge-and-merge-scores.md
    condition: when the judge harness, its red persistence tests, or merging scored records is the task
last_updated: "2026-08-15"
---

# Session Bootstrap

If you haven't already read `.mex/AGENTS.md`, read it now — it contains the project identity, non-negotiables, and commands.

Then read this file fully before doing anything else in this session.

## Current Project State

**Working:**
- The repository retains an editable manuscript source under `paper/`, alongside
  the study materials and active generation data. GitHub Actions compiles it as
  a downloadable artifact without committing generated PDFs.
- As of 2026-08-10, the active flat `runs/results/` dataset contains exactly
  six completed models: GPT-OSS 20B, Gemma 4 12B QAT, Llama 3.1 8B, Granite 4
  H Tiny, Mistral 7B Instruct v0.3, and Qwen 3.5 9B Q4_K_M. Each has 320 final
  conditions and 1,156 raw records; the combined dataset has 6,936 unique
  records. Qwen's index retains its seed and 16K-to-22,528 context segments;
  Granite's first context-length retry is likewise recorded. Cydonia, prior
  reasoning-mode outputs, failed/partial attempts, diagnostics, and caches
  are isolated under `runs/test/older_outputs/`.
- The project goal is defined: evaluate whether LLM performance degrades in multi-turn conversations.
- `runs/run_experiment.py` evaluates 160 creative-writing tasks across six
  domains using full and sharded multi-turn conditions.
- The runner supports both LM Studio and Ollama. Collaborators select explicit
  model IDs with `--backend {lmstudio,ollama} --models …`; every run is capped
  at 16,384 context tokens and uses the OpenAI-compatible LM Studio endpoint.
  It appends every raw response immediately to a readable per-model JSONL file
  and an independent combined JSONL dataset; `results/index.json` records
  provenance and progress. `--resume` is reserved for a known interrupted run
  in the active results directory.
  Historical, partial, reasoning-mode, and diagnostic outputs are isolated
  under `runs/test/older_outputs/`.
- Do not use `runs/context error/` as run history.
- The root README is publication-facing: it states the research question,
  distinguishes active results from archival diagnostics, links operational
  run instructions, and provides the current manuscript citation. `CITATION.cff`
  mirrors the title and author metadata for repository citation tools.
- Root-level `evaluations/` now holds real derived-annotation and scoring work:
  `constraints.jsonl` (one atomic-constraint record per `story_id`, extracted
  from all 160 `runs/benchmark_data.json` tasks, 1,278 constraints total) and
  `constraint_schema.json` (its taxonomy and extraction provenance, including
  a batch-6 extraction defect found and fixed via a 36-story human spot-check
  — see that file's `human_spot_check` field before trusting unspotchecked
  records). It still references generation `record_id`s rather than
  duplicating them; model generations remain under `runs/results/`.
- A judge protocol is designed and partially executed. `judge_config.json`
  defines the rubric (per-constraint adherence 0/0.5/1 + reason; 5-dimension
  creative-quality score 1–5 with no reason field, `characterization`
  nullable). A prior parallel attempt at a persistence/validation module
  (`evaluations/run_judge_harness.py` + `test_run_judge_harness.py`) was
  removed as failed work on 2026-08-14 — do not recreate those exact
  filenames expecting prior context; there is no persistence-layer code to
  build on, start fresh if one is wanted.
- Automated judging ran ad hoc via a Claude Code Workflow: 784 of 1,874 eligible final records are scored, mechanically
  validated (0 structural errors — exact constraint-ID coverage, valid score
  ranges, consistent `characterization`/`characterization_na`), and saved to
  `evaluations/scores_auto.jsonl`. This run never completed an LLM-based
  verify pass (0/240 verify-stage calls ever finished across two run
  attempts) — validity rests entirely on the mechanical check, which is
  sufficient but worth knowing.
- 46 final records were excluded from automated judging before scoring
  (>10,000 characters, overwhelmingly `qwen/qwen3.5-9b` sharded — the same
  model that needed a context-length increase during generation) and saved
  to `evaluations/excluded_for_manual_annotation.jsonl` for the same reason:
  automated judge batches containing them risked degraded judgment quality.
- The remaining 1,093 unscored records plus those 46 excluded ones (1,139
  total) were routed to manual human scoring because the automated judging
  run exhausted its API/agent budget partway through. A self-contained
  scoring web tool was built and published as a Claude Artifact:
  **https://claude.ai/code/artifact/edd9fbb2-2942-404d-8719-e1fd80f77b7f**
  (title "SISTER Manual Scorer"). Its HTML source (with all 1,139 records'
  text/constraints embedded, ~5.3 MB) lives only in that session's temp
  scratchpad, not in this repo — it is not recoverable from the repo alone;
  regenerate from `evaluations/constraints.jsonl` +
  `runs/results/all_results.jsonl` (final records not present in
  `scores_auto.jsonl` or `excluded_for_manual_annotation.jsonl`) if needed
  again. Multiple people may export partial JSONL from that tool; merging
  multiple exports requires checking for the same `record_id` scored
  differently across exports and flagging conflicts rather than silently
  picking one — see `patterns/judge-and-merge-scores.md`.
- On 2026-08-14, native Codex judging completed the 1,093 non-outlier,
  not-already-scored final records in 137 fresh, blinded `gpt-5.6-terra`
  medium-reasoning batches. The batch inputs are under
  `evaluations/native_judge_batches/` and the corresponding append-only
  candidate outputs are under `evaluations/native_judge_scores/` (1,093 rows).
  The 46 long-output records remained excluded; three that also occur in
  `scores_auto.jsonl` must be excluded from any future canonical merge.
  Only batch/file and row-count completion checks have run so far; structural
  validation and sampling remain explicitly deferred.
- The 46 long outputs were subsequently judged in a separate one-record-per-
  worker pass using fresh `gpt-5.6-sol` high-reasoning contexts. Its 46
  candidate rows live in `evaluations/native_judge_long_scores/`; they remain
  separate from the non-outlier candidates and from any future canonical merge
  pending the same validation/sampling review.
- A full active-pool structural check has now passed: 1,920 final records have
  exactly one active score (781 non-overlapping legacy automatic rows, 1,085
  valid native rows, 42 valid long rows, and 12 strict one-record repairs).
  The three historical auto/long overlaps are excluded only from the active
  pool via `evaluations/scores_auto_nonoverlap.jsonl`; the original
  `scores_auto.jsonl` remains preserved. The repair pass corrected eight
  native rows that omitted their final supplied constraint and four early long
  rows with non-canonical quality fields. No score aggregation, sampling, or
  canonical merge has been performed.
- Matched pairwise evaluator validation now has frozen primary and
  reversed-order model passes over the existing blind 30-pair sample (60
  responses). `evaluations/human_validation/` contains both sanitized case
  files, both 30-row model-judgment files and SHA-256 receipts, an
  ordinal-analysis-only representation, position consistency, and a
  methodology/results report. After translating the reversed labels back to
  primary A/B orientation, directional consistency is 76.7% for constraint
  following and 83.3% for creative quality (80.0% across 60 decisions), with
  12 directional changes listed in the artifact. A supplied external human
  export contains 11 completed cases (case-01 through case-11), and its raw
  JSONL is not committed. Primary-order human-model comparison over N=11 is
  now recorded in `human_model_agreement_summary.json` and
  `human_model_disagreements.md`: exact/directional agreement is 36.4%/54.5%
  for constraints and 54.5%/54.5% for creative quality; quadratic weighted
  kappa is 0.421 and 0.480, respectively. The remaining 19 cases are not
  imputed, and the unknown development/pilot versus held-out boundary remains
  an explicit limitation.
- A second evidence-first pairwise evaluator has now completed independent
  primary and reversed passes over the same 30 cases. Its judge contexts saw
  only sanitized instruction, constraints, and A/B response text; they did
  not see human data, simple-pairwise outputs, scores, or provenance. Each
  record audits every constraint as satisfied/partial/violated with concise
  evidence and completes eight creative comparison dimensions before a final
  preference. After restoring reversed orientation, final directional
  consistency is 70.0% for constraints and 80.0% for creative quality; exact
  five-level consistency is 46.7% and 70.0%; opposite-direction reversals are
  2 and 5. Constraint-status stability is 430/496 (86.7%); all changed final
  preferences also have changed intermediate evidence decisions, rather than
  a stable-evidence aggregation change. See `evaluations/human_validation/`
  `evidence_first_*`; no human comparison has been run for this evaluator.
- The dataset is also published independently on Hugging Face:
  `runs/BENCHMARK.md` and `runs/results/README.md` document the two
  artifacts (`benchmark_data.json`, `results/`), and `runs/hf_upload/`
  (`push_benchmark.py`, `push_generations.py`) pushes them to the separate
  `sister-benchmark` and `sister-benchmark-generations` Hub repos.

- The canonical score merge now exists: `evaluations/merge_scores.py` (+
  `test_merge_scores.py`) combines `scores_auto_nonoverlap.jsonl`, retained
  native/long rows, and repairs into `evaluations/scores.jsonl` (1,920 rows,
  each keeping its original `source` tag), with structural validation
  (record_id uniqueness, exact constraint-ID coverage, canonical quality-key
  set, adherence scale, `characterization`/`characterization_na`
  consistency) enforced before writing. The raw 11-case human pairwise
  export is now committed as
  `evaluations/human_validation/annotations.jsonl`, and the 30-case blind
  sample is also available under the explicit name
  `evaluations/human_validation/sample_30.jsonl`.
- A citation-facing snapshot is being cut in parallel: a new sibling repo
  `incremental-instruction-creative-writing` (clean scripts/configs/final
  outputs only, no dev scaffolding or diagnostic runs) and one consolidated
  Hugging Face dataset repo of the same name (six configs: `benchmark`,
  `generations`, `pointwise_scores`, `pairwise_validation`,
  `evidence_first_validation`, `human_eval`), alongside the existing
  `sister-benchmark` / `sister-benchmark-generations` repos which remain
  published as legacy. Not tagged/released yet — pending manuscript results
  sync.

**Not yet built:**
- A judging persistence/validation module (a prior parallel attempt was
  removed as failed work — see above). Needed before running further
  automated judging in a repeatable way.
- Qualitative sampling of the structurally valid active score pool
  (`evaluations/scores.jsonl`), including the 46 long outputs.
- Completion of the remaining 19 human pairwise cases before any 30-case
  human-model estimate; pointwise-score statistics over merged scores (paired
  deltas, Wilcoxon, Cohen's d_z, the instruction-loss vs.
  creative-degradation decomposition).
- The transfer of verified results into manuscript text, figures, or tables.

**Known issues:**
- LM Studio model IDs must be obtained from the running server; UI display names may be truncated or differ from API IDs.
- The project must remain an experiment-and-paper repository rather than a product.

## Routing Table

| Task type | Load |
|-----------|------|
| Understanding how the evaluation and paper workflow works | `context/architecture.md` |
| Working with Python, LaTeX, or evaluation technologies | `context/stack.md` |
| Writing or reviewing code or paper files | `context/conventions.md` |
| Making a design or technology decision | `context/decisions.md` |
| Setting up, compiling, or running the project | `context/setup.md` |
| Working on datasets, protocols, metrics, or result artifacts | `context/evaluation.md` |
| Running a dataset-based multi-turn evaluation | `patterns/run-evaluation.md` |
| Updating the paper with verified results | `patterns/update-paper-results.md` |
| Adding or editing derived constraint/evaluation records | `patterns/derived-evaluation.md` |
| Diagnosing a failed or stuck evaluation run | `patterns/debug-evaluation-run.md` |
| Running or resuming judge scoring, or merging automated/manual score exports | `patterns/judge-and-merge-scores.md` |
| Reproducing the 30-pair evaluator-validation pass or analyzing a supplied human export | `patterns/pairwise-evaluator-validation.md` |
| Any specific task | Check `patterns/INDEX.md` for a matching pattern |

## Behavioural Contract

For every task, follow this loop:

1. **CONTEXT** — Load the relevant context file(s) from the routing table above. Check `patterns/INDEX.md` for a matching pattern. If one exists, follow it. Narrate what you load: "Loading architecture context..."
2. **BUILD** — Do the work. If a pattern exists, follow its Steps. If you are about to deviate from an established pattern, say so before writing code — state the deviation and why.
3. **VERIFY** — Load `context/conventions.md` and run the Verify Checklist item by item. State each item and whether the output passes. Do not summarise — enumerate explicitly.
4. **DEBUG** — If verification fails or something breaks, check `patterns/INDEX.md` for a debug pattern. Follow it. Fix the issue and re-run VERIFY.
5. **GROW** — After meaningful work, run this binary checklist:
   - **Ground:** What changed in reality? Name the changed behavior, system, command, dependency, or workflow.
   - **Record:** If project state changed, update the "Current Project State" section above. If documented facts changed, update the relevant `context/` file surgically.
   - **Orient:** If this task can recur and no pattern exists, create one in `patterns/` using `patterns/README.md`, then add it to `patterns/INDEX.md`. If a pattern exists but you learned a gotcha, update it.
   - **Write:** Update the `last_updated` marker in every scaffold file you changed when a real project date is available.
