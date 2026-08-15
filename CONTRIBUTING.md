# Contributing

Contributions should preserve the joke and improve the engineering.

## Persona requirements

A persona contribution must include `SKILL.md`, `persona.yaml`, and `examples.md`. It must have:

- a unique, repeatable behavioral identity;
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

Personas declaring `convictions`, `pushback`, or `uncertainty` must include matching `## Convictions`, `## Pushback`, or `## Uncertainty` guidance in `SKILL.md`. Convictions must be stable values rather than restated preferences. Pushback must name observable actions and target work or reasoning, never the user. Uncertainty rules must preserve evidence boundaries and prohibit fabrication.

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
python -m unittest discover -s tests -v
```

Examples should be funny enough to identify the persona and sober enough to demonstrate a correct answer. Humor should target the situation, technology, or fictional agent—not the user.
