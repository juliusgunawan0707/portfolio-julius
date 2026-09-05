# portfolio-julius

Personal site — **Julius Gunawan, AI Automation Engineer**. Static, no build step.

```
index.html                  # everything: markup, CSS, JS (ES module)
assets/hero-base.jpg        # hero base layer (dark suit, no glasses)
assets/hero-reveal.jpg      # painted under the cursor (warm orange, glasses)
work/gbk-3d/index.html      # live demo — copy of ../../gbk-3d/index.html + a back link
```

`work/gbk-3d/index.html` is a **copy**, not a symlink. Rebuild the source with
`python build.py` in `gbk-3d/`, then re-copy it here and re-inject the `#back-to-porto`
anchor before `</body>`. The GBK 3D portfolio card is the only clickable card; the other
three are marked "Private project" because they cannot be demoed publicly.

## Deploy to Vercel

From this folder:

```bash
vercel deploy --prod
```

No framework, no config. Vercel detects a static site and serves `index.html` at the
root. If asked for a framework preset, choose **Other**; leave build command and
output directory empty.

## How it works

- **Smooth scroll** — Lenis, loaded as an ES module from unpkg via an importmap.
  It is the only external dependency besides the Onest webfont.
- **Adaptive grid** — every size is in `rem`; the root font-size tracks the viewport
  (`vw`-based media queries below 1920px, a damped JS formula above it), so the layout
  scales proportionally instead of reflowing.
- **Liquid reveal** — the hero paints `hero-reveal.jpg` along the pointer trail onto a
  canvas layered over `hero-base.jpg`. Brush radius 143px, trail decay 0.010/frame, and
  a hard clear after 120 idle frames so the trail never obscures the headline. Skipped
  entirely under `prefers-reduced-motion`.
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
