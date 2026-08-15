# Composition examples

Version 0.1 uses ordered behavioral profiles and one primary persona.

```yaml
behavior:
  - skeptical-engineer
  - quality-focused-reviewer
persona:
  primary: greybeard
```

Load the persona's inherited profiles first, then caller-supplied profiles in order. Ignore exact duplicates after their first appearance. Combine applicable actions additively; later layers do not erase earlier requirements.

If `skeptical-engineer` requires a simpler alternative and `quality-focused-reviewer` requires an actionable improvement, a response should do both when applicable. Greybeard may express the result with dry humor, but cannot suppress either behavior.

When requirements cannot coexist, prefer the higher-precedence instruction. For equal-precedence profile conflicts, choose the safer interpretation when one exists; otherwise report the conflict. Do not silently invent priority from list order.

Weighted blends such as `greybeard: 0.7` plus `security-paranoid: 0.3` are a future experiment, not v0.2 conforming composition. We have enough fractions in distributed systems already.
