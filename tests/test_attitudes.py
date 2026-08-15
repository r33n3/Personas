from __future__ import annotations

import subprocess
import sys
import unittest
import json
from zipfile import ZipFile
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS))

CONCEPT_PERSONAS = {
    "greybeard", "mainframe-operator", "cobol-survivor", "bell-labs-ghost",
    "bbs-sysop", "usenet-elder", "lan-party-veteran", "irc-operator",
    "computer-store-guy", "radioshack-wizard", "redditor",
    "stack-overflow-elder", "forum-moderator", "slashdot-veteran",
    "open-source-maintainer", "github-issue-archaeologist", "discord-developer",
    "tech-blogger-2007", "burned-out-sysadmin", "old-school-network-engineer",
    "security-paranoid", "pentester", "incident-commander", "retired-engineer",
    "nasa-engineer-1969", "soviet-engineer", "old-shop-teacher",
    "ham-radio-operator", "embedded-engineer", "database-curmudgeon",
    "enterprise-architect", "scrum-master-supreme", "management-consultant",
    "mba-executive", "change-control-bureaucrat", "it-helpdesk-veteran",
    "corporate-survivor", "startup-founder", "vc-bro", "ai-founder",
    "prompt-influencer", "crypto-bro", "gen-z-developer",
    "millennial-developer", "diva", "british-butler", "film-noir-detective",
    "mad-scientist", "victorian-scholar", "caveman-developer",
}

from attitudes import (  # noqa: E402
    build_instruction,
    load_yaml,
    profile_index,
    reference_errors,
    resolve_profiles,
    schema_errors,
)


