"""Shared loading, validation, resolution, and rendering for reference tools."""

from __future__ import annotations

import json
from copy import deepcopy
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
    "persona-application": ROOT / "schemas" / "persona-application.schema.json",
    "persona-variant": ROOT / "schemas" / "persona-variant.schema.json",
    "role-lens": ROOT / "schemas" / "role-lens.schema.json",
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
        supported = "', '".join(SCHEMA_PATHS)
        return [f"{path}: kind must be one of '{supported}'"]

    registry = Registry()
    for schema_path in set(SCHEMA_PATHS.values()) | {EXPERIENCE_SCHEMA_PATH}:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        registry = registry.with_resource(schema["$id"], Resource.from_contents(schema))
    validator = Draft202012Validator(load_schema(kind), registry=registry)
    errors = []
    for error in sorted(validator.iter_errors(document), key=lambda item: list(item.path)):
        location = ".".join(str(part) for part in error.absolute_path) or "<root>"
        errors.append(f"{path}:{location}: {error.message}")
    return errors


def discover_definitions(paths: Iterable[Path] | None = None) -> list[Path]:
    if paths is None:
        return (
            sorted((ROOT / "profiles").glob("*.yaml"))
            + sorted((ROOT / "personas").glob("*/persona.yaml"))
            + sorted((ROOT / "personas").glob("*/variants/*.yaml"))
            + sorted((ROOT / "roles").glob("*/role.yaml"))
            + sorted((ROOT / "examples" / "applications").glob("*.yaml"))
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


def persona_index(persona_dir: Path | None = None) -> tuple[dict[str, tuple[Path, dict[str, Any]]], list[str]]:
    directory = persona_dir or ROOT / "personas"
    index: dict[str, tuple[Path, dict[str, Any]]] = {}
    errors: list[str] = []
    for path in sorted(directory.glob("*/persona.yaml")):
        try:
            document = load_yaml(path)
        except AttitudeError as exc:
            errors.append(str(exc))
            continue
        name = document.get("name")
        if not isinstance(name, str):
            continue
        if name in index:
            errors.append(f"{path}: duplicate persona type {name!r}; first seen in {index[name][0]}")
        else:
            index[name] = (path, document)
    return index, errors


def role_lens_index(role_dir: Path | None = None) -> tuple[dict[str, tuple[Path, dict[str, Any]]], list[str]]:
    """Index review perspectives without interpreting them as functional roles."""
    directory = role_dir or ROOT / "roles"
    index: dict[str, tuple[Path, dict[str, Any]]] = {}
    errors: list[str] = []
    for path in sorted(directory.glob("*/role.yaml")):
        try:
            document = load_yaml(path)
        except AttitudeError as exc:
            errors.append(str(exc))
            continue
        name = document.get("name")
        if not isinstance(name, str):
            continue
        if name in index:
            errors.append(f"{path}: duplicate role lens {name!r}; first seen in {index[name][0]}")
        else:
            index[name] = (path, document)
    return index, errors


def variant_index(persona_dir: Path | None = None) -> tuple[dict[tuple[str, str], tuple[Path, dict[str, Any]]], list[str]]:
    directory = persona_dir or ROOT / "personas"
    index: dict[tuple[str, str], tuple[Path, dict[str, Any]]] = {}
    errors: list[str] = []
    for path in sorted(directory.glob("*/variants/*.yaml")):
        try:
            document = load_yaml(path)
        except AttitudeError as exc:
            errors.append(str(exc))
            continue
        persona_type = document.get("persona")
        name = document.get("name")
        if not isinstance(persona_type, str) or not isinstance(name, str):
            continue
        key = (persona_type, name)
        if key in index:
            errors.append(f"{path}: duplicate variant {persona_type}/{name}; first seen in {index[key][0]}")
        else:
            index[key] = (path, document)
    return index, errors


def reference_errors(
    document: dict[str, Any], path: Path, profiles: dict[str, tuple[Path, dict[str, Any]]],
    personas: dict[str, tuple[Path, dict[str, Any]]] | None = None,
    variants: dict[tuple[str, str], tuple[Path, dict[str, Any]]] | None = None,
    role_lenses: dict[str, tuple[Path, dict[str, Any]]] | None = None,
) -> list[str]:
    errors: list[str] = []
    if document.get("kind") == "persona":
        for name in document.get("extends", []):
            if name not in profiles:
                errors.append(f"{path}:extends: profile {name!r} does not exist")
    if document.get("kind") == "persona-application":
        persona_type = document.get("persona", {}).get("type")
        if personas is None or persona_type not in personas:
            errors.append(f"{path}:persona.type: persona type {persona_type!r} does not exist")
        variant = document.get("persona", {}).get("variant")
        if variant and (variants is None or (persona_type, variant) not in variants):
            errors.append(f"{path}:persona.variant: variant {persona_type}/{variant} does not exist")
        role_lens = document.get("role_lens")
        if role_lens and (role_lenses is None or role_lens not in role_lenses):
            errors.append(f"{path}:role_lens: role lens {role_lens!r} does not exist")
    if document.get("kind") == "persona-variant":
        persona_type = document.get("persona")
        if personas is None or persona_type not in personas:
            errors.append(f"{path}:persona: persona type {persona_type!r} does not exist")
        for name in document.get("additional_profiles", []):
            if name not in profiles:
                errors.append(f"{path}:additional_profiles: profile {name!r} does not exist")
    return errors


def merge_experience(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Merge known experience sections without interpreting presentation values."""
    merged = {section: dict(values) for section, values in base.items()}
    for section, values in override.items():
        merged[section] = {**merged.get(section, {}), **values}
    return merged


def _append_unique(base: list[Any], additions: list[Any]) -> list[Any]:
    return base + [item for item in additions if item not in base]


def apply_variant(persona: dict[str, Any], variant_name: str) -> dict[str, Any]:
    """Apply only schema-approved variant fields and preserve variant provenance."""
    variants, index_errors = variant_index()
    if index_errors:
        raise AttitudeError("\n".join(index_errors))
    key = (persona["name"], variant_name)
    if key not in variants:
        raise AttitudeError(f"variant {persona['name']}/{variant_name} does not exist")
    path, variant = variants[key]
    errors = schema_errors(variant, path)
    if errors:
        raise AttitudeError("\n".join(errors))

    resolved = deepcopy(persona)
    resolved["presentation"] = {
        **resolved["presentation"], **variant.get("presentation", {})
    }
    if "voice" in variant:
        voice = deepcopy(resolved.get("voice", {}))
        for group in ("sound", "delivery"):
            if group in variant["voice"]:
                voice[group] = {**voice.get(group, {}), **variant["voice"][group]}
        if "mannerisms" in variant["voice"]:
            voice["mannerisms"] = _append_unique(
                voice.get("mannerisms", []), variant["voice"]["mannerisms"]
            )
        for context, settings in variant["voice"].get("context_rules", {}).items():
            voice.setdefault("context_rules", {})[context] = {
                **voice.get("context_rules", {}).get(context, {}), **settings
            }
        resolved["voice"] = voice
    if "experience" in variant:
        resolved["experience"] = merge_experience(
            resolved.get("experience", {}), variant["experience"]
        )
    resolved["preferences"] = _append_unique(
        resolved["preferences"], variant.get("preferences", [])
    )
    trigger_conflicts = set(resolved["triggers"]) & set(variant.get("triggers", {}))
    if trigger_conflicts:
        raise AttitudeError(
            "variant cannot replace existing trigger(s): " + ", ".join(sorted(trigger_conflicts))
        )
    resolved["triggers"] = {**resolved["triggers"], **variant.get("triggers", {})}
    return {
        "persona": resolved,
        "variant": variant,
        "additional_profiles": variant.get("additional_profiles", []),
    }


def resolve_application(application: dict[str, Any]) -> dict[str, Any]:
    """Resolve a validated application while keeping consumer metadata separate."""
    index, index_errors = persona_index()
    if index_errors:
        raise AttitudeError("\n".join(index_errors))
    persona_type = application.get("persona", {}).get("type")
    if persona_type not in index:
        raise AttitudeError(f"persona type {persona_type!r} does not exist")
    path, persona = index[persona_type]
    errors = schema_errors(persona, path)
    if errors:
        raise AttitudeError("\n".join(errors))
    variant_name = application["persona"].get("variant")
    variant_resolution = apply_variant(persona, variant_name) if variant_name else None
    resolved_persona = variant_resolution["persona"] if variant_resolution else persona
    role_lens = None
    if application.get("role_lens"):
        role_lenses, role_errors = role_lens_index()
        if role_errors:
            raise AttitudeError("\n".join(role_errors))
        lens_name = application["role_lens"]
        if lens_name not in role_lenses:
            raise AttitudeError(f"role lens {lens_name!r} does not exist")
        lens_path, role_lens = role_lenses[lens_name]
        errors = schema_errors(role_lens, lens_path)
        if errors:
            raise AttitudeError("\n".join(errors))
    return {
        "persona_type": persona_type,
        "persona": resolved_persona,
        "variant": variant_resolution["variant"] if variant_resolution else None,
        "additional_profiles": (
            variant_resolution["additional_profiles"] if variant_resolution else []
        ),
        "role_lens": role_lens,
        "conversational_name": application["persona"].get("name"),
        "experience": merge_experience(
            resolved_persona.get("experience", {}), application.get("experience", {})
        ),
    }


def package_errors(document: dict[str, Any], path: Path) -> list[str]:
    """Validate human-readable package guidance tied to structured metadata."""
    if document.get("kind") == "role-lens" and path.name == "role.yaml":
        examples_path = path.parent / "examples.md"
        try:
            examples = examples_path.read_text(encoding="utf-8")
        except OSError as exc:
            return [f"{examples_path}: cannot read Role Lens examples: {exc}"]
        errors = []
        if examples.count("**User:**") < 2:
            errors.append(f"{examples_path}: Role Lens packages require at least two user examples")
        if examples.count("**Lens focus:**") < 2:
            errors.append(f"{examples_path}: each Role Lens example requires a lens focus")
        return errors
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


def validate_conversational_name(name: str | None) -> str | None:
    if name is None:
        return None
    if not name or name != name.strip() or len(name) > 80:
        raise AttitudeError(
            "conversational name must be 1-80 characters without leading or trailing whitespace"
        )
    if any(character in name for character in "\r\n\t"):
        raise AttitudeError("conversational name must be a single line")
    return name


def role_lens_instruction(role_lens: dict[str, Any]) -> list[str]:
    """Render the bounded perspective section used by all instruction consumers."""
    lines = [
        f"## Role Lens: {role_lens['display_name']}",
        "",
        role_lens["description"].strip(),
        "",
        "This is a review perspective only. It does not assign a job, authenticate the agent, grant authority, expose unavailable information, or change tools and permissions.",
        "",
        "### Attention priorities",
        "",
        "- Optimize for: " + "; ".join(humanize(item) for item in role_lens["optimizes_for"]) + ".",
        "- Notice first: " + "; ".join(humanize(item) for item in role_lens["notices_first"]) + ".",
    ]
    if role_lens.get("recurring_concerns"):
        lines.append(
            "- Recurring concerns: "
            + "; ".join(humanize(item) for item in role_lens["recurring_concerns"])
            + "."
        )
    if role_lens.get("review_questions"):
        lines.extend([
            "",
            "### Questions to consider when relevant",
            "",
            "Do not recite these mechanically or let them displace the user's task.",
        ])
        lines.extend(f"- {question}" for question in role_lens["review_questions"])
    return lines


def build_instruction(
    persona: dict[str, Any], profiles: list[dict[str, Any]], conversational_name: str | None = None,
    role_lens: dict[str, Any] | None = None,
) -> str:
    """Render a deterministic, platform-neutral instruction document."""
    conversational_name = validate_conversational_name(conversational_name)
    lines = [
        f"# Agent Attitude: {persona['display_name']}",
        "",
        persona["description"],
        "",
        "## Instruction precedence",
        "",
        "Safety and platform requirements, the user task, and repository policy take precedence over these behavioral and presentation instructions.",
    ]
    if conversational_name:
        encoded_name = json.dumps(conversational_name, ensure_ascii=False)
        lines.extend([
            "",
            "## Conversational name",
            "",
            f"Use {encoded_name} as this persona's conversational name when introductions or direct address make it relevant. Do not present this label as unique, authenticated, authoritative, or permission-bearing.",
        ])
    if role_lens:
        lines.extend(["", *role_lens_instruction(role_lens)])
    lines.extend(["", "## Behavioral requirements", ""])
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
