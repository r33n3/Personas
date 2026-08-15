#!/usr/bin/env python3
"""Build a portable instruction document from a persona and its profiles."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from attitudes import (
        AttitudeError,
        build_instruction,
        load_yaml,
        resolve_profiles,
        schema_errors,
    )
except RuntimeError as exc:
    print(f"error: {exc}", file=sys.stderr)
    raise SystemExit(2)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render one validated persona and its behavioral profiles as Markdown instructions."
    )
    parser.add_argument("persona", type=Path, help="path to persona.yaml")
    parser.add_argument(
        "--profile",
        action="append",
        default=[],
        metavar="NAME",
        help="append a behavioral profile after inherited profiles; repeatable",
    )
    parser.add_argument("--output", type=Path, help="write output instead of stdout")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        persona = load_yaml(args.persona)
        errors = schema_errors(persona, args.persona)
        if errors:
            raise AttitudeError("\n".join(errors))
        if persona.get("kind") != "persona":
            raise AttitudeError(f"{args.persona}: expected kind 'persona'")
        profiles = resolve_profiles(persona, args.profile)
        output = build_instruction(persona, profiles)
        if args.output:
            args.output.write_text(output, encoding="utf-8")
        else:
            print(output, end="")
    except (AttitudeError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
