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
    package_errors,
    profile_index,
    reference_errors,
    resolve_profiles,
    schema_errors,
)
from build_site_catalog import catalog_experience  # noqa: E402


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

    def test_every_persona_has_distinct_advisory_voice_metadata(self) -> None:
        definitions = set()
        banned_terms = {
            "elevenlabs", "openai_voice", "azure_voice", "amazon_polly",
            "voice_id", "sounds_like", "imitate", "celebrity", "famous_actor",
        }
        for path in sorted((ROOT / "personas").glob("*/persona.yaml")):
            with self.subTest(persona=path.parent.name):
                persona = load_yaml(path)
                self.assertEqual(persona["schema_version"], "0.2")
                voice = persona["voice"]
                self.assertTrue(voice["sound"])
                self.assertTrue(voice["delivery"])
                self.assertGreaterEqual(len(voice["mannerisms"]), 2)
                self.assertGreaterEqual(len(voice["context_rules"]), 2)
                serious = voice["context_rules"]["serious_context"]
                self.assertTrue(
                    serious.get("clarity") in {"high", "maximum"}
                    or serious.get("humor") == "none"
                    or serious.get("sarcasm") == "none"
                )
                rendered = json.dumps(voice, sort_keys=True)
                self.assertNotIn(rendered, definitions, path.parent.name)
                definitions.add(rendered)
                lowered = rendered.lower()
                for term in banned_terms:
                    self.assertNotIn(term, lowered)

                skill = (path.parent / "SKILL.md").read_text(encoding="utf-8")
                self.assertEqual(skill.count("## Voice Performance"), 1)
                for term in banned_terms:
                    self.assertNotIn(term, skill.lower())
                self.assertEqual(package_errors(persona, path), [])

    def test_voice_metadata_is_optional_in_persona_02(self) -> None:
        path = ROOT / "personas" / "professional" / "persona.yaml"
        persona = load_yaml(path)
        persona.pop("voice")
        self.assertEqual(schema_errors(persona, path), [])

    def test_professional_is_the_neutral_voice_control(self) -> None:
        professional = load_yaml(ROOT / "personas" / "professional" / "persona.yaml")
        self.assertEqual(professional["voice"]["sound"]["register"], "neutral")
        self.assertEqual(professional["voice"]["delivery"]["emotional_tone"], "professional")

    def test_voice_metadata_requires_matching_skill_guidance(self) -> None:
        professional = load_yaml(ROOT / "personas" / "professional" / "persona.yaml")
        professional.pop("convictions")
        professional.pop("pushback")
        professional.pop("uncertainty")
        persona_path = ROOT / "tests" / "fixtures" / "persona.yaml"
        errors = package_errors(professional, persona_path)
        self.assertEqual(len(errors), 1)
        self.assertIn("package guidance", errors[0])

    def test_behavioral_depth_pilot_is_structured_and_human_readable(self) -> None:
        expected_pushback = {
            "greybeard": "unnecessary_complexity",
            "diva": "sloppy_work",
            "redditor": "unsupported_claim",
            "burned-out-sysadmin": "fragile_operations",
            "professional": "unsupported_assumption",
        }
        for name, trigger in expected_pushback.items():
            path = ROOT / "personas" / name / "persona.yaml"
            persona = load_yaml(path)
            with self.subTest(persona=name):
                self.assertGreaterEqual(len(persona["convictions"]), 3)
                self.assertIn(trigger, persona["pushback"])
                self.assertIn(
                    persona["pushback"][trigger]["strength"],
                    {"measured", "strong", "absolute"},
                )
                self.assertTrue(persona["pushback"][trigger]["actions"])
                self.assertEqual(persona["uncertainty"]["acknowledgment"], "explicit")
                self.assertIn("fabricate", " ".join(persona["uncertainty"]["never"]))
                skill = (path.parent / "SKILL.md").read_text(encoding="utf-8")
                for heading in ("## Convictions", "## Pushback", "## Uncertainty"):
                    self.assertEqual(skill.count(heading), 1)
                self.assertEqual(package_errors(persona, path), [])

    def test_behavioral_depth_fields_remain_optional_in_persona_02(self) -> None:
        path = ROOT / "personas" / "professional" / "persona.yaml"
        persona = load_yaml(path)
        for field in ("convictions", "pushback", "uncertainty"):
            persona.pop(field)
        self.assertEqual(schema_errors(persona, path), [])

    def test_pushback_rejects_unknown_strength(self) -> None:
        path = ROOT / "personas" / "greybeard" / "persona.yaml"
        persona = load_yaml(path)
        persona["pushback"]["unnecessary_complexity"]["strength"] = "petulant"
        errors = schema_errors(persona, path)
        self.assertTrue(any("petulant" in error for error in errors))

    def test_experience_is_optional_complete_or_partial(self) -> None:
        path = ROOT / "personas" / "greybeard" / "persona.yaml"
        complete = load_yaml(path)
        self.assertEqual(schema_errors(complete, path), [])

        absent = dict(complete)
        absent.pop("experience")
        self.assertEqual(schema_errors(absent, path), [])

        partial = dict(absent)
        partial["experience"] = {"visual": {"mode": "dark"}}
        self.assertEqual(schema_errors(partial, path), [])

    def test_experience_rejects_unknown_malformed_and_executable_content(self) -> None:
        path = ROOT / "personas" / "professional" / "persona.yaml"
        persona = load_yaml(path)
        invalid_blocks = (
            {"soundtrack": {"style": "ominous"}},
            {"visual": {"mode": "sepia"}},
            {"terminal": "unix"},
            {"visual": {"accent": "javascript:alert(1)"}},
            {"terminal": {"script": "rm -rf /"}},
            {"avatar": {"url": "https://example.invalid/avatar.png"}},
        )
        for experience in invalid_blocks:
            with self.subTest(experience=experience):
                candidate = dict(persona)
                candidate["experience"] = experience
                self.assertTrue(schema_errors(candidate, path))


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
        self.assertIn("## Voice performance (advisory)", output)
        self.assertIn("tone: calm authority", output)
        self.assertIn("## Convictions", output)
        self.assertIn("Complexity requires justification", output)
        self.assertIn("## Pushback", output)
        self.assertIn("Unnecessary Complexity (strong)", output)
        self.assertIn("## Uncertainty", output)
        self.assertIn("fabricate missing evidence", output)
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
                self.assertIn("Character affects performance; context controls intensity.", output)

    def test_experience_does_not_change_behavioral_prompt_output(self) -> None:
        persona = load_yaml(ROOT / "personas" / "greybeard" / "persona.yaml")
        with_experience = build_instruction(persona, resolve_profiles(persona))
        without_experience = dict(persona)
        without_experience.pop("experience")
        self.assertEqual(
            with_experience,
            build_instruction(without_experience, resolve_profiles(without_experience)),
        )
        self.assertNotIn("phosphor", with_experience.lower())
        self.assertNotIn("scanline", with_experience.lower())


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


