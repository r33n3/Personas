# Behavioral Depth Design

## Status

Phase 1 is implemented as an additive persona-schema 0.2 pilot. Later phases remain design backlog and are not normative fields.

## Boundary

Behavioral profiles remain the reusable source of observable policy. Personas may add three low-precedence behavioral contracts:

- convictions: stable values used across contexts;
- pushback: persona-specific reasons and methods for challenging work;
- uncertainty: explicit epistemic discipline.

These contracts cannot grant tools, permissions, knowledge, memory, authority, or any property of the underlying agent. They yield to safety, user tasks, repository policy, inherited profiles, and competence invariants.

## Designs considered

### Put all depth in behavioral profiles

This keeps personas presentation-only, but it forces small persona-specific distinctions into a growing set of nearly duplicate profiles. A consumer must also inspect several documents to understand why a persona challenges something.

### Add bounded persona contracts

This design keeps reusable behavior in profiles while allowing the persona package to state its stable values, challenge boundaries, and uncertainty behavior directly. The fields are optional, structured, and rendered by the existing instruction builder. This is the selected design because it keeps the common portable package self-describing without introducing a new runtime or composition engine.

The tradeoff is some conceptual overlap with profile behavior. The specification therefore assigns distinct ownership: profiles define reusable actions; convictions explain stable values; pushback defines persona-specific activation and firmness; uncertainty defines epistemic handling.

## Pilot

The first rollout covers Greybeard, Diva, Redditor, Burned-Out Sysadmin, and Professional. These are already the dialogue-conformance controls and provide meaningfully different pushback targets. Expansion to the remaining catalog should follow review of the pilot rather than adjective substitution.

## Deferred phases

- Activation scope needs consumer semantics before it becomes schema.
- Modality restructuring must preserve the existing flat `presentation` and optional `voice` compatibility contract.
- Capability-firewall documentation and textual security scanning should arrive together so declared boundaries have enforceable checks.
- Adaptation requires a clear distinction between session preferences and persistent state; Agent Attitudes will not provide memory.
- A persona builder should generate this stable format only after the format has survived contribution use.

Numeric persona blending, model execution, memory, orchestration, TTS adapters, avatar rendering, and provider-specific configuration remain outside the normative scope.
