---
name: architecture
description: How the evaluation workflow and collaborative paper workspace connect. Load when working on system design, integrations, or understanding how components interact.
triggers:
  - "architecture"
  - "system design"
  - "evaluation flow"
  - "how does an experiment connect to the paper"
edges:
  - target: context/stack.md
    condition: when specific Python, evaluation, or LaTeX technology details are needed
  - target: context/evaluation.md
    condition: when the dataset, multi-turn protocol, metrics, or result contract is involved
  - target: context/conventions.md
    condition: when implementing a new evaluation or editing paper-supporting code
  - target: patterns/run-evaluation.md
    condition: when executing or reproducing an evaluation run
  - target: patterns/update-paper-results.md
    condition: when verified evaluation results are being transferred into the paper
  - target: patterns/derived-evaluation.md
    condition: when adding or editing derived constraint/evaluation records under evaluations/
grounds_to: []
last_updated: "2026-08-14"
---

# Architecture

## System Overview

A dataset is supplied to a Python evaluation workflow.
The workflow evaluates whether LLM performance degrades across multi-turn conversations.
The evaluator entry point is `runs/run_experiment.py`; it supports explicit
model selection through LM Studio or Ollama, rather than a fixed model queue.
Every generated raw response is written immediately to a flat per-model JSONL
file and to `runs/results/all_results.jsonl`.
`runs/results/index.json` records provenance, progress, generation segments,
context segments, and integrity metadata for the active dataset.
Collaborators use verified results while editing the manuscript source retained
under `paper/`. GitHub Actions compiles `paper/main.tex` and publishes the PDF
as a workflow artifact; the repository does not commit generated PDFs or keep
local build wrappers.

## Key Components

- **Python evaluation workflow** — `runs/run_experiment.py` runs dataset-based multi-turn LLM evaluations.
- **Evaluation dataset** — `runs/benchmark_data.json` supplies 160
  creative-writing tasks across six genres in full-instruction and sharded
  multi-turn conditions.
- **Result artifacts** — one flat JSONL file per active model configuration,
  `runs/results/all_results.jsonl` for independent analysis across all active
  runs, and `runs/results/index.json` for provenance, progress, compact record
  digests, and integrity metadata. Superseded and diagnostic outputs are
  isolated under `runs/test/older_outputs/`.
- **Manuscript source** — `paper/` holds the editable draft, section files,
  figures, tables, macros, and bibliography.
- **Derived evaluation** — `evaluations/constraints.jsonl` and
  `constraint_schema.json` hold atomic creative-writing constraints extracted
  from `runs/benchmark_data.json`, one record per `story_id`, referencing
  generation `record_id`s rather than duplicating raw text. The judge harness
  and statistics layer that will consume these are not yet built.
- **Hugging Face publishing** — `runs/hf_upload/push_benchmark.py` and
  `push_generations.py` push the benchmark and the generation evidence to two
  independently versioned Hub dataset repos (`sister-benchmark`,
  `sister-benchmark-generations`); documented in `runs/BENCHMARK.md` and
  `runs/results/README.md`.

## External Dependencies

- **Python 3.10+ runtime** — runs the evaluator, merger, and dashboard using
  only the standard library.
- **LLM inference access** — LM Studio and Ollama provide local model listing
  and chat completion over OpenAI-compatible HTTP APIs; endpoints are
  configurable.
- **Git repository** — supports collaboration and review of Python, results, and `.tex` changes.

## What Does NOT Exist Here

- No product UI, production service, or user-facing application.
- No database or persistent service layer has been selected; this is [TO BE DETERMINED].
- No production deployment or over-engineered platform architecture.
- No committed PDF output or local document-generation wrapper is maintained in
  this repository.
