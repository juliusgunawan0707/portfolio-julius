# -*- coding: utf-8 -*-
"""
Portfolio update: new Selected Work, real brand marks, live service links,
measured stats, a stack grid in place of the globe, and a contact form that
actually delivers.

Every replacement asserts its expected hit count, so a silent partial edit
fails loudly instead of shipping a half-changed page.

    python tools/update_portfolio.py
"""
import io
import sys

P = "index.html"
s = io.open(P, encoding="utf-8").read()
log = []


def rep(old, new, label, n=1):
    global s
    found = s.count(old)
    if found != n:
        sys.exit("ABORT: %s -> found %d, expected %d" % (label, found, n))
    s = s.replace(old, new)
    log.append((label, found))


# ------------------------------------------------- 1. email everywhere
rep("juliusgunawan0707@gmail.com", "juliusgunawan1307@gmail.com",
    "email -> 1307", s.count("juliusgunawan0707@gmail.com"))

# ------------------------------------------- 2. official brand marks
rep('<symbol id="i-dot"',
    '<symbol id="i-github" viewBox="0 0 24 24" fill="currentColor">'
    '<path d="M12 .5C5.37.5 0 5.87 0 12.5c0 5.3 3.44 9.8 8.21 11.39.6.11.82-.26.82-.58'
    ' 0-.29-.01-1.05-.02-2.06-3.34.73-4.04-1.61-4.04-1.61-.55-1.39-1.34-1.76-1.34-1.76'
    '-1.09-.75.08-.73.08-.73 1.21.09 1.84 1.24 1.84 1.24 1.07 1.83 2.81 1.3 3.5.99.11'
    '-.78.42-1.3.76-1.6-2.67-.3-5.47-1.33-5.47-5.93 0-1.31.47-2.38 1.24-3.22-.13-.3'
    '-.54-1.52.12-3.18 0 0 1.01-.32 3.3 1.23a11.5 11.5 0 0 1 6.01 0c2.28-1.55 3.29'
    '-1.23 3.29-1.23.66 1.66.25 2.88.12 3.18.77.84 1.23 1.91 1.23 3.22 0 4.61-2.8 5.63'
    '-5.48 5.92.43.37.81 1.1.81 2.22 0 1.6-.01 2.9-.01 3.29 0 .32.22.7.83.58A12.01'
    ' 12.01 0 0 0 24 12.5C24 5.87 18.63.5 12 .5z"/></symbol>\n'
    '<symbol id="i-linkedin" viewBox="0 0 24 24" fill="currentColor">'
    '<path d="M20.45 20.45h-3.56v-5.57c0-1.33-.03-3.04-1.85-3.04-1.86 0-2.14 1.45-2.14'
    ' 2.94v5.67H9.35V9h3.41v1.56h.05c.48-.9 1.63-1.85 3.36-1.85 3.6 0 4.27 2.37 4.27'
    ' 5.45v6.29zM5.34 7.43a2.06 2.06 0 1 1 0-4.13 2.06 2.06 0 0 1 0 4.13zM7.12'
    ' 20.45H3.55V9h3.57v11.45zM22.22 0H1.77C.79 0 0 .77 0 1.72v20.56C0 23.23.79 24'
    ' 1.77 24h20.45c.98 0 1.78-.77 1.78-1.72V1.72C24 .77 23.2 0 22.22 0z"/></symbol>\n'
    '<symbol id="i-dot"',
    "brand symbols (github + linkedin)")

rep('<a href="https://github.com/juliusgunawan0707" target="_blank" rel="noopener" '
    'aria-label="GitHub"><svg class="ic"><use href="#i-dot"/></svg></a>',
    '<a href="https://github.com/juliusgunawan0707" target="_blank" rel="noopener" '
    'aria-label="GitHub"><svg class="ic"><use href="#i-github"/></svg></a>',
    "github mark in About")

