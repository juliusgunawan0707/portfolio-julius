# portfolio-julius

Personal site — **Julius Gunawan, AI Automation Engineer**. Static, no build step.

```
index.html                  # everything: markup, CSS, JS (ES module)
assets/hero-base.jpg        # hero wallpaper - DARK theme
assets/hero-light.jpg       # hero wallpaper - LIGHT theme
assets/hero-reveal.jpg      # painted under the cursor (dark theme only)
assets/work/*.webp          # Selected Work card images, captured from the live demos
work/gbk-3d/index.html      # live demo - copy of ../../gbk-3d/index.html + a back link
work/oracle/                # ORACLE architecture diagram (proof for Services 01)
tools/capture.mjs           # re-capture the card images
tools/sync_gbk.py           # re-copy the GBK build
tools/build_oracle.py       # re-render the ORACLE diagram
```

**Card images.** `node tools/capture.mjs [workline|nusantara|colawars|gbk]` drives headless
Chrome over the DevTools protocol (Node 24, no dependencies) and waits until each demo is
really drawn - a readiness check in the page (e.g. model-viewer `.loaded` for Cola Wars)
plus a lit, settled screen - before shooting a 1280x1200 viewport, the card's own shape,
to `assets/work/<name>.webp` at 960x900. Re-run it whenever a demo changes.

**GBK 3D** is a **copy**, not a link: rebuild `gbk-3d/`, then `python tools/sync_gbk.py`.

**ORACLE** is private, so the site shows its wiring only - no bot name, token, chat ID or
portfolio figures. Edit `work/oracle/oracle.architecture.json`, then
`python tools/build_oracle.py` (renders it with the archify skill under the showcase
quality gate and re-injects the back link).

## Deploy to Vercel

From this folder:

```bash
vercel deploy --prod
```

No framework, no config. Vercel detects a static site and serves `index.html` at the
root. If asked for a framework preset, choose **Other**; leave build command and
output directory empty.

## How it works

- **Smooth scroll** — Lenis 1.3.23, vendored at `assets/vendor/lenis.mjs` and loaded as
  an ES module via an importmap. Previously loaded from unpkg at runtime; vendored
  23 Sep 2026 so a compromised or renamed CDN package can't swap the script the site
  runs. Only external dependency left is the Onest webfont from Google Fonts.
- **Adaptive grid** — every size is in `rem`; the root font-size tracks the viewport
  (`vw`-based media queries below 1920px, a damped JS formula above it), so the layout
  scales proportionally instead of reflowing.
- **Liquid reveal** — the hero paints `hero-reveal.jpg` along the pointer trail onto a
  canvas layered over `hero-base.jpg`. Brush radius 143px, trail decay 0.010/frame, and
  a hard clear after 120 idle frames so the trail never obscures the headline. Skipped
  entirely under `prefers-reduced-motion`.
- **Theming** - one set of components, two token sets. Dark is the default; light is
  opt-in via the header toggle and remembered in `localStorage`. An inline script in
  `<head>` applies the stored theme before first paint, so there is no flash. Colours
  live in CSS custom properties on `:root` (dark) and `[data-theme="light"]`; nothing
  is duplicated per theme. The orange accent is a brand constant and never changes.
  Note: `.eyebrow.light` and `.pill.light` are shared with the always-dark Stats panel
  and Footer, so their light-theme overrides are scoped to `#home` - do not lift them
  to the global rule or the footer button turns dark-on-dark.
- **Motion** — entrance reveals are CSS transitions gated by an IntersectionObserver
  (hero reveals additionally wait for the intro loader to finish); hovers run on a small
  rAF spring integrator and are disabled on touch.

## Notes

- The contact modal is a **stub** — submit shows the success state without sending
  anything. Wire it to Formspree, Resend, or a Vercel function when you want real mail.
- `window.__lenis` and `window.__liquid` are exposed **only on localhost** for debugging.
- The stat figures (6 / 12 / 47 / 36,000) are drawn from real projects — check them
  before this goes public.

## Local preview

```bash
python -m http.server 8124
```

Then open http://localhost:8124 — the ES module importmap needs a real HTTP origin, so
opening `index.html` from the filesystem will not work.
