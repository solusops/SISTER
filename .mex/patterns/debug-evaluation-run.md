---
name: debug-evaluation-run
description: Diagnose a failed, stuck, or suspicious evaluation run — connectivity, model ID mismatches, rejected/overflowed completions, reasoning-mode leakage.
triggers:
  - "run failed"
  - "evaluation stuck"
  - "finish_reason"
  - "context overflow"
  - "debug run"
edges:
  - target: patterns/run-evaluation.md
    condition: for the normal run steps and command reference this pattern assumes
  - target: context/evaluation.md
    condition: for the full list of model-specific quirks already recorded (Granite, Qwen, GPT-OSS, Mistral, Bonsai)
  - target: context/setup.md
    condition: when the backend itself (LM Studio/Ollama) may not be running or reachable
grounds_to:
  - node: "class:f99c6c10b0f7c0b62decbea75bc24c17"
    fingerprint: "mh:64:7b226d696e68617368223a5b31383134343139392c313134333135323739362c3836333436343639302c3234333834363135342c313330313436373933352c323431313835323434332c3135313431343531372c3536333530333831372c313431393035343033302c313430343338393131352c3135303738303934362c3132353037333139332c3935383231393537352c3434343834313132332c3735393330393530302c32373732313037342c3737363234303335342c3832373734363539372c3135303733353532342c31363538383035392c3338303134343636332c323032363037353137312c3331333536323535312c313434303332363937382c3239333632393835382c3731333331303832372c3334383434343538322c3231333137393432312c3430313436353230392c3337353531393738352c3631323437303432302c3538353336313531342c3435333330333332342c3534313139313834392c38383736343531392c3531373337383830322c3539333438303139312c31303836393338392c3539363233303931302c3737393034383135362c3534333038363534362c313036333233303230332c3435353336313934352c3437303938363532372c313030393030373336302c3132393138363339382c3339383634353135382c3435343439313636392c3431333033353737322c3132303632313938342c3638393733383734312c3331373831383530332c313735383835303631312c3631353736383632312c3632393534373037382c3639393438333633352c3133363036323735352c3638333539333932392c3535303538333235322c3932333131303830392c313736383933333631382c313231393135343139352c3133303139353939332c31313732363932355d2c226e65696768626f7273223a5b5d2c22746f6b656e436f756e74223a397d"
last_updated: "2026-08-14"
---

# Debug Evaluation Run

## Context

The runner (`runs/run_experiment.py`) rejects any completion whose `finish_reason` is not `stop` before writing it, and treats a context-length overflow via a dedicated retry path (see [`ContextOverflowStopped`](mex://class:f99c6c10b0f7c0b62decbea75bc24c17)). This makes "run failed" almost always one of a small number of known boundaries rather than a generic crash — check them in order.

## Steps (diagnosis order)

1. **Backend reachable?** Confirm the selected backend is actually running: `python3 runs/run_experiment.py --backend {lmstudio,ollama} --list-models`. A connection error here means LM Studio/Ollama isn't up, not a runner bug.
2. **Model ID exact?** LM Studio and Ollama UI display names can be truncated or differ from the API ID. Always take the ID from `--list-models` output, never from the app's UI.
3. **Context overflow?** A `finish_reason: length` response is rejected before it's written — this is expected behavior, not a bug. Check `results/index.json` for a recorded retry/seed increment. Two consecutive overflow responses stop the run cleanly as `stopped_context_overflow` by design.
4. **Reasoning leaking through?** Some models ignore reasoning-off settings (`reasoning: "off"`, `thinking_budget_tokens: 0`) — recorded precedent: Bonsai 27B Q1_0 emitted 685 reasoning tokens despite a zero budget; Qwen 3.5 9B Q4_K_M ignored both fields on its default template and needed a verified custom template before its run counted as reproducible; GPT-OSS 20B evaluations are classified reasoning-enabled entirely because every collected variant has nonzero reasoning tokens on nearly every row. Before trusting a "reasoning-off" run, check actual reasoning-token counts in the raw output, not just the request settings.
5. **Mixed result provenance?** If numbers look inconsistent, check whether some rows came from `runs/test/older_outputs/` (archived/partial/reasoning-mode/diagnostic) rather than the active `runs/results/` set — these must never be treated as the same evidence pool.
6. **Dual-write mismatch?** If a record appears in `results_<model>.jsonl` but not `all_results.jsonl` (or vice versa), the process likely stopped between the two writes — `--resume` reconciles this; do not hand-edit either file to fix it.

## Gotchas

- A context cap is not a completion-token ceiling — a model can consume the entire remaining context and return `finish_reason: length` well before hitting any intended output limit (recorded precedent: Granite 4 H Tiny).
- `--resume` is only for a genuinely interrupted run in the *current* `results/` directory — it must never be pointed at archived/error-context artifacts to "recover" them.
- LM Studio may omit `selected_variant` for an installed model; the runner falls back to `model_key@quant_name`, never a local filesystem path. If you see a local path in a record, something upstream of the runner's own logic wrote it.
- GPU KV-cache allocation can fail silently at high context windows on some models (recorded precedent: Mistral 7B Q8 failing at 32K, needing 16K or 22,528-with-offload) — a load failure isn't always a code bug.

## Verify

- [ ] The failure boundary was identified from the list above before any code change was proposed.
- [ ] `results/index.json` for the affected model shows the expected lifecycle status (`completed`, `stopped_context_overflow`, or an explicit interrupted state) — not silence.
- [ ] No archived/partial/`older_outputs` data was mixed into the active result set to "complete" a run.
- [ ] If a retry or resume was used, the record count in both JSONL files still matches `results/index.json`'s recorded totals.

## Debug

If none of the above explains the failure, read the runner's own printed diagnostics first — it reports HTTP failures, unreachable servers, malformed responses, and non-text assistant content directly. Reproduce with `--limit 3` before re-running the full sequence.

## Update Scaffold

- [ ] Add a new bullet to `.mex/context/evaluation.md` when a new model-specific quirk is discovered, following the existing per-model bullet style there.
- [ ] If a genuinely new failure boundary is found (not covered by steps 1–6 above), add it here rather than starting a separate debug pattern.
