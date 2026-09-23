// Capture the Selected Work card images from the live demos.
//
//   node tools/capture.mjs              # all four
//   node tools/capture.mjs colawars     # just one
//
// Why not `chrome --screenshot --virtual-time-budget`: that fires on a timer,
// so it shot Cola Wars before model-viewer had loaded the can. This drives
// Chrome over the DevTools protocol and waits for the page to be REALLY drawn:
//   1. a per-demo readiness check in the page (e.g. model-viewer .loaded), then
//   2. the screen must be lit (share of non-dark pixels above a floor) and
//      stable (two samples a second apart barely differ).
// The pixel test reads a real screenshot, so it also works for WebGL canvases
// whose drawing buffer cannot be read back from script.
//
// Node 24, zero dependencies: global fetch + WebSocket, zlib for PNG decode.
// Output: assets/work/<name>.webp, 960x900 (1280x1200 viewport scaled 3/4).
// The viewport matches the card's near-square shape (596x576 at 1440), so each
// demo lays itself out for that frame and object-fit has almost nothing to
// crop. A 16:10 shot lost a third of its width and cut the demos' own
// headlines mid-word.

import { spawn } from 'node:child_process';
import { mkdtempSync, rmSync, writeFileSync, existsSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { inflateSync } from 'node:zlib';

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..');
const OUT = join(ROOT, 'assets', 'work');
const PORT = 9333;
const VIEW = { width: 1280, height: 1200 };
const SCALE = 0.75;

const DEMOS = {
  workline: {
    url: 'https://juliusgunawan0707.github.io/workline/',
    minWait: 2500,
  },
  nusantara: {
    url: 'https://juliusgunawan0707.github.io/nusantara/',
    minWait: 6000,
    ready: `!!document.querySelector('canvas')`,
    maxDiff: 9, // the rainforest keeps moving; only wait out the intro fade
  },
  colawars: {
    url: 'https://juliusgunawan0707.github.io/cola-wars/',
    minWait: 3000,
    ready: `(() => { const m = document.querySelector('model-viewer'); return !!(m && m.loaded); })()`,
    settle: 2000, // textures land after the model's load event
    maxDiff: 9, // the can idles in motion
  },
  gbk: {
    url: 'https://juliusgunawan0707.github.io/portfolio-julius/work/gbk-3d/',
    minWait: 8000,
    ready: `!!document.querySelector('canvas')`,
    maxDiff: 9, // the match keeps playing
    // hide the portfolio's back link and the debug FPS/stats box: its counts
    // follow the auto quality level (swiftshader here), not the card's figures
    prep: `(() => {
      const b = document.getElementById('back-to-porto'); if (b) b.style.display = 'none';
      const f = document.getElementById('gbkFpsLine'); if (f) f.parentElement.style.display = 'none';
    })()`,
  },
};

const CHROME = [
  'C:/Program Files/Google/Chrome/Application/chrome.exe',
  'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
].find(existsSync);

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// ---------- minimal CDP client ----------
class CDP {
  constructor(ws) {
    this.ws = ws; this.id = 0; this.pending = new Map();
    ws.addEventListener('message', (ev) => {
      const msg = JSON.parse(ev.data);
      const p = msg.id && this.pending.get(msg.id);
      if (!p) return;
      this.pending.delete(msg.id);
      msg.error ? p.reject(new Error(msg.error.message)) : p.resolve(msg.result);
    });
  }
  static async open(url) {
    const ws = new WebSocket(url);
    await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
    return new CDP(ws);
  }
  send(method, params = {}) {
    const id = ++this.id;
    this.ws.send(JSON.stringify({ id, method, params }));
    return new Promise((resolve, reject) => this.pending.set(id, { resolve, reject }));
  }
  async eval(expr) {
    const r = await this.send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true });
    return r.result && r.result.value;
  }
  close() { this.ws.close(); }
}

// ---------- PNG decode (8-bit RGB/RGBA, non-interlaced: what Chrome emits) ----------
function decodePNG(buf) {
  let pos = 8, w = 0, h = 0, ctype = 0;
  const idat = [];
  while (pos < buf.length) {
    const len = buf.readUInt32BE(pos), type = buf.toString('ascii', pos + 4, pos + 8);
    const data = buf.subarray(pos + 8, pos + 8 + len);
    if (type === 'IHDR') { w = data.readUInt32BE(0); h = data.readUInt32BE(4); ctype = data[9]; }
    else if (type === 'IDAT') idat.push(data);
    else if (type === 'IEND') break;
    pos += 12 + len;
  }
  const bpp = ctype === 6 ? 4 : 3, stride = w * bpp;
  const raw = inflateSync(Buffer.concat(idat));
  const px = Buffer.alloc(h * stride);
  for (let y = 0; y < h; y++) {
    const f = raw[y * (stride + 1)], src = y * (stride + 1) + 1, dst = y * stride;
    for (let x = 0; x < stride; x++) {
      const a = x >= bpp ? px[dst + x - bpp] : 0;
      const b = y ? px[dst - stride + x] : 0;
      const c = x >= bpp && y ? px[dst - stride + x - bpp] : 0;
      let v = raw[src + x];
      if (f === 1) v += a;
      else if (f === 2) v += b;
      else if (f === 3) v += (a + b) >> 1;
      else if (f === 4) { const p = a + b - c, pa = Math.abs(p - a), pb = Math.abs(p - b), pc = Math.abs(p - c); v += pa <= pb && pa <= pc ? a : pb <= pc ? b : c; }
      px[dst + x] = v & 255;
    }
  }
  return { w, h, bpp, px };
}

