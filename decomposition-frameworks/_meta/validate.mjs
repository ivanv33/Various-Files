#!/usr/bin/env node
// Validate one or more framework folders against SPEC.md sections 3, 4 and 11.
// Usage: node _meta/validate.mjs <framework-dir> [<framework-dir> ...]
//        node _meta/validate.mjs --all
//        add --json for machine-readable output
// Exit code 1 when any folder has errors. Warnings never fail the run.
import fs from 'node:fs';
import path from 'node:path';
import url from 'node:url';

const META = path.dirname(url.fileURLToPath(import.meta.url));
const DF = path.dirname(META);
const REPO = path.dirname(DF);
const registry = JSON.parse(fs.readFileSync(path.join(META, 'frameworks.json'), 'utf8'));
const CATEGORY_IDS = new Set(registry.categories.map(c => c.id));
const LAYOUT_MODES = new Set(['force', 'tree', 'ring', 'plane']);
const PROV = new Set(['fact', 'derived', 'schema']);
const TYPICAL = new Set(['fact', 'derived', 'either', 'schema']);
const MIN_NODES = 8, MAX_NODES = 30, MAX_LABEL = 40, MIN_QUOTE_WORDS = 5, PARAPHRASE_CAP = 0.30;

export function normalize(s) {
  return String(s)
    .toLowerCase()
    .replace(/[‘’‚‛′]/g, "'")
    .replace(/[“”„‟″]/g, '"')
    .replace(/[–—−]/g, '-')
    .replace(/[^a-z0-9]+/g, ' ')
    .trim();
}

export function allFrameworkDirs() {
  const dirs = [];
  for (const c of registry.categories) {
    const cdir = path.join(DF, c.id);
    if (!fs.existsSync(cdir)) continue;
    for (const name of fs.readdirSync(cdir)) {
      const d = path.join(cdir, name);
      if (fs.statSync(d).isDirectory() && fs.existsSync(path.join(d, 'graph.json'))) dirs.push(d);
    }
  }
  return dirs;
}

