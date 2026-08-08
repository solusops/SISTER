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
last_updated: "2026-08-08"
---

# Evaluation

## Purpose

Measure whether LLM performance degrades in multi-turn conversations for the research paper.

## Protocol

- Dataset source and schema: `runs/benchmark_data.json`, containing 160 items
  across comedy, fantasy, historical fiction, mystery, romance, and science
  fiction; each item has one full instruction and 5–9 ordered shards.
- Models and inference interface: collaborators select exact model IDs with
  `--backend lmstudio|ollama --models MODEL …`. Every run uses a fixed 16,384
  context-token cap and omits the reasoning field. LM Studio loads one model at
  a time through native `POST /api/v1/models/load`, sends completions through
  `POST /v1/chat/completions`, and unloads the returned instance. Ollama uses
  `GET /api/tags` for model discovery and `POST /api/chat` with `num_ctx` set
  to the same cap. The explicit selection is recorded in `index.json` so the
  dashboard can project a batch ETA from the active model's observed rate.
- Context policy: use at most 32K for models under 20B parameters and 16K for
  models at or above 20B. Mistral 7B Q8 also uses 16K: at 32K its GPU KV cache
  required an additional 4 GiB and failed to allocate on the available GPU.
- Active run policy: every explicit model selection uses 16,384 context tokens
  and sends no `reasoning_effort` field. Keep result sets from different
  reasoning modes separate: the earlier partial high-reasoning attempt is
  archived in `runs/results/reasoning_on/`, while non-reasoning baselines are
  archived in `runs/results/reasoning_off/`; the brief unsupported `none`
  attempt is isolated in `runs/results/reasoning_none/`. The fresh
  non-reasoning sequence writes to `runs/results/`.
- Conversation prompts, turn count, and state handling: The `full` condition
  sends the complete instruction in one user turn. The `sharded` condition
  sends each shard as a separate user turn, retaining every assistant reply in
  the conversation and scoring the final reply.
- Baselines and comparison conditions: archived or error-context artifacts are
  not experiment evidence and must not be treated as saved runs. A normal
  invocation starts a fresh, versioned raw-result run; it does not mix or
  silently resume legacy files. Use `--resume` only when deliberately
  recovering a known interrupted run in the active results directory.

## Metrics and Results

- Primary performance metric: [TO BE DETERMINED — populate after first implementation].
- Supporting metrics and aggregation: [TO BE DETERMINED — populate after first implementation].
- Result artifacts and storage location: the runner appends each raw generated
  response to `results/results_<model>.jsonl` and to
  `results/all_results.jsonl`, the independent combined dataset. Every JSONL
  line contains `model_id`, `model_name`, `parameters`, and `quant_file` as
  well as the task, condition, turn, text, and metrics. `results/index.json`
  is the only metadata file; it records model configuration, lifecycle,
  progress, and integrity checks. Result artifacts contain no absolute local
  paths. If a process stops between the two writes, `--resume` reconciles the
  matching record IDs without regenerating output.
- Minimum metadata needed to reproduce a result: the raw record plus its
  matching `results/index.json` entry, which supplies the exact run ID, model
  identity, context, inference settings, dataset/protocol/runner hashes,
  lifecycle, and file hashes needed for independent review.
- Collaborator merge: use `runs/merge_results.py` only after each collaborator
  has completed a distinct model. It validates each source index and dual raw
  datasets, rejects duplicate models or record IDs, and creates fresh
  per-model files, combined JSONL, and one rebuilt index without source paths.

## Boundaries

- This domain supports research experiments and paper reporting, not a product or production service.
- Do not change the dataset, model, prompt, turn count, or metric silently between runs.
- Keep experiment-specific complexity in this context and its patterns rather than spreading it across general architecture.
- Treat raw results as immutable evidence. Future scoring or annotation writes
  separate derived artifacts and never overwrites the per-model JSONL file or
  `all_results.jsonl`.
