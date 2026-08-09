---
name: run-evaluation
description: Run and verify a dataset-based evaluation of LLM performance across multi-turn conversations.
triggers:
  - "run evaluation"
  - "run experiment"
  - "benchmark"
  - "multi-turn evaluation"
edges:
  - target: context/evaluation.md
    condition: when checking the dataset, protocol, metrics, or result contract
  - target: context/stack.md
    condition: when the Python runtime, model client, or analysis library is involved
  - target: context/conventions.md
    condition: when reviewing code cleanliness, comments, or artifact naming
  - target: context/architecture.md
    condition: when the evaluation's connection to result artifacts or paper updates is involved
  - target: context/setup.md
    condition: when the runtime or dependencies are not yet configured
grounds_to: []
last_updated: "2026-08-10"
---

# Run Evaluation

## Context

Load `context/evaluation.md` and confirm the current dataset, selected backend, model, multi-turn protocol, metrics, and result contract before running anything. The Python entry point is `runs/run_experiment.py`; it uses only the standard library and supports LM Studio and Ollama.

## Steps

1. Confirm the intended dataset version, model, prompt/turn configuration, and metric configuration.
2. Confirm Python 3.10+, start the selected backend, list its exact model IDs or tags, then use `python3 runs/run_experiment.py --backend BACKEND --models MODEL …` for a fresh evaluation. Every run is capped at 16,384 context tokens. Use `--limit 3` for a smoke test. Add `--resume` only to deliberately recover a known interrupted run in the active `results/` directory.
3. Run the evaluator without silently changing protocol inputs.
4. The runner appends every generated raw response immediately to `results/results_<model>.jsonl` and `results/all_results.jsonl`. Every JSONL line carries the model name, parameters, and quant file; `all_results.jsonl` is the combined independent dataset, and `results/index.json` is the only metadata file. LM Studio loads and unloads each selected model; Ollama manages model residency itself. Use `--resume` only for an exact model/protocol/context/runner match; it reconciles interrupted dual writes before generating anything new.
5. Inspect the result for completion, errors, and the metadata needed to reproduce it.
6. Pass only verified results to the paper-editing workflow.

## Gotchas

- Do not compare runs whose dataset, model, prompt, turn count, or metric differs without recording the difference.
- Before changing a reasoning mode, archive the prior result set in a distinct
  subdirectory and start from an empty active results root; never mix the two.
- Verify risky model-load settings with a temporary load and immediate unload
  before launching the benchmark. In the current setup, Mistral 7B Q8 fails at
  32K but has been verified at 22,528 tokens with GPU KV-cache offload enabled.
- High reasoning can consume an entire context window without visible output;
  do not enable it for this full sequential benchmark without an explicit
  completion-token policy and an updated runtime estimate.
- For the current GPT-OSS installation, disable reasoning by omitting
  `reasoning_effort`; do not send `off` or `none`. Validate the exact API
  behavior with a temporary load/request/unload before a full restart.
- Do not add product infrastructure or abstractions to solve a one-off experiment need.
- Treat missing reproducibility metadata as a failure until the required fields are defined.
- Some LM Studio records omit `selected_variant`. Verify that the runner emits
  the safe fallback `model_key@quant_name` before a full run; never use a
  local model path as a substitute.
- Reject a reply with any finish reason other than `stop` before writing it to
  either raw dataset. Do not retrofit a token ceiling or resume an affected
  run without an explicit user decision, because either could change outputs.
- When the user explicitly elects recovery after a `length` response, use the
  runner's first-overflow retry rule rather than admitting a truncated reply:
  it removes the incomplete attempt, increments and logs the seed, and stops
  cleanly if a second context-length response occurs. Use
  `--wait-for-run-id` only for a user-approved one-model handoff.
- A zero thinking-token budget is model-specific evidence, not a general
  reasoning-off control. Probe every new model for visible reasoning content
  and reasoning-token usage before its full run.

## Verify

- [ ] Dataset and protocol inputs are identified.
- [ ] The evaluator completed without silent failures.
- [ ] Every generated raw response appears with the same `record_id` in both its per-model JSONL file and `results/all_results.jsonl`.
- [ ] `results/index.json` includes the exact model, instance, context, inference parameters, lifecycle status, progress, compact record digests, and hashes.
- [ ] A `--resume` invocation either skips an exact completed run or reconciles the matching incomplete run without producing duplicate record IDs.
- [ ] The independent `results/all_results.jsonl` can be consumed by the later analysis workflow.

## Debug

Check the dataset interface, model access, protocol configuration, metric computation, and result serialization in that order. The runner prints diagnostics for HTTP failures, unreachable LM Studio servers, malformed responses, and non-text assistant content.

## Update Scaffold

- [ ] Update `.mex/context/evaluation.md` with facts learned from the run.
- [ ] Update `.mex/ROUTER.md` if the project state changed.
- [ ] Record recurring failure modes here after they occur.
