#!/usr/bin/env node
// Render every part and assembly in an Onshape document to PNGs, from every angle.
//
// Only re-renders elements whose microversion changed since the last run, so most
// weeks this does nothing and costs nothing. The cache file is the "what changed"
// signal friday reads.
//
// Usage:
//   node scripts/onshape-render.mjs            # render what changed
//   node scripts/onshape-render.mjs --force    # re-render everything
//   node scripts/onshape-render.mjs --probe    # one part, every view, into _probe/
//
// Env: ONSHAPE_ACCESS_KEY, ONSHAPE_SECRET_KEY

import fs from 'node:fs/promises';
import path from 'node:path';

const ROOT = path.resolve(import.meta.dirname, '..');
const BASE = process.env.ONSHAPE_BASE ?? 'https://cad.onshape.com/api/v6';
const ACCESS = process.env.ONSHAPE_ACCESS_KEY;
const SECRET = process.env.ONSHAPE_SECRET_KEY;
const FORCE = process.argv.includes('--force');
const PROBE = process.argv.includes('--probe');

if (!ACCESS || !SECRET) {
  console.error('missing ONSHAPE_ACCESS_KEY / ONSHAPE_SECRET_KEY');
  process.exit(1);
}

// Row-major 3x4 view matrices for a Z-up world.
// Rows are: screen-right, screen-up, camera direction. 4th column is translation.
// If the framing comes out wrong on the first run, this table is the only thing to fix.
const VIEWS = {
  iso:    '0.707,0.707,0,0,-0.408,0.408,0.816,0,0.577,-0.577,0.577,0',
  front:  '1,0,0,0,0,0,1,0,0,-1,0,0',
  back:   '-1,0,0,0,0,0,1,0,0,1,0,0',
  right:  '0,1,0,0,0,0,1,0,1,0,0,0',
  left:   '0,-1,0,0,0,0,1,0,-1,0,0,0',
  top:    '1,0,0,0,0,1,0,0,0,0,1,0',
  bottom: '1,0,0,0,0,-1,0,0,0,0,-1,0',
};

const SIZE = 1200;
const THROTTLE_MS = 900; // shaded views are expensive; be polite

const auth = 'Basic ' + Buffer.from(`${ACCESS}:${SECRET}`).toString('base64');
const sleep = ms => new Promise(r => setTimeout(r, ms));
const slug = s => s.replace(/[^a-zA-Z0-9._-]+/g, '-').replace(/^-|-$/g, '').slice(0, 80) || 'unnamed';

async function api(pathname, params) {
  const url = new URL(BASE + pathname);
  for (const [k, v] of Object.entries(params ?? {})) url.searchParams.set(k, String(v));
  const res = await fetch(url, { headers: { Authorization: auth, Accept: 'application/json' } });
  const body = await res.text();
  if (!res.ok) {
    throw new Error(`${res.status} ${res.statusText}\n  GET ${url.pathname}${url.search}\n  ${body.slice(0, 600)}`);
  }
  return JSON.parse(body);
}

function parseDocUrl(u) {
  // https://cad.onshape.com/documents/{did}/w/{wid}/e/{eid}
  const m = u.match(/\/documents\/([0-9a-f]+)\/w\/([0-9a-f]+)/i);
  if (!m) throw new Error(`cannot parse document url: ${u}`);
  return { did: m[1], wid: m[2] };
}

async function shadedViews(kind, did, wid, eid, partId) {
  const seg = partId
    ? `/parts/d/${did}/w/${wid}/e/${eid}/partid/${encodeURIComponent(partId)}/shadedviews`
    : `/${kind}/d/${did}/w/${wid}/e/${eid}/shadedviews`;
  const out = {};
  for (const [name, matrix] of Object.entries(VIEWS)) {
    const json = await api(seg, {
      viewMatrix: matrix,
      outputHeight: SIZE,
      outputWidth: SIZE,
      pixelSize: 0,            // 0 = auto fit to frame, keeps framing consistent
      edges: 'show',
      useAntiAliasing: true,
      ...(partId ? {} : { showAllParts: true }),
    });
    const b64 = json.images?.[0];
    if (!b64) throw new Error(`no image returned for view "${name}"`);
    out[name] = Buffer.from(b64, 'base64');
    await sleep(THROTTLE_MS);
  }
  return out;
}

async function writeViews(dir, views) {
  await fs.mkdir(dir, { recursive: true });
  for (const [name, buf] of Object.entries(views)) {
    await fs.writeFile(path.join(dir, `${name}.png`), buf);
  }
  return Object.keys(views).map(n => path.relative(ROOT, path.join(dir, `${n}.png`)));
}

async function renderProject(project) {
  const { did, wid } = parseDocUrl(project.documentUrl);
  const outRoot = path.join(ROOT, project.folder, 'renders');
  const cachePath = path.join(ROOT, project.folder, '.onshape-cache.json');

  let cache = {};
  try { cache = JSON.parse(await fs.readFile(cachePath, 'utf8')); } catch {}

  const elements = await api(`/documents/d/${did}/w/${wid}/elements`);
  const wanted = elements.filter(e =>
    ['PARTSTUDIO', 'ASSEMBLY'].includes(e.elementType) &&
    (!project.tabs?.length || project.tabs.includes(e.name))
  );

  const manifest = { document: project.documentUrl, renderedAt: new Date().toISOString(), elements: [] };
  const changed = [];

  for (const el of wanted) {
    const mv = el.microversionId ?? 'unknown';
    const key = el.id;
    const stale = FORCE || cache[key]?.microversionId !== mv;
    const elDir = path.join(outRoot, slug(el.name));

    if (!stale) {
      console.log(`  = ${el.name} (unchanged)`);
      manifest.elements.push(cache[key].manifest);
      continue;
    }
    console.log(`  * ${el.name} (${el.elementType})`);
    const entry = { name: el.name, id: el.id, type: el.elementType, microversionId: mv, renders: {} };

    if (el.elementType === 'ASSEMBLY') {
      entry.renders.assembly = await writeViews(path.join(elDir, '_assembly'), 
        await shadedViews('assemblies', did, wid, el.id));
    } else {
      entry.renders.studio = await writeViews(path.join(elDir, '_all'),
        await shadedViews('partstudios', did, wid, el.id));
      const parts = await api(`/parts/d/${did}/w/${wid}/e/${el.id}`);
      for (const p of parts) {
        console.log(`      - ${p.name}`);
        entry.renders[p.name] = await writeViews(path.join(elDir, slug(p.name)),
          await shadedViews('parts', did, wid, el.id, p.partId));
        if (PROBE) break;
      }
    }

    manifest.elements.push(entry);
    cache[key] = { microversionId: mv, manifest: entry };
    changed.push(el.name);
    if (PROBE) break;
  }

  await fs.mkdir(outRoot, { recursive: true });
  await fs.writeFile(path.join(outRoot, 'manifest.json'), JSON.stringify(manifest, null, 2));
  await fs.writeFile(cachePath, JSON.stringify(cache, null, 2));
  return changed;
}

const config = JSON.parse(await fs.readFile(path.join(ROOT, 'onshape.json'), 'utf8'));
const allChanged = [];
for (const project of config.projects) {
  console.log(`\n${project.folder}`);
  allChanged.push(...(await renderProject(project)).map(n => `${project.folder}/${n}`));
}
console.log(`\nchanged: ${allChanged.length ? allChanged.join(', ') : 'nothing'}`);
await fs.writeFile(path.join(ROOT, '.friday-onshape-changed.json'), JSON.stringify(allChanged, null, 2));
