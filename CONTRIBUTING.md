# Contributing

Contributions should preserve the joke and improve the engineering.

## Persona requirements

A persona contribution must include `SKILL.md`, `persona.yaml`, and `examples.md`. It must have:

- a unique, repeatable behavioral identity;
- an existing behavioral profile or a well-justified new one;
- clear presentation characteristics;
- all four competence invariants;
- explicit prohibited behavior;
- at least three meaningfully different example interactions;
- valid schema and profile references;
- relevant scenario coverage when it introduces new behavior.

Set `category` to one of the values allowed by the persona schema. Categories organize discovery only; they do not imply behavior or instruction priority.

Do not contribute a persona that is merely “be sarcastic,” depends on impersonating a copyrighted fictional character, targets a protected class, uses personal abuse as its main joke, or intentionally makes answers less correct or complete.

## Design changes

Keep v0.1 portable. Prefer changes to Markdown, YAML, schemas, examples, and small utilities. Proposals for runtimes, services, registries, model SDKs, or composition engines must begin with a concrete use case that cannot be handled by the current format.

When a schema changes, update `SPEC.md`, fixtures, every affected definition, and tests in the same change. Incompatible changes require a `schema_version` decision.

## Checks

```console
python tools/validate_persona.py
python -m unittest discover -s tests -v
```

Examples should be funny enough to identify the persona and sober enough to demonstrate a correct answer. Humor should target the situation, technology, or fictional agent—not the user.
