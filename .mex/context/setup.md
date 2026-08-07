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
last_updated: "2026-08-07"
---

# Setup

## Prerequisites

- Python: Python 3.10+ is recommended; the runner uses only the standard library.
- A LaTeX distribution with `latexmk`: supported distribution/version is [TO BE DETERMINED].
- Git for collaborative repository work.

## First-time Setup

1. Clone or open the repository and confirm the Python environment: [TO BE DETERMINED].
2. No Python package installation is required for the runner.
3. Configure LM Studio's local server and load the desired models.
4. Compile the paper with `make` to verify the LaTeX toolchain.

## Environment Variables

- LM Studio endpoint: `LM_STUDIO_BASE_URL` (defaults to
  `http://localhost:1234/v1`). Optional bearer token:
  `LM_STUDIO_API_KEY` (defaults to `lm-studio`).
- Dataset location or identifier: [TO BE DETERMINED].
- Evaluation configuration/output location: [TO BE DETERMINED].

## Common Commands

- `make` — compile the paper PDF.
- `make watch` — continuously recompile the paper while editing.
- `make clean` — remove LaTeX build artifacts and the generated PDF.
- `make diff REF=HEAD~1` — generate a LaTeX diff against a Git revision.
- `python3 runs/run_experiment.py --list-models` — list exact model IDs exposed
  by LM Studio.
- `python3 runs/run_experiment.py --sequence --resume` — run or resume the
  tracked `runs/models.json` sequence. Each entry carries its own context
  length; each model is explicitly loaded and unloaded before the next starts.
- Use `--no-manage-models` only when LM Studio is already managing model
  lifecycles externally.
- Add `--limit 3` for a smoke test. The default `--output results` writes
  immediate raw copies to `results/<run-id>/outputs.json` and the matching run
  group in `results/all.json`; `results/index.json` contains the provenance,
  progress, hashes, and compact record digests required to audit or resume.

## Common Issues

- Evaluation setup or execution failures: Confirm LM Studio's server is
  running, use `--list-models` to obtain exact API IDs, and ensure each model
  is available to the server before starting a long run.
- LaTeX compilation failures: [TO BE DETERMINED after the first collaborative build issue].
