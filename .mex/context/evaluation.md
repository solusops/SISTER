---
name: evaluation
description: Experimental protocol and result contract for measuring LLM performance across multi-turn conversations. Load when changing datasets, prompts, models, metrics, or evaluation outputs.
triggers:
  - "evaluation"
  - "experiment"
  - "multi-turn"
  - "dataset"
  - "metric"
  - "benchmark"
edges:
  - target: context/architecture.md
    condition: when the evaluation flow or its connection to the paper changes
  - target: context/stack.md
    condition: when choosing Python libraries, model clients, or analysis tools
  - target: context/conventions.md
    condition: when implementing or reviewing evaluation code and result artifacts
  - target: patterns/run-evaluation.md
    condition: when executing an evaluation or reproducing a result
  - target: patterns/update-paper-results.md
    condition: when transferring verified evaluation results into the paper
grounds_to: []
last_updated: "2026-08-07"
---

# Evaluation

## Purpose

Measure whether LLM performance degrades in multi-turn conversations for the research paper.

## Protocol

- Dataset source and schema: `runs/benchmark_data.json`, containing 160 items
  across comedy, fantasy, historical fiction, mystery, romance, and science
  fiction; each item has one full instruction and 5–9 ordered shards.
- Models and inference interface: The tracked `runs/models.json` plan contains
  the exact LM Studio model IDs, per-model context lengths, and optional
  reasoning settings. The runner loads one model at a time through native
  `POST /api/v1/models/load`, sends completions through
  `POST /v1/chat/completions`, and unloads the returned instance before
  continuing. `--sequence` executes this plan in order; command-line context
  and reasoning overrides are recorded in the affected run.
- Conversation prompts, turn count, and state handling: The `full` condition
  sends the complete instruction in one user turn. The `sharded` condition
  sends each shard as a separate user turn, retaining every assistant reply in
  the conversation and scoring the final reply.
- Baselines and comparison conditions: historical collaborator outputs are
  isolated artifacts. The new runner deliberately uses its own versioned raw
  result contract; it does not mix or silently resume any legacy result file.

## Metrics and Results

- Primary performance metric: [TO BE DETERMINED — populate after first implementation].
- Supporting metrics and aggregation: [TO BE DETERMINED — populate after first implementation].
- Result artifacts and storage location: the runner writes every raw generated
  response immediately to both `results/<run-id>/outputs.json` (one
  self-contained model/configuration run) and the matching run group in
  `results/all.json` (the independently usable raw dataset across all models
  and runs). Run-level fields—model/context settings, generation settings, and
  dataset/protocol provenance—are stored once in the run manifest and once in
  the aggregate run group; compact output records contain only item identity,
  turn/output data, and a stable record ID. `results/index.json` is the proof
  and review index: it records run configuration fingerprints, hashes of the
  dataset/prompt/runner and raw files, model identity, lifecycle state, errors,
  progress, and compact record-count/record-ID digests. If a process stops
  between the two writes, `--resume` reconciles matching record IDs without
  regenerating output.
- Minimum metadata needed to reproduce a result: the raw record and its
  enclosing run directory or aggregate run group; the matching index entry
  supplies the exact run ID, model identity, context, inference settings,
  dataset/protocol/runner hashes, lifecycle, and file hashes needed for
  independent review.

## Boundaries

- This domain supports research experiments and paper reporting, not a product or production service.
- Do not change the dataset, model, prompt, turn count, or metric silently between runs.
- Keep experiment-specific complexity in this context and its patterns rather than spreading it across general architecture.
- Treat raw results as immutable evidence. Future scoring or annotation writes
  separate derived artifacts and never overwrites `outputs.json` or `all.json`.
