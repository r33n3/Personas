#!/usr/bin/env python3
"""Build the website catalog and downloadable bundles from repository source."""

from __future__ import annotations

import json
import re
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import yaml

from attitudes import apply_variant, build_instruction, resolve_profiles, role_lens_instruction
from persona_similarity import compare_personas

ROOT = Path(__file__).resolve().parents[1]
PERSONAS = ROOT / "personas"
ROLES = ROOT / "roles"
PROFILES = ROOT / "profiles"
SITE = ROOT / "site"
OUTPUT_JSON = SITE / "src" / "personas.generated.json"
PUBLIC_JSON = SITE / "public" / "catalog.json"
ROLE_OUTPUT_JSON = SITE / "src" / "roles.generated.json"
ROLE_PUBLIC_JSON = SITE / "public" / "roles.json"
DOWNLOADS = SITE / "public" / "downloads"
CATEGORY_ORDER = {
    "computing-history": 0, "internet-culture": 1, "it-and-engineering": 2,
    "corporate-life": 3, "startup-and-modern-tech": 4,
    "character-archetypes": 5, "control": 6,
}


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as stream:
        return yaml.safe_load(stream)


def first_example(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    prompt = re.search(r"\*\*User:\*\*\s*(.+)", text)
    response = re.search(r"\*\*[^*]+:\*\*\s*(.+)", text)
    return {
        "prompt": prompt.group(1).strip() if prompt else "",
        "response": response.group(1).strip() if response else "",
    }


def first_role_example(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    prompt = re.search(r"\*\*User:\*\*\s*(.+)", text)
    focus = re.search(r"\*\*Lens focus:\*\*\s*(.+)", text)
    return {
        "prompt": prompt.group(1).strip() if prompt else "",
        "focus": focus.group(1).strip() if focus else "",
    }


def skill_instructions(path: Path) -> str:
    """Return portable skill instructions without the discovery frontmatter."""
    text = path.read_text(encoding="utf-8").strip()
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            return parts[2].strip()
    return text


def humanize_voice(value: str) -> str:
    return value.replace("_", " ").replace("-", " ")


def summarize_voice_traits(traits: dict[str, str]) -> str:
    return ", ".join(humanize_voice(value) for value in traits.values()) + "."


def catalog_voice(voice: dict) -> dict | None:
    if not voice:
        return None
    sound = voice.get("sound", {})
    delivery = voice.get("delivery", {})
    preferred = [
        sound.get("register"),
        sound.get("texture"),
        delivery.get("pace"),
        delivery.get("emotional_tone"),
        delivery.get("cadence"),
    ]
    summary_parts = []
    for value in preferred:
        if value and value not in summary_parts:
            summary_parts.append(value)
    return {
        "summary": ", ".join(humanize_voice(value) for value in summary_parts) + ".",
        "soundSummary": summarize_voice_traits(sound),
        "deliverySummary": summarize_voice_traits(delivery),
        "sound": sound,
        "delivery": delivery,
        "mannerisms": voice.get("mannerisms", []),
        "contextRules": voice.get("context_rules", {}),
    }


def catalog_behavioral_depth(persona: dict) -> dict | None:
    """Expose optional depth metadata without inventing defaults for older personas."""
    convictions = persona.get("convictions")
    pushback = persona.get("pushback")
    uncertainty = persona.get("uncertainty")
    if not any((convictions, pushback, uncertainty)):
        return None
    return {
        "convictions": convictions or [],
        "pushback": pushback or {},
        "uncertainty": uncertainty,
    }


PREVIEW_TOKENS = {
    "mode": {"dark", "light"},
    "accent": {"phosphor-green", "amber", "ice-blue", "paper-white"},
    "typography": {"monospace", "sans-serif", "serif"},
    "terminal": {"modern", "unix", "crt", "dos", "workstation", "minimal"},
    "scanlines": {"none", "subtle", "medium"},
    "glow": {"none", "low", "medium"},
    "motion": {"none", "subtle", "moderate"},
}


def preview_token(group: str, value: str | None) -> str:
    """Map open semantic metadata to a small, non-executable preview vocabulary."""
    return value if value in PREVIEW_TOKENS[group] else "default"


def catalog_experience(experience: dict) -> dict | None:
    if not experience:
        return None
    visual = experience.get("visual", {})
    terminal = experience.get("terminal", {})
    motion = experience.get("motion", {})
    return {
        **experience,
        "preview": {
            "mode": preview_token("mode", visual.get("mode")),
            "accent": preview_token("accent", visual.get("accent")),
            "typography": preview_token("typography", visual.get("typography")),
            "terminal": preview_token("terminal", terminal.get("style")),
            "scanlines": preview_token("scanlines", terminal.get("scanlines")),
            "glow": preview_token("glow", terminal.get("glow")),
            "motion": preview_token("motion", motion.get("intensity")),
        },
    }


def catalog_behavior(profile_names: list[str], profile_index: dict) -> list[dict]:
    behavior = []
    for profile_name in profile_names:
        profile = profile_index[profile_name]
        for rule_name, rule in profile["behavior"].items():
            behavior.append({
                "profile": profile_name,
                "rule": rule_name.replace("_", " "),
                "when": rule.get("when", "generally").replace("_", " "),
                "actions": [action.replace("_", " ") for action in rule["actions"]],
            })
    return behavior


def catalog_variants(persona: dict, profile_index: dict) -> list[dict]:
    variants = []
    for path in sorted((PERSONAS / persona["name"] / "variants").glob("*.yaml")):
        variant = load_yaml(path)
        resolution = apply_variant(persona, variant["name"])
        resolved = resolution["persona"]
        profile_names = list(dict.fromkeys(persona["extends"] + resolution["additional_profiles"]))
        variants.append({
            "name": variant["name"],
            "displayName": humanize_voice(variant["name"]).title(),
            "description": variant["description"],
            "profiles": profile_names,
            "presentation": resolved["presentation"],
            "voice": catalog_voice(resolved.get("voice", {})),
            "experience": catalog_experience(resolved.get("experience", {})),
            "preferences": resolved["preferences"],
            "behavior": catalog_behavior(profile_names, profile_index),
            "instructions": build_instruction(
                resolved, resolve_profiles(resolved, resolution["additional_profiles"])
            ),
        })
    return variants


def main() -> int:
    profile_index = {path.stem: load_yaml(path) for path in PROFILES.glob("*.yaml")}
    records = []
    persona_documents = {}
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)

    for persona_path in PERSONAS.glob("*/persona.yaml"):
        package = persona_path.parent
        persona = load_yaml(persona_path)
        persona_documents[persona["name"]] = persona
        behavior = catalog_behavior(persona["extends"], profile_index)

        slug = persona["name"]
        with ZipFile(DOWNLOADS / f"{slug}.zip", "w", compression=ZIP_DEFLATED) as archive:
            for filename in ("SKILL.md", "persona.yaml", "examples.md"):
                archive.write(package / filename, arcname=f"{slug}/{filename}")
            for variant_path in sorted((package / "variants").glob("*.yaml")):
                archive.write(
                    variant_path,
                    arcname=f"{slug}/variants/{variant_path.name}",
                )

        records.append({
            "name": slug,
            "displayName": persona["display_name"],
            "family": persona.get("persona_family"),
            "signature": persona.get("persona_signature", []),
            "category": persona["category"],
            "description": persona["description"],
            "profiles": persona["extends"],
            "presentation": persona["presentation"],
            "voice": catalog_voice(persona.get("voice", {})),
            "experience": catalog_experience(persona.get("experience", {})),
            "behavioralDepth": catalog_behavioral_depth(persona),
            "preferences": persona["preferences"],
            "behavior": behavior,
            "variants": catalog_variants(persona, profile_index),
            "related": [],
            "instructions": skill_instructions(package / "SKILL.md"),
            "example": first_example(package / "examples.md"),
            "image": f"images/{slug}.webp",
            "download": f"downloads/{slug}.zip",
            "source": f"https://github.com/r33n3/Personas/tree/main/personas/{slug}",
        })

    records.sort(key=lambda item: (CATEGORY_ORDER[item["category"]], item["displayName"].lower()))
    for record in records:
        source = persona_documents[record["name"]]
        candidates = []
        for other in records:
            if other["name"] == record["name"]:
                continue
            result = compare_personas(source, persona_documents[other["name"]])
            if result["same_family"] or max(result["behavioral"], result["character"]) >= 0.45:
                reason = (
                    "Same persona family"
                    if result["same_family"]
                    else "Shared behavior"
                    if result["behavioral"] >= result["character"]
                    else "Related presentation"
                )
                candidates.append((result["same_family"], max(result["behavioral"], result["character"]), other, reason))
        candidates.sort(key=lambda item: (-int(item[0]), -item[1], item[2]["displayName"].lower()))
        record["related"] = [
            {"name": other["name"], "displayName": other["displayName"], "reason": reason}
            for _, _, other, reason in candidates[:3]
        ]
    rendered = json.dumps(records, indent=2, ensure_ascii=False) + "\n"
    OUTPUT_JSON.write_text(rendered, encoding="utf-8")
    PUBLIC_JSON.write_text(rendered, encoding="utf-8")

    role_records = []
    role_downloads = DOWNLOADS / "roles"
    role_downloads.mkdir(parents=True, exist_ok=True)
    for role_path in sorted(ROLES.glob("*/role.yaml")):
        package = role_path.parent
        role = load_yaml(role_path)
        slug = role["name"]
        with ZipFile(role_downloads / f"{slug}.zip", "w", compression=ZIP_DEFLATED) as archive:
            for filename in ("role.yaml", "examples.md"):
                archive.write(package / filename, arcname=f"{slug}/{filename}")
        role_records.append({
            "name": slug,
            "displayName": role["display_name"],
            "category": role["category"],
            "description": role["description"].strip(),
            "optimizesFor": role["optimizes_for"],
            "noticesFirst": role["notices_first"],
            "recurringConcerns": role.get("recurring_concerns", []),
            "reviewQuestions": role.get("review_questions", []),
            "instructions": "\n".join(role_lens_instruction(role)) + "\n",
            "example": first_role_example(package / "examples.md"),
            "download": f"downloads/roles/{slug}.zip",
            "source": f"https://github.com/r33n3/Personas/tree/main/roles/{slug}",
        })
    role_records.sort(key=lambda item: (item["category"], item["displayName"].lower()))
    rendered_roles = json.dumps(role_records, indent=2, ensure_ascii=False) + "\n"
    ROLE_OUTPUT_JSON.write_text(rendered_roles, encoding="utf-8")
    ROLE_PUBLIC_JSON.write_text(rendered_roles, encoding="utf-8")
    print(
        f"Built website catalog, {len(records)} persona bundles, "
        f"and {len(role_records)} Role Lens bundles."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
