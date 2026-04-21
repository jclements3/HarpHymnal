#!/usr/bin/env python3
"""Generate per-hymn static variation pages that work over file:// URLs.

Takes `jazz/variations.html` as a template, clones it to
`jazz/variations.<slug>.html` per hymn with a JSON data block inlined so
no `fetch()` is needed at view time.

The original `variations.html` stays as the HTTP-served version — when
opened via a server, it falls back to fetching `data/reharm/catalog.json`
and the per-variation JSON. The per-hymn static pages skip both fetches.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = ROOT / "data" / "reharm" / "catalog.json"
VARIATIONS_DIR = ROOT / "data" / "reharm" / "variations"
TEMPLATE_PATH = ROOT / "jazz" / "variations.html"
OUT_DIR = ROOT / "jazz"


def build_page(slug: str, hymn_catalog: dict, template: str, shared: dict) -> str:
    """Return HTML for jazz/variations.<slug>.html with data inlined."""
    preloaded_vs: dict[str, dict] = {}
    vdir = VARIATIONS_DIR / slug
    if vdir.is_dir():
        for vf in sorted(vdir.glob("v*.json")):
            if "manifest" in vf.name:
                continue
            try:
                preloaded_vs[vf.stem] = json.loads(vf.read_text())
            except Exception:
                pass

    mini_catalog = {
        "version": shared["version"],
        "tactic_name_table": shared["tactic_name_table"],
        "dimension_order": shared["dimension_order"],
        "tactic_index_flat_stride": shared.get("tactic_index_flat_stride", 3),
        "hymns": {slug: hymn_catalog},
    }
    preloaded = {"catalog": mini_catalog, "variations": preloaded_vs}
    data_block = (
        '<script id="PRELOADED_REHARM" type="application/json">\n'
        + json.dumps(preloaded, separators=(",", ":"))
        + '\n</script>\n'
    )
    return template.replace("</head>", data_block + "</head>")


def main() -> None:
    catalog = json.loads(CATALOG_PATH.read_text())
    template = TEMPLATE_PATH.read_text()
    shared = {
        "version": catalog.get("version"),
        "tactic_name_table": catalog.get("tactic_name_table", []),
        "dimension_order": catalog.get("dimension_order", []),
        "tactic_index_flat_stride": catalog.get("tactic_index_flat_stride", 3),
    }
    count = 0
    for slug, hymn_catalog in catalog.get("hymns", {}).items():
        out_path = OUT_DIR / f"variations.{slug}.html"
        out_path.write_text(build_page(slug, hymn_catalog, template, shared))
        count += 1
    print(f"wrote {count} per-hymn variation pages to {OUT_DIR}")


if __name__ == "__main__":
    main()
