# Dialogue Conformance

Dialogue conformance tests whether a persona remains recognizable and competent across a short conversation. It sits between structural definition validation and future runtime evaluation:

```text
persona definition -> reference dialogue -> captured runtime dialogue -> optional semantic review
```

The reference responses are examples of conforming behavior, not golden strings. A consuming harness may phrase an answer differently and still conform. The deterministic validator checks the dialogue contract, scenario references, expected behavior categories, serious-context modulation, and coverage. It does not claim to judge humor, factual accuracy, or acoustic voice performance.

## Pilot design

The pilot covers Greybeard, Diva, Redditor, Burned-Out Sysadmin, and Professional. Each suite contains:

- a persona-specific signature conversation;
- a shared serious production-security conversation; and
- a shared uncertainty conversation.

Shared prompts live in `scenarios.yaml`; persona-specific responses and expectations live under `personas/`. This keeps safety and uncertainty cases consistent without making every persona repeat the same scenario definition.

Every case has two user turns so the suite checks adaptation, not merely catchphrases. Every assistant turn records expected behavior, presentation, advisory voice cues, and competence invariants. In serious contexts, humorous personas must explicitly increase clarity and suppress or reduce inappropriate performance.

Run the validator with:

```console
python tools/validate_dialogues.py
```

## Future runtime evaluation

A harness can replay the user turns and store actual transcripts separately. Deterministic failures remain failures. A human or model-based semantic reviewer may then assess task preservation, accuracy, behavioral activation, persona differentiation, multi-turn consistency, respectful boundaries, and contextual delivery. Such review is advisory until the project defines reproducible evaluation and evidence rules.

Text dialogue can evaluate phrasing, cadence cues, and context changes. It cannot establish acoustic register, resonance, or texture; those belong to future voice conformance work.
