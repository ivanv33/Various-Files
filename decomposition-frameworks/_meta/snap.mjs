#!/usr/bin/env node
// Headless screenshots + legibility metrics for a framework page, for the viz critic loop.
// Usage: node _meta/snap.mjs <framework-dir> [--out <dir>] [--width 1400] [--height 900]
// Output: PNGs and report.json in <out> (default _meta/.snaps/<slug>/, git-ignored).
// Needs a Chromium-based browser: set CHROME_PATH or have Chrome / Brave / Chromium / Edge in /Applications.
import fs from 'node:fs';
import path from 'node:path';
import url from 'node:url';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const puppeteer = require('puppeteer-core');

const META = path.dirname(url.fileURLToPath(import.meta.url));
const argv = process.argv.slice(2);
const opt = (k, d) => { const i = argv.indexOf(k); return i >= 0 ? argv[i + 1] : d; };
const dir = path.resolve(argv.find(a => !a.startsWith('--') && a !== opt('--out') && a !== opt('--width') && a !== opt('--height')) || '');
if (!dir || !fs.existsSync(path.join(dir, 'index.html'))) { console.error('usage: node _meta/snap.mjs <framework-dir> [--out dir] [--width 1400] [--height 900]'); process.exit(2); }
const slug = path.basename(dir);
const out = path.resolve(opt('--out', path.join(META, '.snaps', slug)));
const width = parseInt(opt('--width', '1400'), 10), height = parseInt(opt('--height', '900'), 10);
fs.mkdirSync(out, { recursive: true });

const candidates = [process.env.CHROME_PATH, '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser', '/Applications/Chromium.app/Contents/MacOS/Chromium', '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge', '/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser'].filter(Boolean);
const executablePath = candidates.find(p => fs.existsSync(p));
if (!executablePath) { console.error('no Chromium-based browser found; set CHROME_PATH'); process.exit(2); }

const graph = JSON.parse(fs.readFileSync(path.join(dir, 'graph.json'), 'utf8'));
const pageUrl = url.pathToFileURL(path.join(dir, 'index.html')).href;

