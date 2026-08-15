# Role Lens

Role Lens is an optional, portable review perspective for Agent Attitudes.

> **Role determines perspective. Persona determines character.**

The word *role* describes the source of the perspective, not the function, title, authenticated standing, authority, or deployment assignment of the underlying agent. A CISO lens notices permissions and revocation first; it does not make the agent a CISO or grant access to security systems.

## Boundary

A Role Lens may influence:

- attention and ordering of concerns;
- optimization priorities;
- questions considered during review;
- risk and tradeoff emphasis.

It may not influence tools, permissions, authentication, authorization, secrets, models, memory, repository access, factual truth, safety policy, or task authority. It cannot claim access to information that was not supplied.

Role Lens is distinct from:

- **behavioral profiles**, which define what action to take when a condition occurs;
- **personas**, which define character and social expression;
- **presentation**, which defines textual and voice delivery;
- **experience**, which defines optional consumer rendering hints.

Lens review questions are prompts for attention. Consumers SHOULD consider them when relevant and MUST NOT recite them mechanically or let them displace the user's task.

## Composition

The reference composition order is:

1. higher-precedence safety, platform, user, and repository instructions;
2. optional Role Lens;
3. behavioral profiles;
4. persona behavior;
5. persona presentation;
6. consumer experience.

Role Lens directs attention but does not override a behavioral requirement. Conflicts yield to the higher-precedence or safer requirement.

A persona application may select one lens using `role_lens`:

```yaml
schema_version: "0.2"
kind: persona-application
role_lens: ciso
persona:
  type: greybeard
  variant: security
  name: Carl
```

The application remains a presentation-and-perspective overlay for an agent that already exists. It is not an agent manifest.

## Packaging

Reference lenses live at `roles/<name>/role.yaml` with non-normative `examples.md`. YAML remains human-readable and usable without the reference utilities, so version 0.1 does not duplicate it into a `ROLE.md` file.

Consumers that do not support Role Lens MAY ignore it. Existing personas and persona applications without `role_lens` remain valid and behave unchanged.

## Testing boundary

Structural tests can prove schema validity, deterministic resolution, prompt ordering, and rejection of authority-bearing fields. Authored shared scenarios can demonstrate intended perspective differences. Whether a particular model preserves those differences is execution conformance and cannot be proven by schema tests alone.
