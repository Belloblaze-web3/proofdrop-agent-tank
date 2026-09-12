#!/usr/bin/env python3
"""Run the rubric-aligned ten-seed evaluation."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from robotics.so101_bimanual.policy import run_episode


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate SO-101 bimanual dinner-table task")
    parser.add_argument("--seeds", type=int, default=10)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    results = [run_episode(args.offset + seed) for seed in range(args.seeds)]
    summary = {
        "benchmark": "so101-bimanual-dinner-table-v1",
        "seeds": [r["seed"] for r in results],
        "success_rate": sum(r["success"] for r in results) / len(results),
        "mean_score": sum(r["score"] for r in results) / len(results),
        "mean_steps": sum(r["steps"] for r in results) / len(results),
        "episodes": results,
    }
    text = json.dumps(summary, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text)
    print(text, end="")
    return 0 if summary["success_rate"] >= 0.8 else 1


if __name__ == "__main__":
    raise SystemExit(main())
