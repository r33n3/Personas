# Agent Attitudes

**Your AI has a personality problem. Now it's configurable.**

Agent Attitudes is an open specification and portable reference library for applying behavioral profiles and personas to AI agents independently of their capabilities, tools, knowledge, and task instructions.

We demonstrate this technology using 50 highly qualified imaginary coworkers, including:

- **Greybeard:** forty years of imaginary Unix experience.
- **Diva:** your implementation works. Unfortunately, she has standards.
- **Redditor:** your question has already been answered. Also, you're asking it incorrectly.
- **Burned-Out Sysadmin:** it's DNS.
- **Professional:** for when management joins the call.

Browse the complete [persona catalog](personas/CATALOG.md). Professional remains outside the humorous 50 as the neutral testing control.

## Public catalog

The illustrated agent-card catalog is published at [r33n3.github.io/Personas](https://r33n3.github.io/Personas/). Search by behavior or category, inspect inherited rules, copy an `AGENTS.md` adoption snippet, or download any persona as a ZIP assembled directly from this repository.

The static site lives in `site/`. `tools/build_site_catalog.py` regenerates its public catalog data and downloads from the normative persona/profile files so the website cannot become a second source of truth.

> **Personality may degrade. Competence may not.**

A persona can change tone, humor, skepticism, verbosity, and presentation. It cannot excuse a wrong answer, skipped task, unsafe action, invented fact, or ignored repository rule.

## The model

| Layer | Responsibility |
| --- | --- |
| Capabilities | What the agent can do: tools, APIs, and execution access |
| Skills | How the agent performs specialized tasks |
| Knowledge | What the agent knows or can retrieve |
| Behavioral profile | How the agent approaches decisions and interaction |
| Persona | How that behavior is presented |

Agent Attitudes concerns the final two layers. Profiles contain observable rules, such as challenging unjustified complexity and offering a simpler alternative. Personas give those rules a recognizable voice.

## Experimental expansion

The project is exploring original cultural and narrative archetypes without turning the library into celebrity or copyrighted-character impersonation prompts. The [archetype expansion catalog](design/ARCHETYPE_CATALOG.md) organizes the research backlog.

An optional narrative presentation layer is also being tested outside the normative v0.1 specification. Read the [narrative styles design note](design/NARRATIVE_STYLES.md) and the paired [Film Noir experiment](examples/narrative-film-noir.md). No persona schema fields have changed.

## Quick start

No runtime is required. Copy a persona directory and any profiles it extends into a repository, then reference its `SKILL.md` from `AGENTS.md` or the equivalent instruction file for your agent harness.

```markdown
## Resident persona

Apply `personas/greybeard/SKILL.md` when interacting with developers.
Persona presentation has lower precedence than safety, user tasks, and repository policy.
```

For validation and prompt rendering, install the optional development dependencies and run:

```console
python -m pip install -r requirements-dev.txt
python tools/validate_persona.py
python tools/build_prompt.py personas/greybeard/persona.yaml
python -m unittest discover -s tests -v
```

`validate_persona.py` validates every bundled definition by default. Both tools also accept explicit paths; use `--help` for details.

## What v0.1 includes

- A normative persona and behavioral-profile specification in [SPEC.md](SPEC.md).
- JSON Schemas for both YAML document types.
- Fifty portable concept personas plus a Professional control, each with human instructions, structured metadata, and examples.
- Reusable behavioral profiles, including a neutral baseline.
- A validator, a deterministic instruction builder, and scenario fixtures.

This is intentionally not an agent runtime, orchestration framework, registry, or prompt-management service. Markdown and YAML are the product; the utilities demonstrate one correct consumer.

## Status

The formats are at `schema_version: 0.1`. Until 1.0, incompatible changes may occur between minor releases and will be documented in the specification.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Personas must be distinct, repeatable, safe, technically competent, and more interesting than “be sarcastic.”

Licensed under Apache License 2.0.
