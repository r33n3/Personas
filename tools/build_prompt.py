#!/usr/bin/env python3
"""Build a portable instruction document from a persona and its profiles."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from attitudes import (
        AttitudeError,
        apply_variant,
        build_instruction,
        load_yaml,
        resolve_application,
        resolve_profiles,
        role_lens_index,
        schema_errors,
    )
except RuntimeError as exc:
    print(f"error: {exc}", file=sys.stderr)
    raise SystemExit(2)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render one validated persona and its behavioral profiles as Markdown instructions."
    )
    parser.add_argument("persona", nargs="?", type=Path, help="path to persona.yaml")
    parser.add_argument(
        "--role-lens",
        help="optional review perspective; does not grant a functional role or authority",
    )
    parser.add_argument(
        "--application",
        type=Path,
        help="resolve a persona-application YAML document instead of a direct persona path",
    )
    parser.add_argument(
        "--name",
        help="optional conversational name when building directly from persona.yaml",
    )
    parser.add_argument(
        "--variant",
        help="optional variant name when building directly from persona.yaml",
    )
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
        if args.application and args.persona:
            raise AttitudeError("provide either a persona path or --application, not both")
        if args.application and args.name:
            raise AttitudeError("--name cannot override the name in a persona application")
        if args.application and args.variant:
            raise AttitudeError("--variant cannot override the variant in a persona application")
        if args.application and args.role_lens:
            raise AttitudeError("--role-lens cannot override the lens in a persona application")
        if not args.application and not args.persona:
            raise AttitudeError("provide a persona path or --application")

        conversational_name = args.name
        additional_profiles = list(args.profile)
        role_lens = None
        if args.application:
            application = load_yaml(args.application)
            errors = schema_errors(application, args.application)
            if errors:
                raise AttitudeError("\n".join(errors))
            if application.get("kind") != "persona-application":
                raise AttitudeError(
                    f"{args.application}: expected kind 'persona-application'"
                )
            resolved = resolve_application(application)
            persona = resolved["persona"]
            conversational_name = resolved["conversational_name"]
            additional_profiles = resolved["additional_profiles"] + additional_profiles
            role_lens = resolved["role_lens"]
        else:
            persona = load_yaml(args.persona)
            errors = schema_errors(persona, args.persona)
            if errors:
                raise AttitudeError("\n".join(errors))
            if persona.get("kind") != "persona":
                raise AttitudeError(f"{args.persona}: expected kind 'persona'")
            if args.variant:
                resolved = apply_variant(persona, args.variant)
                persona = resolved["persona"]
                additional_profiles = resolved["additional_profiles"] + additional_profiles
            if args.role_lens:
                role_lenses, role_errors = role_lens_index()
                if role_errors:
                    raise AttitudeError("\n".join(role_errors))
                if args.role_lens not in role_lenses:
                    raise AttitudeError(f"role lens {args.role_lens!r} does not exist")
                lens_path, role_lens = role_lenses[args.role_lens]
                errors = schema_errors(role_lens, lens_path)
                if errors:
                    raise AttitudeError("\n".join(errors))
        profiles = resolve_profiles(persona, additional_profiles)
        output = build_instruction(persona, profiles, conversational_name, role_lens)
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
