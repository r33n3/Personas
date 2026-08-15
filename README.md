# Agent Attitudes

## Your AI has a personality problem. Now it’s collectible.

Welcome to the personnel department for coworkers who do not technically exist.

Agent Attitudes is an open specification and portable catalogue of review perspectives, behavioral profiles, and personas for AI agents. Pick what the agent should notice, pick a character, and receive the same competent answer with considerably more workplace atmosphere.

Current employees include:

- **Greybeard:** forty years of imaginary Unix experience and no patience for your third database.
- **Diva:** your implementation works. Unfortunately, she has standards.
- **Redditor:** your question has already been answered. Also, you asked it incorrectly.
- **Burned-Out Sysadmin:** it might be DNS. They would prefer evidence before enjoying the moment.
- **Professional:** for when management joins the call and everyone suddenly stops doing voices.

Browse the complete [persona catalog](personas/CATALOG.md). Professional remains outside the humorous 50 as the neutral testing control.

## Public catalog

The illustrated catalog is published at [r33n3.github.io/Personas](https://r33n3.github.io/Personas/). Browse characters or professional perspectives, search concerns such as permissions, cost, reliability, and evidence, combine a Role Lens with any persona, name the resulting coworker, and copy or download portable instructions.

The static site lives in `site/`. `tools/build_site_catalog.py` regenerates public catalog data and downloads from the normative Role Lens, persona, and profile files so the website cannot become a second source of truth.

> **Personality may degrade. Competence may not.**

> **Role determines perspective. Persona determines character.**

> **Character affects performance. Context controls intensity.**

> **Presentation may disappear. The persona must still work.**

A persona can change tone, humor, skepticism, verbosity, text presentation, and advisory voice performance. It cannot excuse a wrong answer, skipped task, unsafe action, invented fact, or ignored repository rule.

## Pick one. Name it. Tamper responsibly.

Every catalogue card can optionally give the selected persona a conversational name such as Carl or Bob. That name is a user-controlled label, not an agent identifier, permission, or authority claim.

The catalogue offers these portable paths:

- **Use in Chat** copies the complete persona instructions for one conversation.
- **Use in Coding** copies a repository-safe `AGENTS.md` adoption block for the growing cross-agent ecosystem.
- **Remix This** copies an editable prompt for changing voice, humor, verbosity, scope, or borrowed traits while preserving competence.
- **Download Setup** creates a small `persona-application` YAML file containing an optional Role Lens, persona type, conversational name, and supported experience overrides.

Remixing requires no composition engine. Try: “Use Burned-Out Sysadmin’s operational instincts, Greybeard’s suspicion of unnecessary complexity, and Film Noir narration. During incidents, drop the jokes and become direct.”

See [Remixing Personas](examples/remixing.md) for more recipes and the boundaries that keep a funny combination useful.

`AGENTS.md` is the recommended cross-agent default. If a coding agent does not discover it automatically, paste the same block into that tool's project-instructions file or explicitly reference the downloaded `SKILL.md`.

## The model

| Layer | Responsibility |
| --- | --- |
| Capabilities | What the agent can do: tools, APIs, and execution access |
| Skills | How the agent performs specialized tasks |
| Knowledge | What the agent knows or can retrieve |
| Role Lens | What the agent notices and optimizes for first |
| Behavioral profile | How the agent approaches decisions and interaction |
| Persona | How that behavior is presented in text or voice |
| Experience | How compatible software may optionally represent it |

Agent Attitudes primarily concerns the final four layers. Role Lenses encode professional attention without assigning a functional role. Profiles contain observable rules, such as challenging unjustified complexity and offering a simpler alternative. Personas give those rules a recognizable voice. Optional `experience` metadata gives compatible clients provider-neutral visual, terminal, avatar, motion, audio, and notification hints without changing authority or behavior.

## Perspective versus persona

> **Role determines perspective. Persona determines character.**

A CISO Role Lens notices permissions, trust boundaries, accountability, and revocation. Professional expresses those concerns plainly; Greybeard expresses the same concerns with dry operational skepticism. The lens does not make the agent a CISO and never grants security access, tools, permissions, or organizational authority.

The website calls Role Lenses **Perspectives** so the distinction is visible without reading the specification. See [Role Lens design](design/ROLE_LENS.md) and the [initial lens catalog](design/ROLE_CATALOG.md).

## Behavior versus experience

`presentation` describes expression: dry humor, concise answers, or theatrical delivery. `experience` describes optional consumer UI intent: a dark Unix-style preview, monospace typography, subdued motion, or measured audio delivery. Consumers may support any subset or ignore the entire block. Accessibility preferences always win, and experience data is never executable.

Greybeard is the canonical example. His package requests a restrained dark Unix console with phosphor-green accents and measured, low-energy audio guidance. A plain text chat that ignores every one of those hints remains fully conforming—and should still question your personal-blog Kubernetes cluster.

See [Portable Experience Metadata](examples/experience.md) for the contract and a complete example.

## One persona, many coworkers

A large agent population does not require hundreds of nearly identical personas. Reuse a persona type, optionally apply a constrained variant, and give each application a conversational name:

```yaml
schema_version: "0.2"
kind: persona-application
role_lens: ciso
persona:
  type: greybeard
  variant: security
  name: Carl
```

Carl and Bob can both use Greybeard without becoming separate catalogue entries. Either may optionally use a Role Lens, but their external agent references, functional roles, capabilities, tools, and permissions remain entirely outside Agent Attitudes.

Related personas may share a catalogue family while retaining different signatures. The initial `veteran-engineer` family demonstrates Greybeard, Retired Engineer, and Old Shop Teacher. Families organize discovery; they do not inherit behavior.

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
python tools/build_prompt.py --application examples/applications/carl-greybeard.yaml
python tools/build_prompt.py personas/greybeard/persona.yaml --variant security --name Carl
python tools/build_prompt.py personas/greybeard/persona.yaml --role-lens ciso --name Carl
python tools/check_persona_similarity.py --threshold 0.80
python -m unittest discover -s tests -v
```

`validate_persona.py` validates every bundled Role Lens, profile, persona, variant, and example application by default, while `validate_dialogues.py` validates the bundled conformance pilot. The prompt builder accepts either a direct persona path with optional `--role-lens`, `--name`, and `--variant`, or an `--application` document; use `--help` for details.

## What v0.2 includes

- A normative persona and behavioral-profile specification in [SPEC.md](SPEC.md).
- JSON Schemas for Role Lenses, behavioral profiles, personas, persona applications, and portable experience metadata.
- Eight provider-neutral reference perspectives with shared-scenario examples and downloadable packages.
- Fifty portable concept personas plus a Professional control, each with human instructions, structured metadata, and examples.
- Provider-neutral sound, delivery, mannerism, and contextual voice guidance for every persona.
- An optional provider-neutral experience contract, demonstrated by Greybeard and exposed by the static catalog.
- Minimal persona applications that select an optional Role Lens, reusable persona type, conversational name, and experience overrides without describing the underlying agent.
- Optional catalogue families and persona signatures, piloted across three veteran-engineer personas.
- Constrained persona variants, demonstrated by Greybeard Security without creating another primary card.
- Deterministic two-axis similarity reports for behavioral and persona-character overlap.
- Optional convictions, structured pushback, and uncertainty contracts, piloted across the five dialogue-conformance personas.
- Reusable behavioral profiles, including a neutral baseline.
- A validator, a deterministic instruction builder, and scenario fixtures.
- A five-persona [multi-turn dialogue conformance pilot](tests/dialogues/README.md) covering signature behavior, serious-context restraint, and uncertainty.

The [behavioral depth design](design/BEHAVIORAL_DEPTH.md) explains why these contracts are separate from reusable profiles and which later phases remain intentionally deferred.

This is intentionally not an agent runtime, orchestration framework, registry, or prompt-management service. Markdown and YAML are the product; the utilities demonstrate one correct consumer.

## Status

Persona and persona-application documents are at `schema_version: 0.2`; Role Lens and unchanged behavioral-profile documents begin at `0.1`. Existing persona applications without a lens remain valid. Until 1.0, incompatible changes may occur between minor releases and will be documented in the specification.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Personas must be distinct, repeatable, safe, technically competent, and more interesting than “be sarcastic.”

Licensed under Apache License 2.0.
