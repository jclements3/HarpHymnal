"""Phase 5 — post-hoc legality checks and bias scoring for reharm variations.

Layers on top of the selector output (``data/reharm/variations/<slug>/*.json``)
without modifying the selector itself.  Responsibilities:

* Hard legality: hand-span, string range, bass/top invariants, cross-bar
  reach, lever-flip budgeting, and a belt-and-suspenders re-run of
  :func:`trefoil.reharm.schema.compatibility` per bar.
* Bias scoring: one score per bias declared in ``data/reharm/tactics.json``
  (density_axis, spread_axis, satb_zone_avoidance, expose_extremes), plus a
  weighted ``total_score``.
* Corpus aggregation: pass / warn / fail counts across a directory of
  variation JSONs.

Thresholds and weights are deliberately *conservative defaults* — they're
constants at the top of the module so they're easy to tune without
touching any call site.  Each one carries a comment explaining what it
represents.

Stdlib-only.  The module is importable from both tests and the CLI
(``python -m cli.reharm_legality``).
"""
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Optional

# ---------------------------------------------------------------- #
# Package-relative import with script-mode fallback                #
# ---------------------------------------------------------------- #
try:
    from trefoil.reharm.schema import TacticsSpec, compatibility
except ImportError:  # pragma: no cover
    here = Path(__file__).resolve().parent.parent.parent
    sys.path.insert(0, str(here))
    from trefoil.reharm.schema import TacticsSpec, compatibility  # type: ignore


REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_DEFAULT_TACTICS = REPO_ROOT / "data" / "reharm" / "tactics.json"


# ---------------------------------------------------------------- #
# Tunable thresholds and weights                                   #
# ---------------------------------------------------------------- #
#
# All numeric thresholds below are the single source of truth — tune here,
# not at call sites.  Defaults are conservative: we prefer to warn rather
# than fail, because Phase 5 is post-hoc validation on a
# coverage-targeted selector (Phase 4), not a bias-optimised one.

# Per-hand span in string indices.  Decision 1: each hand ≤ 10 strings.
HAND_SPAN_LIMIT = 10

# Full instrument range.  Decision 1: 47 strings, indexed 1..47.
STRING_MIN = 1
STRING_MAX = 47

# Cross-bar reach warning threshold.  Two diatonic octaves on a 47-string
# harp = 14 strings; larger jumps are uncommon and worth flagging.
CROSS_BAR_REACH_WARN = 14

# Lever flip budget per phrase; flips in the same 2-bar window are hard
# errors (cannot physically flip and unflip within two bars without a
# disruptive reach).
LEVER_FLIPS_PER_PHRASE_WARN = 2
LEVER_FLIPS_IN_TWO_BAR_WINDOW_ERROR = 1

# Density-axis scoring: map each density tactic to a numeric position on
# the attack-count axis.  1 = sparsest, 4 = densest.  Shape-only
# tactics (front/back-loaded, syncopated) land in the middle at 2.5.
_DENSITY_POSITIONS = {
    "density.one_attack":   1.0,
    "density.per_beat":     2.0,
    "density.two_per_beat": 4.0,
    "density.syncopated":   2.5,
    "density.front_loaded": 2.5,
    "density.back_loaded":  2.5,
}
# Target mean density per the prompt: 1.5 to 2.0, weighted toward sparse.
DENSITY_TARGET_CENTER = 1.75
DENSITY_TARGET_HALFWIDTH = 0.25  # => target band [1.5, 2.0]

# Spread axis target: 3–5 octaves of registral spread translates to
# 21–35 strings on the 47-string harp (7 strings per octave).
SPREAD_TARGET_MIN = 21
SPREAD_TARGET_MAX = 35

# Expose-extremes threshold: a bar has a "properly low bass" if its bass
# string index is ≤ 15 (C3). The 47-string formula places C1=1, C2=8,
# C3=15, C4=22. "Low bass" in jazz-harp context is C3 or below — mid-range
# (C4+) doesn't register as "low" to the listener. See REHARM_TACTICS.md
# expose_extremes bias, penalty target (c).
EXPOSE_LOW_BASS_THRESHOLD = 15
EXPOSE_TOP_ABOVE_LH_GAP = 4  # strings between RH top and highest LH voice

