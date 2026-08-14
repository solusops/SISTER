"""
Push the SISTER benchmark (the 160 tasks) to its own Hugging Face dataset
repo. Run this independently of push_generations.py -- the benchmark has
its own lifecycle (grows over time via new task versions) and shouldn't be
coupled to any one experiment run.

Setup:
    pip install datasets huggingface_hub
    huggingface-cli login          # or: export HF_TOKEN=hf_xxx

Usage (run from the repo root):
    python runs/hf_upload/push_benchmark.py --repo-id YOUR_USERNAME/sister-benchmark

    # public instead of the default private:
    python runs/hf_upload/push_benchmark.py --repo-id YOUR_USERNAME/sister-benchmark --public

After pushing, tag the release on the Hub (Settings -> or via
`huggingface-cli tag`) so anyone can pin to the exact version their
generations were run against, e.g. v1.0 for the initial 160 tasks. See
../BENCHMARK.md for the version table to keep updated alongside this.
"""

import argparse
import json

from datasets import Dataset


def load_benchmark(path: str) -> Dataset:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return Dataset.from_list(data)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo-id", required=True, help="e.g. your-username/sister-benchmark")
    ap.add_argument("--benchmark", default="runs/benchmark_data.json")
    ap.add_argument("--public", dest="private", action="store_false", default=True,
                     help="Push as a public repo instead of the default private repo.")
    args = ap.parse_args()

    print(f"Loading benchmark tasks from {args.benchmark} ...")
    prompts = load_benchmark(args.benchmark)
    print(f"  {len(prompts)} tasks")

    visibility = "private" if args.private else "PUBLIC"
    print(f"Pushing to {args.repo_id} ({visibility}) ...")
    prompts.push_to_hub(args.repo_id, private=args.private)

    print(f"\nDone: https://huggingface.co/datasets/{args.repo_id}")
    print("Now: paste runs/hf_upload/DATASET_CARD_benchmark.md content into the repo's README,")
    print("then tag this commit as a release (e.g. v1.0) once you confirm it looks right.")


if __name__ == "__main__":
    main()
