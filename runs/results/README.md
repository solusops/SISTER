# `runs/results/` — what this folder actually is

This is not benchmark data — it's evidence from running the benchmark
against baseline models. Every file here is an *output* of
`run_experiment.py`, not something you'd hand-edit.

- `results_<model>.jsonl` — one file per completed model, raw generation
  records (1,156 rows / 320 final conditions each).
- `all_results.jsonl` — the same rows, combined across all completed
  models. Kept locally for convenience; not re-pushed to the Hub
  separately (it's a duplicate of the per-model files — see
  `runs/hf_upload/README.md`).
- `index.json` — run provenance and integrity metadata: which
  `benchmark_data.json` version (by `sha256`) each run used, per-model
  progress, generation/context segments.

Published on Hugging Face as its own dataset repo, one split per model:
`YOUR_USERNAME/sister-benchmark-generations`.

## The prompts these responses are to

Not in this folder. See `../benchmark_data.json` and `../BENCHMARK.md` —
published separately as `YOUR_USERNAME/sister-benchmark`. Each row here
only carries a lightweight `item` back-reference (`domain`, `item_id`,
`title`); join on those against the benchmark for the actual
instruction/shard text.

## What's still missing here

Scores. This folder has raw model *outputs*, not evaluation *results* —
whether a given output actually satisfied its task's constraints hasn't
been computed yet. That scoring layer belongs in `../evaluations/`, keyed
by `record_id`, and must never modify these files.