const browser = await puppeteer.launch({ executablePath, headless: true, args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--allow-file-access-from-files', '--hide-scrollbars', '--no-first-run', '--no-default-browser-check'] });
const report = { slug, generated_at: new Date().toISOString(), viewport: [width, height], browser: path.basename(executablePath), examples: [] };
try {
  const page = await browser.newPage();
  await page.setViewport({ width, height, deviceScaleFactor: 1 });
  const errors = [];
  page.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') errors.push(`${m.type()}: ${m.text()}`); });
  page.on('pageerror', e => errors.push(`pageerror: ${e.message}`));
  page.on('requestfailed', r => errors.push(`requestfailed: ${r.url()} ${r.failure()?.errorText || ''}`));

  const metrics = () => page.evaluate(() => {
    const main = document.querySelector('main').getBoundingClientRect();
    // Node labels AND edge labels: an edge label sitting on a node label is the collision class
    // critics kept reporting by eye because the metrics could not see it.
    const vis = (e) => e.style.display !== 'none' && e.offsetParent !== null;
    // Measure the inner .lab span when there is one: it carries the translateY plate offset and any
    // rotation, and getBoundingClientRect on the root ignores both, so the root box sat 11px above
    // the drawn label and a rotated axis title was measured unrotated.
    const box = (e, kind) => { const t = e.querySelector('.lab') || e; const r = t.getBoundingClientRect(); return { t: e.textContent.trim(), kind, x: r.left, y: r.top, w: r.width, h: r.height }; };
    const nodeRects = [...document.querySelectorAll('#labels .nlabel')].filter(vis).map(e => box(e, 'node'));
    const edgeRects = [...document.querySelectorAll('#labels .elabel')].filter(vis).map(e => box(e, 'edge'));
    const decorRects = [...document.querySelectorAll('#labels .axlabel, #labels .tick, #labels .rlabel, #labels .glabel')].filter(vis).map(e => box(e, 'decor'));
    const rects = [...nodeRects, ...edgeRects, ...decorRects];
    let overlaps = 0; const pairs = [];
    for (let i = 0; i < rects.length; i++) for (let j = i + 1; j < rects.length; j++) { const a = rects[i], b = rects[j]; if (a.x < b.x + b.w && b.x < a.x + a.w && a.y < b.y + b.h && b.y < a.y + a.h) { overlaps++; if (pairs.length < 12) pairs.push([a.t, b.t]); } }
    const cards = ['legend', 'panel'].map(id => document.getElementById(id)).filter(e => e && !e.hidden).map(e => e.getBoundingClientRect());
    const offscreen = rects.filter(r => r.x < main.left || r.y < main.top || r.x + r.w > main.right || r.y + r.h > main.bottom).length;
    const underCards = rects.filter(r => cards.some(c => r.x < c.right && c.left < r.x + r.w && r.y < c.bottom && c.top < r.y + r.h)).length;
    const stats = document.getElementById('stats')?.textContent || '';
    return { labels: rects.length, node_labels: nodeRects.length, edge_labels: edgeRects.length, decor_labels: decorRects.length, overlapping_pairs: overlaps, overlap_examples: pairs, offscreen, under_cards: underCards, stats };
  });

  for (let i = 0; i < graph.examples.length; i++) {
    const ex = graph.examples[i];
    const rec = { index: i, id: ex.id, kind: ex.kind, title: ex.title, layout: ex.layout?.mode, shots: {}, console: [] };
    errors.length = 0;
    await page.goto(`${pageUrl}?example=${i}`, { waitUntil: 'load' });
    try { await page.waitForFunction(() => window.__engineReady === true, { timeout: 25000 }); } catch { rec.console.push('engine did not report ready within 25s'); }
    await new Promise(r => setTimeout(r, 900));
    rec.metrics_default = await metrics();
    const shot = async (name) => { const f = path.join(out, `${ex.id}-${name}.png`); await page.screenshot({ path: f }); rec.shots[name] = path.relative(process.cwd(), f); };
    await shot('default');
    await page.click('#t-derived'); await new Promise(r => setTimeout(r, 400));
    rec.metrics_facts_only = await metrics();
    await shot('facts-only');
    await page.click('#t-derived'); await page.click('#t-grounding'); await new Promise(r => setTimeout(r, 400));
    await shot('grounding');
    await page.click('#t-grounding');
    // click the first node to show the panel
    const clicked = await page.evaluate(() => { const c = document.querySelector('#stage canvas'); if (!c) return false; return true; });
    if (clicked) {
      // Open the panel on a DERIVED node, preferring one carrying an idea: that panel shows the
      // confidence, the rationale, the supporting facts and the opportunity, which is the whole
      // point of this library. Clicking the first label in DOM order (the old behaviour) almost
      // always landed on a fact node, so no critic ever saw the inference panel.
      // Capture BOTH panels. The derived one carries the confidence, rationale, supporting facts
      // and opportunity; the fact one carries the verbatim quote and its reference. Sampling only
      // one leaves half of the provenance story unverified on every page.
      const locate = (want) => page.evaluate((want) => {
        const vis = (e) => e.style.display !== 'none' && e.offsetParent !== null;
        const all = [...document.querySelectorAll('#labels .nlabel')].filter(vis);
        const target = want === 'derived'
          ? (all.find(e => e.classList.contains('derived') && e.querySelector('.idea-star')) || all.find(e => e.classList.contains('derived')))
          : all.find(e => e.classList.contains('fact'));
        if (!target) return null;
        const r = target.getBoundingClientRect();
        return { x: r.left + r.width / 2, y: r.top - 8, kind: target.className, idea: !!target.querySelector('.idea-star') };
      }, want);
      const readPanel = () => page.evaluate(() => {
        const p = document.getElementById('panel');
        if (!p || p.hidden) return null;
        return { badge: p.querySelector('.badge')?.textContent || null, headings: [...p.querySelectorAll('h4')].map(h => h.textContent), quoted: !!p.querySelector('blockquote') };
      });
      rec.panels = {};
      for (const want of ['derived', 'fact']) {
        const pick = await locate(want);
        if (!pick) { rec.panels[want] = 'no visible node of this kind'; continue; }
        await page.mouse.click(pick.x, pick.y);
        await new Promise(r => setTimeout(r, 300));
        await shot(`panel-${want}`);
        rec.panels[want] = { node: pick.kind, has_idea: pick.idea, panel: await readPanel() };
        await page.keyboard.press('Escape');
        await new Promise(r => setTimeout(r, 150));
      }
    }
    rec.console = [...rec.console, ...errors];
    report.examples.push(rec);
  }
} finally { await browser.close(); }
fs.writeFileSync(path.join(out, 'report.json'), JSON.stringify(report, null, 2));
for (const ex of report.examples) {
  const m = ex.metrics_default;
  console.log(`${slug} [${ex.index}] ${ex.id} (${ex.layout}): labels ${m.labels} (${m.node_labels} node / ${m.edge_labels} edge / ${m.decor_labels} decor), overlapping pairs ${m.overlapping_pairs}, offscreen ${m.offscreen}, under cards ${m.under_cards}; console ${ex.console.length ? ex.console.length + ' issue(s)' : 'clean'}`);
  for (const c of ex.console) console.log(`    ! ${c}`);
}
console.log(`screenshots + report.json in ${path.relative(process.cwd(), out)}`);
