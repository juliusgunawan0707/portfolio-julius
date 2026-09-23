# -*- coding: utf-8 -*-
"""
Render the ORACLE architecture diagram and add the back link to the portfolio.

The diagram is the proof behind Services 01 "Multi-Agent Systems": ORACLE
itself is private, so the page shows how it is wired, never its data (no bot
name, token, chat ID or portfolio figures - keep it that way when editing).

    python tools/build_oracle.py
    git add work/oracle && git commit -m "Rebuild ORACLE diagram" && git push

Edit work/oracle/oracle.architecture.json, not index.html: this script
re-renders the page with the archify skill (showcase quality gate) and then
re-injects the back link, so hand edits to index.html are lost.
"""
import io
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DIR = os.path.normpath(os.path.join(HERE, "..", "work", "oracle"))
SPEC = os.path.join(DIR, "oracle.architecture.json")
OUT = os.path.join(DIR, "index.html")
ARCHIFY = os.path.join(os.path.expanduser("~"), ".claude", "skills", "archify", "bin", "archify.mjs")

# The archify page gives every <svg> a min-width (the back arrow came
# out 109px wide), so the arrow overrides are !important.
BACK = """<a id="back-to-porto" href="../../" aria-label="Back to Julius Gunawan's site"><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M19 12H5M11 18l-6-6 6-6"/></svg>Julius Gunawan</a>
<style>
#back-to-porto{position:fixed;left:14px;bottom:14px;z-index:9999;display:inline-flex;align-items:center;gap:8px;padding:8px 14px;border-radius:12px;border:1px solid rgba(255,255,255,.18);background:rgba(10,10,10,.72);-webkit-backdrop-filter:blur(6px);backdrop-filter:blur(6px);color:rgba(255,255,255,.85);font:500 12px/1 system-ui,-apple-system,"Segoe UI",sans-serif;letter-spacing:.02em;text-decoration:none;transition:color .2s,border-color .2s,background .2s}
#back-to-porto:hover{color:#fff;border-color:rgba(255,255,255,.4);background:rgba(10,10,10,.88)}
#back-to-porto svg{display:block!important;flex:none!important;width:13px!important;height:13px!important;margin:0!important;max-width:none!important;min-width:0!important;position:static!important}
#back-to-porto{width:auto;height:auto;white-space:nowrap;box-sizing:border-box}
@media (max-width:640px){#back-to-porto{padding:7px 10px;font-size:11px}}
</style>
</body>"""

r = subprocess.run(["node", ARCHIFY, "deliver", "architecture", SPEC, OUT, "--quality", "showcase", "--json"],
                   capture_output=True, text=True, encoding="utf-8")
try:
    receipt = json.loads(r.stdout)
except ValueError:
    sys.exit("ABORT: archify gave no receipt:\n%s%s" % (r.stdout, r.stderr))
if r.returncode != 0 or not receipt.get("ok"):
    sys.exit("ABORT: archify rejected the diagram:\n%s" % receipt.get("error", r.stdout))
v = receipt["validation"]
print("archify: %d/%d checks, %s, %d errors, %d warnings" % (
    v["checksPassed"], v["checkCount"], v["compositionStatus"], v["errors"], v["warnings"]))

html = io.open(OUT, encoding="utf-8").read()
if html.count("</body>") != 1:
    sys.exit("ABORT: expected exactly one </body> in %s" % OUT)
io.open(OUT, "w", encoding="utf-8", newline="").write(html.replace("</body>", BACK))
print("ORACLE diagram: %s (%.0f KB)" % (OUT, os.path.getsize(OUT) / 1024))
