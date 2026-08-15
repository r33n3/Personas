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
            "preferences": persona["preferences"],
            "behavior": behavior,
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
