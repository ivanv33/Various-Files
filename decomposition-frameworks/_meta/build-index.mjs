#!/usr/bin/env node
// Regenerate decomposition-frameworks/index.html from the registry and the per-framework state files.
// Usage: node _meta/build-index.mjs
import fs from 'node:fs';
import path from 'node:path';
import url from 'node:url';
import { collect } from './status.mjs';

const META = path.dirname(url.fileURLToPath(import.meta.url));
const DF = path.dirname(META);
const registry = JSON.parse(fs.readFileSync(path.join(META, 'frameworks.json'), 'utf8'));
const rows = new Map(collect().map(r => [r.slug, r]));
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

// slot strip: one dot per slot; solid = typically fact, hollow = typically derived, half = either, square = schema
function strip(f) {
  const dots = f.slots.map(s => {
    const tp = s.typical_provenance;
    if (s.structural || tp === 'schema') return `<span class="dot schema" title="${esc(s.label)}: schema"></span>`;
    if (tp === 'fact') return `<span class="dot fact" title="${esc(s.label)}: fact"></span>`;
    if (tp === 'derived') return `<span class="dot derived" title="${esc(s.label)}: derived"></span>`;
    return `<span class="dot either" title="${esc(s.label)}: either"></span>`;
  }).join('');
  const nf = f.slots.filter(s => s.typical_provenance === 'fact').length, nd = f.slots.filter(s => s.typical_provenance === 'derived').length, ne = f.slots.filter(s => s.typical_provenance === 'either').length;
  return `<div class="strip" aria-label="${nf} fact, ${ne} either, ${nd} derived slots">${dots}<span class="strip-n">${nf}·${ne}·${nd}</span></div>`;
}

function card(f) {
  const r = rows.get(f.slug) || {};
  const dir = `${f.category}/${f.slug}`;
  const done = r.status === 'done';
  const status = r.status || 'pending';
  const ex = r.tbpn_example ? `<div class="ex"><span class="ex-k">TBPN</span> ${esc(r.tbpn_example.date || '')} ${esc(r.tbpn_example.episode_title || '')}</div>` : `<div class="ex ex-none">transcript example: not chosen yet</div>`;
  const links = done || (r.files || []).includes('index.html')
    ? `<a class="btn" href="${dir}/index.html">Open graph</a><a class="btn ghost" href="${dir}/README.md">README</a>`
    : `<span class="btn disabled">Graph</span><span class="btn ghost disabled">README</span>`;
  return `<article class="card ${status}">
  <div class="card-top"><h3>${esc(f.name)}</h3><span class="status ${status}">${esc(status.replace('_', ' '))}</span></div>
  <p>${esc(f.blurb)}</p>
  ${strip(f)}
  ${ex}
  <div class="links">${links}<a class="wiki" href="${esc(f.wikipedia)}" target="_blank" rel="noopener">Wikipedia</a></div>
</article>`;
}

const sections = registry.categories.sort((a, b) => a.order - b.order).map(c => {
  const fws = registry.frameworks.filter(f => f.category === c.id);
  return `<section id="${c.id}">
  <header class="sec"><span class="eyebrow">${esc(c.id.slice(0, 2))}</span><h2>${esc(c.name)}</h2><span class="count">${fws.length} frameworks</span></header>
  <div class="grid">${fws.map(card).join('\n')}</div>
</section>`;
}).join('\n');