rep('<a href="https://www.linkedin.com/" target="_blank" rel="noopener" '
    'aria-label="LinkedIn"><svg class="ic"><use href="#i-dot"/></svg></a>',
    '<a href="https://www.linkedin.com/in/juliusgunawan/" target="_blank" '
    'rel="noopener" aria-label="LinkedIn"><svg class="ic"><use href="#i-linkedin"/>'
    '</svg></a>',
    "linkedin mark in About")

# ------------------------------------------ 3. globe block -> stack grid
rep("""    <div class="globe-wrap">
      <svg class="ic globe-bg" aria-hidden="true"><use href="#i-globe"/></svg>
      <p class="eyebrow" style="position:relative">About</p>
      <div class="globe-note rv" style="--ty:12px">
        <svg class="ic"><use href="#i-globe"/></svg>
        <span>Based in Indonesia, UTC+8 — working with teams in any time zone.</span>
      </div>
    </div>""",
    """    <div class="stackwrap">
      <p class="eyebrow">About</p>
      <ul class="stackgrid rv" style="--ty:14px">
        <li><span class="k">Python</span><span class="v">Agents, data pipelines, document generation</span></li>
        <li><span class="k">JavaScript</span><span class="v">Web apps and realtime interfaces</span></li>
        <li><span class="k">three.js / WebGL</span><span class="v">Realtime 3D in the browser</span></li>
        <li><span class="k">Apps Script</span><span class="v">Tools that live inside Google Sheets</span></li>
        <li><span class="k">LLM APIs</span><span class="v">Orchestration, with the numbers kept deterministic</span></li>
        <li><span class="k">Git &amp; static hosting</span><span class="v">Ship on push, no server to babysit</span></li>
      </ul>
      <p class="stacknote rv" style="--d:200ms;--ty:10px">
        <svg class="ic" aria-hidden="true"><use href="#i-globe"/></svg>
        Based in Indonesia, UTC+8 — working with teams in any time zone.
      </p>
    </div>""",
    "globe -> stack grid")

rep(""".globe-wrap{position:relative;min-height:14rem}
.globe-bg{position:absolute;left:-1rem;top:50%;transform:translateY(-50%);font-size:12rem;color:rgba(17,17,17,.1)}
.globe-note{position:absolute;left:0;bottom:0;display:flex;align-items:center;gap:.75rem;font-size:.875rem;color:rgba(17,17,17,.7)}
.globe-note .ic{font-size:1.5rem;color:var(--fg)}
.globe-note span{max-width:14rem}""",
    """.stackwrap{display:flex;flex-direction:column;gap:1.5rem}
.stackgrid{display:grid;grid-template-columns:1fr;gap:1px;background:var(--line);
  border:1px solid var(--line);border-radius:var(--radius-card-sm);overflow:hidden}
.stackgrid li{background:var(--bg);padding:1rem 1.125rem;display:flex;flex-direction:column;gap:.25rem}
.stackgrid .k{font-size:.9375rem;font-weight:600;letter-spacing:-.01em}
.stackgrid .v{font-size:.8125rem;line-height:1.45;color:rgba(17,17,17,.6)}
.stacknote{display:flex;align-items:center;gap:.625rem;font-size:.875rem;color:rgba(17,17,17,.6)}
.stacknote .ic{font-size:1.25rem;color:var(--fg);flex:none}""",
    "globe css -> stack css")

# the old globe sizing rules in the breakpoint blocks
rep("  .globe-bg{font-size:16rem}\n", "  .stackgrid{grid-template-columns:1fr 1fr}\n",
    "sm breakpoint")
rep("  .globe-wrap{min-height:20rem}\n  .globe-bg{left:-1.5rem;font-size:20rem}\n", "",
    "lg breakpoint")

io.open(P, "w", encoding="utf-8", newline="").write(s)
print("pass 1 selesai")
for label, n in log:
    print("   %-38s %d" % (label, n))
