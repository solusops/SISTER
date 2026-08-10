---
name: router
description: Session bootstrap and navigation hub. Read at the start of every session before any task. Contains project state, routing table, and behavioural contract.
edges:
  - target: context/architecture.md
    condition: when working on system design, integrations, or understanding how evaluation and paper components connect
  - target: context/stack.md
    condition: when working with Python, LaTeX, evaluation libraries, or making technology decisions
  - target: context/conventions.md
    condition: when writing or reviewing Python or LaTeX changes
  - target: context/decisions.md
    condition: when making an architectural or technology choice, or understanding why one was made
  - target: context/setup.md
    condition: when setting up the environment, compiling the paper, or running project commands
  - target: context/evaluation.md
    condition: when working on datasets, models, multi-turn protocols, metrics, or result artifacts
  - target: patterns/INDEX.md
    condition: when starting any task and looking for a repeatable workflow
last_updated: "2026-08-10"
---

# Session Bootstrap

If you haven't already read `.mex/AGENTS.md`, read it now — it contains the project identity, non-negotiables, and commands.

Then read this file fully before doing anything else in this session.

## Current Project State

**Working:**
- The repository retains an editable manuscript source under `paper/`, alongside
  the study materials and active generation data. GitHub Actions compiles it as
  a downloadable artifact without committing generated PDFs.
- As of 2026-08-10, the active flat `runs/results/` dataset contains exactly
  six completed models: GPT-OSS 20B, Gemma 4 12B QAT, Llama 3.1 8B, Granite 4
  H Tiny, Mistral 7B Instruct v0.3, and Qwen 3.5 9B Q4_K_M. Each has 320 final
  conditions and 1,156 raw records; the combined dataset has 6,936 unique
  records. Qwen's index retains its seed and 16K-to-22,528 context segments;
  Granite's first context-length retry is likewise recorded. Cydonia, prior
  reasoning-mode outputs, failed/partial attempts, diagnostics, and caches
  are isolated under `runs/test/older_outputs/`.
- The project goal is defined: evaluate whether LLM performance degrades in multi-turn conversations.
- `runs/run_experiment.py` evaluates 160 creative-writing tasks across six
  domains using full and sharded multi-turn conditions.
- The runner supports both LM Studio and Ollama. Collaborators select explicit
  model IDs with `--backend {lmstudio,ollama} --models …`; every run is capped
  at 16,384 context tokens and uses the OpenAI-compatible LM Studio endpoint.
  It appends every raw response immediately to a readable per-model JSONL file
  and an independent combined JSONL dataset; `results/index.json` records
  provenance and progress. `--resume` is reserved for a known interrupted run
  in the active results directory.
  Historical, partial, reasoning-mode, and diagnostic outputs are isolated
  under `runs/test/older_outputs/`.
- Do not use `runs/context error/` as run history.
- The root README is publication-facing: it states the research question,
  distinguishes active results from archival diagnostics, links operational
  run instructions, and provides the current manuscript citation. `CITATION.cff`
  mirrors the title and author metadata for repository citation tools.
- Root-level `evaluations/` is reserved for future derived scoring. It remains
  intentionally empty except for its README until the protocol is decided;
  model generations remain under `runs/results/`.

**Not yet built:**
- The scoring workflow and the transfer of verified results into manuscript text,
  figures, or tables.

**Known issues:**
- LM Studio model IDs must be obtained from the running server; UI display names may be truncated or differ from API IDs.
- The project must remain an experiment-and-paper repository rather than a product.

## Routing Table

| Task type | Load |
|-----------|------|
| Understanding how the evaluation and paper workflow works | `context/architecture.md` |
| Working with Python, LaTeX, or evaluation technologies | `context/stack.md` |
| Writing or reviewing code or paper files | `context/conventions.md` |
| Making a design or technology decision | `context/decisions.md` |
| Setting up, compiling, or running the project | `context/setup.md` |
| Working on datasets, protocols, metrics, or result artifacts | `context/evaluation.md` |
| Running a dataset-based multi-turn evaluation | `patterns/run-evaluation.md` |
| Updating the paper with verified results | `patterns/update-paper-results.md` |
| Any specific task | Check `patterns/INDEX.md` for a matching pattern |

## Behavioural Contract

For every task, follow this loop:

1. **CONTEXT** — Load the relevant context file(s) from the routing table above. Check `patterns/INDEX.md` for a matching pattern. If one exists, follow it. Narrate what you load: "Loading architecture context..."
2. **BUILD** — Do the work. If a pattern exists, follow its Steps. If you are about to deviate from an established pattern, say so before writing code — state the deviation and why.
3. **VERIFY** — Load `context/conventions.md` and run the Verify Checklist item by item. State each item and whether the output passes. Do not summarise — enumerate explicitly.
4. **DEBUG** — If verification fails or something breaks, check `patterns/INDEX.md` for a debug pattern. Follow it. Fix the issue and re-run VERIFY.
5. **GROW** — After meaningful work, run this binary checklist:
   - **Ground:** What changed in reality? Name the changed behavior, system, command, dependency, or workflow.
   - **Record:** If project state changed, update the "Current Project State" section above. If documented facts changed, update the relevant `context/` file surgically.
   - **Orient:** If this task can recur and no pattern exists, create one in `patterns/` using `patterns/README.md`, then add it to `patterns/INDEX.md`. If a pattern exists but you learned a gotcha, update it.
   - **Write:** Update the `last_updated` marker in every scaffold file you changed when a real project date is available.
