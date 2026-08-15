#!/usr/bin/env python3
"""Validate reference multi-turn dialogue conformance suites."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print(
        "error: PyYAML is required; install requirements-dev.txt",
        file=sys.stderr,
    )
    raise SystemExit(2)


ROOT = Path(__file__).resolve().parents[1]
DIALOGUE_ROOT = ROOT / "tests" / "dialogues"
SCENARIO_PATH = DIALOGUE_ROOT / "scenarios.yaml"
SUITE_ROOT = DIALOGUE_ROOT / "personas"
PILOT_PERSONAS = {
    "greybeard",
    "diva",
    "redditor",
    "burned-out-sysadmin",
    "professional",
}
REQUIRED_CASES = {"signature", "serious-context", "uncertainty"}
EXPECTATION_GROUPS = {"behavior", "presentation", "voice", "invariants"}


def load_document(path: Path) -> tuple[dict[str, Any], list[str]]:
    try:
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        return {}, [f"{path}: could not load YAML: {exc}"]
    if not isinstance(document, dict):
        return {}, [f"{path}: document must be a mapping"]
    return document, []


def string_list_errors(value: Any, location: str, minimum: int = 1) -> list[str]:
    if not isinstance(value, list) or len(value) < minimum:
        return [f"{location}: must be a list with at least {minimum} item(s)"]
    if any(not isinstance(item, str) or not item.strip() for item in value):
        return [f"{location}: entries must be non-empty strings"]
    return []


def validate_scenario_bank(
    document: dict[str, Any], path: Path
) -> tuple[dict[str, dict[str, Any]], list[str]]:
    errors: list[str] = []
    if document.get("schema_version") != "0.1":
        errors.append(f"{path}:schema_version: expected '0.1'")
    if document.get("kind") != "dialogue-scenario-bank":
        errors.append(f"{path}:kind: expected 'dialogue-scenario-bank'")
    scenarios = document.get("scenarios")
    if not isinstance(scenarios, dict) or not scenarios:
        return {}, errors + [f"{path}:scenarios: must be a non-empty mapping"]

    for name, scenario in scenarios.items():
        location = f"{path}:scenarios.{name}"
        if not isinstance(name, str) or not name.strip() or not isinstance(scenario, dict):
            errors.append(f"{location}: must be a named mapping")
            continue
        if not isinstance(scenario.get("purpose"), str) or not scenario["purpose"].strip():
            errors.append(f"{location}.purpose: must be a non-empty string")
        errors.extend(string_list_errors(scenario.get("user_turns"), f"{location}.user_turns", 2))
        errors.extend(
            string_list_errors(
                scenario.get("required_invariants"),
                f"{location}.required_invariants",
            )
        )
    return scenarios, errors


def validate_suite(
    document: dict[str, Any],
    path: Path,
    scenarios: dict[str, dict[str, Any]],
    seen_responses: dict[str, str],
) -> tuple[str | None, int, int, list[str]]:
    errors: list[str] = []
    persona = document.get("persona")
    if document.get("schema_version") != "0.1":
        errors.append(f"{path}:schema_version: expected '0.1'")
    if document.get("kind") != "persona-dialogue-suite":
        errors.append(f"{path}:kind: expected 'persona-dialogue-suite'")
    if not isinstance(persona, str) or not persona.strip():
        errors.append(f"{path}:persona: must be a non-empty string")
        persona = None
    elif persona != path.stem:
        errors.append(f"{path}:persona: {persona!r} does not match filename {path.stem!r}")
    elif not (ROOT / "personas" / persona / "persona.yaml").is_file():
        errors.append(f"{path}:persona: no bundled persona definition exists for {persona!r}")

    cases = document.get("cases")
    if not isinstance(cases, list) or not cases:
        return persona, 0, 0, errors + [f"{path}:cases: must be a non-empty list"]

    case_ids: list[str] = []
    turn_count = 0
    for index, case in enumerate(cases):
        location = f"{path}:cases[{index}]"
        if not isinstance(case, dict):
            errors.append(f"{location}: must be a mapping")
            continue
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id.strip():
            errors.append(f"{location}.id: must be a non-empty string")
            continue
        case_ids.append(case_id)
        scenario_name = case.get("scenario")
        inline_turns = case.get("user_turns")
        if (scenario_name is None) == (inline_turns is None):
            errors.append(f"{location}: define exactly one of scenario or user_turns")
            user_turns: list[str] = []
            required_invariants: set[str] = set()
        elif scenario_name is not None:
            if not isinstance(scenario_name, str) or scenario_name not in scenarios:
                errors.append(f"{location}.scenario: unknown scenario {scenario_name!r}")
                user_turns = []
                required_invariants = set()
            else:
                user_turns = scenarios[scenario_name]["user_turns"]
                required_invariants = set(scenarios[scenario_name]["required_invariants"])
        else:
            if not isinstance(case.get("purpose"), str) or not case["purpose"].strip():
                errors.append(f"{location}.purpose: inline cases require a non-empty string")
            errors.extend(string_list_errors(inline_turns, f"{location}.user_turns", 2))
            user_turns = inline_turns if isinstance(inline_turns, list) else []
            required_invariants = set()

        assistant_turns = case.get("assistant_turns")
        if not isinstance(assistant_turns, list):
            errors.append(f"{location}.assistant_turns: must be a list")
            continue
        if len(assistant_turns) != len(user_turns):
            errors.append(
                f"{location}.assistant_turns: has {len(assistant_turns)} turn(s); "
                f"expected {len(user_turns)}"
            )
        turn_count += len(assistant_turns)
        observed_invariants: set[str] = set()
        observed_voice: set[str] = set()
        for turn_index, turn in enumerate(assistant_turns):
            turn_location = f"{location}.assistant_turns[{turn_index}]"
            if not isinstance(turn, dict):
                errors.append(f"{turn_location}: must be a mapping")
                continue
            response = turn.get("response")
            if not isinstance(response, str) or not response.strip():
                errors.append(f"{turn_location}.response: must be a non-empty string")
            else:
                normalized = " ".join(response.split()).casefold()
                if normalized in seen_responses:
                    errors.append(
                        f"{turn_location}.response: duplicates reference response at "
                        f"{seen_responses[normalized]}"
                    )
                else:
                    seen_responses[normalized] = f"{turn_location}.response"

            expectations = turn.get("expectations")
            if not isinstance(expectations, dict):
                errors.append(f"{turn_location}.expectations: must be a mapping")
                continue
            missing = EXPECTATION_GROUPS - set(expectations)
            extra = set(expectations) - EXPECTATION_GROUPS
            if missing:
                errors.append(f"{turn_location}.expectations: missing {sorted(missing)}")
            if extra:
                errors.append(f"{turn_location}.expectations: unknown groups {sorted(extra)}")
            for group in EXPECTATION_GROUPS:
                values = expectations.get(group)
                errors.extend(string_list_errors(values, f"{turn_location}.expectations.{group}"))
                if isinstance(values, list):
                    if group == "invariants":
                        observed_invariants.update(value for value in values if isinstance(value, str))
                    elif group == "voice":
                        observed_voice.update(value for value in values if isinstance(value, str))

        missing_invariants = required_invariants - observed_invariants
        if missing_invariants:
            errors.append(
                f"{location}: does not cover scenario invariants {sorted(missing_invariants)}"
            )
        if case_id == "serious-context":
            if "clarity_high" not in observed_voice:
                errors.append(f"{location}: serious context must require clarity_high")
            if persona != "professional" and not observed_voice.intersection(
                {"humor_none", "sarcasm_none", "theatricality_reduced"}
            ):
                errors.append(
                    f"{location}: humorous persona must suppress or reduce performance"
                )

    duplicates = sorted({item for item in case_ids if case_ids.count(item) > 1})
    if duplicates:
        errors.append(f"{path}:cases: duplicate case ids {duplicates}")
    missing_cases = REQUIRED_CASES - set(case_ids)
    if missing_cases:
        errors.append(f"{path}:cases: missing required cases {sorted(missing_cases)}")
    return persona, len(cases), turn_count, errors


def validate_all() -> tuple[int, int, int, list[str]]:
    if not SCENARIO_PATH.is_file() or not SUITE_ROOT.is_dir():
        return 0, 0, 0, [f"{DIALOGUE_ROOT}: dialogue test assets are missing"]
    bank, errors = load_document(SCENARIO_PATH)
    scenarios, bank_errors = validate_scenario_bank(bank, SCENARIO_PATH)
    errors.extend(bank_errors)
    suite_paths = sorted(SUITE_ROOT.glob("*.yaml"))
    if not suite_paths:
        return 0, 0, 0, errors + [f"{SUITE_ROOT}: no dialogue suites found"]

    personas: list[str] = []
    case_count = 0
    turn_count = 0
    seen_responses: dict[str, str] = {}
    for path in suite_paths:
        document, load_errors = load_document(path)
        errors.extend(load_errors)
        if load_errors:
            continue
        persona, cases, turns, suite_errors = validate_suite(
            document, path, scenarios, seen_responses
        )
        if persona:
            personas.append(persona)
        case_count += cases
        turn_count += turns
        errors.extend(suite_errors)

    duplicates = sorted({name for name in personas if personas.count(name) > 1})
    if duplicates:
        errors.append(f"{SUITE_ROOT}: duplicate persona suites {duplicates}")
    missing_pilot = PILOT_PERSONAS - set(personas)
    if missing_pilot:
        errors.append(f"{SUITE_ROOT}: missing pilot personas {sorted(missing_pilot)}")
    return len(suite_paths), case_count, turn_count, errors


def main() -> int:
    suite_count, case_count, turn_count, errors = validate_all()
    if errors:
        for error in errors:
            print(f"ERROR {error}", file=sys.stderr)
        print(f"Validation failed with {len(errors)} error(s).", file=sys.stderr)
        return 1 if suite_count else 2
    print(
        f"Validated {suite_count} dialogue suite(s), {case_count} case(s), "
        f"and {turn_count} assistant turn(s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
