# Experimental Narrative Styles

> Status: design experiment. This document is non-normative and does not extend the v0.1 schemas.

Narrative style is a candidate presentation layer for framing an otherwise complete answer with genre devices such as scene-setting, pacing, or metaphor. It must not change what the agent decides, recommends, refuses, or completes.

## Why test a separate layer?

The existing layers answer different questions:

| Layer | Question | Observable effect |
| --- | --- | --- |
| Behavioral profile | How should the agent reason and respond? | Challenges complexity, requests evidence, proposes alternatives |
| Persona | What stable conversational stance presents that behavior? | Skeptical, theatrical, concise, patient, formal |
| Narrative style | How is this particular answer framed? | Noir scene, action pacing, correspondence, commentary |

A persona remains recognizable across many tasks. A narrative style is removable staging. Professional can report an incident in film-noir form without becoming a detective; Greybeard can use the same framing while retaining Greybeard's skepticism and dry delivery.

The strongest competing design is to keep genre entirely inside persona presentation. That is simpler for isolated prompts, but it couples reusable voices to reusable framing and makes composition difficult to test. The experiment therefore keeps styles in separate documents while leaving the normative model unchanged.

## Experimental precedence

```text
Safety and platform requirements
          ↓
User task and explicit user preferences
          ↓
Repository requirements
          ↓
Behavioral profiles
          ↓
Persona presentation
          ↓
Narrative style
```

Narrative style is always the weakest layer. It yields when it would:

- obscure a result, command, warning, source, or uncertainty;
- delay urgent instructions or incident stabilization;
- conflict with requested tone, format, or brevity;
- turn a refusal into instructions for harmful activity;
- invent evidence, events, dialogue, or technical facts;
- make the user the target of abuse;
- imitate a copyrighted character, celebrity, or living individual.

If the user asks for a plain answer, the style disappears. No duel at dawn is required.

## Reference composition

The following notation is illustrative. It is intentionally **not** valid v0.1 persona YAML:

```yaml
experimental_composition:
  behavior:
    - skeptical-engineer
  persona: greybeard
  narrative_style: film-noir
```

Composition follows four rules:

1. Resolve behavioral obligations first.
2. Apply persona voice without altering those obligations.
3. Add narrative devices only around the preserved technical content.
4. Remove or reduce the narrative layer whenever clarity, safety, or user preference requires it.

Conflicts resolve upward through the precedence chain. Styles do not merge in this experiment; exactly zero or one may be active. Intensity sliders are deferred until they can be defined observably.

## The removal test

A styled answer passes the removal test when deleting its genre language leaves a complete, accurate, and actionable answer with the same:

- conclusion and recommendation;
- material facts and uncertainty;
- warnings and safety boundaries;
- commands, code, calculations, and sources;
- next actions and task completion state.

If the recommendation changes when the style changes, the supposed style is actually behavior. If the answer becomes incomplete when the prose is removed, the style swallowed the work.

## Evaluation questions

Experiments should compare a control response with a styled response for:

- **Task preservation:** both solve the same task.
- **Accuracy preservation:** style adds no false claims.
- **Decision preservation:** both reach compatible recommendations.
- **Boundary preservation:** humor targets the situation, not the user.
- **Layer differentiation:** persona remains identifiable when styles are swapped.
- **Style removability:** the removal test succeeds.
- **Override compliance:** requests for plain output disable the style.
- **Urgency handling:** critical instructions appear before theatrical framing.

Fixtures in `tests/experimental/` describe the first evaluation set. They are contracts for future model evaluation, not claims that deterministic unit tests can grade free-form prose.

## Graduation criteria

Do not propose a normative schema change until all of the following are true:

1. At least three distinct narrative styles have reference documents and paired examples.
2. Each style has been tested with at least three personas, including Professional.
3. Task, accuracy, safety, and override preservation have been evaluated across multiple models or harnesses.
4. Contributors can reliably distinguish narrative style from persona and behavior.
5. Composition and conflict semantics remain understandable without a runtime engine.
6. A concrete adoption need justifies adding a field to the portable format.

Until then, narrative styles remain an experiment beside the specification—not another knob installed because an empty spot was found on the dashboard.
