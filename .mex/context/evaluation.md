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
last_updated: "2026-08-10"
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
  archived in `runs/test/older_outputs/reasoning_on/`, while non-reasoning baselines are
  archived in `runs/test/older_outputs/reasoning_off/`; the brief unsupported `none`
  attempt is isolated in `runs/test/older_outputs/reasoning_none/`. The fresh
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
- Result artifacts and storage location: the active flat root contains only
  the six completed current-model files, their independent combined dataset,
  and one index. The runner appends each raw generated
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
- LM Studio may omit `selected_variant` for an installed model. In that case,
  the runner records the safe derived quant identifier `model_key@quant_name`;
  it never records a local model path.
- A context cap is not a completion-token ceiling. Granite 4 H Tiny showed
  that a model can consume the remaining context and return `finish_reason:
  length`. The runner rejects that reply before writing it. For an explicitly
  chosen continuation, its first such response discards that entire attempt,
  increments the seed, and records the retry in `index.json`; a second ends
  the run cleanly as `stopped_context_overflow`.
- In the paused Granite partial run, all 15 non-`stop` rows were sharded
  turns at exactly 16,384 total tokens. Ten were intermediate turns; their
  oversized assistant messages altered the conversation subsequently sent to
  LM Studio, so 14 final conditions in that partial run are not valid evidence
  even where their own finish reason is `stop`. Before its continuation, use
  `--discard-context-overflow-attempts` to remove every one of those complete
  trajectories from both raw datasets and record the aggregate cleanup in the
  single index. This cleanup was performed before Granite's completed active
  result was finalized; its one remaining abandoned normal-stop intermediate
  row was also removed, leaving 1,156 active raw rows.
- The runner rejects any completion whose finish reason is not `stop` before
  it writes a raw record. This preserves immutable outputs without changing a
  model's prompt, sampling, or output ceiling; an affected run fails for
  review instead of admitting a truncated row.
- Bonsai 27B Q1_0 ignored `thinking_budget_tokens: 0` in a 2026-08-09 probe
  and emitted 685 reasoning tokens. Do not start its evaluation under that
  field alone; test an explicitly approved reasoning-off configuration first.
- Qwen 3.5 9B Q4_K_M ignored `reasoning: "off"` and
  `thinking_budget_tokens: 0` on LM Studio's OpenAI-compatible endpoint with
  its default template. Its brief native-API run is stopped and excluded
  because native chat cannot preserve the fixed-seed, OpenAI-compatible
  protocol used by the other model evaluations. A later OpenAI-compatible
  baseline start used the standard `{temperature: 0.8, seed: 12345,
  thinking_budget_tokens: 0}` settings and was stopped before its first raw
  response; it is likewise excluded. With a user-loaded custom template, a
  disposable request under those same settings returned `stop`, 58 completion
  tokens, and zero API-reported reasoning tokens. Record the template identity
  before treating a full run as reproducible evidence.
- The completed Qwen run uses that verified custom template, single-slot LM
  Studio configuration, and the flat active root. After two 16,384-context
  stops, its final continuation used 22,528 tokens; the index records every
  seed and context segment. Its retained raw rows all have `finish_reason:
  stop` and zero API-reported reasoning tokens.
- The Qwen run stopped after 254 saved raw records and 64 completed conditions:
  `historical_fiction/13` in the full condition returned `finish_reason:
  length` at 16,220 completion tokens and 16,384 total tokens. The runner
  rejected that response before writing it, then unloaded the model in its
  normal cleanup path. A disposable seed-1234 probe of that same instruction
  stopped normally at 879 completion tokens with zero reasoning tokens.
  Per user direction, the run continued at raw sequence 255 with seed 1234;
  `results/index.json` records the initial seed-12345 segment and the
  seed-1234 continuation segment. The older native-API Qwen partial is stored
  separately in `test/older_outputs/qwen_native_api_attempt/`.
- The installed Mistral target is `mistralai/mistral-7b-instruct-v0.3` at
  Q4_K_M.
- Mistral v0.3 Q4_K_M completed all 320 conditions with 1,156 raw records,
  normal stops, and zero reasoning-token rows. No collected GPT-OSS 20B run
  is a zero-reasoning baseline: the completed active-root file has nonzero
  reasoning tokens on 1,155/1,156 rows, and the completed file under the
  misleading `reasoning_off/` name has nonzero reasoning tokens on
  1,154/1,156 rows. The 8-row `reasoning_none/` and 282-row `reasoning_on/`
  partials also report nonzero reasoning on every row. Classify all GPT-OSS
  outputs as reasoning-enabled.
- Collaborator merge: use `runs/merge_results.py` only after each collaborator
  has completed a distinct model. It validates each source index and dual raw
  datasets, rejects duplicate models or record IDs, and creates fresh
  per-model files, combined JSONL, and one rebuilt index without source paths.
- A one-model queue is opt-in: `--wait-for-run-id RUN_ID` waits without
  touching result files until that exact predecessor is `completed`, then starts
  the explicitly supplied model. It never creates a default global sequence.
- `--context-length TOKENS` records a new `context_segments` entry when an
  explicitly continued run changes its context window. Previous raw rows retain
  their historical window through the preceding segment; the run-level model
  context denotes the active setting.
- Historical, partial, reasoning-mode, and diagnostic outputs are kept under
  `runs/test/older_outputs/`; they are not entries in the active index or
  combined dataset. Cydonia's 81-row partial is archived there separately.

## Boundaries

- This domain supports research experiments and paper reporting, not a product or production service.
- Do not change the dataset, model, prompt, turn count, or metric silently between runs.
- Keep experiment-specific complexity in this context and its patterns rather than spreading it across general architecture.
- Treat raw results as immutable evidence. Future scoring or annotation writes
  separate derived artifacts and never overwrites the per-model JSONL file or
  `all_results.jsonl`.
- Reserve the root-level `evaluations/` directory for those derived artifacts.
  It contains only an orientation README until the scoring protocol is decided.
