"""Build the Jazz Hymnal: arrange every hymn (Somerset LH x Larsen licks) and
render to SVG through the abcjsharp FORK (harp grand-staff stems: V:1 up, V:2 down)
so it matches the rest of the harp apps instead of looking like an abcm2ps "PDF".
Writes:
  tablet_app/app/src/main/assets/jazz/hymns/<slug>.svg
  tablet_app/app/src/main/assets/jazz/jazz_hymns.js   (manifest for the hub tile)
"""
import json, os, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from jazz.arrange import arrange, pick_bpl, KERN
ASSETS = os.path.join(os.path.dirname(HERE), "tablet_app", "app", "src", "main", "assets")
HYMN_JSON = os.path.join(os.path.dirname(HERE), "data", "hymns")
REHARM_JS = os.path.join(ASSETS, "reharm", "reharm_hymns.js")
OUT_SVG = os.path.join(ASSETS, "jazz", "hymns")
FORK_RENDER = os.path.join(HERE, "fork_render.js")
JSDOM_MODULES = os.path.join(os.path.expanduser("~"), "projects", "hymnal", "node_modules")
os.makedirs(OUT_SVG, exist_ok=True)

# hymn list (+ numbering) from the reharm manifest, for consistency across tiles
rj = open(REHARM_JS, encoding="utf-8").read()
REHARM = json.loads(rj[rj.index('['):rj.rindex(']')+1])

manifest, items, miss = [], [], 0
for rec in REHARM:
    slug = rec["slug"]
    jpath = os.path.join(HYMN_JSON, slug + ".json")
    if not os.path.exists(jpath):
        miss += 1; print("  MISSING json", slug); continue
    nb = len(json.load(open(jpath))["bars"])
    bpl = pick_bpl(nb)
    items.append({"slug": slug, "abc": arrange(jpath, bpl=bpl), "staffwidth": bpl * KERN})
    manifest.append({"slug": slug, "num": rec["num"], "title": rec["title"],
                     "key": rec["key"], "meter": rec["meter"], "bars": rec["bars"],
                     "svgs": {"1": "jazz/hymns/%s.svg" % slug}, "pages": 1})

# one node process renders every ABC through the fork
with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as jf:
    json.dump({"outdir": OUT_SVG, "items": items}, jf)
    job = jf.name
env = dict(os.environ, NODE_PATH=JSDOM_MODULES)
res = subprocess.run(["node", FORK_RENDER, job], capture_output=True, text=True, env=env)
os.unlink(job)
if res.returncode != 0:
    print("node render failed:\n", res.stderr[-2000:]); sys.exit(1)
report = json.loads(res.stdout.strip().splitlines()[-1])
ok = report["ok"]; fail = report["fail"]

# keep the manifest to only the hymns that actually rendered
rendered = {it["slug"] for it in items} - {f.split(":")[0] for f in fail}
manifest = [m for m in manifest if m["slug"] in rendered]
open(os.path.join(ASSETS, "jazz", "jazz_hymns.js"), "w", encoding="utf-8").write(
    "window.JAZZ_HYMNS = " + json.dumps(manifest) + ";\n")

print("\nbuilt %d / %d hymns | render failures %d | missing json %d | manifest -> jazz/jazz_hymns.js"
      % (ok, len(items), len(fail), miss))
for f in fail[:10]:
    print("  FAIL", f[:100])
