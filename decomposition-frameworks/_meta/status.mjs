#!/usr/bin/env node
// Scan every framework folder, print a resume table, write _meta/state.json.
// Usage: node _meta/status.mjs [--json]
import fs from 'node:fs';
import path from 'node:path';
import url from 'node:url';

const META = path.dirname(url.fileURLToPath(import.meta.url));
const DF = path.dirname(META);
const registry = JSON.parse(fs.readFileSync(path.join(META, 'frameworks.json'), 'utf8'));
const STEPS = ['research', 'scout', 'graph', 'validate', 'readme', 'viz', 'reconcile', 'commit'];

export function collect() {
  const rows = [];
  for (const f of registry.frameworks) {
    const dir = path.join(DF, f.category, f.slug);
    const files = ['README.md', 'graph.json', 'index.html', 'state.json'].filter(n => fs.existsSync(path.join(dir, n)));
    let state = null;
    if (files.includes('state.json')) { try { state = JSON.parse(fs.readFileSync(path.join(dir, 'state.json'), 'utf8')); } catch { state = { status: 'corrupt' }; } }
    const status = state ? state.status : (fs.existsSync(dir) ? 'pending' : 'missing');
    const steps = state?.steps || {};
    const lastStep = [...STEPS].reverse().find(s => steps[s] === 'done') || '-';
    rows.push({ slug: f.slug, name: f.name, category: f.category, dir: path.relative(DF, dir), status, last_step: lastStep, files, tbpn_example: state?.tbpn_example || null, updated_at: state?.updated_at || null, notes: state?.notes || '' });
  }
  return rows;
}

const isMain = process.argv[1] && path.resolve(process.argv[1]) === url.fileURLToPath(import.meta.url);
if (isMain) {
  const rows = collect();
  const summary = { generated_at: new Date().toISOString(), done: rows.filter(r => r.status === 'done').length, total: rows.length, frameworks: rows };
  fs.writeFileSync(path.join(META, 'state.json'), JSON.stringify(summary, null, 2) + '\n');
  if (process.argv.includes('--json')) { console.log(JSON.stringify(summary, null, 2)); process.exit(0); }
  const pad = (s, n) => String(s).padEnd(n);
  console.log(pad('slug', 28) + pad('status', 13) + pad('last step', 11) + pad('files', 6) + 'tbpn example');
  for (const r of rows) console.log(pad(r.slug, 28) + pad(r.status, 13) + pad(r.last_step, 11) + pad(r.files.length + '/4', 6) + (r.tbpn_example ? `${r.tbpn_example.date} ${r.tbpn_example.episode_title || ''}` : '-'));
  console.log(`\n${summary.done}/${summary.total} done. Not done: ${rows.filter(r => r.status !== 'done').map(r => r.slug).join(', ') || 'none'}`);
}
