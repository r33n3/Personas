import { useMemo, useState } from "react";
import { createRoot, type Root } from "react-dom/client";
import catalog from "./personas.generated.json";
import "./styles.css";

type Behavior = { profile: string; rule: string; when: string; actions: string[] };
type Voice = {
  summary: string; soundSummary: string; deliverySummary: string;
  sound: Record<string, string>; delivery: Record<string, string>;
  mannerisms: string[]; contextRules: Record<string, Record<string, string>>;
};
type PushbackRule = { strength: "measured" | "strong" | "absolute"; actions: string[] };
type Uncertainty = {
  acknowledgment: string; speculation: string; confidence_language: string;
  missing_context: string[]; never: string[];
};
type BehavioralDepth = {
  convictions: string[]; pushback: Record<string, PushbackRule>;
  uncertainty: Uncertainty | null;
};
type ExperienceSection = Record<string, string | boolean>;
type Experience = {
  visual?: ExperienceSection; terminal?: ExperienceSection; avatar?: ExperienceSection;
  motion?: ExperienceSection; audio?: ExperienceSection; notifications?: ExperienceSection;
  preview: Record<"mode" | "accent" | "typography" | "terminal" | "scanlines" | "glow" | "motion", string>;
};
type Persona = {
  name: string; displayName: string; category: string; description: string;
  profiles: string[]; presentation: Record<string, string>; preferences: string[];
  voice: Voice;
  experience: Experience | null;
  behavioralDepth: BehavioralDepth | null;
  behavior: Behavior[]; example: { prompt: string; response: string };
  instructions: string;
  image: string; download: string; source: string;
};

const personas = catalog as unknown as Persona[];
const base = import.meta.env.BASE_URL;
const categoryLabels: Record<string, string> = {
  "computing-history": "Computing History", "internet-culture": "Internet Culture",
  "it-and-engineering": "IT & Engineering", "corporate-life": "Corporate Life",
  "startup-and-modern-tech": "Startup & Modern Tech",
  "character-archetypes": "Character Archetypes", control: "Control",
};

function asset(path: string) {
  return `${base}${path}`.replace(/([^:]\/)\/+/g, "$1");
}

function words(value: string) {
  return value.replaceAll("_", " ").replaceAll("-", " ");
}

function experienceSummary(section?: ExperienceSection) {
  if (!section) return "";
  return Object.values(section)
    .filter((value) => value !== true && value !== false)
    .map((value) => words(String(value)))
    .join(" · ");
}

function previewClasses(experience: Experience) {
  return Object.entries(experience.preview)
    .map(([key, value]) => `xp-${key}-${value}`)
    .join(" ");
}

