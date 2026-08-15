# Contributing

Contributions should preserve the joke and improve the engineering.

## Persona requirements

A persona contribution must include `SKILL.md`, `persona.yaml`, and `examples.md`. It must have:

- a unique, repeatable persona character;
- an existing behavioral profile or a well-justified new one;
- clear presentation characteristics;
- provider-neutral voice metadata with distinct sound and delivery guidance;
- contextual voice rules that reduce inappropriate performance in serious situations;
- all four competence invariants;
- explicit prohibited behavior;
- at least three meaningfully different example interactions;
- valid schema and profile references;
- relevant scenario coverage when it introduces new behavior.

The dialogue pilot under `tests/dialogues/` uses shared serious and uncertainty scenarios plus a persona-specific signature conversation. Reference responses demonstrate acceptable behavior; they are not exact prose that every model must reproduce. New suites should test at least two turns, carry behavior, presentation, voice, and invariant expectations on every assistant turn, and show that the persona adapts when the user adds information.

Set `category` to one of the values allowed by the persona schema. Categories organize discovery only; they do not imply behavior or instruction priority.

Do not contribute a persona that is merely “be sarcastic,” depends on impersonating a copyrighted fictional character or living individual, targets a protected class, uses personal abuse as its main joke, or intentionally makes answers less correct or complete.

Voice-capable personas must keep `persona.yaml` and the `## Voice Performance` section in `SKILL.md` consistent. Describe acoustic and delivery characteristics rather than named voices, celebrities, actors, or proprietary provider identifiers. Voice metadata is advisory and must bend to context without weakening competence.

Optional `experience` metadata describes consumer presentation intent, not agent instructions. Use only the declarative fields in `schemas/experience.schema.json`; do not add URLs, code, CSS, HTML, scripts, provider identifiers, or executable assets. Consumers may ignore any supported section, and accessibility settings take precedence. A persona does not need an experience block to conform.

Persona applications contain only an optional `role_lens`, persona `type`, conversational `name`, and optional `experience` overrides. Names must remain single-line user labels and must never be described as identifiers, authentication, provenance, authority, or permission. A Role Lens is a review perspective, not a functional role. Do not add agent jobs, tools, models, credentials, memory, routing, or deployment settings to the application schema.

## Role Lenses

Add a Role Lens only when it contributes a distinct attention pattern: what it optimizes for, notices first, and repeatedly considers. Reusable reactions and challenge actions belong in behavioral profiles. Character, humor, and social delivery belong in personas.

Role Lens definitions must:

- remain provider-neutral and usable without a runtime;
- describe attention rather than authority;
- use review questions only as relevant considerations, never a mandatory script;
- avoid tools, permissions, access claims, credentials, models, memory, and deployment configuration;
- include `role.yaml` and at least two non-normative examples using shared scenarios where practical.

Absence of a lens is neutral. Do not add an empty generalist lens merely to fill a selector.

Personas declaring `convictions`, `pushback`, or `uncertainty` must include matching `## Convictions`, `## Pushback`, or `## Uncertainty` guidance in `SKILL.md`. Convictions must be stable values rather than restated preferences. Pushback must name observable actions and target work or reasoning, never the user. Uncertainty rules must preserve evidence boundaries and prohibit fabrication.

## Profiles, personas, and variants

Before adding another catalogue entry, use this decision sequence:

1. If the contribution introduces reusable problem-solving behavior, create or update a behavioral profile.
2. If it creates a recognizably different character even while performing the same work, create a persona.
3. If the same character is merely specialized for a domain, create a constrained variant.

New persona proposals should answer: “What makes this persona recognizably different from existing personas even when performing the same work?” Optional `persona_signature` metadata provides that answer in two to five concise statements. `persona_family` organizes related characters but never creates inheritance.

Variants may use only fields allowed by `schemas/persona-variant.schema.json`. They cannot change family, signature, convictions, invariants, pushback, uncertainty, prohibited behavior, or anything about the underlying agent. The base persona is already the Classic selection; do not add an empty classic variant.

Run `python tools/check_persona_similarity.py --threshold 0.80` before proposing a similar persona. Findings are advisory and show behavioral overlap separately from persona-character overlap. High shared behavior with distinct character usually suggests a shared profile, while high overlap on both axes suggests a duplicate or variant.

## Archetype proposals

Check the [archetype expansion catalog](design/ARCHETYPE_CATALOG.md) before proposing a new persona. A proposal should identify the underlying behavioral mechanics, the reusable behavioral profile it needs, how it differs from existing personas, and how it avoids direct impersonation.

Narrative styles are experimental and non-normative. Add design notes, paired control/styled examples, and preservation scenarios under `tests/experimental/`; do not add a `narrative_style` field to persona YAML or change the schemas without first satisfying the graduation criteria in [the narrative styles design](design/NARRATIVE_STYLES.md).

## Design changes

Keep the format portable. Prefer changes to Markdown, YAML, schemas, examples, and small utilities. Proposals for runtimes, services, registries, model SDKs, voice-provider adapters, or composition engines must begin with a concrete use case that cannot be handled by the current format.

When a schema changes, update `SPEC.md`, fixtures, every affected definition, and tests in the same change. Incompatible changes require a `schema_version` decision.

## Checks

```console
python tools/validate_persona.py
python tools/validate_dialogues.py
python tools/build_prompt.py personas/professional/persona.yaml --role-lens ciso
python tools/check_persona_similarity.py --threshold 0.80
python -m unittest discover -s tests -v
```

Examples should be funny enough to identify the persona and sober enough to demonstrate a correct answer. Humor should target the situation, technology, or fictional agent—not the user.