class DefinitionTests(unittest.TestCase):
    def test_all_bundled_definitions_validate(self) -> None:
        result = subprocess.run(
            [sys.executable, str(TOOLS / "validate_persona.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Validated 69 definition(s).", result.stdout)

    def test_invalid_persona_reports_schema_errors(self) -> None:
        path = ROOT / "tests" / "fixtures" / "invalid-persona.yaml"
        errors = schema_errors(load_yaml(path), path)
        self.assertGreaterEqual(len(errors), 4)

    def test_missing_profile_reference_is_reported(self) -> None:
        path = ROOT / "tests" / "fixtures" / "missing-profile-persona.yaml"
        profiles, index_errors = profile_index()
        self.assertEqual(index_errors, [])
        errors = reference_errors(load_yaml(path), path, profiles)
        self.assertEqual(len(errors), 1)
        self.assertIn("does-not-exist", errors[0])

    def test_each_persona_package_has_required_files_and_examples(self) -> None:
        for persona_dir in sorted(path for path in (ROOT / "personas").iterdir() if path.is_dir()):
            with self.subTest(persona=persona_dir.name):
                self.assertTrue((persona_dir / "SKILL.md").is_file())
                self.assertTrue((persona_dir / "persona.yaml").is_file())
                examples = (persona_dir / "examples.md").read_text(encoding="utf-8")
                self.assertGreaterEqual(examples.count("**User:**"), 3)

    def test_catalog_contains_exactly_the_50_concepts_plus_control(self) -> None:
        persona_dirs = {path.name for path in (ROOT / "personas").iterdir() if path.is_dir()}
        self.assertEqual(persona_dirs, CONCEPT_PERSONAS | {"professional"})

        category_counts = {}
        signature_actions = set()
        for name in persona_dirs:
            persona = load_yaml(ROOT / "personas" / name / "persona.yaml")
            category = persona["category"]
            category_counts[category] = category_counts.get(category, 0) + 1
            if name != "professional":
                signature = persona["must"][1]
                self.assertNotIn(signature, signature_actions, name)
                signature_actions.add(signature)

        self.assertEqual(category_counts, {
            "computing-history": 10,
            "internet-culture": 8,
            "it-and-engineering": 12,
            "corporate-life": 7,
            "startup-and-modern-tech": 7,
            "character-archetypes": 6,
            "control": 1,
        })


class CompositionTests(unittest.TestCase):
    def test_profile_resolution_preserves_order_and_deduplicates(self) -> None:
        persona = load_yaml(ROOT / "personas" / "greybeard" / "persona.yaml")
        profiles = resolve_profiles(
            persona, ["quality-focused-reviewer", "skeptical-engineer"]
        )
        self.assertEqual(
            [profile["name"] for profile in profiles],
            ["skeptical-engineer", "quality-focused-reviewer"],
        )

    def test_builder_includes_behavior_presentation_and_invariants(self) -> None:
        persona = load_yaml(ROOT / "personas" / "greybeard" / "persona.yaml")
        output = build_instruction(persona, resolve_profiles(persona))
        self.assertIn("propose simpler alternative", output)
        self.assertIn("Sarcasm: moderate", output)
        self.assertIn("Prefer minimal dependencies.", output)
        self.assertIn("Kubernetes for tiny workloads: extreme", output)
        self.assertIn("Personality may degrade; competence may not.", output)
        self.assertLess(output.index("## Behavioral requirements"), output.index("## Presentation"))

    def test_builder_cli_rejects_missing_profile(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(TOOLS / "build_prompt.py"),
                str(ROOT / "personas" / "professional" / "persona.yaml"),
                "--profile",
                "does-not-exist",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("does not exist", result.stderr)

    def test_every_persona_builds_a_complete_instruction_document(self) -> None:
        for path in sorted((ROOT / "personas").glob("*/persona.yaml")):
            with self.subTest(persona=path.parent.name):
                persona = load_yaml(path)
                profiles = resolve_profiles(persona)
                output = build_instruction(persona, profiles)
                self.assertIn(f"# Agent Attitude: {persona['display_name']}", output)
                self.assertIn(persona["must"][1].replace("_", " "), output.lower())
                for profile in profiles:
                    self.assertIn(f"### {profile['name']}", output)
                self.assertIn("Personality may degrade; competence may not.", output)


class ScenarioTests(unittest.TestCase):
    def test_scenario_catalog_has_consistent_minimum_contract(self) -> None:
        scenario_paths = sorted((ROOT / "tests" / "scenarios").glob("*.yaml"))
        self.assertGreaterEqual(len(scenario_paths), 10)
        names = set()
        for path in scenario_paths:
            with self.subTest(scenario=path.name):
                scenario = yaml.safe_load(path.read_text(encoding="utf-8"))
                self.assertEqual(path.stem, scenario["name"])
                self.assertNotIn(scenario["name"], names)
                names.add(scenario["name"])
                self.assertTrue(scenario["prompt"].strip())
                self.assertTrue(scenario["expectations"]["behavioral"])
                self.assertTrue(scenario["expectations"]["invariants"])
                self.assertIn("professional", scenario["persona_expectations"])


class ExperimentalDesignTests(unittest.TestCase):
    def test_narrative_style_scenarios_have_preservation_contracts(self) -> None:
        path = ROOT / "tests" / "experimental" / "narrative_style_scenarios.yaml"
        experiment = yaml.safe_load(path.read_text(encoding="utf-8"))
        self.assertFalse(experiment["normative"])
        self.assertIn("film-noir", experiment["styles"])
        self.assertGreaterEqual(len(experiment["scenarios"]), 8)

        names = set()
        for scenario in experiment["scenarios"]:
            with self.subTest(scenario=scenario["name"]):
                self.assertNotIn(scenario["name"], names)
                names.add(scenario["name"])
                self.assertTrue(scenario["prompt"].strip())
                self.assertTrue(scenario["expectations"]["preserve"])

    def test_archetype_boundary_scenarios_are_non_normative(self) -> None:
        path = ROOT / "tests" / "experimental" / "archetype_boundaries.yaml"
        experiment = yaml.safe_load(path.read_text(encoding="utf-8"))
        self.assertFalse(experiment["normative"])
        self.assertGreaterEqual(len(experiment["scenarios"]), 5)
        for scenario in experiment["scenarios"]:
            with self.subTest(scenario=scenario["name"]):
                self.assertTrue(scenario["expected"])

    def test_experiment_does_not_enter_normative_persona_documents(self) -> None:
        for path in sorted((ROOT / "personas").glob("*/persona.yaml")):
            with self.subTest(persona=path.parent.name):
                persona = load_yaml(path)
                self.assertNotIn("narrative_style", persona)
                self.assertNotIn("experimental_composition", persona)


class WebsiteCatalogTests(unittest.TestCase):
    def test_site_catalog_and_downloads_derive_from_all_personas(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "build_site_catalog.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        catalog = json.loads(
            (ROOT / "site" / "public" / "catalog.json").read_text(encoding="utf-8")
        )
        self.assertEqual({item["name"] for item in catalog}, CONCEPT_PERSONAS | {"professional"})
        for item in catalog:
            with self.subTest(persona=item["name"]):
                self.assertTrue((ROOT / "site" / "public" / item["image"]).is_file())
                bundle = ROOT / "site" / "public" / item["download"]
                self.assertTrue(bundle.is_file())
                with ZipFile(bundle) as archive:
                    self.assertEqual(
                        set(archive.namelist()),
                        {
                            f"{item['name']}/SKILL.md",
                            f"{item['name']}/persona.yaml",
                            f"{item['name']}/examples.md",
                        },
                    )


if __name__ == "__main__":
    unittest.main()
