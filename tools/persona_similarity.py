"""Deterministic, explainable similarity signals for persona maintenance."""

from __future__ import annotations

import re
from typing import Any


def _jaccard(left: set[str], right: set[str]) -> float:
    if not left and not right:
        return 0.0
    return len(left & right) / len(left | right)


def _tokens(values: list[str]) -> set[str]:
    return {
        token
        for value in values
        for token in re.findall(r"[a-z0-9]+", value.lower())
        if len(token) > 2
    }


def _flatten(value: Any, prefix: str = "") -> set[str]:
    if isinstance(value, dict):
        return {
            item
            for key, child in value.items()
            for item in _flatten(child, f"{prefix}.{key}" if prefix else key)
        }
    if isinstance(value, list):
        return {
            item
            for child in value
            for item in _flatten(child, prefix)
        }
    return {f"{prefix}={str(value).lower()}"}


def _pushback(persona: dict[str, Any]) -> set[str]:
    return {
        item
        for trigger, rule in persona.get("pushback", {}).items()
        for item in [trigger, rule.get("strength", ""), *rule.get("actions", [])]
        if item
    }


def compare_personas(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    """Return behavioral and persona-character similarity with visible reasons."""
    if left == right:
        return {
            "behavioral": 1.0,
            "character": 1.0,
            "overall": 1.0,
            "same_family": bool(left.get("persona_family")),
            "shared": {
                "profiles": sorted(set(left.get("extends", []))),
                "convictions": sorted(set(left.get("convictions", []))),
                "pushback": sorted(_pushback(left)),
                "preferences": sorted(set(left.get("preferences", []))),
                "signature_terms": sorted(_tokens(left.get("persona_signature", []))),
            },
        }

    left_profiles, right_profiles = set(left.get("extends", [])), set(right.get("extends", []))
    left_convictions, right_convictions = set(left.get("convictions", [])), set(right.get("convictions", []))
    left_pushback, right_pushback = _pushback(left), _pushback(right)
    left_preferences, right_preferences = set(left.get("preferences", [])), set(right.get("preferences", []))
    behavior = (
        0.35 * _jaccard(left_profiles, right_profiles)
        + 0.20 * _jaccard(left_convictions, right_convictions)
        + 0.25 * _jaccard(left_pushback, right_pushback)
        + 0.20 * _jaccard(left_preferences, right_preferences)
    )

    left_signature, right_signature = _tokens(left.get("persona_signature", [])), _tokens(right.get("persona_signature", []))
    character = (
        0.30 * _jaccard(left_signature, right_signature)
        + 0.25 * _jaccard(_flatten(left.get("presentation", {})), _flatten(right.get("presentation", {})))
        + 0.30 * _jaccard(_flatten(left.get("voice", {})), _flatten(right.get("voice", {})))
        + 0.15 * _jaccard(_flatten(left.get("experience", {})), _flatten(right.get("experience", {})))
    )
    return {
        "behavioral": round(behavior, 4),
        "character": round(character, 4),
        "overall": round((behavior + character) / 2, 4),
        "same_family": bool(
            left.get("persona_family")
            and left.get("persona_family") == right.get("persona_family")
        ),
        "shared": {
            "profiles": sorted(left_profiles & right_profiles),
            "convictions": sorted(left_convictions & right_convictions),
            "pushback": sorted(left_pushback & right_pushback),
            "preferences": sorted(left_preferences & right_preferences),
            "signature_terms": sorted(left_signature & right_signature),
        },
    }


def recommendation(result: dict[str, Any]) -> str:
    behavioral, character = result["behavioral"], result["character"]
    if behavioral >= 0.75 and character >= 0.75:
        return "Likely duplicate or variant; clarify why both persona types are needed."
    if behavioral >= 0.65 and character < 0.50:
        return "Shared behavior with distinct character; consider extracting common profiles."
    if behavioral < 0.50 and character >= 0.65:
        return "Similar character with divergent behavior; verify whether this should be a variant."
    return "No strong structural duplication signal."
