#!/usr/bin/env python3
"""Validate Agent Attitudes persona and behavioral-profile definitions."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from attitudes import (
        AttitudeError,
        discover_definitions,
        load_yaml,
        profile_index,
        reference_errors,
        schema_errors,
    )
except RuntimeError as exc:
    print(f"error: {exc}", file=sys.stderr)
    raise SystemExit(2)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate persona/profile YAML and inherited profile references."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="YAML files or directories; defaults to all bundled definitions",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    paths = discover_definitions(args.paths or None)
    if not paths:
        print("error: no YAML definitions found", file=sys.stderr)
        return 2

    profiles, errors = profile_index()
    for path in paths:
        if not path.exists():
            errors.append(f"{path}: path does not exist")
            continue
        try:
            document = load_yaml(path)
        except AttitudeError as exc:
            errors.append(str(exc))
            continue
        errors.extend(schema_errors(document, path))
        errors.extend(reference_errors(document, path, profiles))

        expected_name = path.parent.name if path.name == "persona.yaml" else path.stem
        if document.get("name") != expected_name:
            errors.append(
                f"{path}:name: {document.get('name')!r} does not match path identity {expected_name!r}"
            )

    if errors:
        for error in errors:
            print(f"ERROR {error}", file=sys.stderr)
        print(f"Validation failed with {len(errors)} error(s).", file=sys.stderr)
        return 1

    print(f"Validated {len(paths)} definition(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