class DialogueConformanceTests(unittest.TestCase):
    def test_pilot_dialogue_suites_validate(self) -> None:
        result = subprocess.run(
            [sys.executable, str(TOOLS / "validate_dialogues.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            "Validated 5 dialogue suite(s), 15 case(s), and 30 assistant turn(s).",
            result.stdout,
        )

    def test_pilot_uses_shared_serious_and_uncertainty_scenarios(self) -> None:
        suite_paths = sorted((ROOT / "tests" / "dialogues" / "personas").glob("*.yaml"))
        self.assertEqual(
            {path.stem for path in suite_paths},
            {"greybeard", "diva", "redditor", "burned-out-sysadmin", "professional"},
        )
        for path in suite_paths:
            suite = yaml.safe_load(path.read_text(encoding="utf-8"))
            cases = {case["id"]: case for case in suite["cases"]}
            with self.subTest(persona=suite["persona"]):
                self.assertEqual(cases["serious-context"]["scenario"], "exposed-production-credential")
                self.assertEqual(cases["uncertainty"]["scenario"], "missing-evidence")
                self.assertIn("user_turns", cases["signature"])
                self.assertNotIn("scenario", cases["signature"])
                self.assertEqual(len(cases["signature"]["assistant_turns"]), 2)


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
        self.assertEqual(
            len({item["voice"]["summary"] for item in catalog}),
            len(catalog),
        )
        depth_personas = {
            item["name"] for item in catalog if item["behavioralDepth"] is not None
        }
        self.assertEqual(
            depth_personas,
            {"greybeard", "diva", "redditor", "burned-out-sysadmin", "professional"},
        )
        experience_personas = {
            item["name"] for item in catalog if item["experience"] is not None
        }
        self.assertEqual(experience_personas, {"greybeard"})
        greybeard = next(item for item in catalog if item["name"] == "greybeard")
        self.assertEqual(greybeard["experience"]["visual"]["accent"], "phosphor-green")
        self.assertEqual(greybeard["experience"]["preview"]["terminal"], "unix")
        for item in catalog:
            with self.subTest(persona=item["name"]):
                self.assertTrue(item["instructions"].startswith("# "))
                self.assertIn("invariant", item["instructions"].lower())
                self.assertTrue(item["voice"]["summary"])
                self.assertTrue(item["voice"]["soundSummary"])
                self.assertTrue(item["voice"]["deliverySummary"])
                self.assertIn("serious_context", item["voice"]["contextRules"])
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
                    bundled = yaml.safe_load(
                        archive.read(f"{item['name']}/persona.yaml").decode("utf-8")
                    )
                    self.assertIn("voice", bundled)
                    depth = item["behavioralDepth"]
                    if item["name"] in depth_personas:
                        self.assertEqual(depth["convictions"], bundled["convictions"])
                        self.assertEqual(depth["pushback"], bundled["pushback"])
                        self.assertEqual(depth["uncertainty"], bundled["uncertainty"])

    def test_experience_preview_uses_safe_fallbacks(self) -> None:
        experience = catalog_experience({
            "visual": {"mode": "adaptive", "accent": "future-purple", "typography": "display"},
            "terminal": {"style": "crt", "scanlines": "subtle", "glow": "low"},
            "motion": {"intensity": "subtle"},
        })
        self.assertIsNotNone(experience)
        self.assertEqual(experience["preview"]["mode"], "default")
        self.assertEqual(experience["preview"]["accent"], "default")
        self.assertEqual(experience["preview"]["typography"], "default")
        self.assertEqual(experience["preview"]["terminal"], "crt")

    def test_experience_preview_respects_reduced_motion(self) -> None:
        styles = (ROOT / "site" / "src" / "styles.css").read_text(encoding="utf-8")
        self.assertIn("@media(prefers-reduced-motion:reduce)", styles)
        self.assertIn(".experience-preview *{animation:none!important}", styles)


if __name__ == "__main__":
    unittest.main()
