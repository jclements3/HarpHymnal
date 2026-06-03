"""Build the Jazz Hymnal: arrange every hymn (Somerset LH x Larsen licks) and
render to SVG with abcm2ps -g, matching the reharm/retab pipeline. Writes:
  tablet_app/app/src/main/assets/jazz/hymns/<slug>.svg
  tablet_app/app/src/main/assets/jazz/jazz_hymns.js   (manifest for the hub tile)
"""
import json, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from jazz.arrange import arrange
ASSETS = os.path.join(os.path.dirname(HERE), "tablet_app", "app", "src", "main", "assets")
HYMN_JSON = os.path.join(os.path.dirname(HERE), "data", "hymns")
REHARM_JS = os.path.join(ASSETS, "reharm", "reharm_hymns.js")
OUT_SVG = os.path.join(ASSETS, "jazz", "hymns")
os.makedirs(OUT_SVG, exist_ok=True)

def add_viewbox(svg):
    m = re.search(r'<svg[^>]*width="([\d.]+)px"\s+height="([\d.]+)px"', svg)
    if not m or 'viewBox=' in svg: return svg
    w, h = m.group(1), m.group(2)
    return svg.replace('<svg', '<svg viewBox="0 0 %s %s"' % (w, h), 1)

# hymn list (+ numbering) from the reharm manifest, for consistency across tiles
rj = open(REHARM_JS, encoding="utf-8").read()
REHARM = json.loads(rj[rj.index('['):rj.rindex(']')+1])

manifest, ok, fail = [], 0, 0
for rec in REHARM:
    slug = rec["slug"]
    jpath = os.path.join(HYMN_JSON, slug + ".json")
    if not os.path.exists(jpath):
        fail += 1; print("  MISSING json", slug); continue
    try:
        abc = arrange(jpath)
        with tempfile.TemporaryDirectory() as td:
            ap = os.path.join(td, "a.abc"); open(ap, "w").write(abc)
            pre = os.path.join(td, slug)
            subprocess.run(["abcm2ps", ap, "-g", "-O", pre], check=True,
                           capture_output=True, text=True)
            svgs = sorted(__import__("glob").glob(pre + "[0-9][0-9][0-9].svg"))
            if not svgs: raise RuntimeError("no svg")
            txt = add_viewbox(open(svgs[0], encoding="utf-8").read())
            open(os.path.join(OUT_SVG, slug + ".svg"), "w", encoding="utf-8").write(txt)
        manifest.append({"slug": slug, "num": rec["num"], "title": rec["title"],
                         "key": rec["key"], "meter": rec["meter"], "bars": rec["bars"],
                         "svgs": {"1": "jazz/hymns/%s.svg" % slug}, "pages": 1})
        ok += 1
    except Exception as e:
        fail += 1; print("  FAIL", slug, str(e)[:90])

open(os.path.join(ASSETS, "jazz", "jazz_hymns.js"), "w", encoding="utf-8").write(
    "window.JAZZ_HYMNS = " + json.dumps(manifest) + ";\n")
print("\nbuilt %d / %d hymns | failures %d | manifest -> jazz/jazz_hymns.js" %
      (ok, ok + fail, fail))
