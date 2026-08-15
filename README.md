# Agent Attitudes

## Your AI has a personality problem. Now it’s collectible.

Welcome to the personnel department for coworkers who do not technically exist.

Agent Attitudes is an open specification and portable catalogue of behavioral profiles for AI agents. Pick a character, drop the readable instructions into a chat or coding project, and receive the same competent answer with considerably more workplace atmosphere.

Current employees include:

- **Greybeard:** forty years of imaginary Unix experience and no patience for your third database.
- **Diva:** your implementation works. Unfortunately, she has standards.
- **Redditor:** your question has already been answered. Also, you asked it incorrectly.
- **Burned-Out Sysadmin:** it might be DNS. They would prefer evidence before enjoying the moment.
- **Professional:** for when management joins the call and everyone suddenly stops doing voices.

Browse the complete [persona catalog](personas/CATALOG.md). Professional remains outside the humorous 50 as the neutral testing control.

## Public catalog

The illustrated agent-card catalog is published at [r33n3.github.io/Personas](https://r33n3.github.io/Personas/). Search by behavior, behavioral depth, category, or voice characteristics; inspect inherited rules, convictions, pushback, uncertainty handling, and contextual voice changes; copy instructions for Chat or coding; remix a persona in plain language; or download any persona as a ZIP assembled directly from this repository.

The static site lives in `site/`. `tools/build_site_catalog.py` regenerates its public catalog data and downloads from the normative persona/profile files so the website cannot become a second source of truth.

> **Personality may degrade. Competence may not.**

> **Character affects performance. Context controls intensity.**

> **Presentation may disappear. The persona must still work.**

A persona can change tone, humor, skepticism, verbosity, text presentation, and advisory voice performance. It cannot excuse a wrong answer, skipped task, unsafe action, invented fact, or ignored repository rule.

## Pick one. Use it. Tamper responsibly.

Every catalogue card offers three copy-ready paths:

- **Use in Chat** copies the complete persona instructions for one conversation.
- **Use in Coding** copies a repository-safe `AGENTS.md` adoption block for the growing cross-agent ecosystem.
- **Remix This** copies an editable prompt for changing voice, humor, verbosity, scope, or borrowed traits while preserving competence.

Remixing requires no composition engine. Try: “Use Burned-Out Sysadmin’s operational instincts, Greybeard’s suspicion of unnecessary complexity, and Film Noir narration. During incidents, drop the jokes and become direct.”

See [Remixing Personas](examples/remixing.md) for more recipes and the boundaries that keep a funny combination useful.

`AGENTS.md` is the recommended cross-agent default. If a coding agent does not discover it automatically, paste the same block into that tool's project-instructions file or explicitly reference the downloaded `SKILL.md`.

## The model

| Layer | Responsibility |
| --- | --- |
| Capabilities | What the agent can do: tools, APIs, and execution access |
| Skills | How the agent performs specialized tasks |
| Knowledge | What the agent knows or can retrieve |
| Behavioral profile | How the agent approaches decisions and interaction |
| Persona | How that behavior is presented in text or voice |
| Experience | How compatible software may optionally represent it |

Agent Attitudes primarily concerns the final three layers. Profiles contain observable rules, such as challenging unjustified complexity and offering a simpler alternative. Personas give those rules a recognizable voice. Optional `experience` metadata gives compatible clients provider-neutral visual, terminal, avatar, motion, audio, and notification hints without changing the prompt or the agent's behavior.

## Behavior versus experience

`presentation` describes expression: dry humor, concise answers, or theatrical delivery. `experience` describes optional consumer UI intent: a dark Unix-style preview, monospace typography, subdued motion, or measured audio delivery. Consumers may support any subset or ignore the entire block. Accessibility preferences always win, and experience data is never executable.

Greybeard is the canonical example. His package requests a restrained dark Unix console with phosphor-green accents and measured, low-energy audio guidance. A plain text chat that ignores every one of those hints remains fully conforming—and should still question your personal-blog Kubernetes cluster.

See [Portable Experience Metadata](examples/experience.md) for the contract and a complete example.

## Experimental expansion

The project is exploring original cultural and narrative archetypes without turning the library into celebrity or copyrighted-character impersonation prompts. The [archetype expansion catalog](design/ARCHETYPE_CATALOG.md) organizes the research backlog.

An optional narrative presentation layer is also being tested outside the normative specification. Read the [narrative styles design note](design/NARRATIVE_STYLES.md) and the paired [Film Noir experiment](examples/narrative-film-noir.md). Narrative style remains experimental and is distinct from the advisory voice metadata in persona schema 0.2.

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
python tools/validate_dialogues.py
python tools/build_prompt.py personas/greybeard/persona.yaml
python -m unittest discover -s tests -v
```

`validate_persona.py` validates every bundled definition by default, while `validate_dialogues.py` validates the bundled conformance pilot. The definition validator and prompt builder also accept explicit paths; use `--help` for details.

## What v0.2 includes

- A normative persona and behavioral-profile specification in [SPEC.md](SPEC.md).
- JSON Schemas for both YAML document types.
- Fifty portable concept personas plus a Professional control, each with human instructions, structured metadata, and examples.
- Provider-neutral sound, delivery, mannerism, and contextual voice guidance for every persona.
- An optional provider-neutral experience contract, demonstrated by Greybeard and exposed by the static catalog.
- Optional convictions, structured pushback, and uncertainty contracts, piloted across the five dialogue-conformance personas.
- Reusable behavioral profiles, including a neutral baseline.
- A validator, a deterministic instruction builder, and scenario fixtures.
- A five-persona [multi-turn dialogue conformance pilot](tests/dialogues/README.md) covering signature behavior, serious-context restraint, and uncertainty.

The [behavioral depth design](design/BEHAVIORAL_DEPTH.md) explains why these contracts are separate from reusable profiles and which later phases remain intentionally deferred.

This is intentionally not an agent runtime, orchestration framework, registry, or prompt-management service. Markdown and YAML are the product; the utilities demonstrate one correct consumer.

## Status

Persona documents are at `schema_version: 0.2`; unchanged behavioral-profile documents remain at `0.1`. Strict 0.1 persona validators will reject the new optional field, so the version boundary is explicit. Until 1.0, incompatible changes may occur between minor releases and will be documented in the specification.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Personas must be distinct, repeatable, safe, technically competent, and more interesting than “be sarcastic.”

Licensed under Apache License 2.0.