# SATB-zone cluster heuristic: "compressed" spread means < 14 strings
# (two octaves) between bass and top; plus the other three coordinates
# fire when the bar's tactic_manifest matches.
SATB_ZONE_SPREAD_STRINGS = 14
SATB_ZONE_DENSITIES = {"density.two_per_beat", "density.per_beat"}

# total_score weights — conservative defaults; flip signs / re-tune as
# feedback arrives.  Density / spread / SATB are penalties (lower is
# better), expose-extremes is a reward (higher is better).  We subtract
# penalties from a baseline of 1.0 and add the reward directly.
_TOTAL_WEIGHTS = {
    "density_axis":      0.25,
    "spread_axis":       0.25,
    "satb_zone":         0.25,
    "expose_extremes":   0.25,
}


# ---------------------------------------------------------------- #
# Dataclasses                                                      #
# ---------------------------------------------------------------- #

@dataclass
class LegalityReport:
    """Result of a single-variation legality pass.

    ``errors`` are hard failures (physically unplayable, malformed output).
    ``warnings`` flag soft concerns like SATB-zone clustering or bias
    deviations the harpist may want to review.  ``passed`` is True iff
    ``errors`` is empty.
    """
    passed: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def fail(self, msg: str) -> None:
        self.errors.append(msg)
        self.passed = False

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)


# ---------------------------------------------------------------- #
# String-index helpers (matches shape_gen.py)                      #
# ---------------------------------------------------------------- #

def _string_index(note: Optional[Iterable[int]]) -> Optional[int]:
    """Return string index for a ``[degree, octave]`` pair, or ``None``.

    Formula mirrors ``trefoil/reharm/shape_gen.py``:
        idx = (oct - 1) * 7 + (deg - 1) + 1
    """
    if note is None:
        return None
    try:
        deg, oct_ = note[0], note[1]
    except (TypeError, IndexError):
        return None
    return (int(oct_) - 1) * 7 + (int(deg) - 1) + 1


def _indices(notes: Iterable) -> list[int]:
    """Map a list of [deg, oct] pairs to string indices, skipping malformed."""
    out: list[int] = []
    for n in notes or []:
        idx = _string_index(n)
        if idx is not None:
            out.append(idx)
    return out


# ---------------------------------------------------------------- #
# Phrase grouping from a variation                                 #
# ---------------------------------------------------------------- #

def _group_bars_by_phrase(bars: list[dict]) -> list[list[dict]]:
    """Segment the bar sequence at ``phrase_role.opening`` boundaries.

    The variation JSON doesn't carry the hymn's phrase list, but every
    phrase-opening bar is tagged with ``phrase_role.opening`` by the
    selector.  That's enough to re-derive phrase groupings for
    lever-budget checking.  A degenerate fallback treats the whole
    variation as one phrase when no openings are present.
    """
    groups: list[list[dict]] = []
    current: list[dict] = []
    for b in bars:
        role = (b.get("tactic_manifest") or {}).get("phrase_role")
        if role == "phrase_role.opening" and current:
            groups.append(current)
            current = []
        current.append(b)
    if current:
        groups.append(current)
    if not groups:
        groups = [bars]
    return groups


# ---------------------------------------------------------------- #
# Hard legality                                                    #
# ---------------------------------------------------------------- #

