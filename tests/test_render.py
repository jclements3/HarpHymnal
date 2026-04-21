"""Phase 7 render tests — MIDI + LilyPond emission from reharm variations.

Runnable as a script (``python3 tests/test_render.py``) or under pytest
(``pytest tests/test_render.py``).  Stdlib only + the render modules.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from trefoil.reharm.render_midi import render_variation_midi
from trefoil.reharm.render_lily import render_variation_lily


AMAZING_GRACE_VARIATION = REPO_ROOT / "data" / "reharm" / "variations" / "amazing_grace" / "v28.json"
AMAZING_GRACE_HYMN = REPO_ROOT / "data" / "hymns" / "amazing_grace.json"


def _load_ag() -> tuple[dict, dict]:
    with AMAZING_GRACE_VARIATION.open("r", encoding="utf-8") as f:
        variation = json.load(f)
    with AMAZING_GRACE_HYMN.open("r", encoding="utf-8") as f:
        hymn = json.load(f)
    return variation, hymn


def _count_note_ons(midi_bytes: bytes) -> int:
    """Scan MIDI data for note-on events (0x9X with non-zero velocity)."""
    # Skip header and MTrk header; crude but sufficient for counting.
    # Find each 0x9X status byte; but status can be running — so we do a
    # conservative scan that treats every 0x90..0x9F byte in the track body
    # as a note-on status marker, then reads pitch+velocity.  For our
    # single-track, non-running-status writer this matches exactly.
    count = 0
    i = 0
    while i < len(midi_bytes) - 2:
        b = midi_bytes[i]
        if 0x90 <= b <= 0x9F:
            velocity = midi_bytes[i + 2]
            if velocity > 0:
                count += 1
            i += 3
        else:
            i += 1
    return count


def test_midi_bytes_valid_header() -> None:
    variation, hymn = _load_ag()
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "v28.mid"
        render_variation_midi(variation, hymn, out)
        data = out.read_bytes()
        assert len(data) > 100, "MIDI file suspiciously small"
        assert data[:4] == b"MThd", f"bad MIDI header magic: {data[:4]!r}"
        # header length field = 6
        assert data[4:8] == b"\x00\x00\x00\x06"
        # should contain at least one MTrk chunk
        assert b"MTrk" in data


def test_lily_syntax_markers() -> None:
    variation, hymn = _load_ag()
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "v28.ly"
        render_variation_lily(variation, hymn, out)
        text = out.read_text(encoding="utf-8")
        assert text.startswith("\\version"), f"bad LilyPond start: {text[:40]!r}"
        assert "\\score" in text, "no \\score block"
        assert text.rstrip().endswith("}"), "unclosed braces"
        assert "\\key" in text
        assert "\\time" in text


def test_density_affects_attack_count() -> None:
    """Two fake variations differing only in density produce different attack counts."""
    variation, hymn = _load_ag()
    # Strip to a 2-bar stub with a single known chord and simple melody,
    # holding everything else constant.
    base_bar = copy.deepcopy(variation["bars"][0])
    # Force every tactic field to simple settings so density is the only
    # rhythmic variable.
    base_bar["tactic_manifest"] = {
        "substitution": "substitution.as_written",
        "shape": "shape.full_4",
        "register": "register.same",
        "density": "density.one_attack",
        "texture": "texture.block",
        "lh_activity": "lh_activity.sustain",
        "rh_activity": "rh_activity.melody_alone",
        "connect_from": "connect_from.released",
        "connect_to": "connect_to.land_down",
        "lever": "lever.no_flip",
        "range": "range.stay",
        "phrase_role": "phrase_role.middle",
    }

    var_one = copy.deepcopy(variation)
    var_one["bars"] = [copy.deepcopy(base_bar), copy.deepcopy(base_bar)]

    var_two = copy.deepcopy(var_one)
    for b in var_two["bars"]:
        b["tactic_manifest"]["density"] = "density.two_per_beat"

    with tempfile.TemporaryDirectory() as td:
        p1 = Path(td) / "one.mid"
        p2 = Path(td) / "two.mid"
        render_variation_midi(var_one, hymn, p1)
        render_variation_midi(var_two, hymn, p2)

        n1 = _count_note_ons(p1.read_bytes())
        n2 = _count_note_ons(p2.read_bytes())
        assert n2 > n1, (
            f"density.two_per_beat should yield more LH attacks than "
            f"density.one_attack (got {n1} vs {n2})"
        )


def test_midi_deterministic() -> None:
    """Same variation → byte-identical MIDI on repeat."""
    variation, hymn = _load_ag()
    with tempfile.TemporaryDirectory() as td:
        p1 = Path(td) / "a.mid"
        p2 = Path(td) / "b.mid"
        render_variation_midi(variation, hymn, p1)
        render_variation_midi(variation, hymn, p2)
        h1 = hashlib.sha256(p1.read_bytes()).hexdigest()
        h2 = hashlib.sha256(p2.read_bytes()).hexdigest()
        assert h1 == h2, f"non-deterministic MIDI: {h1} vs {h2}"


def _run_all() -> int:
    failures = 0
    for fn in (
        test_midi_bytes_valid_header,
        test_lily_syntax_markers,
        test_density_affects_attack_count,
        test_midi_deterministic,
    ):
        try:
            fn()
            print(f"PASS  {fn.__name__}")
        except AssertionError as exc:
            print(f"FAIL  {fn.__name__}: {exc}")
            failures += 1
        except Exception as exc:
            print(f"ERROR {fn.__name__}: {type(exc).__name__}: {exc}")
            failures += 1
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(_run_all())
