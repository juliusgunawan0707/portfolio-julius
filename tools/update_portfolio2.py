# -*- coding: utf-8 -*-
"""Pass 2: Selected Work, Services links, Stats, hero copy, contact form."""
import io
import re
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


# --------------------------------------------------------- meta + hero
rep('content="I build multi-agent systems and automation that quietly remove the '
    'manual work — agents that debate, documents that write themselves, numbers '
    'you can audit."',
    'content="I build automation and realtime interfaces — a work manager that '
    'writes its own paperwork, and 3D that runs in a browser tab. Four live demos, '
    'no slide decks."',
    "meta description")

rep("<span class=\"txt\">6 systems shipped end to end</span>",
    "<span class=\"txt\">4 live demos you can open right now</span>",
    "hero rating line")

# ------------------------------------------------------- Selected Work
CARDS = [
    ("Automation", "Workline",
     "A work manager for public-sector staff: log a task once and the attendance "
     "recap, quarterly performance report and meeting minutes generate themselves "
     "— every figure computed, never invented.",
     ["Single-file app", "Offline-first", "Document generation"],
     "https://juliusgunawan0707.github.io/workline/"),
    ("WebGL", "Nusantara",
     "Four acts along the nationhood axis of Indonesia's new capital, rendered "
     "live in the browser — architecture, terrain and light, sourced from official "
     "figures.",
     ["three.js", "Realtime 3D", "Art direction"],
     "https://juliusgunawan0707.github.io/nusantara/"),
    ("3D Product", "Cola Wars",
     "One soda can, two brand worlds. The model tracks your cursor, and a single "
     "click swaps the label, the palette and the entire design language around it.",
     ["model-viewer", "GLB", "UV mapping"],
     "https://juliusgunawan0707.github.io/cola-wars/"),
    ("Realtime", "GBK 3D",
     "A browser replica of Gelora Bung Karno — 36,150 instanced spectators, a real "
     "match simulated end to end, held at 138 draw calls.",
     ["three.js", "WebGL", "Simulation"],
     "work/gbk-3d/"),
]

items = []
for i, (cat, name, desc, tags, href) in enumerate(CARDS):
    ext = href.startswith("http")
    tgt = ' target="_blank" rel="noopener"' if ext else ' target="_blank" rel="noopener"'
    tagsm = "".join('<span class="tag">%s</span>' % t for t in tags)
    items.append(
        '      <li class="rv" style="--d:%dms;--ty:48px"><a href="%s"%s>\n'
        '        <article class="card">\n'
        '          <div class="meta"><span>%s &mdash; 2026</span>\n'
        '            <span class="live">Live demo <span class="cbadge">'
        '<svg class="ic"><use href="#i-arrow-ur"/></svg></span></span></div>\n'
        '          <div class="cmark"><svg class="ic"><use href="#i-logo"/></svg></div>\n'
        '          <div class="body">\n'
        '            <h3>%s</h3>\n'
        '            <p>%s</p>\n'
        '            <div class="tags">%s</div>\n'
        '          </div>\n'
        '        </article></a></li>' % (i * 90, href, tgt, cat, name, desc, tagsm))

new_cards = "\n".join(items)
m = re.search(r'(<ul class="cards">\n).*?(\n    </ul>)', s, re.S)
if not m:
    sys.exit("ABORT: cards block not found")
s = s[:m.start()] + m.group(1) + new_cards + m.group(2) + s[m.end():]
log.append(("Selected Work -> 4 live demos", 4))

# ------------------------------------------------------------ Services
SERV = [
    ("01", "Multi-Agent Systems",
     "Agents that argue, audit each other, and reach a verdict you can trace.",
     None),
    ("02", "Workflow Automation",
     "Document work that used to take a week, done in one command.",
     "https://juliusgunawan0707.github.io/workline/"),
    ("03", "Data &amp; Analysis",
     "Deterministic numbers from real sources — the model only writes the prose.",
     "https://juliusgunawan0707.github.io/btc-intrinsic-value/"),
    ("04", "Web Applications",
     "Dashboards and tools that people actually open the next morning.",
     "https://juliusgunawan0707.github.io/nusantara/"),
]
rows = []
for i, (idx, title, desc, href) in enumerate(SERV):
    inner = ('<div class="r"><span class="idx">%s</span><h3>%s</h3>\n'
             '        <p>%s</p>\n        %s</div>')
    if href:
        badge = ('<span class="sbadge"><svg class="ic"><use href="#i-arrow-ur"/>'
                 '</svg></span>')
        body = inner % (idx, title, desc, badge)
        rows.append('      <li class="srow rv" style="--d:%dms;--ty:24px">'
                    '<a href="%s" target="_blank" rel="noopener">\n        %s</a></li>'
                    % (i * 80, href, body))
    else:
        badge = '<span class="spriv">Private work</span>'
        body = inner % (idx, title, desc, badge)
        rows.append('      <li class="srow rv" style="--d:%dms;--ty:24px">\n        %s'
                    '</li>' % (i * 80, body))

m = re.search(r'(<section id="services">.*?<ul>\n).*?(\n    </ul>)', s, re.S)
if not m:
    sys.exit("ABORT: services block not found")
s = s[:m.start()] + m.group(1) + "\n".join(rows) + m.group(2) + s[m.end():]
log.append(("Services -> live demo links", 4))

rep(".srow .sbadge{width:2.5rem;height:2.5rem;",
    ".srow .spriv{font-size:.75rem;text-transform:uppercase;letter-spacing:.025em;"
    "color:rgba(17,17,17,.32);flex:none;white-space:nowrap}\n.srow .sbadge{",
    "private-work label css")

# --------------------------------------------------------------- Stats
STATS = [
    (36150, "", "Spectators rendered in realtime"),
    (138, "", "Draw calls, down from 245"),
    (4, "", "Live demos you can open now"),
    (0, "", "Backends — everything runs client-side"),
]
li = []
for i, (v, suf, label) in enumerate(STATS):
    li.append('        <li class="rv" style="--d:%dms;--ty:20px">'
              '<div class="n"><span data-count="%d">0</span>%s</div>'
              '<div class="l">%s</div></li>' % (i * 90, v, suf, label))
m = re.search(r'(<ul class="statgrid">\n).*?(\n      </ul>)', s, re.S)
if not m:
    sys.exit("ABORT: statgrid not found")
s = s[:m.start()] + m.group(1) + "\n".join(li) + m.group(2) + s[m.end():]
log.append(("Stats -> measured metrics", 4))

io.open(P, "w", encoding="utf-8", newline="").write(s)
print("pass 2 selesai")
for label, n in log:
    print("   %-38s %d" % (label, n))
