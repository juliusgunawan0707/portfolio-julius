# -*- coding: utf-8 -*-
"""
Copy the latest GBK 3D build into the portfolio and re-inject the back link.

The portfolio serves a COPY of gbk-3d/index.html, not a link to it, so a new
GBK build does not reach the live site until this runs and is pushed:

    python tools/sync_gbk.py
    git add work/gbk-3d && git commit -m "Sync GBK 3D" && git push
"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, "..", "..", "gbk-3d", "index.html"))
DST = os.path.normpath(os.path.join(HERE, "..", "work", "gbk-3d", "index.html"))

BACK = """<a id="back-to-porto" href="../../" aria-label="Back to Julius Gunawan's site"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M19 12H5M11 18l-6-6 6-6"/></svg>Julius Gunawan</a>
<style>
#back-to-porto{position:fixed;top:14px;right:14px;z-index:150;display:inline-flex;align-items:center;gap:8px;padding:8px 14px;border-radius:12px;border:1px solid rgba(255,255,255,.18);background:rgba(10,10,10,.55);-webkit-backdrop-filter:blur(6px);backdrop-filter:blur(6px);color:rgba(255,255,255,.78);font:500 12px/1 system-ui,-apple-system,"Segoe UI",sans-serif;letter-spacing:.02em;text-decoration:none;transition:color .2s,border-color .2s,background .2s}
#back-to-porto:hover{color:#fff;border-color:rgba(255,255,255,.4);background:rgba(10,10,10,.75)}
@media (max-width:640px){#back-to-porto{padding:7px 10px;font-size:11px}}
</style>
</body>"""

html = io.open(SRC, encoding="utf-8").read()
if html.count("</body>") != 1:
    sys.exit("ABORT: expected exactly one </body> in %s" % SRC)
if "back-to-porto" in html:
    sys.exit("ABORT: source already carries the back link - edit the source, not the copy")

io.open(DST, "w", encoding="utf-8", newline="").write(html.replace("</body>", BACK))
print("GBK synced: %s (%.2f MB) -> %s (%.2f MB)" % (
    SRC, os.path.getsize(SRC) / 1048576, DST, os.path.getsize(DST) / 1048576))
