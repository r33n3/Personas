# Remixing Personas

Personas are readable instructions. You may edit them. The standards committee has been informed and is coping as well as can be expected.

## In a chat

Open a persona in the public catalogue and choose **Use in Chat**. Paste the copied instructions into a conversation, followed by your request.

Choose **Remix This** when you want changes. Replace the bracketed lines with ordinary language:

```text
MY CHANGES
- Be more patient and explain unfamiliar terms.
- Borrow Diva's precise delivery, but keep Greybeard's engineering judgment.
- Apply this for the whole conversation.
```

You do not need numeric weights. Describe which persona supplies the primary judgment, which traits are presentation-only, and when the remix should stop.

## In a coding project

Download the persona package, place it in the repository, and choose **Use in Coding** to copy an `AGENTS.md` adoption block. Keep repository requirements and persona instructions separate so the persona remains the lower-precedence layer.

`AGENTS.md` is supported by a broad and growing range of coding agents. Discovery, nesting, and precedence can vary. If your tool does not load it automatically, put the same block in the tool's project-instructions file or tell the agent to apply the downloaded `SKILL.md` explicitly.

For a temporary coding remix, state it in the task:

```text
Apply the Greybeard persona for this review, but borrow Professional's concise delivery. Keep Greybeard's complexity pushback. Stop applying the remix after the review.
```

## Good remix recipes

### Noir Sysadmin

```text
Use Burned-Out Sysadmin as the behavioral base and add Film Noir narration. During production incidents, suppress narration and sarcasm until recovery is complete.
```

### Patient Greybeard

```text
Use Greybeard's convictions and complexity pushback. Increase patience, explanation depth, and teaching warmth. Keep the dry humor brief.
```

### Diva Security Review

```text
Use Security Paranoid's threat awareness and safety boundaries with Diva's polished, exacting delivery. Critique defects, never the author. Remove theatrics for active incidents or exposed credentials.
```

## Keep these fixed

A remix may change humor, voice, verbosity, pacing, explanation depth, or conversational quirks. It must not weaken:

- factual or technical accuracy;
- safety and security requirements;
- task completion;
- uncertainty honesty;
- tool or repository restrictions;
- authorization boundaries; or
- higher-precedence instructions.

If removing the character styling also removes the useful answer, the remix has eaten the agent. Please put it back.
