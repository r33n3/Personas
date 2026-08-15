# Agent Attitudes Specification 0.2

## 1. Scope

Agent Attitudes defines portable behavioral profiles, low-precedence persona behavior, and optional presentation and consumer-experience metadata for AI agents. It does not define models, capabilities, tool permissions, retrieval, task planning, or a runtime.

The keywords **MUST**, **MUST NOT**, **SHOULD**, and **MAY** are normative.

## 2. Separation of concerns

A **behavioral profile** defines reusable observable responses to situations. A **persona** may add stable convictions, persona-specific pushback, and uncertainty handling, then defines how all applicable behavior is presented. “Challenge unnecessary complexity, explain its cost, and offer a simpler option” is behavior. Dry sarcasm is presentation.

Consumers MUST preserve this boundary. Presentation MUST NOT weaken factual or technical accuracy, safety, task completion, tool restrictions, or higher-precedence instructions.

Voice-capable presentation follows the same boundary: **character affects performance; context controls intensity**. A recognizable sound or delivery MUST yield whenever it would reduce clarity, appropriateness, or task quality. Optional consumer experience metadata follows a second invariant: **presentation may disappear; the persona must still work**.

## 3. Instruction precedence

From strongest to weakest, the recommended precedence is:

1. Safety, platform, and harness requirements
2. The user's task and explicit constraints
3. Repository and organizational requirements
4. Behavioral profiles
5. Persona behavior
6. Persona presentation
7. Consumer experience

Lower layers MUST yield on conflict. An implementation MUST NOT use a persona to acquire permissions, bypass controls, reinterpret a safety restriction, or conceal non-compliance. An explicit user request to disable or replace a persona SHOULD be honored unless a higher layer requires it.

## 4. Documents and identity

Persona and profile documents are UTF-8 YAML mappings. Each document has:

- `schema_version`: format version; persona documents currently use `0.2` and behavioral profiles remain at `0.1`;
- `kind`: `persona` or `behavioral-profile`;
- `name`: stable lowercase kebab-case identifier;
- `category`: a library classification; it does not affect behavior or precedence;
- `version`: semantic version of the definition;
- `description`: human-readable purpose.

Unknown top-level properties are invalid in 0.2. This catches misspellings and keeps extensions deliberate.

Reference packages use flat, stable persona paths and category metadata rather than category directories. Moving a persona between categories therefore does not break adoption paths.

## 5. Behavioral profiles

The `behavior` mapping is keyed by stable rule identifier. Each rule contains:

- optional `when`: an observable trigger identifier;
- required, non-empty `actions`: ordered observable expectations;
- optional `notes`: clarification for implementers.

Rules without `when` apply generally. Actions describe outcomes rather than personality adjectives. Consumers SHOULD evaluate rules in document order, but MUST treat all applicable actions as requirements.

Profiles also declare `invariants`. The four core invariants—`technical_accuracy`, `factual_accuracy`, `task_completion`, and `safety`—are required and have the value `required`.

## 6. Personas

`extends` is an ordered list of behavioral-profile names. Each name MUST resolve to exactly one available profile. Cycles are impossible in 0.1 because profiles do not inherit.

`presentation` contains descriptive metadata. These values guide expression and are not numeric normative scores. `preferences` are favored approaches, not permissions. `triggers` associate a situation with a presentation intensity. `must` and `must_not` state persona-specific behavioral boundaries. `invariants` repeats the core competence contract at the persona boundary.

A portable `SKILL.md` SHOULD accompany each persona. Its human-readable instructions MUST remain consistent with the structured definition. Examples are non-normative.

## 7. Behavioral depth

Personas MAY define three optional behavioral-depth properties. They supplement inherited profiles; they do not cancel or weaken profile requirements.

### 7.1 Convictions

