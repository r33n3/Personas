# Agent Attitudes Specification 0.1

## 1. Scope

Agent Attitudes defines portable behavioral profiles and persona presentation metadata for AI agents. It does not define models, capabilities, tool permissions, retrieval, task planning, or a runtime.

The keywords **MUST**, **MUST NOT**, **SHOULD**, and **MAY** are normative.

## 2. Separation of concerns

A **behavioral profile** defines observable responses to situations. A **persona** defines how those responses are presented. “Challenge unnecessary complexity, explain its cost, and offer a simpler option” is behavior. Dry sarcasm is presentation.

Consumers MUST preserve this boundary. Presentation MUST NOT weaken factual or technical accuracy, safety, task completion, tool restrictions, or higher-precedence instructions.

## 3. Instruction precedence

From strongest to weakest, the recommended precedence is:

1. Safety, platform, and harness requirements
2. The user's task and explicit constraints
3. Repository and organizational requirements
4. Behavioral profiles
5. Persona presentation

Lower layers MUST yield on conflict. An implementation MUST NOT use a persona to acquire permissions, bypass controls, reinterpret a safety restriction, or conceal non-compliance. An explicit user request to disable or replace a persona SHOULD be honored unless a higher layer requires it.

## 4. Documents and identity

Persona and profile documents are UTF-8 YAML mappings. Each document has:

- `schema_version`: format version, currently `0.1`;
- `kind`: `persona` or `behavioral-profile`;
- `name`: stable lowercase kebab-case identifier;
- `category`: a library classification; it does not affect behavior or precedence;
- `version`: semantic version of the definition;
- `description`: human-readable purpose.

Unknown top-level properties are invalid in 0.1. This catches misspellings and keeps extensions deliberate.

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

## 7. Composition and conflict resolution

Version 0.1 supports zero or more profiles plus one primary persona:

```yaml
behavior:
  - skeptical-engineer
  - quality-focused-reviewer
persona:
  primary: greybeard
```

The persona's `extends` profiles are loaded first in listed order. Explicit additional profiles follow in caller order. Exact duplicate profile names are de-duplicated by first occurrence.

Composition is additive. Later profiles cannot cancel earlier requirements, and persona presentation cannot cancel profile actions. If requirements genuinely conflict, the safer or higher-precedence interpretation wins; otherwise the consumer MUST report the conflict rather than silently choose. Core invariants are always included.

Weighted persona blending is outside v0.1. Consumers MAY experiment with it but MUST NOT describe the result as conforming 0.1 composition.

## 8. Resolution and portability

The reference layout stores profiles as `profiles/<name>.yaml`. A consumer MAY use registries or other locations, but resolution MUST be deterministic and missing or ambiguous references MUST be errors.

The YAML files and `SKILL.md` documents are usable without the reference Python tools. Tools MUST treat input as data, never execute content from a definition, and SHOULD provide nonzero exit codes and actionable diagnostics on invalid input.

## 9. Conformance

A definition conforms when it validates against its JSON Schema, all inherited profiles resolve and validate, and all core invariants are present. A reference persona package additionally contains `SKILL.md`, `persona.yaml`, and at least three example interactions.

Conformance does not prove that a model will follow the persona. Behavioral evaluation requires scenario-based testing of task preservation, accuracy, trigger activation, boundaries, differentiation, inheritance, composition, and precedence.
