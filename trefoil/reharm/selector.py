"""Per-measure reharm-tactic selector (Phase 4).

Given a hymn JSON (``data/hymns/<slug>.json``), a seed, a tactic-pool spec
(``data/reharm/tactics.json`` via :class:`TacticsSpec`), and a shape library
(``data/reharm/shape_library.json``), this module emits a per-variation
manifest: one tactic tuple per bar plus the chosen shape and its voicing.

The selector is **layered**: it picks tactics one dimension at a time in
the natural pick order (substitution → shape → register → density →
texture → activities → connections → lever → range → phrase_role), using
:func:`trefoil.reharm.schema.legal_completions` to keep every pick
pairwise-compatible with prior picks.  Within the legal subset per
dimension, picks are weighted inversely to the variation's rolling
coverage count (coverage-targeted bias), and shapes are additionally
weighted by voice-leading proximity to the previous bar's top/bass.

CLI entry point::

    python3 -m trefoil.reharm.selector amazing_grace \
        --n 40 --out data/reharm/variations/amazing_grace/

No third-party deps (stdlib ``json``, ``random``, ``hashlib``).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import sys
from pathlib import Path
from typing import Iterable, Optional

# Package-relative imports (module is runnable as ``python3 -m trefoil.reharm.selector``)
try:
    from trefoil.reharm.schema import (
        TacticsSpec,
        Tactic,
        compatibility,
        legal_completions,
    )
    from trefoil.reharm.state import HarpistState
except ImportError:  # pragma: no cover — when run as script without -m
    here = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(here))
    from trefoil.reharm.schema import (  # type: ignore
        TacticsSpec,
        Tactic,
        compatibility,
        legal_completions,
    )
    from trefoil.reharm.state import HarpistState  # type: ignore


REPO_ROOT = Path(__file__).resolve().parent.parent.parent


# --------------------------------------------------------------------------- #
# Mode + roman-numeral translation                                            #
# --------------------------------------------------------------------------- #
#
# Per REHARM_TACTICS Decision 5: minor-key hymns are treated modally
# (Aeolian default, optional Dorian).  Their chord romans translate to the
# relative-Ionian frame so the shape library (labeled I/ii/iii/IV/V/vi/vii°)
# can be queried without expansion.

MODE_TO_IONIAN: dict[str, dict[str, str]] = {
    "ionian": {
        "I": "I", "ii": "ii", "iii": "iii", "IV": "IV",
        "V": "V", "vi": "vi", "vii°": "vii°", "vii○": "vii°",
    },
    "aeolian": {
        # Canonical Aeolian vocabulary → Ionian-rel.
        "i":    "vi",
        "ii°":  "vii°",  "ii○": "vii°",
        "III":  "I",
        "iv":   "ii",
        "v":    "iii",
        # Harmonic-minor V/V7 show up in the parsed hymns' chord data;
        # under modal treatment we drop the raised 7 and read them as
        # modal v → Ionian-rel iii.
        "V":    "iii",
        "♭VI":  "IV",  "bVI": "IV",  "VI": "IV",
        "♭VII": "V",   "bVII": "V",  "VII": "V",
        # Major I inside an Aeolian hymn (rare; picardy third) — treat
        # as III → I so it's at least looked up.
        "I":    "III",
    },
    "dorian": {
        "i":    "ii",
        "ii":   "iii",
        "♭III": "IV",  "bIII": "IV",  "III": "IV",
        "IV":   "V",
        "v":    "vi",
        "V":    "vi",  # modal v under Dorian
        "vi°":  "vii°",  "vi○": "vii°",  "vi":   "vii°",
        "♭VII": "I",   "bVII": "I",  "VII":  "I",
    },
}

# Shape library uses U+00B0 DEGREE SIGN; hymn data sometimes carries
# U+25CB WHITE CIRCLE or U+266F etc.  Normalise to the library form.
_NUMERAL_NORMALISE = {
    "○": "°",
    "o": "°",
}


def _normalise_numeral(n: str) -> str:
    if not n:
        return n
    for src, dst in _NUMERAL_NORMALISE.items():
        n = n.replace(src, dst)
    return n


def pick_mode(hymn_json: dict, overrides_json: dict) -> str:
    """Return one of ``"ionian"``, ``"aeolian"``, ``"dorian"`` for the hymn.

    Rules:

    * major hymn → ``"ionian"``
    * minor hymn → ``"aeolian"`` unless the slug appears in
      ``overrides_json["overrides"]`` with value ``"dorian"``.

    The hymn slug is not carried in the hymn JSON itself, so callers pass
    the already-resolved override dict for one hymn (or the full file with
    the slug pre-applied).  ``overrides_json`` can be either::

        {"overrides": {"slug": "dorian", ...}}    # full overrides file
        {"_resolved": "dorian"}                   # pre-applied override

    The second form is what ``select_variation`` uses after it knows the
    slug; the first form is what the overrides file on disk looks like.
    """
    key = hymn_json.get("key") or {}
    mode = (key.get("mode") or "").lower()
    if mode != "minor":
        return "ionian"

    resolved = overrides_json.get("_resolved")
    if resolved in ("aeolian", "dorian"):
        return resolved

    # Unresolved — caller passed the full overrides file but not a slug;
    # default to aeolian.
    return "aeolian"


def translate_roman(roman: str, mode: str) -> str:
    """Translate a roman numeral from ``mode`` into the Ionian-relative frame.

    Strips inversion superscripts (``¹`` / ``²`` / ``³``) before lookup —
    the shape library is keyed on the plain numeral.  Unknown numerals
    fall through unchanged (caller may skip / log).
    """
    if not roman:
        return roman
    clean = roman.rstrip("¹²³⁴⁵⁶⁷")
    clean = _normalise_numeral(clean)
    table = MODE_TO_IONIAN.get(mode, MODE_TO_IONIAN["ionian"])
    return table.get(clean, clean)


# --------------------------------------------------------------------------- #
# Phrase-role inference (Decision 6)                                          #
# --------------------------------------------------------------------------- #

_CADENCE_PAIRS = {
    # (prev_numeral, this_numeral) — recognisable cadential motions
    ("V", "I"),    ("V", "i"),    # authentic
    ("V", "vi"),   ("V", "VI"),   # deceptive
    ("IV", "I"),   ("iv", "i"),   # plagal
}


def _phrase_role_positional(bar_idx_in_phrase: int, phrase_len: int) -> str:
    """Positional default: first / last / cadence_approach / middle."""
    if phrase_len <= 1:
        return "phrase_role.cadence"  # degenerate single-bar phrase
    if bar_idx_in_phrase == 0:
        return "phrase_role.opening"
    if bar_idx_in_phrase == phrase_len - 1:
        return "phrase_role.cadence"
    if phrase_len >= 3 and bar_idx_in_phrase == phrase_len - 2:
        return "phrase_role.cadence_approach"
    return "phrase_role.middle"


def infer_phrase_role(
    bar_idx_in_phrase: int,
    phrase_len: int,
    chord_motion: Optional[tuple[str, str]] = None,
    is_phrase_end: bool = False,
) -> str:
    """Hybrid phrase-role inference per REHARM_TACTICS Decision 6.

    Step 1 — positional default.
    Step 2 — chord-motion override: if ``chord_motion`` is one of the
    canonical cadence pairs, this bar is a ``cadence`` (and its
    predecessor was a ``cadence_approach``).  Half-cadences (``X → V``)
    count only at phrase end.
    Step 3 — positional wins when motion is ambiguous (mid-phrase V→V).
    """
    base = _phrase_role_positional(bar_idx_in_phrase, phrase_len)

    if chord_motion is not None:
        prev_n = (chord_motion[0] or "").rstrip("¹²³⁴⁵⁶⁷")
        this_n = (chord_motion[1] or "").rstrip("¹²³⁴⁵⁶⁷")
        # Explicit cadence pair → override to cadence.
        if (prev_n, this_n) in _CADENCE_PAIRS:
            return "phrase_role.cadence"
        # Half-cadence only at phrase end.
        if is_phrase_end and this_n == "V":
            return "phrase_role.cadence"

    return base


# --------------------------------------------------------------------------- #
# Coverage-targeted weighted random                                           #
# --------------------------------------------------------------------------- #

def _coverage_weights(
    candidates: Iterable[Tactic], coverage: dict[str, int]
) -> list[float]:
    """Weight = 1 / (1 + count).  Less-covered tactics get bigger weight."""
    return [1.0 / (1.0 + coverage.get(t.id, 0)) for t in candidates]


def _weighted_choice(rng: random.Random, items: list, weights: list[float]):
    if not items:
        return None
    total = sum(weights)
    if total <= 0:
        return rng.choice(items)
    r = rng.random() * total
    acc = 0.0
    for item, w in zip(items, weights):
        acc += w
        if r <= acc:
            return item
    return items[-1]


# --------------------------------------------------------------------------- #
# String index helper (matches shape_gen's formula)                           #
# --------------------------------------------------------------------------- #

def _string_index(note: tuple[int, int]) -> int:
    deg, oct_ = note
    return (oct_ - 1) * 7 + (deg - 1) + 1


def _voice_lead_proximity(
    shape: dict, prev_top: Optional[tuple[int, int]], prev_bass: Optional[tuple[int, int]]
) -> float:
    """Smaller distance → higher weight.  Returns weight in (0, 1].

    Distance is the sum of absolute string-index gaps for top and bass.
    No previous voicing → uniform weight.
    """
    if prev_top is None and prev_bass is None:
        return 1.0

    top = tuple(shape.get("top") or [])
    bass = tuple(shape.get("bass") or [])
    dist = 0
    if prev_top and len(top) == 2:
        dist += abs(_string_index(top) - _string_index(prev_top))
    if prev_bass and len(bass) == 2:
        dist += abs(_string_index(bass) - _string_index(prev_bass))
    return 1.0 / (1.0 + dist)


# --------------------------------------------------------------------------- #
# Shape-library index                                                         #
# --------------------------------------------------------------------------- #

def _build_shape_index(shape_library: dict) -> dict[tuple[str, str], list[dict]]:
    """Index shapes by (numeral, quality_str) for fast lookup."""
    idx: dict[tuple[str, str], list[dict]] = {}
    for s in shape_library.get("shapes", []):
        ch = s.get("chord") or {}
        numeral = _normalise_numeral(ch.get("numeral", ""))
        q = ch.get("quality") or ""
        idx.setdefault((numeral, q), []).append(s)
    return idx


def _lookup_shapes(
    shape_index: dict, numeral: str, quality: Optional[str]
) -> list[dict]:
    """Fallback chain: exact (n, q) → (n, '') → (n, '7') → []."""
    q = quality or ""
    for cand_q in (q, "", "7", "Δ"):
        shapes = shape_index.get((numeral, cand_q))
        if shapes:
            return shapes
    return []


# --------------------------------------------------------------------------- #
# Per-dimension legal pick                                                    #
# --------------------------------------------------------------------------- #

def _pick_dim(
    spec: TacticsSpec,
    chosen: set[str],
    dimension: str,
    coverage: dict[str, int],
    rng: random.Random,
    exclude_derived: bool = True,
    force: Optional[str] = None,
) -> Optional[str]:
    """Pick one tactic from ``dimension`` that's legal given ``chosen``.

    * ``force=<tactic_id>`` — bypass weighted pick when a rule demands it
      (e.g. ``lh_activity.none`` whenever ``shape.no_lh`` was chosen).
    * ``exclude_derived=True`` — skip ``derived_from`` tactics from the
      weighted pool; they're picked only by explicit ``force=``.
    """
    if force is not None:
        if force in spec.tactic_index() and compatibility(spec, chosen | {force}):
            return force
        # fall through to normal pick if the forced id is invalid

    cands = legal_completions(spec, chosen, dimension)
    if exclude_derived:
        cands = [t for t in cands if t.derived_from is None]
    if not cands:
        # Fall back: include derived tactics.
        cands = legal_completions(spec, chosen, dimension)
    if not cands:
        return None
    weights = _coverage_weights(cands, coverage)
    chosen_tactic = _weighted_choice(rng, cands, weights)
    return chosen_tactic.id if chosen_tactic else None


# --------------------------------------------------------------------------- #
# Per-measure selection                                                       #
# --------------------------------------------------------------------------- #

def select_measure(
    bar: dict,
    state: HarpistState,
    spec: TacticsSpec,
    shape_index: dict,
    rng: random.Random,
    mode: str,
    next_bar: Optional[dict] = None,
    is_phrase_end: bool = False,
) -> dict:
    """Pick tactics + shape for one bar, return the per-bar manifest entry.

    See module docstring + REHARM_TACTICS "Compatibility model" for the
    layered pick order.  Returns::

        {
          "bar": <1-indexed>,
          "tactic_manifest": {dim: tactic_id, ...},
          "shape_id": <str>,
          "lh": [[deg, oct], ...],
          "rh": [[deg, oct], ...],
          "bass": [deg, oct],
          "top": [deg, oct],
          "gap": <int>,
          "chord_used": {"numeral": ..., "quality": ..., "translated": ...},
        }
    """
    chord = bar.get("chord") or {}
    raw_numeral = chord.get("numeral") or ""
    quality = chord.get("quality")

    # Translate to Ionian-rel for shape lookup.
    translated = translate_roman(raw_numeral, mode)

    chosen: set[str] = set()
    manifest: dict[str, str] = {}

    def _set(dim: str, tid: Optional[str]) -> None:
        if tid is not None:
            chosen.add(tid)
            manifest[dim] = tid

    # 1. substitution (default as_written, coverage-weighted over alternatives)
    _set("substitution", _pick_dim(spec, chosen, "substitution",
                                   state.coverage, rng))

    # 2. shape — restrict to shape tactics that actually have shapes in the
    #    library for this chord.  The current library (Phase 3, 1680 shapes)
    #    only supports shape.full_4, shape.three_finger, shape.root_10; other
    #    shape.* tactics are coverage-selectable at the spec level but have
    #    no instantiable voicing yet, so picking them silently falls back to
    #    a generic triad.  We filter here so each bar's shape pick is
    #    actually representable.
    available_shapes = _lookup_shapes(shape_index, translated, quality)
    supported_shape_ids: set[str] = set()
    for sh in available_shapes:
        for sup in sh.get("supports") or []:
            supported_shape_ids.add(sup)
    shape_cands_all = legal_completions(spec, chosen, "shape")
    shape_cands = [
        t for t in shape_cands_all
        if t.derived_from is None and t.id in supported_shape_ids
    ]
    if not shape_cands:
        # nothing in the library matches — fall back to the full legal set
        # so the manifest still records something.
        shape_cands = [t for t in shape_cands_all if t.derived_from is None]
    if shape_cands:
        w = _coverage_weights(shape_cands, state.coverage)
        shape_pick = _weighted_choice(rng, shape_cands, w)
        _set("shape", shape_pick.id if shape_pick else None)

    # 3. register (voice-leading aware via prev_top/prev_bass; here we only
    #    restrict when the last bar was very high/low so register.down_oct
    #    or up_oct doesn't pile on; the weighting is handled by coverage).
    _set("register", _pick_dim(spec, chosen, "register", state.coverage, rng))

    # 4. density + texture
    _set("density", _pick_dim(spec, chosen, "density", state.coverage, rng))
    _set("texture", _pick_dim(spec, chosen, "texture", state.coverage, rng))

    # 5. lh_activity + rh_activity.  If shape.no_lh was picked, force
    #    lh_activity.none.
    if "shape.no_lh" in chosen:
        _set("lh_activity", _pick_dim(spec, chosen, "lh_activity",
                                      state.coverage, rng,
                                      exclude_derived=False,
                                      force="lh_activity.none"))
    else:
        _set("lh_activity", _pick_dim(spec, chosen, "lh_activity",
                                      state.coverage, rng))
    _set("rh_activity", _pick_dim(spec, chosen, "rh_activity",
                                  state.coverage, rng))

    # 6. connect_from — state-aware: same shape ⇒ same; otherwise step/third/larger.
    cf_force: Optional[str] = None
    if state.prev_shape_id is None:
        cf_force = "connect_from.released"
    elif state.prev_top is not None:
        # Leave the direction to weighted pick; override only in the
        # "same shape repeated" case where nothing moved.
        pass
    _set("connect_from", _pick_dim(spec, chosen, "connect_from",
                                   state.coverage, rng, force=cf_force))

    # 7. connect_to — state-aware on next_bar; default land_down when no next
    ct_force: Optional[str] = None
    if next_bar is None:
        ct_force = "connect_to.land_down"
    _set("connect_to", _pick_dim(spec, chosen, "connect_to",
                                 state.coverage, rng, force=ct_force))

    # 8. lever — modal treatment: always no_flip unless something else forces
    #    a flip (we don't introduce flip tactics in the baseline).
    _set("lever", _pick_dim(spec, chosen, "lever", state.coverage, rng,
                            force="lever.no_flip"))

    # 9. range
    _set("range", _pick_dim(spec, chosen, "range", state.coverage, rng))

    # 10. phrase_role — from infer_phrase_role.
    prev_chord_numeral = None
    if state.bar_num > 1:
        # We don't have the previous bar's numeral cached; selector is
        # called in order, so the caller passes next_bar; for
        # prev-chord we stash it in state via prev_numeral (added below).
        prev_chord_numeral = getattr(state, "_prev_numeral", None)
    motion = (prev_chord_numeral, raw_numeral) if prev_chord_numeral else None
    role = infer_phrase_role(state.phrase_bar_idx, state.phrase_len,
                             chord_motion=motion, is_phrase_end=is_phrase_end)
    # phrase_role is positionally derived, not coverage-weighted.
    if compatibility(spec, chosen | {role}):
        manifest["phrase_role"] = role
        chosen.add(role)
    else:
        fallback = _pick_dim(spec, chosen, "phrase_role", state.coverage, rng)
        if fallback:
            manifest["phrase_role"] = fallback
            chosen.add(fallback)

    # --- Shape pick from the library ------------------------------------ #
    shapes = _lookup_shapes(shape_index, translated, quality)
    # Filter by the chosen shape.* tactic when possible.
    shape_tactic = manifest.get("shape")
    if shape_tactic:
        filtered = [s for s in shapes if shape_tactic in (s.get("supports") or [])]
        if filtered:
            shapes = filtered
    if not shapes:
        # Last-ditch: any shape that matches the chord; otherwise synthesise.
        shapes = _lookup_shapes(shape_index, translated, None) or []

    if shapes:
        weights = [
            _voice_lead_proximity(s, state.prev_top, state.prev_bass)
            for s in shapes
        ]
        shape = _weighted_choice(rng, shapes, weights)
    else:
        shape = None

    # Update coverage.
    for tid in chosen:
        state.bump_coverage(tid)

    if shape is None:
        return {
            "bar": state.bar_num,
            "tactic_manifest": manifest,
            "shape_id": None,
            "lh": [],
            "rh": [],
            "bass": None,
            "top": None,
            "gap": None,
            "chord_used": {
                "numeral": raw_numeral,
                "quality": quality,
                "translated": translated,
            },
        }

    return {
        "bar": state.bar_num,
        "tactic_manifest": manifest,
        "shape_id": shape.get("id"),
        "lh": [list(p) for p in (shape.get("lh") or [])],
        "rh": [list(p) for p in (shape.get("rh") or [])],
        "bass": list(shape.get("bass") or []),
        "top": list(shape.get("top") or []),
        "gap": shape.get("gap"),
        "chord_used": {
            "numeral": raw_numeral,
            "quality": quality,
            "translated": translated,
        },
    }


# --------------------------------------------------------------------------- #
# Per-variation driver                                                        #
# --------------------------------------------------------------------------- #

def _phrase_map(hymn_json: dict) -> dict[int, tuple[int, int, int, bool]]:
    """Map 1-indexed bar_num → (phrase_idx, bar_idx_in_phrase, phrase_len, is_last).

    Hymns whose phrases don't cover every bar (rare) get a synthetic
    catch-all phrase for the unmapped tail.
    """
    out: dict[int, tuple[int, int, int, bool]] = {}
    n_bars = len(hymn_json.get("bars") or [])
    phrases = hymn_json.get("phrases") or []
    covered: set[int] = set()
    for pi, p in enumerate(phrases):
        ibars = p.get("ibars") or []
        plen = len(ibars)
        for j, b in enumerate(ibars):
            out[b] = (pi, j, plen, j == plen - 1)
            covered.add(b)
    # Fallback: uncovered bars become a trailing pseudo-phrase.
    uncovered = [b for b in range(1, n_bars + 1) if b not in covered]
    if uncovered:
        fallback_pi = len(phrases)
        plen = len(uncovered)
        for j, b in enumerate(uncovered):
            out[b] = (fallback_pi, j, plen, j == plen - 1)
    return out


def select_variation(
    hymn_json: dict,
    seed: int,
    spec: TacticsSpec,
    shape_library: dict,
    overrides: dict,
    tactics_hash: Optional[str] = None,
    coverage: Optional[dict[str, int]] = None,
) -> dict:
    """Run :func:`select_measure` across all bars of ``hymn_json``.

    ``coverage`` is optional; pass a shared dict across multiple variations
    to bias all of them jointly toward under-covered tactics.  The caller
    owns the dict — this function mutates it in place.
    """
    rng = random.Random(seed)
    mode = pick_mode(hymn_json, overrides)
    state = HarpistState.initial(hymn_json, mode)
    if coverage is not None:
        state.coverage = coverage

    shape_index = _build_shape_index(shape_library)
    phrase_map = _phrase_map(hymn_json)

    bars = hymn_json.get("bars") or []
    out_bars: list[dict] = []

    for i, bar in enumerate(bars):
        bar_num = i + 1
        state.bar_num = bar_num
        pi, bj, plen, is_end = phrase_map.get(bar_num, (0, 0, 1, True))
        state.phrase_idx = pi
        state.phrase_bar_idx = bj
        state.phrase_len = plen

        next_bar = bars[i + 1] if (i + 1) < len(bars) else None
        entry = select_measure(
            bar, state, spec, shape_index, rng, mode,
            next_bar=next_bar, is_phrase_end=is_end,
        )
        out_bars.append(entry)

        # Update state for the next iteration.
        state.prev_lh = [tuple(p) for p in entry.get("lh") or []]
        state.prev_rh = [tuple(p) for p in entry.get("rh") or []]
        state.prev_bass = (
            tuple(entry["bass"]) if entry.get("bass") else None
        )
        state.prev_top = (
            tuple(entry["top"]) if entry.get("top") else None
        )
        state.prev_shape_id = entry.get("shape_id")
        # Rolling stats (proxy values — density = attack count; spread =
        # octave-count of the voicing).
        attacks = len(state.prev_lh) + len(state.prev_rh)
        state.push_density(attacks)
        all_octs = [p[1] for p in state.prev_lh + state.prev_rh]
        spread = (max(all_octs) - min(all_octs)) if all_octs else 0
        state.push_spread(spread)
        # Save the raw numeral for next bar's motion inference.
        state._prev_numeral = (bar.get("chord") or {}).get("numeral")

    return {
        "seed": seed,
        "mode": mode,
        "key": hymn_json.get("key"),
        "title": hymn_json.get("title"),
        "tactics_hash": tactics_hash,
        "bars": out_bars,
        "tactic_coverage": dict(state.coverage),
    }


# --------------------------------------------------------------------------- #
# Batch driver                                                                #
# --------------------------------------------------------------------------- #

def _slug_override(overrides_json: dict, slug: str) -> dict:
    """Extract the override for one slug; return a ``_resolved`` wrapper."""
    ov = (overrides_json.get("overrides") or {})
    resolved = ov.get(slug)
    if resolved in ("aeolian", "dorian"):
        return {"_resolved": resolved}
    return {}


def _tactics_hash(tactics_path: Path) -> str:
    return hashlib.sha256(tactics_path.read_bytes()).hexdigest()


def generate_variations(
    hymn_slug: str,
    n_variations: int = 40,
    tactics_path: Optional[Path] = None,
    shape_library_path: Optional[Path] = None,
    overrides_path: Optional[Path] = None,
    hymns_dir: Optional[Path] = None,
) -> list[dict]:
    """Generate ``n_variations`` seeded manifests for one hymn.

    Uses a shared coverage dict across all N so under-covered tactics
    rise in priority within the batch.  Each variation's seed is
    ``hash(slug) ^ i`` so repeat runs are deterministic.
    """
    tactics_path = tactics_path or (REPO_ROOT / "data" / "reharm" / "tactics.json")
    shape_library_path = shape_library_path or (
        REPO_ROOT / "data" / "reharm" / "shape_library.json"
    )
    overrides_path = overrides_path or (
        REPO_ROOT / "data" / "reharm" / "mode_overrides.json"
    )
    hymns_dir = hymns_dir or (REPO_ROOT / "data" / "hymns")

    spec = TacticsSpec.load(tactics_path)
    shape_library = json.loads(shape_library_path.read_text())
    overrides_raw = json.loads(overrides_path.read_text())
    overrides = _slug_override(overrides_raw, hymn_slug)

    hymn = json.loads((hymns_dir / f"{hymn_slug}.json").read_text())

    t_hash = _tactics_hash(tactics_path)

    # Deterministic per-slug base seed.
    base = int(hashlib.sha256(hymn_slug.encode()).hexdigest(), 16) & 0xFFFF_FFFF
    shared_coverage: dict[str, int] = {}

    variations: list[dict] = []
    for i in range(n_variations):
        seed = (base + i) & 0xFFFF_FFFF
        var = select_variation(
            hymn, seed, spec, shape_library, overrides,
            tactics_hash=t_hash, coverage=shared_coverage,
        )
        var["slug"] = hymn_slug
        var["variation_index"] = i + 1
        variations.append(var)
    return variations


# --------------------------------------------------------------------------- #
# CLI                                                                         #
# --------------------------------------------------------------------------- #

def _write_variations(
    variations: list[dict], out_dir: Path
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for i, var in enumerate(variations, start=1):
        fpath = out_dir / f"v{i:02d}.json"
        fpath.write_text(json.dumps(var, indent=2, ensure_ascii=False))


def _needs_rebuild(out_dir: Path, n_variations: int, t_hash: str) -> bool:
    """Return True when a full rebuild is needed for this slug.

    A rebuild is skipped when every ``v01..vNN.json`` exists and each file's
    ``tactics_hash`` matches the current tactics-pool hash.  Any mismatch or
    missing file forces a full rebuild.
    """
    for i in range(1, n_variations + 1):
        fpath = out_dir / f"v{i:02d}.json"
        if not fpath.exists():
            return True
        try:
            existing = json.loads(fpath.read_text())
        except Exception:
            return True
        if existing.get("tactics_hash") != t_hash:
            return True
    return False


def _generate_one(args: tuple[str, int, Path]) -> tuple[str, str, int]:
    """Worker entry for :class:`multiprocessing.Pool`.

    Returns ``(slug, status, n_written)`` where status is one of
    ``"ok"``, ``"skipped"``, or ``"error: <msg>"``.
    """
    slug, n_variations, out_root = args
    out_dir = out_root / slug

    # Determine current tactics hash once per worker.
    tactics_path = REPO_ROOT / "data" / "reharm" / "tactics.json"
    try:
        t_hash = _tactics_hash(tactics_path)
    except Exception as exc:  # pragma: no cover
        return (slug, f"error: tactics_hash: {exc}", 0)

    if out_dir.exists() and not _needs_rebuild(out_dir, n_variations, t_hash):
        return (slug, "skipped", 0)

    try:
        variations = generate_variations(slug, n_variations=n_variations)
    except Exception as exc:
        return (slug, f"error: {type(exc).__name__}: {exc}", 0)

    try:
        _write_variations(variations, out_dir)
    except Exception as exc:
        return (slug, f"error: write: {exc}", 0)

    return (slug, "ok", len(variations))


def _run_all(
    n_variations: int,
    workers: Optional[int] = None,
    hymns_dir: Optional[Path] = None,
    out_root: Optional[Path] = None,
) -> int:
    """Bulk-generate variations for every hymn in ``hymns_dir``.

    Multiprocessing by hymn; per-hymn failures are logged and do not halt
    the batch.  Skips hymns whose full set already exists AND whose
    tactics_hash matches.
    """
    import multiprocessing
    import time

    hymns_dir = hymns_dir or (REPO_ROOT / "data" / "hymns")
    out_root = out_root or (REPO_ROOT / "data" / "reharm" / "variations")
    out_root.mkdir(parents=True, exist_ok=True)

    slugs = sorted(p.stem for p in hymns_dir.glob("*.json"))
    if not slugs:
        print(f"error: no hymns found in {hymns_dir}", file=sys.stderr)
        return 2

    if workers is None:
        workers = max(1, multiprocessing.cpu_count())
    tasks = [(s, n_variations, out_root) for s in slugs]

    print(f"generating up to {n_variations} variations for {len(slugs)} hymns "
          f"using {workers} workers")

    t0 = time.time()
    ok = 0
    skipped = 0
    failed: list[tuple[str, str]] = []

    # chunksize=1 because each hymn is relatively balanced in cost.
    with multiprocessing.Pool(processes=workers) as pool:
        for slug, status, _n in pool.imap_unordered(_generate_one, tasks, chunksize=1):
            if status == "ok":
                ok += 1
            elif status == "skipped":
                skipped += 1
            else:
                failed.append((slug, status))

    elapsed = time.time() - t0
    print(f"done in {elapsed:.1f}s  ok={ok}  skipped={skipped}  failed={len(failed)}")
    for slug, err in failed[:20]:
        print(f"  {slug}: {err}")
    if len(failed) > 20:
        print(f"  ... {len(failed) - 20} more")
    return 0 if not failed else 1


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("slug", nargs="?", default=None,
                    help="hymn slug (e.g. amazing_grace); omit with --all")
    ap.add_argument("--all", action="store_true",
                    help="generate variations for every hymn in data/hymns/")
    ap.add_argument("--n", type=int, default=40,
                    help="number of variations to generate (default 40)")
    ap.add_argument("--out", type=str, default=None,
                    help="output dir (default data/reharm/variations/<slug>/)")
    ap.add_argument("--workers", type=int, default=None,
                    help="parallel workers for --all (default: all CPUs)")
    args = ap.parse_args(argv)

    if args.all:
        out_root = Path(args.out) if args.out else None
        return _run_all(
            n_variations=args.n,
            workers=args.workers,
            out_root=out_root,
        )

    if not args.slug:
        ap.error("slug is required unless --all is passed")

    out_dir = Path(args.out) if args.out else (
        REPO_ROOT / "data" / "reharm" / "variations" / args.slug
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    variations = generate_variations(args.slug, n_variations=args.n)
    _write_variations(variations, out_dir)

    print(f"wrote {len(variations)} variations to {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())


__all__ = [
    "MODE_TO_IONIAN",
    "pick_mode",
    "translate_roman",
    "infer_phrase_role",
    "select_measure",
    "select_variation",
    "generate_variations",
]