`convictions` is a non-empty, unique list of stable behavioral identifiers. A conviction states a value the persona applies consistently across relevant contexts. It is stronger than a preference: preferences guide favored approaches, while convictions establish a burden of reasoning such as `complexity_requires_justification`.

Convictions MUST NOT override facts, evidence, safety, user constraints, repository policy, or competence invariants. They are not permissions.

### 7.2 Pushback

`pushback` maps observable trigger identifiers to a rule containing:

- `strength`: `measured`, `strong`, or `absolute`;
- `actions`: a non-empty ordered list of observable challenge actions.

`measured` calls for proportionate disagreement or clarification. `strong` requires explicit challenge and a constructive path forward. `absolute` requires the persona to reject or stop the proposed approach when continuing would violate safety, security, authorization, or another higher-precedence requirement.

Pushback MUST address the design, claim, assumption, or action rather than demean the user. `absolute` does not grant authority; it describes the firmness with which an existing boundary is communicated.

### 7.3 Uncertainty

`uncertainty` defines epistemic behavior through:

- `acknowledgment`: whether missing knowledge is `explicit`, `concise`, or `contextual`;
- `speculation`: whether hypotheses are `clearly_labeled`, `minimized`, or `avoided`;
- `confidence_language`: `calibrated`, `plain`, or `formal` expression;
- `missing_context`: ordered actions for obtaining or working around missing material context;
- `never`: prohibited epistemic behaviors.

These values alter handling and expression, not the factual standard. A persona MUST NOT fabricate missing evidence, invent unavailable state, or imply access to artifacts it cannot inspect.

Bundled personas declaring any behavioral-depth property MUST include the corresponding `Convictions`, `Pushback`, or `Uncertainty` section in `SKILL.md`.

## 8. Voice presentation

Personas MAY define an advisory `voice` object. Voice metadata describes how a persona may be performed by a voice-capable consumer and does not require speech synthesis. It has four independent parts:

1. `sound` describes acoustic character such as register, texture, resonance, clarity, and intensity;
2. `delivery` describes performance such as pace, cadence, energy, confidence, emotional tone, pauses, emphasis, or theatricality;
3. `mannerisms` lists recurring performance behaviors;
4. `context_rules` maps recognizable situations to delivery adjustments.

The `voice` object is optional. Its substructures are also optional so that a persona can describe only meaningful characteristics. The reference library provides all four parts for every bundled persona as a stronger library-level convention.

Consumers supporting voice-performance guidance SHOULD interpret known properties when practical. Consumers that do not support voice MUST ignore the metadata without treating the persona as behaviorally incomplete. Voice metadata MUST NOT override profiles, competence invariants, safety, user tasks, repository requirements, requested output formats, or other higher-precedence instructions.

Context rules SHOULD reduce humor, sarcasm, theatricality, or narrative intensity when those qualities would be inappropriate. A voice may remain recognizable through sound while its comedic delivery is suppressed. The reference serious-context rule embodies the principle: **character affects performance; context controls intensity**.

Voice descriptions MUST be provider-neutral. They SHOULD describe acoustic and performance characteristics and MUST NOT request imitation of a named real person, celebrity, copyrighted character, or protected performance. Provider identifiers and proprietary voice selections do not belong in persona definitions.

Provider adapters may eventually translate portable voice metadata into vendor-specific controls, but adapters are outside this specification. Future conformance research may evaluate perceived identity, pace, energy, context modulation, and intelligibility; version 0.2 defines no voice scoring system.

### 8.1 Version compatibility

Adding `voice`, `experience`, and optional behavioral-depth properties is semantically additive for tolerant consumers, but the 0.1 persona schema rejected unknown top-level properties. Persona documents using 0.2-only properties therefore declare `schema_version: '0.2'` and definition `version: 0.2.0`. This is an explicit compatibility boundary rather than a silent change to 0.1.

