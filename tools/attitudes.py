"""Shared loading, validation, resolution, and rendering for reference tools."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

try:
    import yaml
except ImportError as exc:  # pragma: no cover - exercised by CLI environments
    raise RuntimeError(
        "PyYAML is required for the reference tools; install requirements-dev.txt"
    ) from exc

try:
    from jsonschema import Draft202012Validator
    from referencing import Registry, Resource
except ImportError as exc:  # pragma: no cover - exercised by CLI environments
    raise RuntimeError(
        "jsonschema is required for the reference tools; install requirements-dev.txt"
    ) from exc


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATHS = {
    "persona": ROOT / "schemas" / "persona.schema.json",
    "behavioral-profile": ROOT / "schemas" / "behavioral-profile.schema.json",
}
EXPERIENCE_SCHEMA_PATH = ROOT / "schemas" / "experience.schema.json"


class AttitudeError(Exception):
    """A definition cannot be loaded, resolved, or rendered safely."""


def load_yaml(path: Path) -> dict[str, Any]:
    """Load a YAML mapping without constructing application-specific objects."""
    try:
        with path.open("r", encoding="utf-8") as stream:
            document = yaml.safe_load(stream)
    except (OSError, yaml.YAMLError) as exc:
        raise AttitudeError(f"{path}: cannot load YAML: {exc}") from exc
    if not isinstance(document, dict):
        raise AttitudeError(f"{path}: expected a YAML mapping at the document root")
    return document


def load_schema(kind: str) -> dict[str, Any]:
    try:
        with SCHEMA_PATHS[kind].open("r", encoding="utf-8") as stream:
            return json.load(stream)
    except KeyError as exc:
        raise AttitudeError(f"unsupported definition kind: {kind!r}") from exc
    except (OSError, json.JSONDecodeError) as exc:
        raise AttitudeError(f"cannot load schema for {kind}: {exc}") from exc


def schema_errors(document: dict[str, Any], path: Path) -> list[str]:
    kind = document.get("kind")
    if kind not in SCHEMA_PATHS:
        return [f"{path}: kind must be 'persona' or 'behavioral-profile'"]

    experience_schema = json.loads(EXPERIENCE_SCHEMA_PATH.read_text(encoding="utf-8"))
    registry = Registry().with_resource(
        experience_schema["$id"], Resource.from_contents(experience_schema)
    )
    validator = Draft202012Validator(load_schema(kind), registry=registry)
    errors = []
    for error in sorted(validator.iter_errors(document), key=lambda item: list(item.path)):
        location = ".".join(str(part) for part in error.absolute_path) or "<root>"
        errors.append(f"{path}:{location}: {error.message}")
    return errors


def discover_definitions(paths: Iterable[Path] | None = None) -> list[Path]:
    if paths is None:
        return sorted((ROOT / "profiles").glob("*.yaml")) + sorted(
            (ROOT / "personas").glob("*/persona.yaml")
        )

    discovered: list[Path] = []
    for path in paths:
        if path.is_dir():
            discovered.extend(sorted(path.rglob("*.yaml")))
        else:
            discovered.append(path)
    return discovered


def profile_index(profile_dir: Path | None = None) -> tuple[dict[str, tuple[Path, dict[str, Any]]], list[str]]:
    directory = profile_dir or ROOT / "profiles"
    index: dict[str, tuple[Path, dict[str, Any]]] = {}
    errors: list[str] = []
    for path in sorted(directory.glob("*.yaml")):
        try:
            document = load_yaml(path)
        except AttitudeError as exc:
            errors.append(str(exc))
            continue
        name = document.get("name")
        if not isinstance(name, str):
            continue
        if name in index:
            errors.append(f"{path}: duplicate profile name {name!r}; first seen in {index[name][0]}")
        else:
            index[name] = (path, document)
    return index, errors


def reference_errors(
    document: dict[str, Any], path: Path, profiles: dict[str, tuple[Path, dict[str, Any]]]
) -> list[str]:
    errors: list[str] = []
    if document.get("kind") == "persona":
        for name in document.get("extends", []):
            if name not in profiles:
                errors.append(f"{path}:extends: profile {name!r} does not exist")
    return errors


def package_errors(document: dict[str, Any], path: Path) -> list[str]:
    """Validate human-readable package guidance tied to structured metadata."""
    if document.get("kind") != "persona":
        return []
    if path.name != "persona.yaml":
        return []

    skill_path = path.parent / "SKILL.md"
    try:
        skill = skill_path.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"{skill_path}: cannot read package guidance: {exc}"]
    required_sections = {
        "voice": "## Voice Performance",
        "convictions": "## Convictions",
        "pushback": "## Pushback",
        "uncertainty": "## Uncertainty",
    }
    errors = []
    for field, heading in required_sections.items():
        if field in document and heading not in skill:
            errors.append(
                f"{skill_path}: personas declaring {field} metadata must include "
                f"a {heading!r} section"
            )
    return errors


def resolve_profiles(
    persona: dict[str, Any], additional_names: Iterable[str] = ()
) -> list[dict[str, Any]]:
    index, index_errors = profile_index()
    if index_errors:
        raise AttitudeError("\n".join(index_errors))

    ordered_names = list(persona.get("extends", [])) + list(additional_names)
    profiles: list[dict[str, Any]] = []
    seen: set[str] = set()
    for name in ordered_names:
        if name in seen:
            continue
        seen.add(name)
        if name not in index:
            raise AttitudeError(f"profile {name!r} does not exist")
        path, profile = index[name]
        errors = schema_errors(profile, path)
        if errors:
            raise AttitudeError("\n".join(errors))
        profiles.append(profile)
    return profiles


def humanize(identifier: str) -> str:
    return identifier.replace("_", " ").replace("-", " ")


def build_instruction(persona: dict[str, Any], profiles: list[dict[str, Any]]) -> str:
    """Render a deterministic, platform-neutral instruction document."""
    lines = [
        f"# Agent Attitude: {persona['display_name']}",
        "",
        persona["description"],
        "",
        "## Instruction precedence",
        "",
        "Safety and platform requirements, the user task, and repository policy take precedence over these behavioral and presentation instructions.",
        "",
        "## Behavioral requirements",
        "",
    ]
    for profile in profiles:
        lines.append(f"### {profile['name']}")
        lines.append("")
        lines.append(profile["description"])
        lines.append("")
        for rule_name, rule in profile["behavior"].items():
            condition = f"When {humanize(rule['when'])}" if "when" in rule else "Generally"
            actions = "; ".join(humanize(action) for action in rule["actions"])
            lines.append(f"- **{humanize(rule_name).title()}:** {condition}, {actions}.")
        lines.append("")

    convictions = persona.get("convictions")
    if convictions:
        lines.extend(["## Convictions", ""])
        lines.extend(f"- {humanize(item).capitalize()}." for item in convictions)

    pushback = persona.get("pushback")
    if pushback:
        lines.extend(["", "## Pushback", ""])
        for trigger, rule in pushback.items():
            actions = "; ".join(humanize(action) for action in rule["actions"])
            lines.append(
                f"- **{humanize(trigger).title()} ({rule['strength']}):** {actions}."
            )

    uncertainty = persona.get("uncertainty")
    if uncertainty:
        lines.extend(["", "## Uncertainty", ""])
        lines.append(f"- Acknowledgment: {humanize(uncertainty['acknowledgment'])}.")
        lines.append(f"- Speculation: {humanize(uncertainty['speculation'])}.")
        lines.append(
            f"- Confidence language: {humanize(uncertainty['confidence_language'])}."
        )
        lines.append(
            "- When context is missing: "
            + "; ".join(humanize(item) for item in uncertainty["missing_context"])
            + "."
        )
        lines.append(
            "- Never: "
            + "; ".join(humanize(item) for item in uncertainty["never"])
            + "."
        )

    lines.extend(["", "## Presentation", ""])
    for trait, value in persona["presentation"].items():
        lines.append(f"- {humanize(trait).title()}: {value}")

    voice = persona.get("voice")
    if voice:
        lines.extend(
            [
                "",
                "## Voice performance (advisory)",
                "",
                "Character affects performance; context controls intensity. Ignore this section when voice guidance is unsupported.",
                "",
            ]
        )
        for group_name in ("sound", "delivery"):
            traits = voice.get(group_name, {})
            if not traits:
                continue
            rendered = "; ".join(
                f"{humanize(name)}: {humanize(value)}" for name, value in traits.items()
            )
            lines.append(f"- **{group_name.title()}:** {rendered}.")
        if voice.get("mannerisms"):
            lines.append("- **Mannerisms:** " + "; ".join(voice["mannerisms"]) + ".")
        for context, settings in voice.get("context_rules", {}).items():
            rendered = "; ".join(
                f"{humanize(name)}: {humanize(value)}" for name, value in settings.items()
            )
            lines.append(f"- **When {humanize(context)}:** {rendered}.")

    lines.extend(["", "## Preferences", ""])
    lines.extend(f"- Prefer {preference}." for preference in persona["preferences"])
    if persona["triggers"]:
        lines.extend(["", "## Presentation triggers", ""])
        for trigger, settings in persona["triggers"].items():
            lines.append(
                f"- {humanize(trigger).capitalize()}: {settings['intensity']} presentation intensity."
            )

    lines.extend(["", "## Persona requirements", ""])
    lines.extend(f"- {humanize(item).capitalize()}." for item in persona["must"])
    lines.extend(["", "## Prohibited behavior", ""])
    lines.extend(f"- Do not {humanize(item)}." for item in persona["must_not"])
    lines.extend(
        [
            "",
            "## Competence invariants",
            "",
            "Technical accuracy, factual accuracy, task completion, and safety are required. Personality may degrade; competence may not.",
            "",
        ]
    )
    return "\n".join(lines)
