#!/usr/bin/env python3
"""Build the website catalog and downloadable bundles from repository source."""

from __future__ import annotations

import json
import re
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import yaml

ROOT = Path(__file__).resolve().parents[1]
PERSONAS = ROOT / "personas"
PROFILES = ROOT / "profiles"
SITE = ROOT / "site"
OUTPUT_JSON = SITE / "src" / "personas.generated.json"
PUBLIC_JSON = SITE / "public" / "catalog.json"
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


def main() -> int:
    profile_index = {path.stem: load_yaml(path) for path in PROFILES.glob("*.yaml")}
    records = []
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)

    for persona_path in PERSONAS.glob("*/persona.yaml"):
        package = persona_path.parent
        persona = load_yaml(persona_path)
        behavior = []
        for profile_name in persona["extends"]:
            profile = profile_index[profile_name]
            for rule_name, rule in profile["behavior"].items():
                behavior.append({
                    "profile": profile_name,
                    "rule": rule_name.replace("_", " "),
                    "when": rule.get("when", "generally").replace("_", " "),
                    "actions": [action.replace("_", " ") for action in rule["actions"]],
                })

        slug = persona["name"]
        with ZipFile(DOWNLOADS / f"{slug}.zip", "w", compression=ZIP_DEFLATED) as archive:
            for filename in ("SKILL.md", "persona.yaml", "examples.md"):
                archive.write(package / filename, arcname=f"{slug}/{filename}")

        records.append({
            "name": slug,
            "displayName": persona["display_name"],
            "category": persona["category"],
            "description": persona["description"],
            "profiles": persona["extends"],
            "presentation": persona["presentation"],
            "voice": catalog_voice(persona.get("voice", {})),
            "experience": catalog_experience(persona.get("experience", {})),
            "behavioralDepth": catalog_behavioral_depth(persona),
            "preferences": persona["preferences"],
            "behavior": behavior,
            "instructions": skill_instructions(package / "SKILL.md"),
            "example": first_example(package / "examples.md"),
            "image": f"images/{slug}.webp",
            "download": f"downloads/{slug}.zip",
            "source": f"https://github.com/r33n3/Personas/tree/main/personas/{slug}",
        })

    records.sort(key=lambda item: (CATEGORY_ORDER[item["category"]], item["displayName"].lower()))
    rendered = json.dumps(records, indent=2, ensure_ascii=False) + "\n"
    OUTPUT_JSON.write_text(rendered, encoding="utf-8")
    PUBLIC_JSON.write_text(rendered, encoding="utf-8")
    print(f"Built website catalog and {len(records)} persona bundles.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
