---
name: setup
description: Development environment setup and commands for running evaluations and compiling the paper.
triggers:
  - "setup"
  - "install"
  - "environment"
  - "getting started"
  - "how do I run"
edges:
  - target: context/stack.md
    condition: when specific technology versions or libraries are needed
  - target: context/architecture.md
    condition: when understanding how setup commands fit the evaluation-to-paper flow
  - target: context/evaluation.md
    condition: when configuring a dataset, model access, evaluation protocol, or result output
  - target: patterns/run-evaluation.md
    condition: when setup is complete and an evaluation run is being executed
grounds_to: []
last_updated: "2026-08-14"
---

# Setup

## Prerequisites

- Python: Python 3.10+ is recommended; the runner uses only the standard library.
- Git for collaborative repository work.

## First-time Setup

1. Clone or open the repository and confirm `python3 --version` reports 3.10+. No virtualenv or requirements file exists — the runner is stdlib-only (see `context/stack.md`).
2. No Python package installation is required for the runner. `runs/hf_upload/` (Hugging Face publishing only, not needed to run evaluations) additionally requires `datasets` and `huggingface_hub`.
3. Configure either LM Studio's local server or Ollama with the desired model.

The manuscript source is compiled by the GitHub Actions workflow; no local PDF
build setup is required for this repository.

## Environment Variables

- LM Studio endpoint: `LM_STUDIO_BASE_URL` (defaults to
  `http://localhost:1234/v1`). Optional bearer token:
  `LM_STUDIO_API_KEY` (defaults to `lm-studio`).
- Ollama endpoint: `OLLAMA_BASE_URL` (defaults to `http://localhost:11434`).
- Dataset location: `runs/benchmark_data.json`, resolved by the runner
  relative to its own file location — it must stay next to
  `run_experiment.py` unless the `DATA_PATH` constant is changed.
- Evaluation output location: `--output results` (default) writes into
  `runs/results/` — `results_<model>.jsonl` per model, `all_results.jsonl`
  combined, `index.json` as the single status/provenance file.

## Common Commands

- `python3 runs/run_experiment.py --backend lmstudio --list-models` — list
  exact LM Studio model IDs.
- `python3 runs/run_experiment.py --backend ollama --list-models` — list exact
  locally available Ollama tags.
- `python3 runs/run_experiment.py --backend lmstudio --models MODEL_ID` — run
  one or more explicit LM Studio model IDs.
- `python3 runs/run_experiment.py --backend ollama --models MODEL_TAG` — run
  one or more explicit Ollama tags. Every run uses a fixed 16,384-token cap.
- Add `--resume` only to recover a known interrupted run in the current
  `results/` directory. Do not infer resumable work from archived, legacy, or
  error-context artifacts.
- Add `--limit 3` for a smoke test. The default `--output results` appends to
  `results/results_<model>.jsonl` and `results/all_results.jsonl`; every line
  identifies its model, parameters, and quant file. `results/index.json` is
  the single status and provenance index.
- `python3 runs/merge_results.py --output merged_results collaborator_a/results collaborator_b/results`
  — validate and merge completed, distinct-model collaborator result directories.

## Common Issues

- Evaluation setup or execution failures: Confirm the selected backend is
  running, use its `--list-models` output to obtain exact IDs or tags, and
  ensure each requested model is available before starting a long run.
- LaTeX compilation failures: [TO BE DETERMINED after the first collaborative build issue].
