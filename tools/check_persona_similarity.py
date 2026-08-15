#!/usr/bin/env python3
"""Report explainable structural overlap between bundled personas."""

from __future__ import annotations

import argparse
import itertools
import sys
from pathlib import Path

from attitudes import AttitudeError, load_yaml
from persona_similarity import compare_personas, recommendation

ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Report two-axis persona similarity without external models or APIs."
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.80,
        help="minimum behavioral or character score to report (default: 0.80)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not 0 <= args.threshold <= 1:
        print("error: --threshold must be between 0 and 1", file=sys.stderr)
        return 2
    try:
        personas = [
            load_yaml(path) for path in sorted((ROOT / "personas").glob("*/persona.yaml"))
        ]
    except AttitudeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    findings = []
    for left, right in itertools.combinations(personas, 2):
        result = compare_personas(left, right)
        if max(result["behavioral"], result["character"]) >= args.threshold:
            findings.append((left, right, result))

    findings.sort(key=lambda item: max(item[2]["behavioral"], item[2]["character"]), reverse=True)
    for left, right, result in findings:
        print(f"{left['name']} ↔ {right['name']}")
        print(f"  behavioral: {result['behavioral']:.0%}")
        print(f"  character:  {result['character']:.0%}")
        print(f"  same family: {'yes' if result['same_family'] else 'no'}")
        shared = result["shared"]
        reasons = [f"{key}={', '.join(values)}" for key, values in shared.items() if values]
        print("  shared: " + ("; ".join(reasons) if reasons else "no exact structural signals"))
        print(f"  recommendation: {recommendation(result)}")

    print(f"Checked {len(personas)} personas; reported {len(findings)} advisory pair(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