const doneCount = [...rows.values()].filter(r => r.status === 'done').length;
const html = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Decomposition Frameworks</title>
<style>
  :root { color-scheme: dark; --plane:#0d0d0d; --surface:#1a1a19; --card:#202020; --ink:#fff; --ink-2:#c3c2b7; --muted:#898781; --hairline:#2c2c2a; --accent:#3987e5; --mono: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; --sans: system-ui, -apple-system, "Segoe UI", sans-serif; }
  * { box-sizing: border-box; }
  body { margin: 0; background: var(--plane); color: var(--ink-2); font: 15px/1.5 var(--sans); }
  a { color: var(--ink-2); }
  main { max-width: 1180px; margin: 0 auto; padding: 40px 24px 80px; }
  .hero { display: grid; grid-template-columns: minmax(0, 1.4fr) minmax(280px, 1fr); gap: 40px; align-items: start; padding-bottom: 32px; border-bottom: 1px solid var(--hairline); margin-bottom: 40px; }
  .eyebrow { font: 12px/1.2 var(--mono); letter-spacing: .1em; text-transform: uppercase; color: var(--muted); }
  h1 { font-size: 34px; line-height: 1.1; letter-spacing: -.02em; color: var(--ink); margin: 8px 0 14px; font-weight: 650; }
  .hero p { margin: 0 0 12px; max-width: 60ch; }
  .key { background: var(--surface); border: 1px solid var(--hairline); border-radius: 10px; padding: 16px 18px; font-size: 14px; }
  .key h2 { font: 12px/1.2 var(--mono); letter-spacing: .1em; text-transform: uppercase; color: var(--muted); margin: 0 0 10px; }
  .key-row { display: flex; gap: 10px; align-items: center; padding: 4px 0; }
  .key-row .dot { margin: 0; }
  .progress { margin-top: 14px; font: 12px var(--mono); color: var(--muted); }
  .progress b { color: var(--ink-2); font-weight: 500; }
  section { margin-bottom: 44px; }
  .sec { display: flex; align-items: baseline; gap: 14px; margin-bottom: 14px; }
  .sec h2 { font-size: 20px; color: var(--ink); margin: 0; font-weight: 600; letter-spacing: -.01em; }
  .sec .count { font: 12px var(--mono); color: var(--muted); margin-left: auto; }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 14px; }
  .card { background: var(--surface); border: 1px solid var(--hairline); border-radius: 10px; padding: 16px 18px; display: flex; flex-direction: column; gap: 10px; }
  .card.done { border-color: #3a3a37; }
  .card-top { display: flex; align-items: flex-start; gap: 10px; }
  .card h3 { margin: 0; font-size: 16px; color: var(--ink); font-weight: 600; line-height: 1.3; }
  .card p { margin: 0; font-size: 13.5px; color: var(--ink-2); }
  .status { margin-left: auto; flex: none; font: 10px/1 var(--mono); letter-spacing: .08em; text-transform: uppercase; padding: 4px 7px; border-radius: 4px; border: 1px solid var(--hairline); color: var(--muted); }
  .status.done { color: var(--ink); border-color: var(--muted); }
  .status.in_progress { color: var(--accent); border-color: var(--accent); }
  .strip { display: flex; align-items: center; gap: 5px; }
  .dot { width: 11px; height: 11px; border-radius: 50%; display: inline-block; border: 1.5px solid var(--ink-2); flex: none; }
  .dot.fact { background: var(--ink-2); }
  .dot.derived { border-style: dashed; background: transparent; }
  .dot.either { background: linear-gradient(90deg, var(--ink-2) 50%, transparent 50%); }
  .dot.schema { border-radius: 2px; border-color: var(--muted); background: var(--muted); }
  .strip-n { font: 11px var(--mono); color: var(--muted); margin-left: 6px; }
  .ex { font: 12px var(--mono); color: var(--muted); }
  .ex-k { color: var(--ink-2); }
  .ex-none { font-style: italic; }
  .links { display: flex; gap: 8px; align-items: center; margin-top: auto; padding-top: 4px; }
  .btn { font-size: 13px; text-decoration: none; padding: 6px 12px; border-radius: 6px; background: var(--ink-2); color: var(--plane); }
  .btn:hover { background: var(--ink); color: var(--plane); }
  .btn.ghost { background: transparent; color: var(--ink-2); border: 1px solid var(--hairline); }
  .btn.ghost:hover { border-color: var(--muted); color: var(--ink); }
  .btn.disabled { opacity: .35; pointer-events: none; }
  .wiki { margin-left: auto; font-size: 12px; color: var(--muted); text-decoration: none; border-bottom: 1px solid var(--hairline); }
  .wiki:hover { color: var(--ink); }
  footer { color: var(--muted); font-size: 13px; border-top: 1px solid var(--hairline); padding-top: 16px; }
  footer code { font: 12px var(--mono); color: var(--ink-2); }
  :focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
  @media (max-width: 760px) { .hero { grid-template-columns: 1fr; } h1 { font-size: 28px; } }
</style>
</head>
<body>
<main>
  <div class="hero">
    <div>
      <div class="eyebrow">Reference library · 22 frameworks · 4 categories</div>
      <h1>Decomposition frameworks as knowledge-graph schemas</h1>
      <p>Each framework page shows the framework taken apart into its slots, worked through on one classic example and one moment from the TBPN transcript corpus, and rendered as an interactive graph. Every node and edge is marked as either a <strong>fact</strong> stated in the source or an <strong>inference</strong> the LLM added.</p>
      <p>The point of the exercise: when these frameworks are later run over the transcripts to surface underserved markets and startup ideas, the reader can always see which part of a graph is evidence and which part is reasoning.</p>
      <p><a href="README.md">Read the README</a> for the provenance rules, the idea-bearing slot per framework, and how to resume the build.</p>
    </div>
    <aside class="key">
      <h2>Reading a card's slot strip</h2>
      <div class="key-row"><span class="dot fact"></span> slot usually filled from the data</div>
      <div class="key-row"><span class="dot either"></span> stated sometimes, inferred sometimes</div>
      <div class="key-row"><span class="dot derived"></span> slot the LLM must derive</div>
      <div class="key-row"><span class="dot schema"></span> framework scaffolding, not content</div>
      <div class="progress"><b>${doneCount}</b> of ${registry.frameworks.length} framework pages complete · generated ${new Date().toISOString().slice(0, 10)}</div>
    </aside>
  </div>
  ${sections}
  <footer>Graph pages load Three.js from jsDelivr and need internet access; the data is embedded in each page. Rebuild this index with <code>node _meta/build-index.mjs</code>.</footer>
</main>
</body>
</html>
`;
fs.writeFileSync(path.join(DF, 'index.html'), html);

// README tables between markers
const readmePath = path.join(DF, 'README.md');
if (fs.existsSync(readmePath)) {
  let md = fs.readFileSync(readmePath, 'utf8');
  const catName = new Map(registry.categories.map(c => [c.id, c.name]));
  const mdEsc = (t) => String(t ?? '').replace(/\|/g, '\\|');
  const tableRows = registry.frameworks.map(f => {
    const r = rows.get(f.slug) || {};
    const dir = `${f.category}/${f.slug}`;
    const ex = r.tbpn_example ? `${r.tbpn_example.date} ${mdEsc(r.tbpn_example.episode_title || '')}` : '';
    const st = r.status === 'done' ? 'done' : (r.status || 'pending').replace('_', ' ');
    return `| ${catName.get(f.category).replace(/ &.*$/, '')} | [${mdEsc(f.name)}](${dir}/README.md) | ${mdEsc(f.blurb)} | [graph](${dir}/index.html) | ${st} | ${ex} |`;
  });
  const table = ['| Category | Framework | What it does | Graph | Status | TBPN example |', '|---|---|---|---|---|---|', ...tableRows].join('\n');
  md = md.replace(/<!-- FRAMEWORK_TABLE_START -->[\s\S]*?<!-- FRAMEWORK_TABLE_END -->/, `<!-- FRAMEWORK_TABLE_START -->\n${table}\n<!-- FRAMEWORK_TABLE_END -->`);
  const ideaRows = registry.frameworks.map(f => {
    const gpath = path.join(DF, f.category, f.slug, 'graph.json');
    if (!fs.existsSync(gpath)) return `| [${mdEsc(f.name)}](${f.category}/${f.slug}/README.md) | | | |`;
    try {
      const g = JSON.parse(fs.readFileSync(gpath, 'utf8'));
      const ex = g.examples.find(e => e.kind === 'tbpn');
      const slot = ex && g.slots.find(s => s.id === ex.idea_bearing_slot);
      // The idea sentences are the cross-framework opportunity layer: list every node carrying one,
      // whatever its slot, with the node it is read from and its confidence.
      const ideas = ex ? ex.nodes.filter(n => n.idea).map(n => `${mdEsc(n.idea)} <sub>(${mdEsc(n.label)}, ${Math.round((n.confidence || 0) * 100)}%)</sub>`).join('<br>') : '';
      return `| [${mdEsc(f.name)}](${f.category}/${f.slug}/README.md) | ${slot ? mdEsc(slot.label) : ''} | ${ex ? mdEsc(ex.title) : ''} | ${ideas} |`;
    } catch { return `| [${mdEsc(f.name)}](${f.category}/${f.slug}/README.md) | | | |`; }
  });
  const ideaTable = ['| Framework | Idea-bearing slot | TBPN example | Opportunities the graph surfaces (node, confidence) |', '|---|---|---|---|', ...ideaRows].join('\n');
  md = md.replace(/<!-- IDEA_SLOTS_START -->[\s\S]*?<!-- IDEA_SLOTS_END -->/, `<!-- IDEA_SLOTS_START -->\n${ideaTable}\n<!-- IDEA_SLOTS_END -->`);
  fs.writeFileSync(readmePath, md);
}
console.log(`index.html and README tables written: ${doneCount}/${registry.frameworks.length} done`);
