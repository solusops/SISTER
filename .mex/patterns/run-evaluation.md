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
last_updated: "2026-08-07"
---

# Run Evaluation

## Context

Load `context/evaluation.md` and confirm the current dataset, model, multi-turn protocol, metrics, and result contract before running anything. The Python entry point is `runs/run_experiment.py`; it uses only the standard library and sends requests to LM Studio's OpenAI-compatible API.

## Steps

1. Confirm the intended dataset version, model, prompt/turn configuration, and metric configuration.
2. Confirm Python 3.10+, start LM Studio's local server, review the exact IDs and context lengths in `runs/models.json`, then use `python3 runs/run_experiment.py --sequence --resume`; use `--limit 3` for a smoke test.
3. Run the evaluator without silently changing protocol inputs.
4. The runner writes every generated raw response immediately to both `results/<run-id>/outputs.json` and the matching run group in `results/all.json`. Shared model and protocol data appears once per run rather than on every output. By default, it loads one model through LM Studio's native API, runs it, and unloads its returned instance before moving on. `results/index.json` records the exact model identity, instance, context, inference parameters, lifecycle, progress, compact record digests, and hashes needed to review the evidence. Use `--resume` only for an exact model/protocol/context/runner match; it reconciles interrupted dual writes before generating anything new.
5. Inspect the result for completion, errors, and the metadata needed to reproduce it.
6. Pass only verified results to the paper-editing workflow.

## Gotchas

- Do not compare runs whose dataset, model, prompt, turn count, or metric differs without recording the difference.
- Do not add product infrastructure or abstractions to solve a one-off experiment need.
- Treat missing reproducibility metadata as a failure until the required fields are defined.

## Verify

- [ ] Dataset and protocol inputs are identified.
- [ ] The evaluator completed without silent failures.
- [ ] Every generated raw response appears with the same `record_id` in both the run dataset and its `results/all.json` run group.
- [ ] `results/index.json` includes the exact model, instance, context, inference parameters, lifecycle status, progress, compact record digests, and hashes.
- [ ] A `--resume` invocation either skips an exact completed run or reconciles the matching incomplete run without producing duplicate record IDs.
- [ ] The independent `results/all.json` can be consumed by the later analysis workflow.

## Debug

Check the dataset interface, model access, protocol configuration, metric computation, and result serialization in that order. The runner prints diagnostics for HTTP failures, unreachable LM Studio servers, malformed responses, and non-text assistant content.

## Update Scaffold

- [ ] Update `.mex/context/evaluation.md` with facts learned from the run.
- [ ] Update `.mex/ROUTER.md` if the project state changed.
- [ ] Record recurring failure modes here after they occur.
