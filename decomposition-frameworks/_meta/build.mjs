#!/usr/bin/env node
// Embed a framework's graph.json into its index.html.
// Usage: node _meta/build.mjs <framework-dir> [...]   |   node _meta/build.mjs --all
// Every build starts from _meta/graph-engine.html (so engine improvements propagate), injects the data
// between <!--__DATA_START__--> / <!--__DATA_END__-->, and carries over the framework's own extension
// block (between <!--__EXT_START__--> / <!--__EXT_END__-->) from the existing index.html if there is one.
import fs from 'node:fs';
import path from 'node:path';
import url from 'node:url';
import { allFrameworkDirs } from './validate.mjs';

const META = path.dirname(url.fileURLToPath(import.meta.url));
const TEMPLATE = path.join(META, 'graph-engine.html');
const DS = '<!--__DATA_START__-->', DE = '<!--__DATA_END__-->';
const XS = '<!--__EXT_START__-->', XE = '<!--__EXT_END__-->';

function block(html, start, end, file) {
  const s = html.indexOf(start), e = html.indexOf(end);
  if (s < 0 || e < 0 || e < s) throw new Error(`${file}: markers ${start} / ${end} missing or out of order`);
  return { s, e: e + end.length, inner: html.slice(s + start.length, e) };
}

export function buildDir(dir) {
  dir = path.resolve(dir);
  const graphFile = path.join(dir, 'graph.json');
  const out = path.join(dir, 'index.html');
  const graph = JSON.parse(fs.readFileSync(graphFile, 'utf8'));
  const json = JSON.stringify(graph).replace(/<\//g, '<\\/');
  let html = fs.readFileSync(TEMPLATE, 'utf8');
  const existed = fs.existsSync(out);
  let ext = null;
  if (existed) {
    const prev = fs.readFileSync(out, 'utf8');
    try { ext = block(prev, XS, XE, out).inner; } catch { ext = null; }
  }
  const d = block(html, DS, DE, TEMPLATE);
  html = html.slice(0, d.s) + `${DS}\n<script id="graph-data" type="application/json">${json}</script>\n${DE}` + html.slice(d.e);
  if (ext !== null) {
    const x = block(html, XS, XE, TEMPLATE);
    html = html.slice(0, x.s) + XS + ext + XE + html.slice(x.e);
  }
  fs.writeFileSync(out, html);
  return { dir, out, bytes: Buffer.byteLength(html), created: !existed, extensionKept: ext !== null && ext.trim().length > 0 };
}

const isMain = process.argv[1] && path.resolve(process.argv[1]) === url.fileURLToPath(import.meta.url);
if (isMain) {
  const argv = process.argv.slice(2);
  const dirs = argv.includes('--all') ? allFrameworkDirs() : argv.filter(a => !a.startsWith('--'));
  if (dirs.length === 0) { console.error('usage: node _meta/build.mjs <framework-dir>... | --all'); process.exit(2); }
  for (const d of dirs) { const r = buildDir(d); console.log(`built ${path.relative(process.cwd(), r.out)} (${(r.bytes / 1024).toFixed(1)} KB)${r.extensionKept ? ' + extension block kept' : ''}`); }
}