def _check_bar_physical(
    bar: dict, report: LegalityReport, spec: Optional[TacticsSpec]
) -> None:
    """Per-bar invariants: span, range, bass/top, tactic compatibility."""
    bar_num = bar.get("bar")
    lh = bar.get("lh") or []
    rh = bar.get("rh") or []

    lh_idx = _indices(lh)
    rh_idx = _indices(rh)

    # String range.
    for label, indices in (("lh", lh_idx), ("rh", rh_idx)):
        for i in indices:
            if i < STRING_MIN or i > STRING_MAX:
                report.fail(
                    f"bar {bar_num}: {label} string {i} outside [{STRING_MIN},{STRING_MAX}]"
                )

    # Hand span ≤ 10.
    for label, indices in (("lh", lh_idx), ("rh", rh_idx)):
        if indices:
            span = max(indices) - min(indices) + 1
            if span > HAND_SPAN_LIMIT:
                report.fail(
                    f"bar {bar_num}: {label} span {span} > {HAND_SPAN_LIMIT} strings"
                )

    # Bass-is-lowest-LH invariant.
    bass = bar.get("bass")
    bass_idx = _string_index(bass) if bass else None
    if lh_idx and bass_idx is not None:
        if bass_idx != min(lh_idx):
            report.fail(
                f"bar {bar_num}: bass string {bass_idx} is not lowest LH "
                f"(min lh = {min(lh_idx)})"
            )

    # Top-is-highest-RH invariant.  If RH is empty (no_lh-ish), fall back
    # to "top is highest of everything", matching the shape-library
    # convention.
    top = bar.get("top")
    top_idx = _string_index(top) if top else None
    if top_idx is not None:
        hi = max(rh_idx) if rh_idx else (max(lh_idx) if lh_idx else None)
        if hi is not None and top_idx != hi:
            report.fail(
                f"bar {bar_num}: top string {top_idx} is not highest "
                f"({'RH' if rh_idx else 'LH'} max = {hi})"
            )

    # Tactic compatibility belt-and-suspenders.
    if spec is not None:
        tm = bar.get("tactic_manifest") or {}
        chosen = {v for v in tm.values() if v}
        if chosen and not compatibility(spec, chosen):
            report.fail(
                f"bar {bar_num}: tactic tuple incompatible: {sorted(chosen)}"
            )


def _check_cross_bar_reach(bars: list[dict], report: LegalityReport) -> None:
    """Consecutive-bar reach warnings: bass or top jumps > threshold."""
    prev = None
    for b in bars:
        if prev is None:
            prev = b
            continue
        prev_bass = _string_index(prev.get("bass"))
        this_bass = _string_index(b.get("bass"))
        prev_top = _string_index(prev.get("top"))
        this_top = _string_index(b.get("top"))
        if prev_bass is not None and this_bass is not None:
            jump = abs(this_bass - prev_bass)
            if jump > CROSS_BAR_REACH_WARN:
                report.warn(
                    f"cross-bar bass reach: bar {prev.get('bar')}→"
                    f"{b.get('bar')} jumps {jump} strings"
                )
        if prev_top is not None and this_top is not None:
            jump = abs(this_top - prev_top)
            if jump > CROSS_BAR_REACH_WARN:
                report.warn(
                    f"cross-bar top reach: bar {prev.get('bar')}→"
                    f"{b.get('bar')} jumps {jump} strings"
                )
        prev = b


def _check_lever_budget(bars: list[dict], report: LegalityReport) -> None:
    """Lever-flip counting: per-phrase warning + 2-bar-window hard error."""
    # Hard-error check: two flips within a 2-bar window.
    for i in range(len(bars) - 1):
        a = (bars[i].get("tactic_manifest") or {}).get("lever", "")
        c = (bars[i + 1].get("tactic_manifest") or {}).get("lever", "")
        if a.startswith("lever.flip_") and c.startswith("lever.flip_"):
            report.fail(
                f"lever flips in consecutive bars {bars[i].get('bar')} and "
                f"{bars[i+1].get('bar')} (2-bar window budget exceeded)"
            )

    # Per-phrase warning.
    for phrase in _group_bars_by_phrase(bars):
        flips = [
            b for b in phrase
            if ((b.get("tactic_manifest") or {}).get("lever", "") or "").startswith("lever.flip_")
        ]
        if len(flips) > LEVER_FLIPS_PER_PHRASE_WARN:
            first_bar = phrase[0].get("bar") if phrase else "?"
            last_bar = phrase[-1].get("bar") if phrase else "?"
            report.warn(
                f"phrase starting bar {first_bar} through bar {last_bar}: "
                f"{len(flips)} lever flips (budget {LEVER_FLIPS_PER_PHRASE_WARN})"
            )


# ---------------------------------------------------------------- #
# Public entry point — legality                                    #
# ---------------------------------------------------------------- #

def check_variation(
    variation_json: dict, spec: Optional[TacticsSpec] = None
) -> LegalityReport:
    """Run all hard-legality + warning passes on one variation.

    Pass ``spec=None`` to skip the tactic-compatibility cross-check (useful
    when the caller has already validated the spec-to-manifest link).  By
    default the module loads ``data/reharm/tactics.json`` lazily on demand.
    """
    if spec is None:
        spec = _load_spec_cached()

    report = LegalityReport()
    bars = variation_json.get("bars") or []

    # Per-bar physical invariants and tactic-compat cross-check.
    for bar in bars:
        _check_bar_physical(bar, report, spec)

    # Cross-bar reach warnings.
    _check_cross_bar_reach(bars, report)

    # Lever budgeting.
    _check_lever_budget(bars, report)

    return report


