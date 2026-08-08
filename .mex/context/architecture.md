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
grounds_to: []
last_updated: "2026-08-07"
---

# Architecture

## System Overview

A dataset is supplied to a Python evaluation workflow.
The workflow evaluates whether LLM performance degrades across multi-turn conversations.
The evaluator entry point is `runs/run_experiment.py`; it uses LM Studio's
model interface and a tracked `runs/models.json` sequence with per-model
context lengths. Every generated raw response is written immediately to a
self-contained `results/<run-id>/outputs.json` document and to the matching
run group in `results/all.json`.
`results/index.json` connects the run datasets and records proof metadata for
review and exact resume.
Collaborators use verified results while editing the modular LaTeX paper files.
The existing Makefile or `build.ps1` compiles `main.tex` and its sections into the paper PDF.

## Key Components

- **Python evaluation workflow** — `runs/run_experiment.py` runs dataset-based multi-turn LLM evaluations.
- **Evaluation dataset** — `runs/benchmark_data.json` supplies 40 creative-writing tasks across romance and mystery.
- **Result artifacts** — one run directory per model/configuration,
  `results/all.json` for independent analysis across all runs, and
  `results/index.json` for run provenance, progress, compact record digests,
  and hashes.
- **LaTeX paper workspace** — `main.tex`, `sections/`, `figures/`, `tables/`, and `macros/` hold the collaborative manuscript.
- **Paper build pipeline** — `Makefile` and `build.ps1` compile the LaTeX source into a PDF.

## External Dependencies

- **Python runtime** — runs the evaluator; the supported version is [TO BE DETERMINED].
- **LLM inference access** — LM Studio provides model listing and chat completion over its OpenAI-compatible HTTP API; the endpoint and optional bearer token are configurable.
- **LaTeX distribution with `latexmk`** — compiles the paper; the supported distribution and version are [TO BE DETERMINED].
- **Git repository** — supports collaboration and review of Python, results, and `.tex` changes.

## What Does NOT Exist Here

- No product UI, production service, or user-facing application.
- No database or persistent service layer has been selected; this is [TO BE DETERMINED].
- No production deployment or over-engineered platform architecture.
