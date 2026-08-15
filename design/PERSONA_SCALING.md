# Persona Scaling

Agent Attitudes scales by reusing a compact vocabulary of profiles, persona types, variants, names, and experience metadata. It does not describe or operate the underlying agent.

```text
existing agent
      +
optional Role Lens
      +
behavioral profiles
      +
persona type
      +
optional variant
      +
optional conversational name
      +
optional consumer experience
```

## Boundaries

- Behavioral profiles express reusable problem-solving behavior.
- Role Lenses express what receives attention first without assigning a job.
- Persona types express recognizable characters.
- Variants specialize the same character without creating another primary card.
- Names are user-selected conversational labels.
- Families and signatures help people understand catalogue relationships.
- Experience describes optional consumer presentation.

None of these fields grants tools, permissions, authority, provenance, authentication, uniqueness, or control over deployment. Functional roles and external agent references remain in the deploying system; a Role Lens is only a bounded perspective overlay.

## Reference family

The `veteran-engineer` family pilots related but distinct persona types:

- Greybeard frames complexity through systems history and dry operational disappointment.
- Retired Engineer tests ideas with calculations and then helps rebuild them.
- Old Shop Teacher teaches through craft, measurement, and immediate safety intervention.

They may share behavioral profiles without collapsing into one character.

Greybeard Security demonstrates the opposite case: the character remains Greybeard, while a constrained variant adds security-review behavior and an amber console treatment.

## Similarity

The reference similarity tool reports two independent dimensions:

1. behavioral overlap from profiles, convictions, pushback, and preferences;
2. persona-character overlap from signatures, presentation, voice, and experience.

The scores are deterministic maintenance signals, not semantic truth. Findings remain advisory. Exact shared fields and terms are printed so maintainers can understand the result without an embedding service or external model.