function App() {
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("all");
  const [selected, setSelected] = useState<Persona | null>(null);
  const [copied, setCopied] = useState<"chat" | "coding" | "remix" | null>(null);
  const categories = useMemo(() => [...new Set(personas.map((p) => p.category))], []);
  const visible = useMemo(() => {
    const terms = query.trim().toLowerCase().split(/\s+/).filter(Boolean);
    return personas.filter((persona) => {
      const voiceTerms = [
        "voice", persona.voice.summary,
        ...Object.keys(persona.voice.sound), ...Object.values(persona.voice.sound),
        ...Object.keys(persona.voice.delivery), ...Object.values(persona.voice.delivery),
        ...persona.voice.mannerisms,
        ...Object.entries(persona.voice.contextRules).flatMap(([context, settings]) => [context, ...Object.keys(settings), ...Object.values(settings)]),
      ];
      const depth = persona.behavioralDepth;
      const depthTerms = depth ? [
        "behavioral depth", "convictions", "pushback", "uncertainty",
        ...depth.convictions,
        ...Object.entries(depth.pushback).flatMap(([trigger, rule]) => [trigger, rule.strength, ...rule.actions]),
        ...(depth.uncertainty ? [
          depth.uncertainty.acknowledgment,
          depth.uncertainty.speculation,
          depth.uncertainty.confidence_language,
          ...depth.uncertainty.missing_context,
          ...depth.uncertainty.never,
        ] : []),
      ] : [];
      const experienceTerms = persona.experience ? [
        "experience", "visual", "terminal", "avatar", "motion", "audio", "notifications",
        ...Object.entries(persona.experience).flatMap(([section, values]) =>
          section === "preview" ? [] : [section, ...Object.keys(values), ...Object.values(values).map(String)]
        ),
      ] : [];
      const haystack = [persona.displayName, persona.description, ...persona.profiles, ...persona.preferences, ...voiceTerms, ...depthTerms, ...experienceTerms].join(" ").replaceAll("_", " ").replaceAll("-", " ").toLowerCase();
      const searchableWords = haystack.split(/[^a-z0-9]+/).filter(Boolean);
      const matchesTerm = (term: string) => searchableWords.some((word) => term.length <= 3 ? word === term : word.includes(term));
      return (category === "all" || persona.category === category) && terms.every(matchesTerm);
    });
  }, [category, query]);

  async function copyText(kind: "chat" | "coding" | "remix", text: string) {
    await navigator.clipboard.writeText(text);
    setCopied(kind);
    window.setTimeout(() => setCopied(null), 1800);
  }

  function chatPrompt(persona: Persona) {
    return `Apply the following Agent Attitudes persona for this conversation. It changes behavior and presentation only. Accuracy, safety, factual truth, and completing my request still take precedence.\n\n${persona.instructions}`;
  }

  function codingPrompt(persona: Persona) {
    return `## Resident persona\n\nApply \`personas/${persona.name}/SKILL.md\` when interacting in this repository. Persona behavior and presentation are lower precedence than safety, user tasks, repository policy, tool restrictions, and factual accuracy. If the persona conflicts with those requirements, the persona yields.\n\nThis block uses the cross-agent AGENTS.md convention. If your coding agent does not automatically discover AGENTS.md, place the same instructions in its project-instructions file or explicitly reference the downloaded SKILL.md.`;
  }

  function remixPrompt(persona: Persona) {
    return `Remix the following Agent Attitudes persona for this conversation.\n\nBASE PERSONA\n${persona.instructions}\n\nMY CHANGES\n- [Describe the voice, humor, verbosity, or explanation style you want changed.]\n- [Optionally borrow one behavior or presentation trait from another archetype.]\n- [Say whether this applies for one answer or the whole conversation.]\n\nREMIX RULES\n- Preserve accuracy, safety, task completion, uncertainty honesty, and higher-priority instructions.\n- Keep the base persona's convictions and safety pushback unless I explicitly replace them with equally safe behavior.\n- Reduce humor and theatrics in serious or high-risk contexts.\n- Briefly state the resulting remix, then use it.`;
  }

  return <>
    <header className="hero" id="top">
      <nav className="topbar" aria-label="Primary navigation">
        <a className="wordmark" href="#top" aria-label="Personas home"><span>PER</span><span>SON</span><span>AS</span></a>
        <div className="nav-actions"><a href="#remix">Remix guide</a><a href="https://github.com/r33n3/Personas" target="_blank" rel="noreferrer">GitHub ↗</a><a className="nav-download" href="#catalog">Browse agents</a></div>
      </nav>
      <div className="hero-grid">
        <div className="hero-copy">
          <p className="eyebrow">OPEN SPEC · PORTABLE PERSONAS · ZERO RUNTIME</p>
          <h1>Your AI has a<br/><em>personality problem.</em></h1>
          <p className="lede">Now it’s collectible. Download memorable behavioral profiles for serious AI agents—without sacrificing accuracy, safety, or task completion.</p>
          <div className="hero-actions"><a className="button primary" href="#catalog">Meet the coworkers</a><a className="button secondary" href="https://github.com/r33n3/Personas/blob/main/SPEC.md">Read the spec</a></div>
        </div>
        <div className="hero-poster" aria-label="The Greybeard featured agent card">
          <div className="poster-burst"/><img src={asset("images/greybeard.webp")} alt="Cartoon portrait of The Greybeard"/>
          <div className="poster-label"><small>FEATURED AGENT</small><strong>THE GREYBEARD</strong><span>“Three databases? Adorable.”</span></div>
        </div>
      </div>
      <div className="manifesto"><strong>PERSONALITY MAY DEGRADE.</strong><span>COMPETENCE MAY NOT.</span></div>
    </header>

    <main>
      <section className="catalog" id="catalog">
        <div className="section-heading"><div><p className="eyebrow">THE PERSONNEL FILE</p><h2>Pick your problem.</h2></div><p>{personas.length} portable agent cards. Every joke comes with competence invariants, voice direction, and a download button.</p></div>
        <div className="controls">
          <label className="search"><span>⌕</span><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search attitudes, skills, grudges…" aria-label="Search personas"/></label>
          <div className="filters" aria-label="Filter by category"><button className={category === "all" ? "active" : ""} onClick={() => setCategory("all")}>All</button>{categories.map((item) => <button key={item} className={category === item ? "active" : ""} onClick={() => setCategory(item)}>{categoryLabels[item]}</button>)}</div>
        </div>
        <div className="results-line"><span>{visible.length} agents on duty</span><span className="scribble">probably too many</span></div>
        <div className="card-grid">{visible.map((persona, index) => <article className={`agent-card card-tone-${(index % 6) + 1}`} key={persona.name}>
          <button className="card-open" onClick={() => setSelected(persona)} aria-label={`View ${persona.displayName}`}>
            <div className="card-image"><img loading="lazy" src={asset(persona.image)} alt={`Cartoon portrait of ${persona.displayName}`}/><span className="card-index">{String(personas.indexOf(persona) + 1).padStart(2,"0")}</span><span className="category-tag">{categoryLabels[persona.category]}</span></div>
            <div className="card-copy"><h3>{persona.displayName}</h3><p>{persona.description}</p><p className="voice-summary"><strong>Voice:</strong> {persona.voice.summary}</p><div className="profile-tags">{persona.profiles.map((profile) => <span key={profile}>{profile}</span>)}</div></div>
          </button>
          <div className="card-actions"><button onClick={() => setSelected(persona)}>Inspect card</button><a href={asset(persona.download)} download>Download ↓</a></div>
        </article>)}</div>
        {visible.length === 0 && <div className="empty"><strong>No coworkers found.</strong><span>They may be hiding from the sprint planning meeting.</span></div>}
      </section>

      <section className="attitude-lab" id="lab">
        <div className="lab-heading"><div><p className="eyebrow">NOW LEAKING FROM R&amp;D</p><h2>The Attitude Lab</h2></div><p>We’re testing original archetypes and removable narrative styles before anybody adds seventeen genre sliders to the schema.</p></div>
        <div className="lab-grid">
          <article className="lab-card backlog-card"><span className="lab-sticker">BIG LIST</span><p className="eyebrow">EXPANSION CATALOG</p><h3>Archetypes, not impersonations.</h3><p>Cartoon hotheads, exhausted healers, flight directors, court jesters, risk managers, and several hundred other imaginary coworkers are waiting behind a quality gate.</p><a className="button secondary" href="https://github.com/r33n3/Personas/blob/main/design/ARCHETYPE_CATALOG.md">Inspect the backlog ↗</a></article>
          <article className="lab-card noir-card"><span className="lab-sticker">EXPERIMENT 01</span><p className="eyebrow">NARRATIVE STYLE</p><h3>Film Noir entered the logs.</h3><p>The technical answer stays sober. The rain, suspicious timestamps, and world-weary deployment commentary are optional—and always removable.</p><a className="button primary" href="https://github.com/r33n3/Personas/blob/main/examples/narrative-film-noir.md">Read the case file ↗</a></article>
        </div>
        <p className="lab-rule"><strong>THE REMOVAL TEST:</strong> delete the genre framing. If the answer stops being complete, accurate, and actionable, the style has swallowed the work.</p>
      </section>

      <section className="remix-guide" id="remix"><div className="remix-heading"><div><p className="eyebrow">UNAUTHORIZED PERSONNEL MODIFICATIONS</p><h2>Take one.<br/>Mess with it.</h2></div><p>These are readable instructions, not sealed action figures. Start with a coworker, describe your changes in ordinary language, and keep the competence bolts tightened.</p></div><div className="remix-steps">
        <article><b>01</b><h3>Pick a base</h3><p>Choose the persona whose instincts matter most. Greybeard questions complexity; Diva protects quality; Sysadmin keeps production alive.</p></article>
        <article><b>02</b><h3>Describe the mutation</h3><p>“More patient.” “Borrow Diva’s delivery.” “Add noir narration.” “Use this for one answer.” No percentage sliders required.</p></article>
        <article><b>03</b><h3>Protect the useful bits</h3><p>Voice and humor may wander. Accuracy, safety, uncertainty honesty, task completion, and higher-priority instructions do not.</p></article>
      </div><div className="remix-example"><span>EXAMPLE REMIX</span><p>Use Burned-Out Sysadmin’s operational instincts, Greybeard’s suspicion of unnecessary complexity, and Film Noir narration. Keep incident responses direct and sarcasm-free.</p><a href="#catalog">Pick an unwilling participant ↑</a></div></section>

      <section className="how-it-works"><p className="eyebrow">SERIOUS INFRASTRUCTURE, SILLY DEMONSTRATION</p><h2>Behavior is policy.<br/>Persona is presentation.</h2><div className="principles">
        <article><b>01</b><h3>Pick an attitude</h3><p>Choose a recognizable voice backed by observable behavioral expectations.</p></article>
        <article><b>02</b><h3>Drop it in</h3><p>Download three readable files. No runtime, registry, database, or orchestration platform.</p></article>
        <article><b>03</b><h3>Keep it competent</h3><p>Safety, accuracy, repository policy, and the user’s task always outrank the bit.</p></article>
      </div></section>
    </main>

    <footer><div className="wordmark"><span>PER</span><span>SON</span><span>AS</span></div><p>Open-source behavioral profiles for agents with a personality problem.</p><a href="https://github.com/r33n3/Personas">Apache-2.0 · GitHub ↗</a></footer>

    {selected && <div className="modal-backdrop" role="presentation" onMouseDown={() => setSelected(null)}><section className="modal" role="dialog" aria-modal="true" aria-labelledby="persona-title" onMouseDown={(e) => e.stopPropagation()}>
      <button className="modal-close" onClick={() => setSelected(null)} aria-label="Close persona card">×</button>
      <div className="modal-visual"><img src={asset(selected.image)} alt={`Cartoon portrait of ${selected.displayName}`}/><span>{categoryLabels[selected.category]}</span></div>
      <div className="modal-content"><p className="eyebrow">AGENT CARD · {selected.profiles.join(" + ")}</p><h2 id="persona-title">{selected.displayName}</h2><p className="modal-description">{selected.description}</p>
        {selected.behavioralDepth && <><h3>Behavioral depth</h3><div className="depth-panel">
          <section><h4>Convictions</h4><ul>{selected.behavioralDepth.convictions.map((conviction) => <li key={conviction}>{words(conviction)}</li>)}</ul></section>
          <section><h4>Pushback</h4><ul>{Object.entries(selected.behavioralDepth.pushback).map(([trigger, rule]) => <li key={trigger}><strong>{words(trigger)} <em>{rule.strength}</em></strong><span>{rule.actions.map(words).join(" · ")}</span></li>)}</ul></section>
          {selected.behavioralDepth.uncertainty && <section><h4>Uncertainty</h4><p><strong>{words(selected.behavioralDepth.uncertainty.acknowledgment)} acknowledgment</strong> · {words(selected.behavioralDepth.uncertainty.speculation)} speculation · {words(selected.behavioralDepth.uncertainty.confidence_language)} confidence</p><p><b>When context is missing:</b> {selected.behavioralDepth.uncertainty.missing_context.map(words).join(" · ")}</p><p><b>Never:</b> {selected.behavioralDepth.uncertainty.never.map(words).join(" · ")}</p></section>}
        </div></>}
        <h3>Voice</h3><div className="voice-panel"><p><strong>Sound</strong>{selected.voice.soundSummary}</p><p><strong>Delivery</strong>{selected.voice.deliverySummary}</p><h4>Changes when</h4><ul>{Object.entries(selected.voice.contextRules).slice(0,4).map(([context, settings]) => <li key={context}><strong>{words(context)}</strong><span>{Object.entries(settings).map(([key, value]) => `${words(key)}: ${words(value)}`).join(" · ")}</span></li>)}</ul></div>
        {selected.experience && <><h3>Experience <span className="advisory-label">optional consumer metadata</span></h3><div className="experience-panel">
          <div className={`experience-preview ${previewClasses(selected.experience)}`} aria-label={`Illustrative ${selected.displayName} experience preview`}>
            <span className="preview-scanlines" aria-hidden="true"/><div className="preview-chrome"><i/><i/><i/><b>PERSONA CONSOLE</b></div><div className="preview-terminal"><p><span>{String(selected.experience.terminal?.prompt ?? "$ ")}</span> attitude --status</p><p>behavior: operational</p><p>competence: required</p><p className="preview-cursor">presentation: optional</p></div>
          </div>
          <div className="experience-details">{(["visual", "terminal", "audio", "avatar", "motion", "notifications"] as const).map((section) => selected.experience?.[section] && <p key={section}><strong>{words(section)}</strong>{experienceSummary(selected.experience[section])}</p>)}</div>
        </div></>}
        <h3>Observable behavior</h3><ul className="behavior-list">{selected.behavior.slice(0,4).map((rule) => <li key={`${rule.profile}-${rule.rule}`}><strong>{rule.rule}</strong><span>{rule.actions.join(" · ")}</span></li>)}</ul>
        <h3>Prefers</h3><div className="preference-list">{selected.preferences.map((p) => <span key={p}>{p}</span>)}</div>
        <div className="use-actions"><p>Put this one to work</p><button onClick={() => copyText("chat", chatPrompt(selected))}>{copied === "chat" ? "Copied!" : "Use in Chat"}</button><button onClick={() => copyText("coding", codingPrompt(selected))}>{copied === "coding" ? "Copied!" : "Use in Coding"}</button><button onClick={() => copyText("remix", remixPrompt(selected))}>{copied === "remix" ? "Copied!" : "Remix This"}</button></div>
        <p className="use-note">Chat copies complete instructions. Coding uses the widely supported AGENTS.md convention. If your agent does not discover it automatically, paste the block into its project-instructions file or reference the downloaded SKILL.md. Remix gives you a safe, editable starting prompt.</p>
        <div className="modal-actions"><a className="button primary" href={asset(selected.download)} download>Download persona.zip ↓</a><a className="source-link" href={selected.source} target="_blank" rel="noreferrer">View source ↗</a></div>
      </div>
    </section></div>}
  </>;
}

declare global {
  interface Window { __personasRoot?: Root }
}

const container = document.getElementById("root")!;
const root = window.__personasRoot ?? createRoot(container);
window.__personasRoot = root;
root.render(<App/>);