export function validateDir(dir) {
  const errors = [], warnings = [];
  const E = (m) => errors.push(m), W = (m) => warnings.push(m);
  dir = path.resolve(dir);
  const slug = path.basename(dir);
  const category = path.basename(path.dirname(dir));
  const file = path.join(dir, 'graph.json');
  if (!fs.existsSync(file)) { E(`graph.json missing in ${dir}`); return { dir, slug, errors, warnings }; }
  let g;
  try { g = JSON.parse(fs.readFileSync(file, 'utf8')); } catch (e) { E(`graph.json is not valid JSON: ${e.message}`); return { dir, slug, errors, warnings }; }

  // framework block
  const fw = g.framework || {};
  const reg = registry.frameworks.find(f => f.slug === slug);
  if (!reg) E(`folder name ${slug} is not a registry slug`);
  if (fw.slug !== slug) E(`framework.slug "${fw.slug}" does not match folder "${slug}"`);
  if (fw.category !== category) E(`framework.category "${fw.category}" does not match parent folder "${category}"`);
  if (!CATEGORY_IDS.has(category)) E(`parent folder "${category}" is not a known category`);
  if (reg && reg.category !== category) E(`registry says ${slug} belongs to ${reg.category}, found in ${category}`);
  for (const k of ['name', 'wikipedia', 'one_liner']) if (!fw[k]) E(`framework.${k} missing`);
  if (fw.wikipedia && !/^https:\/\//.test(fw.wikipedia)) E(`framework.wikipedia must be https`);

  // slots
  const slots = new Map();
  if (!Array.isArray(g.slots) || g.slots.length < 2) E(`slots must be an array of at least 2`);
  for (const s of (g.slots || [])) {
    if (!s.id) { E(`slot without id`); continue; }
    if (slots.has(s.id)) E(`duplicate slot id ${s.id}`);
    slots.set(s.id, s);
    if (!s.label) E(`slot ${s.id} missing label`);
    if (!s.description || s.description.length < 10) E(`slot ${s.id} needs a description`);
    if (!TYPICAL.has(s.typical_provenance)) E(`slot ${s.id} typical_provenance must be fact|derived|either|schema`);
    if (s.structural && s.typical_provenance !== 'schema') E(`slot ${s.id} is structural but typical_provenance is not schema`);
    if (s.typical_provenance === 'schema' && !s.structural) E(`slot ${s.id} has typical_provenance schema but is not marked structural`);
    if (s.color && !/^#[0-9a-fA-F]{6}$/.test(s.color)) E(`slot ${s.id} color must be #rrggbb`);
  }
  if (reg) for (const rs of reg.slots) if (!slots.has(rs.id)) E(`registry slot "${rs.id}" is missing; keep registry slot ids (unused slots may stay defined)`);

  // relations
  const relations = new Map();
  for (const r of (g.relations || [])) {
    if (!r.id) { E(`relation without id`); continue; }
    if (r.id === 'supported_by') E(`supported_by is reserved and implicit; remove it from relations`);
    if (relations.has(r.id)) E(`duplicate relation id ${r.id}`);
    relations.set(r.id, r);
    if (!r.label) E(`relation ${r.id} missing label`);
  }
  if (relations.size === 0) E(`relations must not be empty`);

  // examples
  const examples = g.examples || [];
  if (!Array.isArray(examples) || examples.length < 2) E(`examples must contain at least classic and tbpn`);
  const kinds = examples.map(x => x.kind);
  if (kinds.filter(k => k === 'classic').length !== 1) E(`exactly one example of kind classic required`);
  if (kinds.filter(k => k === 'tbpn').length !== 1) E(`exactly one example of kind tbpn required`);
  const exIds = new Set();
  for (const ex of examples) {
    const tag = `example ${ex.id || '?'}`;
    if (!ex.id) E(`example without id`); else if (exIds.has(ex.id)) E(`duplicate example id ${ex.id}`); else exIds.add(ex.id);
    for (const k of ['title', 'summary', 'source', 'layout', 'nodes', 'edges']) if (ex[k] === undefined) E(`${tag}: ${k} missing`);
    if (ex.summary && ex.summary.length < 40) E(`${tag}: summary too short`);

    // source
    let sourceText = null;
    const src = ex.source || {};
    if (ex.kind === 'classic') {
      if (src.type !== 'text') E(`${tag}: classic source.type must be text`);
      if (!src.text || src.text.length < 200) E(`${tag}: classic source.text must be at least 200 characters (fact nodes quote it)`);
      sourceText = src.text || '';
    } else if (ex.kind === 'tbpn') {
      if (src.type !== 'transcript') E(`${tag}: tbpn source.type must be transcript`);
      if (!src.file) E(`${tag}: source.file missing`);
      else {
        const abs = path.join(REPO, src.file);
        if (!/^tbpn-transcripts\/transcripts\/\d{4}-\d{2}-\d{2}_.+\.md$/.test(src.file)) E(`${tag}: source.file must be tbpn-transcripts/transcripts/YYYY-MM-DD_<title>.md`);
        if (!fs.existsSync(abs)) E(`${tag}: transcript file not found: ${src.file}`);
        else sourceText = fs.readFileSync(abs, 'utf8');
        if (src.date && src.file && !path.basename(src.file).startsWith(src.date)) E(`${tag}: source.date ${src.date} does not match the file's date prefix`);
      }
      if (!src.date) E(`${tag}: source.date missing`);
      if (!src.episode_title) E(`${tag}: source.episode_title missing`);
      if (!ex.why_this_episode || ex.why_this_episode.length < 40) E(`${tag}: why_this_episode missing or too short`);
      if (!ex.idea_bearing_slot) E(`${tag}: idea_bearing_slot missing`);
      else if (!slots.has(ex.idea_bearing_slot)) E(`${tag}: idea_bearing_slot "${ex.idea_bearing_slot}" is not a slot`);
    } else E(`${tag}: kind must be classic or tbpn`);
    const normSource = sourceText === null ? null : normalize(sourceText);

    // nodes
    const nodes = new Map();
    const list = ex.nodes || [];
    if (list.length < MIN_NODES || list.length > MAX_NODES) E(`${tag}: ${list.length} nodes; must be ${MIN_NODES}..${MAX_NODES}`);
    let factCount = 0, paraCount = 0, derivedCount = 0;
    for (const n of list) {
      const nt = `${tag} node ${n.id || '?'}`;
      if (!n.id) { E(`${tag}: node without id`); continue; }
      if (nodes.has(n.id)) E(`${nt}: duplicate id`);
      nodes.set(n.id, n);
      const slot = slots.get(n.slot);
      if (!slot) E(`${nt}: slot "${n.slot}" is not defined`);
      if (!n.label) E(`${nt}: label missing`); else if (n.label.length > MAX_LABEL) W(`${nt}: label is ${n.label.length} chars (limit ${MAX_LABEL})`);
      if (!n.text) E(`${nt}: text missing`);
      if (!PROV.has(n.provenance)) { E(`${nt}: provenance must be fact|derived|schema`); continue; }
      if (n.provenance === 'schema') {
        if (!slot || !slot.structural) E(`${nt}: provenance schema is only allowed in a structural slot`);
        continue;
      }
      if (slot && slot.structural) E(`${nt}: structural slot ${slot.id} requires provenance schema`);
      if (n.provenance === 'fact') {
        factCount++;
        if (!n.source_ref) W(`${nt}: fact without source_ref`);
        if (n.paraphrase) {
          paraCount++;
          if (!n.source_quote) E(`${nt}: paraphrase still needs source_quote (the paraphrased content)`);
        } else {
          if (!n.source_quote) { E(`${nt}: fact without source_quote`); continue; }
          const words = normalize(n.source_quote).split(' ').filter(Boolean);
          if (words.length < MIN_QUOTE_WORDS) E(`${nt}: verbatim quote has ${words.length} words; need ${MIN_QUOTE_WORDS} (or mark paraphrase)`);
          if (normSource !== null && !normSource.includes(normalize(n.source_quote))) E(`${nt}: source_quote not found verbatim in the source: "${n.source_quote.slice(0, 80)}"`);
        }
      } else {
        derivedCount++;
        if (typeof n.confidence !== 'number' || n.confidence < 0 || n.confidence > 1) E(`${nt}: derived needs confidence 0..1`);
        if (!n.rationale || n.rationale.length < 20) E(`${nt}: derived needs a rationale (20+ chars)`);
        if (n.source_quote) W(`${nt}: derived node carries source_quote; if it is stated in the source it should be a fact`);
      }
    }
    if (factCount > 0 && paraCount / factCount > PARAPHRASE_CAP) E(`${tag}: ${paraCount}/${factCount} facts are paraphrases; cap is ${Math.round(PARAPHRASE_CAP * 100)}%`);
    if (factCount === 0) E(`${tag}: no fact nodes; every example must be grounded`);
    if (derivedCount === 0) W(`${tag}: no derived nodes; the framework adds nothing here`);

    // edges
    const edges = ex.edges || [];
    const edgeIds = new Set();
    const touchesFact = new Set();
    for (const e of edges) {
      const et = `${tag} edge ${e.id || '?'}`;
      if (!e.id) { E(`${tag}: edge without id`); continue; }
      if (edgeIds.has(e.id)) E(`${et}: duplicate id`); edgeIds.add(e.id);
      const a = nodes.get(e.from), b = nodes.get(e.to);
      if (!a) E(`${et}: from "${e.from}" is not a node`);
      if (!b) E(`${et}: to "${e.to}" is not a node`);
      if (!a || !b) continue;
      if (e.relation !== 'supported_by' && !relations.has(e.relation)) E(`${et}: relation "${e.relation}" is not defined`);
      if (!PROV.has(e.provenance)) { E(`${et}: provenance must be fact|derived|schema`); continue; }
      if (e.provenance === 'schema' && a.provenance !== 'schema' && b.provenance !== 'schema') E(`${et}: provenance schema only when an endpoint is a schema node`);
      if (e.provenance === 'derived' && (typeof e.confidence !== 'number' || e.confidence < 0 || e.confidence > 1)) E(`${et}: derived edge needs confidence 0..1`);
      if (e.relation === 'supported_by') {
        if (a.provenance !== 'derived') E(`${et}: supported_by must start at a derived node`);
        if (b.provenance !== 'fact') E(`${et}: supported_by must end at a fact node`);
        if (e.provenance !== 'derived') E(`${et}: supported_by edges are always derived`);
      }
      if (a.provenance === 'fact') touchesFact.add(b.id);
      if (b.provenance === 'fact') touchesFact.add(a.id);
    }
    if (edges.length < list.length - 1) W(`${tag}: ${edges.length} edges for ${list.length} nodes; graph is probably disconnected`);
    for (const n of nodes.values()) if (n.provenance === 'derived' && !touchesFact.has(n.id)) W(`${tag} node ${n.id}: derived node has no edge to any fact (add supported_by)`);

    // layout
    const L = ex.layout || {};
    if (!LAYOUT_MODES.has(L.mode)) E(`${tag}: layout.mode must be force|tree|ring|plane`);
    if (L.mode === 'tree') {
      const allLevels = list.every(n => Number.isInteger(n.level));
      if (!allLevels && !L.root) E(`${tag}: tree layout needs layout.root or a level on every node`);
      if (L.root && !nodes.has(L.root)) E(`${tag}: layout.root "${L.root}" is not a node`);
      if (L.direction && !['down', 'right'].includes(L.direction)) E(`${tag}: layout.direction must be down|right`);
    }
    if (L.mode === 'ring') {
      const missing = list.filter(n => !Number.isInteger(n.order) && !n.pos).map(n => n.id);
      if (missing.length) W(`${tag}: ring layout, nodes without order or pos will be force-placed inside: ${missing.join(', ')}`);
    }
    if (L.mode === 'plane') {
      const missing = list.filter(n => !Array.isArray(n.pos)).map(n => n.id);
      if (missing.length) W(`${tag}: plane layout, nodes without pos will be force-placed: ${missing.join(', ')}`);
    }
    for (const n of list) if (n.pos && (!Array.isArray(n.pos) || n.pos.length < 2 || n.pos.length > 3 || n.pos.some(v => typeof v !== 'number'))) E(`${tag} node ${n.id}: pos must be [x,y] or [x,y,z]`);
    if (L.axes) for (const k of ['x', 'y']) { const ax = L.axes[k]; if (ax && (typeof ax.min !== 'number' || typeof ax.max !== 'number' || !ax.label)) E(`${tag}: axes.${k} needs label, min, max`); }
    for (const r of (L.regions || [])) if (!r.label || !Array.isArray(r.x) || !Array.isArray(r.y) || r.x.length !== 2 || r.y.length !== 2) E(`${tag}: region needs label, x:[x0,x1], y:[y0,y1]`);
    for (const gd of (L.guides || [])) if (!Array.isArray(gd.from) || !Array.isArray(gd.to)) E(`${tag}: guide needs from and to`);
  }

  // state.json sanity (optional file)
  const stateFile = path.join(dir, 'state.json');
  if (fs.existsSync(stateFile)) {
    try { const st = JSON.parse(fs.readFileSync(stateFile, 'utf8')); if (st.slug !== slug) E(`state.json slug "${st.slug}" does not match folder`); }
    catch (e) { E(`state.json is not valid JSON: ${e.message}`); }
  }
  return { dir, slug, errors, warnings };
}

const argv = process.argv.slice(2);
const isMain = process.argv[1] && path.resolve(process.argv[1]) === url.fileURLToPath(import.meta.url);
if (isMain) {
  const json = argv.includes('--json');
  const dirs = argv.includes('--all') ? allFrameworkDirs() : argv.filter(a => !a.startsWith('--'));
  if (dirs.length === 0) { console.error('usage: node _meta/validate.mjs <framework-dir>... | --all [--json]'); process.exit(2); }
  const results = dirs.map(validateDir);
  if (json) console.log(JSON.stringify(results, null, 2));
  else for (const r of results) {
    const status = r.errors.length ? 'FAIL' : 'PASS';
    console.log(`${status} ${r.slug}: ${r.errors.length} errors, ${r.warnings.length} warnings`);
    for (const e of r.errors) console.log(`  E ${e}`);
    for (const w of r.warnings) console.log(`  W ${w}`);
  }
  process.exit(results.some(r => r.errors.length) ? 1 : 0);
}
