"""One-tactic-in-isolation audition rig (pedagogical testing track).

Usage::

    python3 -m cli.reharm_solo --hymn amazing_grace --all

For every tactic in ``data/reharm/tactics.json``, renders a pair of MIDI
snippets (3 bars each) around a spotlight bar:

  * ``<dimension>__<tactic_short_name>__original.mid`` — the plain SATB
    baseline for the snippet window (A side).
  * ``<dimension>__<tactic_short_name>__tactic.mid``   — the same snippet
    with the tactic applied to the middle bar (B side).

Spotlight defaults to bar 5; bar 8 for cadence / phrase_role / connect_to
tactics. The snippet window is ``[spotlight-1, spotlight+1]`` inclusive,
clipped to the piece at edges.

Also emits:
  * ``_baseline.mid`` — the full-hymn SATB chorale (top-of-page control).
  * ``_notes.json``   — tactics with ambiguous single-bar realizations.

Pass ``--no-snippet`` to fall back to the legacy full-hymn-per-tactic
behaviour.

Stdlib only.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from trefoil.reharm.satb_baseline import render_satb_baseline, render_snippet_original
from trefoil.reharm.solo_tactic_demo import render_solo_tactic


_ROOT = Path(__file__).resolve().parents[1]

# Tactics whose effect is cadential; render them at the first cadence bar
# (Amazing Grace's first cadence lands on bar 8).
_CADENCE_DIMS = {"phrase_role"}
_CADENCE_TACTICS = {
    "phrase_role.cadence",
    "phrase_role.cadence_approach",
    "phrase_role.release",
    "connect_to.anticipate",
    "connect_to.delay",
    "connect_to.step_bass",
    "connect_to.common_tone",
    "connect_to.land_down",
}


def _short_name(tactic_id: str) -> str:
    return tactic_id.split(".", 1)[1]


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="Solo-tactic audition MIDI builder")
    ap.add_argument("--hymn", default="amazing_grace",
                    help="hymn slug (default: amazing_grace)")
    ap.add_argument("--all", action="store_true",
                    help="render baseline + every tactic")
    ap.add_argument("--tactic", default=None,
                    help="render a single tactic id (e.g. shape.quartal)")
    ap.add_argument("--spotlight-bar", type=int, default=5,
                    help="default spotlight bar (overridden to 8 for cadence "
                         "tactics)")
    ap.add_argument("--snippet", dest="snippet", action="store_true", default=True,
                    help="emit A/B snippet pairs (default)")
    ap.add_argument("--no-snippet", dest="snippet", action="store_false",
                    help="emit full-hymn per-tactic files (legacy behaviour)")
    ap.add_argument("--snippet-radius", type=int, default=1,
                    help="bars on each side of the spotlight to include "
                         "(default: 1, yielding a 3-bar window)")
    ap.add_argument("--out-dir", default=None,
                    help="override output dir (default: data/reharm/tests/<hymn>/)")
    args = ap.parse_args(argv)

    out_dir = Path(args.out_dir) if args.out_dir else _ROOT / "data" / "reharm" / "tests" / args.hymn
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Baseline (full hymn — always emitted as the top-of-page control).
    baseline_path = out_dir / "_baseline.mid"
    render_satb_baseline(args.hymn, baseline_path)
    print(f"baseline → {baseline_path}")

    tactics = json.loads((_ROOT / "data" / "reharm" / "tactics.json").read_text())
    dim_lookup = {t["id"]: t for t in tactics["tactics"]}

    notes: list[dict] = []

    def render_one(tid: str) -> None:
        t = dim_lookup[tid]
        dim = t["dimension"]
        spotlight = args.spotlight_bar
        if tid in _CADENCE_TACTICS or dim in _CADENCE_DIMS:
            spotlight = 8
        short = _short_name(tid)
        if args.snippet:
            orig_path = out_dir / f"{dim}__{short}__original.mid"
            tact_path = out_dir / f"{dim}__{short}__tactic.mid"
            render_snippet_original(args.hymn, spotlight, orig_path,
                                    snippet_radius=args.snippet_radius)
            _, note = render_solo_tactic(args.hymn, tid, tact_path,
                                         spotlight_bar=spotlight,
                                         snippet_radius=args.snippet_radius)
            msg = f"{tid} → {orig_path.name} + {tact_path.name}"
        else:
            fname = f"{dim}__{short}.mid"
            dest = out_dir / fname
            _, note = render_solo_tactic(args.hymn, tid, dest, spotlight_bar=spotlight)
            msg = f"{tid} → {fname}"
        if note:
            msg += f"  [note: {note}]"
            notes.append({"tactic": tid, "note": note})
        print(msg)

    if args.tactic:
        render_one(args.tactic)
    elif args.all:
        for t in tactics["tactics"]:
            render_one(t["id"])
    else:
        ap.error("pass --all or --tactic <id>")

    # Persist notes
    (out_dir / "_notes.json").write_text(
        json.dumps({"hymn": args.hymn, "ambiguities": notes}, indent=2)
    )
    print(f"\n{len(notes)} ambiguity note(s) saved to _notes.json")


if __name__ == "__main__":
    main()
