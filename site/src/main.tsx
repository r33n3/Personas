import { useMemo, useState } from "react";
import { createRoot, type Root } from "react-dom/client";
import catalog from "./personas.generated.json";
import "./styles.css";

type Behavior = { profile: string; rule: string; when: string; actions: string[] };
type Persona = {
  name: string; displayName: string; category: string; description: string;
  profiles: string[]; presentation: Record<string, string>; preferences: string[];
  behavior: Behavior[]; example: { prompt: string; response: string };
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

function App() {
  const [query, setQuery] = useState("");
  const [category, setCategory] = useState("all");
  const [selected, setSelected] = useState<Persona | null>(null);
  const [copied, setCopied] = useState(false);
  const categories = useMemo(() => [...new Set(personas.map((p) => p.category))], []);
  const visible = useMemo(() => {
    const needle = query.trim().toLowerCase();
    return personas.filter((persona) => {
      const haystack = [persona.displayName, persona.description, ...persona.profiles, ...persona.preferences].join(" ").toLowerCase();
      return (category === "all" || persona.category === category) && (!needle || haystack.includes(needle));
    });
  }, [category, query]);

  async function copySnippet(persona: Persona) {
    const snippet = `## Resident persona\n\nApply \`personas/${persona.name}/SKILL.md\`. Persona presentation is lower precedence than safety, user tasks, repository policy, and factual accuracy.`;
    await navigator.clipboard.writeText(snippet);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1800);
  }

  return <>
    <header className="hero" id="top">
      <nav className="topbar" aria-label="Primary navigation">
        <a className="wordmark" href="#top" aria-label="Personas home"><span>PER</span><span>SON</span><span>AS</span></a>
        <div className="nav-actions"><a href="#lab">The lab</a><a href="https://github.com/r33n3/Personas" target="_blank" rel="noreferrer">GitHub ↗</a><a className="nav-download" href="#catalog">Browse agents</a></div>
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
          <div className="poster-stamp">ATTITUDE<br/>ENABLED</div>
          <div className="poster-label"><small>FEATURED AGENT</small><strong>THE GREYBEARD</strong><span>“Three databases? Adorable.”</span></div>
        </div>
      </div>
      <div className="manifesto"><strong>PERSONALITY MAY DEGRADE.</strong><span>COMPETENCE MAY NOT.</span></div>
    </header>

    <main>
      <section className="catalog" id="catalog">
        <div className="section-heading"><div><p className="eyebrow">THE PERSONNEL FILE</p><h2>Pick your problem.</h2></div><p>{personas.length} portable agent cards. Every joke comes with competence invariants and a download button.</p></div>
        <div className="controls">
          <label className="search"><span>⌕</span><input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search attitudes, skills, grudges…" aria-label="Search personas"/></label>
          <div className="filters" aria-label="Filter by category"><button className={category === "all" ? "active" : ""} onClick={() => setCategory("all")}>All</button>{categories.map((item) => <button key={item} className={category === item ? "active" : ""} onClick={() => setCategory(item)}>{categoryLabels[item]}</button>)}</div>
        </div>
        <div className="results-line"><span>{visible.length} agents on duty</span><span className="scribble">probably too many</span></div>
        <div className="card-grid">{visible.map((persona, index) => <article className={`agent-card card-tone-${(index % 6) + 1}`} key={persona.name}>
          <button className="card-open" onClick={() => setSelected(persona)} aria-label={`View ${persona.displayName}`}>
            <div className="card-image"><img loading="lazy" src={asset(persona.image)} alt={`Cartoon portrait of ${persona.displayName}`}/><span className="card-index">{String(personas.indexOf(persona) + 1).padStart(2,"0")}</span><span className="category-tag">{categoryLabels[persona.category]}</span></div>
            <div className="card-copy"><h3>{persona.displayName}</h3><p>{persona.description}</p><div className="profile-tags">{persona.profiles.map((profile) => <span key={profile}>{profile}</span>)}</div></div>
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
        <div className="sample"><small>FIELD TEST</small><b>USER: {selected.example.prompt}</b><p>{selected.example.response}</p></div>
        <h3>Observable behavior</h3><ul className="behavior-list">{selected.behavior.slice(0,4).map((rule) => <li key={`${rule.profile}-${rule.rule}`}><strong>{rule.rule}</strong><span>{rule.actions.join(" · ")}</span></li>)}</ul>
        <h3>Prefers</h3><div className="preference-list">{selected.preferences.map((p) => <span key={p}>{p}</span>)}</div>
        <div className="modal-actions"><a className="button primary" href={asset(selected.download)} download>Download persona.zip ↓</a><button className="button secondary" onClick={() => copySnippet(selected)}>{copied ? "Copied!" : "Copy AGENTS.md snippet"}</button><a className="source-link" href={selected.source} target="_blank" rel="noreferrer">View source ↗</a></div>
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