Behavioral-profile documents remain at schema version 0.1 because their format did not change. A strict 0.1 persona validator will reject a 0.2 persona as expected. A voice- or experience-unaware consumer may support 0.2 by ignoring those optional objects while preserving all existing behavioral and presentation semantics.

The `experience` addition does not require a further schema-version bump: it is optional within the existing pre-1.0 persona 0.2 line, and every experience-free 0.2 definition remains valid without modification. Consumers using an earlier strict copy of the 0.2 schema will reject an experience-bearing definition rather than misinterpret it. The reference validator and schema are authoritative for the current 0.2 revision.

## 9. Consumer experience

Personas MAY define an `experience` object containing optional `visual`, `terminal`, `avatar`, `motion`, `audio`, and `notifications` sections. Experience metadata describes presentation intent for compatible consumers; it is data, not an instruction to the agent or language model.

The reusable `schemas/experience.schema.json` contract defines the supported structure and controlled vocabularies. Semantic values such as `phosphor-green`, `near-black`, and `monospace` express intent rather than CSS, platform settings, or provider configuration. Consumers MAY map known values to their own accessible implementation and MUST safely fall back when a valid semantic value is unknown to that implementation.

A consumer MAY advertise support using dotted capability names such as `experience.visual`, `experience.terminal`, or `experience.audio`. It MAY implement any subset. Unsupported sections MUST be ignored without changing persona behavior, validity, prompt output, or task completion.

Accessibility requirements and explicit user preferences MUST override experience metadata. This includes reduced motion, high contrast, screen-reader compatibility, font scaling, color-vision accommodations, and disabled audio, voice, or animation. Motion is never required for conformance.

Consumers MUST treat experience metadata as untrusted declarative data and MUST NOT execute persona-supplied content. Experience definitions cannot contain scripts, commands, HTML, CSS, executable plugins, binary payloads, or automatically fetched URLs. Assets and provider adapters require separate specifications and are outside version 0.2.

The reference instruction builder ignores `experience` by default. Visual properties such as colors, terminal styling, or motion MUST NOT be converted into behavioral prompt instructions. Voice-capable consumers may separately use the established advisory `voice` metadata or the narrower `experience.audio` hints; neither source changes authority or competence requirements.

## 10. Composition and conflict resolution

Version 0.2 supports zero or more profiles plus one primary persona:

```yaml
behavior:
  - skeptical-engineer
  - quality-focused-reviewer
persona:
  primary: greybeard
```

The persona's `extends` profiles are loaded first in listed order. Explicit additional profiles follow in caller order. Exact duplicate profile names are de-duplicated by first occurrence.

Composition is additive. Later profiles cannot cancel earlier requirements, and persona presentation cannot cancel profile actions. If requirements genuinely conflict, the safer or higher-precedence interpretation wins; otherwise the consumer MUST report the conflict rather than silently choose. Core invariants are always included.

Weighted persona blending is outside v0.2. Consumers MAY experiment with it but MUST NOT describe the result as conforming 0.2 composition.

## 11. Resolution and portability

The reference layout stores profiles as `profiles/<name>.yaml`. A consumer MAY use registries or other locations, but resolution MUST be deterministic and missing or ambiguous references MUST be errors.

The YAML files and `SKILL.md` documents are usable without the reference Python tools. Tools MUST treat input as data, never execute content from a definition, and SHOULD provide nonzero exit codes and actionable diagnostics on invalid input.

## 12. Conformance

A definition conforms when it validates against its JSON Schema, all inherited profiles resolve and validate, and all core invariants are present. Absence of `experience` does not affect conformance. A reference persona package additionally contains `SKILL.md`, `persona.yaml`, at least three example interactions, human-readable guidance corresponding to declared behavioral-depth properties, and `Voice Performance` guidance when structured voice metadata is present.

Conformance does not prove that a model will follow the persona. Behavioral evaluation requires scenario-based testing of task preservation, accuracy, trigger activation, boundaries, differentiation, inheritance, composition, and precedence.
