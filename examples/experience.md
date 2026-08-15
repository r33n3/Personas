# Portable Experience Metadata

Experience metadata describes how compatible software may present a persona. It is optional consumer data, not agent behavior and not a UI implementation.

```yaml
experience:
  visual:
    mode: dark
    accent: phosphor-green
    background: near-black
    typography: monospace
    density: compact
    contrast: normal
  terminal:
    enabled: true
    style: unix
    prompt: "$"
    scanlines: subtle
    glow: low
    cursor: block
  avatar:
    style: pixel-art
    treatment: monochrome
    expression: skeptical
  motion:
    intensity: subtle
    transitions: restrained
  audio:
    voice_style: weathered
    pacing: measured
    pitch: low
    energy: restrained
    texture: dry
  notifications:
    style: terminal
```

A web catalog could render the visual and terminal hints. A voice client could use only `audio`. A coding harness could ignore the block completely. All three remain conforming consumers because behavior, instruction precedence, and competence are unchanged.

Consumers should advertise support using dotted capability names when useful:

```yaml
supports:
  - experience.visual
  - experience.terminal
  - experience.avatar
```

Unknown supported tokens need a safe local fallback. Unsupported sections are ignored. Accessibility and explicit user preferences always take precedence.

Experience metadata is untrusted data. Never execute it, interpolate it as HTML or CSS, run commands from it, or automatically fetch URLs. The schema intentionally accepts semantic tokens and controlled values rather than application code.