# Lazy-cached spec loader — avoids re-reading tactics.json for every
# variation in a corpus sweep.
_SPEC_CACHE: Optional[TacticsSpec] = None


def _load_spec_cached() -> TacticsSpec:
    global _SPEC_CACHE
    if _SPEC_CACHE is None:
        _SPEC_CACHE = TacticsSpec.load(_DEFAULT_TACTICS)
    return _SPEC_CACHE


# ---------------------------------------------------------------- #
# Bias scoring                                                     #
# ---------------------------------------------------------------- #

def _density_axis_score(bars: list[dict]) -> float:
    """Distance from the target-mean density band — higher = worse.

    Returns the absolute deviation of the variation's mean density
    position from :data:`DENSITY_TARGET_CENTER`, clipped to 0 when the
    mean falls inside ``[center ± halfwidth]``.  Score range ~[0, 2.5];
    rescale before combining into ``total_score``.
    """
    positions: list[float] = []
    for b in bars:
        d = (b.get("tactic_manifest") or {}).get("density")
        pos = _DENSITY_POSITIONS.get(d)
        if pos is not None:
            positions.append(pos)
    if not positions:
        return 0.0
    mean = sum(positions) / len(positions)
    dev = abs(mean - DENSITY_TARGET_CENTER)
    inside = max(0.0, dev - DENSITY_TARGET_HALFWIDTH)
    return inside


def _spread_axis_score(bars: list[dict]) -> float:
    """Proportion of bars with spread inside the target band.

    Higher is better (reward, not penalty).  Range [0, 1].
    """
    if not bars:
        return 0.0
    in_band = 0
    counted = 0
    for b in bars:
        bi = _string_index(b.get("bass"))
        ti = _string_index(b.get("top"))
        if bi is None or ti is None:
            continue
        spread = ti - bi + 1
        counted += 1
        if SPREAD_TARGET_MIN <= spread <= SPREAD_TARGET_MAX:
            in_band += 1
    if counted == 0:
        return 0.0
    return in_band / counted


def _satb_zone_score(bars: list[dict]) -> float:
    """Count of bars that look like an SATB-zone cluster.

    A bar counts when:
      * density ∈ {two_per_beat, per_beat}
      * spread < SATB_ZONE_SPREAD_STRINGS
      * register.compressed OR (register.same following a compressed bar)
      * texture.block

    Lower = better.  Returned as an absolute count — use relative to
    total bar count when combining into ``total_score``.
    """
    count = 0
    prev_compressed = False
    for b in bars:
        tm = b.get("tactic_manifest") or {}
        density = tm.get("density")
        register = tm.get("register")
        texture = tm.get("texture")

        bi = _string_index(b.get("bass"))
        ti = _string_index(b.get("top"))
        spread = (ti - bi + 1) if (bi is not None and ti is not None) else None

        compressed_now = (register == "register.compressed")
        same_from_compressed = (register == "register.same" and prev_compressed)

        if (
            density in SATB_ZONE_DENSITIES
            and spread is not None
            and spread < SATB_ZONE_SPREAD_STRINGS
            and (compressed_now or same_from_compressed)
            and texture == "texture.block"
        ):
            count += 1

        prev_compressed = compressed_now or same_from_compressed
    return float(count)


def _expose_extremes_score(bars: list[dict]) -> float:
    """Reward low-bass exposure + RH-top isolation.  Higher = better.

    Two components averaged:
      (a) proportion of bars with bass ≤ EXPOSE_LOW_BASS_THRESHOLD
      (b) proportion of bars where RH top sits ≥ EXPOSE_TOP_ABOVE_LH_GAP
          strings above the highest LH voice
    Range [0, 1].
    """
    if not bars:
        return 0.0
    low_bass = 0
    counted_bass = 0
    clear_top = 0
    counted_top = 0
    for b in bars:
        bi = _string_index(b.get("bass"))
        if bi is not None:
            counted_bass += 1
            if bi <= EXPOSE_LOW_BASS_THRESHOLD:
                low_bass += 1

        rh_idx = _indices(b.get("rh"))
        lh_idx = _indices(b.get("lh"))
        if rh_idx and lh_idx:
            counted_top += 1
            if max(rh_idx) - max(lh_idx) >= EXPOSE_TOP_ABOVE_LH_GAP:
                clear_top += 1

    a = (low_bass / counted_bass) if counted_bass else 0.0
    b_ = (clear_top / counted_top) if counted_top else 0.0
    return (a + b_) / 2.0