// Luma grid of a small screenshot: enough to tell "lit" and "still moving".
async function sample(cdp) {
  const { data } = await cdp.send('Page.captureScreenshot', {
    format: 'png', clip: { x: 0, y: 0, ...VIEW, scale: 0.1 },
  });
  const { w, h, bpp, px } = decodePNG(Buffer.from(data, 'base64'));
  const luma = new Float32Array(w * h);
  for (let i = 0; i < w * h; i++) {
    const o = i * bpp;
    luma[i] = 0.2126 * px[o] + 0.7152 * px[o + 1] + 0.0722 * px[o + 2];
  }
  return luma;
}
const litShare = (l) => l.reduce((n, v) => n + (v > 24), 0) / l.length;
const meanDiff = (a, b) => a.reduce((s, v, i) => s + Math.abs(v - b[i]), 0) / a.length;

async function capture(cdp, name, demo) {
  console.log(`\n[${name}] ${demo.url}`);
  await cdp.send('Page.navigate', { url: demo.url });
  const t0 = Date.now();
  await sleep(demo.minWait || 2000);

  if (demo.ready) {
    while (!(await cdp.eval(demo.ready).catch(() => false))) {
      if (Date.now() - t0 > 60000) throw new Error(`${name}: readiness check never passed: ${demo.ready}`);
      await sleep(500);
    }
    console.log(`  ready after ${((Date.now() - t0) / 1000).toFixed(1)} s`);
  }
  if (demo.settle) await sleep(demo.settle);
  if (demo.prep) await cdp.eval(demo.prep);

  // lit + stable
  let prev = await sample(cdp), stable = 0, lit = 0;
  while (stable < 2) {
    await sleep(1000);
    const cur = await sample(cdp);
    lit = litShare(cur);
    const d = meanDiff(prev, cur);
    stable = lit > 0.08 && d < (demo.maxDiff || 2.5) ? stable + 1 : 0;
    prev = cur;
    if (Date.now() - t0 > 90000) throw new Error(`${name}: screen never settled (lit ${lit.toFixed(2)}, diff ${d.toFixed(2)})`);
  }
  console.log(`  settled after ${((Date.now() - t0) / 1000).toFixed(1)} s, lit share ${(lit * 100).toFixed(0)}%`);

  const { data } = await cdp.send('Page.captureScreenshot', {
    format: 'webp', quality: 82, clip: { x: 0, y: 0, ...VIEW, scale: SCALE },
  });
  const file = join(OUT, `${name}.webp`);
  writeFileSync(file, Buffer.from(data, 'base64'));
  console.log(`  -> ${file} (${(Buffer.from(data, 'base64').length / 1024).toFixed(0)} KB)`);
}

async function main() {
  const pick = process.argv.slice(2);
  const names = pick.length ? pick : Object.keys(DEMOS);
  for (const n of names) if (!DEMOS[n]) throw new Error(`unknown demo "${n}" (have: ${Object.keys(DEMOS).join(', ')})`);
  if (!CHROME) throw new Error('Chrome/Edge not found');

  const profile = mkdtempSync(join(tmpdir(), 'porto-capture-'));
  const chrome = spawn(CHROME, [
    '--headless=new', `--remote-debugging-port=${PORT}`, `--user-data-dir=${profile}`,
    '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist',
    '--hide-scrollbars', '--mute-audio', '--no-first-run', '--no-default-browser-check',
    `--window-size=${VIEW.width},${VIEW.height}`, 'about:blank',
  ], { stdio: 'ignore' });

  try {
    let target;
    for (let i = 0; i < 40 && !target; i++) {
      await sleep(250);
      target = await fetch(`http://127.0.0.1:${PORT}/json/list`).then((r) => r.json())
        .then((l) => l.find((t) => t.type === 'page')).catch(() => null);
    }
    if (!target) throw new Error('Chrome DevTools endpoint did not come up');
    const cdp = await CDP.open(target.webSocketDebuggerUrl);
    await cdp.send('Page.enable');
    await cdp.send('Emulation.setDeviceMetricsOverride', { ...VIEW, deviceScaleFactor: 1, mobile: false });
    // dark + English are the demos' defaults; pin them so a stored choice cannot leak in
    await cdp.send('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-color-scheme', value: 'dark' }] });

    for (const n of names) await capture(cdp, n, DEMOS[n]);
    cdp.close();
  } finally {
    chrome.kill();
    await sleep(500);
    try { rmSync(profile, { recursive: true, force: true }); } catch {}
  }
}

main().catch((e) => { console.error(e.message); process.exit(1); });
