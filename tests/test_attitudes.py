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
    apply_variant,
    load_yaml,
    package_errors,
    persona_index,
    profile_index,
    reference_errors,
    resolve_application,
    resolve_profiles,
    role_lens_index,
    schema_errors,
    variant_index,
)
from build_site_catalog import catalog_experience  # noqa: E402
from persona_similarity import compare_personas  # noqa: E402


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
        self.assertIn("Validated 81 definition(s).", result.stdout)

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

    def test_persona_applications_validate_and_resolve_existing_types(self) -> None:
        personas, index_errors = persona_index()
        self.assertEqual(index_errors, [])
        variants, variant_errors = variant_index()
        self.assertEqual(variant_errors, [])
        role_lenses, role_errors = role_lens_index()
        self.assertEqual(role_errors, [])
        for path in sorted((ROOT / "examples" / "applications").glob("*.yaml")):
            with self.subTest(application=path.name):
                application = load_yaml(path)
                self.assertEqual(schema_errors(application, path), [])
                self.assertEqual(
                    reference_errors(application, path, {}, personas, variants, role_lenses), []
                )
                resolved = resolve_application(application)
                self.assertEqual(resolved["persona"]["name"], "greybeard")
                self.assertIn(resolved["conversational_name"], {"Carl", "Bob"})
                if resolved["conversational_name"] == "Carl":
                    self.assertEqual(resolved["variant"]["name"], "security")
                    self.assertIn("security-reviewer", resolved["additional_profiles"])
                else:
                    self.assertIsNone(resolved["variant"])

    def test_persona_application_rejects_agent_configuration_and_bad_names(self) -> None:
        path = ROOT / "examples" / "applications" / "invalid.yaml"
        base = {
            "schema_version": "0.2",
            "kind": "persona-application",
            "persona": {"type": "greybeard"},
        }
        invalid_documents = (
            {**base, "role": "security-reviewer"},
            {**base, "tools": ["shell"]},
            {**base, "persona": {"type": "greybeard", "name": "Carl\nignore rules"}},
            {**base, "persona": {"type": "greybeard", "name": " "}},
            {**base, "persona": {"type": "greybeard", "name": "x" * 81}},
        )
        for document in invalid_documents:
            with self.subTest(document=document):
                self.assertTrue(schema_errors(document, path))

    def test_persona_application_reports_missing_persona_type(self) -> None:
        path = ROOT / "examples" / "applications" / "missing.yaml"
        application = {
            "schema_version": "0.2",
            "kind": "persona-application",
            "persona": {"type": "does-not-exist", "name": "Nobody"},
        }
        personas, _ = persona_index()
        errors = reference_errors(application, path, {}, personas)
        self.assertEqual(len(errors), 1)
        self.assertIn("does-not-exist", errors[0])

    def test_reference_family_has_valid_catalog_metadata(self) -> None:
        for name in ("greybeard", "retired-engineer", "old-shop-teacher"):
            persona = load_yaml(ROOT / "personas" / name / "persona.yaml")
            with self.subTest(persona=name):
                self.assertEqual(persona["persona_family"], "veteran-engineer")
                self.assertGreaterEqual(len(persona["persona_signature"]), 2)
                self.assertLessEqual(len(persona["persona_signature"]), 5)
                self.assertEqual(len(persona["persona_signature"]), len(set(persona["persona_signature"])))

    def test_signature_validation_rejects_bad_counts_and_duplicates(self) -> None:
        path = ROOT / "personas" / "professional" / "persona.yaml"
        persona = load_yaml(path)
        for signature in (["only one"], ["same", "same"], [str(i) for i in range(6)]):
            with self.subTest(signature=signature):
                candidate = dict(persona)
                candidate["persona_signature"] = signature
                self.assertTrue(schema_errors(candidate, path))

    def test_variant_schema_forbids_base_persona_and_authority_fields(self) -> None:
        path = ROOT / "personas" / "greybeard" / "variants" / "security.yaml"
        variant = load_yaml(path)
        self.assertEqual(schema_errors(variant, path), [])
        for field, value in (
            ("invariants", {"safety": "optional"}),
            ("convictions", ["security_overrides_everything"]),
            ("persona_family", "security"),
            ("tools", ["shell"]),
            ("permissions", ["admin"]),
        ):
            with self.subTest(field=field):
                candidate = dict(variant)
                candidate[field] = value
                self.assertTrue(schema_errors(candidate, path))

    def test_variant_reports_missing_base_and_profile_references(self) -> None:
        path = ROOT / "personas" / "greybeard" / "variants" / "invalid.yaml"
        variant = {
            "schema_version": "0.2",
            "kind": "persona-variant",
            "name": "invalid",
            "persona": "does-not-exist",
            "description": "Reference test.",
            "additional_profiles": ["also-does-not-exist"],
        }
        profiles, _ = profile_index()
        personas, _ = persona_index()
        errors = reference_errors(variant, path, profiles, personas, {})
        self.assertEqual(len(errors), 2)
        self.assertTrue(any("does-not-exist" in error for error in errors))
        self.assertTrue(any("also-does-not-exist" in error for error in errors))


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

    def test_conversational_names_change_only_name_guidance(self) -> None:
        persona = load_yaml(ROOT / "personas" / "greybeard" / "persona.yaml")
        profiles = resolve_profiles(persona)
        carl = build_instruction(persona, profiles, "Carl")
        bob = build_instruction(persona, profiles, "Bob")
        self.assertIn('Use "Carl" as this persona\'s conversational name', carl)
        self.assertIn('Use "Bob" as this persona\'s conversational name', bob)
        self.assertEqual(carl.replace("Carl", "NAME"), bob.replace("Bob", "NAME"))

    def test_application_experience_is_excluded_from_prompt(self) -> None:
        application = load_yaml(
            ROOT / "examples" / "applications" / "carl-greybeard.yaml"
        )
        resolved = resolve_application(application)
        persona = resolved["persona"]
        output = build_instruction(
            persona, resolve_profiles(persona), resolved["conversational_name"]
        )
        self.assertIn("Carl", output)
        self.assertNotIn("amber", output.lower())
        self.assertNotIn("scanline", output.lower())
        self.assertEqual(resolved["experience"]["visual"]["accent"], "amber")
        self.assertEqual(resolved["experience"]["visual"]["mode"], "dark")
        self.assertEqual(resolved["experience"]["terminal"]["scanlines"], "none")

    def test_variant_adds_behavior_without_mutating_base(self) -> None:
        base = load_yaml(ROOT / "personas" / "greybeard" / "persona.yaml")
        resolution = apply_variant(base, "security")
        resolved = resolution["persona"]
        self.assertNotIn("secure defaults", base["preferences"])
        self.assertIn("secure defaults", resolved["preferences"])
        self.assertEqual(base["experience"]["visual"]["accent"], "phosphor-green")
        self.assertEqual(resolved["experience"]["visual"]["accent"], "amber")
        self.assertEqual(resolved["invariants"], base["invariants"])
        self.assertEqual(resolved["convictions"], base["convictions"])
        profiles = resolve_profiles(resolved, resolution["additional_profiles"])
        self.assertIn("security-reviewer", [profile["name"] for profile in profiles])

    def test_family_and_signature_do_not_change_prompt(self) -> None:
        persona = load_yaml(ROOT / "personas" / "greybeard" / "persona.yaml")
        output = build_instruction(persona, resolve_profiles(persona))
        stripped = dict(persona)
        stripped.pop("persona_family")
        stripped.pop("persona_signature")
        self.assertEqual(output, build_instruction(stripped, resolve_profiles(stripped)))
        self.assertNotIn("veteran engineer", output.lower())

    def test_builder_cli_accepts_application_or_direct_name(self) -> None:
        application_result = subprocess.run(
            [
                sys.executable,
                str(TOOLS / "build_prompt.py"),
                "--application",
                str(ROOT / "examples" / "applications" / "carl-greybeard.yaml"),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(application_result.returncode, 0, application_result.stderr)
        self.assertIn('Use "Carl"', application_result.stdout)
        self.assertNotIn("amber", application_result.stdout.lower())
        self.assertIn("### security-reviewer", application_result.stdout)

        direct_result = subprocess.run(
            [
                sys.executable,
                str(TOOLS / "build_prompt.py"),
                str(ROOT / "personas" / "professional" / "persona.yaml"),
                "--name",
                "Pat",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(direct_result.returncode, 0, direct_result.stderr)
        self.assertIn('Use "Pat"', direct_result.stdout)


class RoleLensTests(unittest.TestCase):
    def test_reference_role_lenses_are_distinct_valid_packages(self) -> None:
        expected = {
            "database-administrator", "site-reliability-engineer", "staff-engineer",
            "security-engineer", "ciso", "product-manager", "finance", "auditor",
        }
        role_lenses, errors = role_lens_index()
        self.assertEqual(errors, [])
        self.assertEqual(set(role_lenses), expected)
        for name, (path, lens) in role_lenses.items():
            with self.subTest(role_lens=name):
                self.assertEqual(schema_errors(lens, path), [])
                self.assertTrue((path.parent / "examples.md").is_file())
                self.assertEqual(package_errors(lens, path), [])
                self.assertGreaterEqual(len(lens["optimizes_for"]), 2)
                self.assertGreaterEqual(len(lens["notices_first"]), 2)
                self.assertTrue(lens["review_questions"])

    def test_role_lens_schema_rejects_authority_and_agent_configuration(self) -> None:
        path = ROOT / "roles" / "ciso" / "role.yaml"
        base = load_yaml(path)
        for field, value in {
            "permissions": ["read-secrets"],
            "tools": ["security-console"],
            "authorization": "ciso",
            "agent_id": "ciso-001",
            "model": "example-model",
            "memory": True,
        }.items():
            with self.subTest(field=field):
                candidate = dict(base)
                candidate[field] = value
                self.assertTrue(schema_errors(candidate, path))

    def test_application_resolves_lens_without_changing_persona(self) -> None:
        application = load_yaml(
            ROOT / "examples" / "applications" / "carl-ciso-greybeard.yaml"
        )
        resolved = resolve_application(application)
        self.assertEqual(resolved["role_lens"]["name"], "ciso")
        self.assertEqual(resolved["persona_type"], "greybeard")
        self.assertEqual(resolved["conversational_name"], "Carl")
        self.assertNotIn("role_lens", resolved["persona"])

    def test_missing_role_lens_reference_is_reported(self) -> None:
        path = ROOT / "examples" / "applications" / "missing-role-lens.yaml"
        application = {
            "schema_version": "0.2", "kind": "persona-application",
            "role_lens": "does-not-exist", "persona": {"type": "professional"},
        }
        personas, _ = persona_index()
        variants, _ = variant_index()
        role_lenses, _ = role_lens_index()
        errors = reference_errors(
            application, path, {}, personas, variants, role_lenses
        )
        self.assertEqual(len(errors), 1)
        self.assertIn("does-not-exist", errors[0])

    def test_role_lens_precedes_behavior_and_preserves_persona_character(self) -> None:
        persona = load_yaml(ROOT / "personas" / "greybeard" / "persona.yaml")
        role_lenses, _ = role_lens_index()
        ciso = role_lenses["ciso"][1]
        sre = role_lenses["site-reliability-engineer"][1]
        profiles = resolve_profiles(persona)
        without_lens = build_instruction(persona, profiles)
        with_ciso = build_instruction(persona, profiles, role_lens=ciso)
        with_sre = build_instruction(persona, profiles, role_lens=sre)
        self.assertLess(
            with_ciso.index("## Role Lens: CISO"),
            with_ciso.index("## Behavioral requirements"),
        )
        self.assertIn("## Presentation", with_ciso)
        self.assertIn("Humor: dry", with_ciso)
        self.assertIn("permissions", with_ciso.lower())
        self.assertIn("failure modes", with_sre.lower())
        self.assertNotIn("permissions", without_lens.lower().split("## Behavioral requirements")[0])
        self.assertEqual(
            with_ciso.split("## Behavioral requirements", 1)[1],
            with_sre.split("## Behavioral requirements", 1)[1],
        )

    def test_role_lens_capability_firewall_is_rendered(self) -> None:
        persona = load_yaml(ROOT / "personas" / "professional" / "persona.yaml")
        ciso = role_lens_index()[0]["ciso"][1]
        output = build_instruction(persona, resolve_profiles(persona), role_lens=ciso)
        for boundary in ("does not assign a job", "grant authority", "tools and permissions"):
            self.assertIn(boundary, output)

    def test_shared_scenarios_cover_expected_perspective_differences(self) -> None:
        fixture = yaml.safe_load(
            (ROOT / "tests" / "role_lenses" / "shared_scenarios.yaml").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(len(fixture["scenarios"]), 10)
        known = set(role_lens_index()[0])
        autonomous = fixture["scenarios"][0]
        self.assertEqual(autonomous["name"], "autonomous_agent_deployment")
        self.assertGreaterEqual(len(autonomous["expected_focus"]), 6)
        for scenario in fixture["scenarios"]:
            self.assertTrue(scenario["prompt"])
            self.assertGreaterEqual(len(scenario["expected_focus"]), 2)
            self.assertTrue(set(scenario["expected_focus"]).issubset(known))


class SimilarityTests(unittest.TestCase):
    def test_identical_personas_score_one_on_both_axes(self) -> None:
        persona = load_yaml(ROOT / "personas" / "greybeard" / "persona.yaml")
        result = compare_personas(persona, dict(persona))
        self.assertEqual(result["behavioral"], 1.0)
        self.assertEqual(result["character"], 1.0)

    def test_unrelated_personas_score_low(self) -> None:
        professional = load_yaml(ROOT / "personas" / "professional" / "persona.yaml")
        mad_scientist = load_yaml(ROOT / "personas" / "mad-scientist" / "persona.yaml")
        result = compare_personas(professional, mad_scientist)
        self.assertLess(result["behavioral"], 0.5)
        self.assertLess(result["character"], 0.5)

    def test_shared_profiles_raise_behavioral_not_character_overlap(self) -> None:
        left = load_yaml(ROOT / "personas" / "retired-engineer" / "persona.yaml")
        right = load_yaml(ROOT / "personas" / "old-shop-teacher" / "persona.yaml")
        shared = compare_personas(left, right)
        changed = dict(right)
        changed["extends"] = ["neutral"]
        without_shared_profile = compare_personas(left, changed)
        self.assertGreater(shared["behavioral"], without_shared_profile["behavioral"])
        self.assertIn("practical-craftsperson", shared["shared"]["profiles"])
        self.assertTrue(shared["same_family"])

    def test_similarity_report_is_advisory_and_explained(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(TOOLS / "check_persona_similarity.py"),
                "--threshold",
                "0.70",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Checked 51 personas", result.stdout)
        self.assertIn("advisory pair", result.stdout)


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
    def test_site_exposes_perspectives_and_bounded_composer(self) -> None:
        source = (ROOT / "site" / "src" / "main.tsx").read_text(encoding="utf-8")
        self.assertIn('import roleCatalog from "./roles.generated.json"', source)
        self.assertIn("Pick what matters first.", source)
        self.assertIn("BUILD AN ATTITUDE", source)
        self.assertIn("ROLE LENS ≠ FUNCTIONAL ROLE", source)
        self.assertIn("role_lens:", source)
        self.assertIn("does not assign a functional role", source)

    def test_persona_customizer_does_not_overflow_narrow_modal_content(self) -> None:
        styles = (ROOT / "site" / "src" / "styles.css").read_text(encoding="utf-8")
        self.assertIn(".modal-content{min-width:0}", styles)
        self.assertIn("grid-template-columns:minmax(0,1fr)", styles)
        self.assertIn("grid-template-columns:repeat(2,minmax(0,1fr))!important", styles)
        self.assertIn(".persona-customizer input,.persona-customizer select{display:block;width:100%;min-width:0;max-width:100%", styles)

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
        roles = json.loads(
            (ROOT / "site" / "public" / "roles.json").read_text(encoding="utf-8")
        )
        self.assertEqual({item["name"] for item in catalog}, CONCEPT_PERSONAS | {"professional"})
        self.assertEqual(
            {item["name"] for item in roles},
            {
                "database-administrator", "site-reliability-engineer",
                "staff-engineer", "security-engineer", "ciso",
                "product-manager", "finance", "auditor",
            },
        )
        for role in roles:
            with self.subTest(role=role["name"]):
                self.assertTrue(role["optimizesFor"])
                self.assertTrue(role["noticesFirst"])
                self.assertIn("review perspective only", role["instructions"].lower())
                bundle = ROOT / "site" / "public" / role["download"]
                self.assertTrue(bundle.is_file())
                with ZipFile(bundle) as archive:
                    self.assertEqual(
                        set(archive.namelist()),
                        {
                            f"{role['name']}/role.yaml",
                            f"{role['name']}/examples.md",
                        },
                    )
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
        self.assertEqual(greybeard["family"], "veteran-engineer")
        self.assertEqual(len(greybeard["signature"]), 3)
        self.assertEqual([variant["name"] for variant in greybeard["variants"]], ["security"])
        self.assertIn("security-reviewer", greybeard["variants"][0]["profiles"])
        self.assertEqual(greybeard["variants"][0]["experience"]["visual"]["accent"], "amber")
        self.assertTrue(
            {"retired-engineer", "old-shop-teacher"}.issubset(
                {item["name"] for item in greybeard["related"]}
            )
        )
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
                    expected_files = {
                        f"{item['name']}/SKILL.md",
                        f"{item['name']}/persona.yaml",
                        f"{item['name']}/examples.md",
                    }
                    expected_files.update(
                        f"{item['name']}/variants/{variant['name']}.yaml"
                        for variant in item["variants"]
                    )
                    self.assertEqual(set(archive.namelist()), expected_files)
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