def score_variation(variation_json: dict) -> dict:
    """Return per-bias scores + weighted ``total_score`` for one variation.

    Scores are returned raw; ``total_score`` combines them via
    :data:`_TOTAL_WEIGHTS`.  Penalties (density, SATB) reduce the score;
    rewards (spread, expose_extremes) increase it.  Total is loosely in
    [0, 1], but can sit outside that range if penalties are large.
    """
    bars = variation_json.get("bars") or []

    density = _density_axis_score(bars)
    spread = _spread_axis_score(bars)
    satb = _satb_zone_score(bars)
    extremes = _expose_extremes_score(bars)

    # Normalise each component to [0, 1] before combining.
    # Density: dev in ~[0, 2.5]; clamp and invert so higher = better.
    density_norm = max(0.0, 1.0 - density / 2.5)
    # SATB: count in [0, n_bars]; normalise by bar count, invert.
    n_bars = max(1, len(bars))
    satb_norm = max(0.0, 1.0 - satb / n_bars)

    total = (
        _TOTAL_WEIGHTS["density_axis"] * density_norm
        + _TOTAL_WEIGHTS["spread_axis"] * spread
        + _TOTAL_WEIGHTS["satb_zone"] * satb_norm
        + _TOTAL_WEIGHTS["expose_extremes"] * extremes
    )

    return {
        "density_axis_score":    density,
        "spread_axis_score":     spread,
        "satb_zone_score":       satb,
        "expose_extremes_score": extremes,
        "total_score":           total,
    }


# ---------------------------------------------------------------- #
# Corpus aggregation                                               #
# ---------------------------------------------------------------- #

def check_corpus(variation_dir: str | Path) -> dict:
    """Aggregate pass/warn/fail counts over every ``*.json`` in a directory.

    Returns::

        {
          "dir": <path>,
          "n_variations": <int>,
          "passed": <int>,          # errors == 0
          "failed": <int>,
          "with_warnings": <int>,   # errors == 0 but warnings > 0
          "errors": [(filename, error_msg), ...],
          "warnings": [(filename, warning_msg), ...],
          "scores": {filename: score_dict, ...},
        }
    """
    vdir = Path(variation_dir)
    files = sorted(p for p in vdir.glob("*.json"))
    spec = _load_spec_cached()

    passed = 0
    failed = 0
    with_warnings = 0
    error_rows: list[tuple[str, str]] = []
    warning_rows: list[tuple[str, str]] = []
    scores: dict[str, dict] = {}

    for f in files:
        var = json.loads(f.read_text())
        rpt = check_variation(var, spec=spec)
        scores[f.name] = score_variation(var)

        if rpt.passed:
            passed += 1
            if rpt.warnings:
                with_warnings += 1
        else:
            failed += 1
            for e in rpt.errors:
                error_rows.append((f.name, e))
        for w in rpt.warnings:
            warning_rows.append((f.name, w))

    return {
        "dir": str(vdir),
        "n_variations": len(files),
        "passed": passed,
        "failed": failed,
        "with_warnings": with_warnings,
        "errors": error_rows,
        "warnings": warning_rows,
        "scores": scores,
    }


__all__ = [
    "LegalityReport",
    "check_variation",
    "score_variation",
    "check_corpus",
    # Tunables (public so tests / CLI can introspect)
    "HAND_SPAN_LIMIT",
    "STRING_MIN",
    "STRING_MAX",
    "CROSS_BAR_REACH_WARN",
    "LEVER_FLIPS_PER_PHRASE_WARN",
    "SPREAD_TARGET_MIN",
    "SPREAD_TARGET_MAX",
    "EXPOSE_LOW_BASS_THRESHOLD",
    "EXPOSE_TOP_ABOVE_LH_GAP",
    "SATB_ZONE_SPREAD_STRINGS",
]
