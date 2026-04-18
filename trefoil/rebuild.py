"""Rebuild ``data/trefoil/HarpTrefoil.json`` from ``source/HarpTrefoil.tex``.

Grammar-native port of ``legacy/tools/rebuild_chord_system_json.py``.  The
authoritative pedagogy lives in the TeX macros; this module extracts the 118
LH/RH fraction entries (42 jazz-progression rows + 76 stacked-chord rows) and
wraps each in typed ``Bishape`` / ``Roman`` records from ``grammar.types``
before serialising back to JSON.

TeX macro argument orderings (copied verbatim from the legacy port — these
orderings are correct; the prior Claude's positional extractor had LH/RH
swapped):

``\\sexcA / \\sexcB / \\sexcC`` (jazz-progression rows)
    #1 = RH-rom   #2 = RH-qual
    #3 = LH-rom   #4 = LH-qual
    #5 = CW-label #6 = CCW-label
    #7 = LH-fig   #8 = RH-fig

``\\spt`` (stacked-chord / pool rows)
    #1 = LH-rom   #2 = LH-qual
    #3 = RH-rom   #4 = RH-qual
    #5 = LH-fig   #6 = RH-fig
    #7 = Name/Mood

The prose sections (``how_to_use``, ``conventions``, ``instrument``,
``patterns``, ``chords_by_pattern_and_degree``, ``cycles``) are passed through
verbatim from ``source/HarpChordSystem.json`` — they live outside the macro
tables and have no TeX source.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Optional

from grammar.parse import parse_figure
from grammar.types import Bishape, Roman, Shape


_CYCLE_BY_LETTER = {'A': '2nds', 'B': '3rds', 'C': '4ths'}


# ───────────────────── Brace-balanced TeX arg reader ─────────────────────

def _parse_braced_args(s: str, start: int, n: int):
    """Read ``n`` brace-balanced ``{...}`` args from ``s`` starting at ``start``.

    Handles nested braces so constructs like ``{\\halfdim\\osf{7}}`` parse as
    a single argument.  Returns ``(args_list, new_pos)`` or ``(None, start)``
    if parsing fails.
    """
    args: list[str] = []
    pos = start
    for _ in range(n):
        while pos < len(s) and s[pos] in ' \t\n':
            pos += 1
        if pos >= len(s) or s[pos] != '{':
            return None, start
        pos += 1
        depth = 1
        arg_start = pos
        while pos < len(s) and depth > 0:
            if s[pos] == '{':
                depth += 1
            elif s[pos] == '}':
                depth -= 1
            pos += 1
        if depth != 0:
            return None, start
        args.append(s[arg_start:pos - 1])
    return args, pos


def _tex_to_plain(s: str) -> str:
    """Strip common LaTeX artifacts from a captured macro argument."""
    if not s:
        return ''
    s = re.sub(r'\\inv\{1\}', '\u00b9', s)
    s = re.sub(r'\\inv\{2\}', '\u00b2', s)
    s = re.sub(r'\\inv\{3\}', '\u00b3', s)
    s = s.replace(r'\halfdim', '\u00f8')
    s = re.sub(r'\\rp\{\}', '+', s)
    s = s.replace(r'\rp', '+')
    prev = None
    while prev != s:
        prev = s
        s = re.sub(r'\\osf\{([^{}]*)\}', r'\1', s)
    return s.strip()


# ──────────────── Grammar-typed records for a single pool entry ──────────

class _TypedEntry:
    """A single LH/RH fraction lifted into grammar.types records.

    We keep the original figure string alongside the typed ``Shape`` so
    JSON serialisation is a straight dict copy (no reliance on
    ``emit_shape`` round-tripping hex anchors A..F).
    """

    __slots__ = (
        'lh_roman', 'rh_roman',         # Roman objects
        'lh_shape', 'rh_shape',         # Shape objects
        'bishape',                      # Bishape wrapping both shapes
        'lh_figure', 'rh_figure',       # original figure strings (round-trip)
    )

    def __init__(self, lh_roman: Roman, rh_roman: Roman,
                 lh_figure: str, rh_figure: str):
        self.lh_roman = lh_roman
        self.rh_roman = rh_roman
        self.lh_figure = lh_figure
        self.rh_figure = rh_figure
        self.lh_shape = _shape_from_figure(lh_figure)
        self.rh_shape = _shape_from_figure(rh_figure)
        self.bishape = Bishape(lh=self.lh_shape, rh=self.rh_shape)


def _shape_from_figure(fig: str) -> Shape:
    """Build a ``Shape`` from a wire-format figure string.

    The anchor character may be ``1..9`` (scale-degrees 1..9) or
    ``A..F`` (10..15).  We pass the anchor straight through as the
    ``degree`` field — Python does not enforce ``Literal`` at runtime,
    and the original figure string is preserved separately for lossless
    JSON serialisation.
    """
    anchor, intervals = parse_figure(fig)
    return Shape(degree=anchor, intervals=intervals)  # type: ignore[arg-type]


def _make_roman(numeral: str, quality: str) -> Roman:
    """Construct a ``Roman`` directly, bypassing ``parse_roman``.

    The pool uses non-standard quality strings (e.g. ``'Δiii'``, ``'7ii'``,
    ``'ø7iii'``) that encode an inner-voice extension rather than one of
    the strict canonical qualities ``parse_roman`` validates.  We keep the
    raw string verbatim so serialisation matches the TeX source byte-for-byte.
    """
    q: Optional[str] = quality if quality else None
    return Roman(numeral=numeral, quality=q, inversion=None)


# ──────────────────────────── Extraction ────────────────────────────────

class _JazzRow:
    """A single jazz-progression row: a ``_TypedEntry`` + cycle + labels."""

    __slots__ = ('cycle', 'entry', 'cw_label', 'ccw_label')

    def __init__(self, cycle: str, entry: _TypedEntry,
                 cw_label: str, ccw_label: str):
        self.cycle = cycle
        self.entry = entry
        self.cw_label = cw_label
        self.ccw_label = ccw_label


def extract_jazz_entries(tex: str) -> list[_JazzRow]:
    """Pull every ``\\sexcA`` / ``\\sexcB`` / ``\\sexcC`` row from the TeX.

    Skips the ``\\newcommand{\\sexc*}`` definition sites — those are preceded
    by the token ``newcommand`` and have a ``[N]{body}`` arity declaration
    rather than the 8-arg instance form.
    """
    rows: list[_JazzRow] = []
    for m in re.finditer(r'\\sexc([ABC])(?![a-zA-Z])', tex):
        letter = m.group(1)
        start = m.start()
        if 'newcommand' in tex[max(0, start - 15):start]:
            continue
        args, _ = _parse_braced_args(tex, m.end(), 8)
        if args is None:
            continue
        # Macro args: #1=RH-rom, #2=RH-qual, #3=LH-rom, #4=LH-qual,
        #             #5=CW-label, #6=CCW-label, #7=LH-fig, #8=RH-fig
        rh_rom, rh_qual, lh_rom, lh_qual = args[0], args[1], args[2], args[3]
        cw_label, ccw_label = args[4], args[5]
        lh_fig, rh_fig = args[6], args[7]
        entry = _TypedEntry(
            lh_roman=_make_roman(_tex_to_plain(lh_rom), _tex_to_plain(lh_qual)),
            rh_roman=_make_roman(_tex_to_plain(rh_rom), _tex_to_plain(rh_qual)),
            lh_figure=_tex_to_plain(lh_fig),
            rh_figure=_tex_to_plain(rh_fig),
        )
        rows.append(_JazzRow(
            cycle=_CYCLE_BY_LETTER[letter],
            entry=entry,
            cw_label=_tex_to_plain(cw_label),
            ccw_label=_tex_to_plain(ccw_label),
        ))
    return rows


def extract_pool_entries(tex: str) -> list[tuple[_TypedEntry, str]]:
    """Pull every ``\\spt`` (stacked-chord) row.  Returns (entry, mood) pairs."""
    out: list[tuple[_TypedEntry, str]] = []
    for m in re.finditer(r'\\spt(?![a-zA-Z])', tex):
        start = m.start()
        if 'newcommand' in tex[max(0, start - 15):start]:
            continue
        args, _ = _parse_braced_args(tex, m.end(), 7)
        if args is None:
            continue
        # #1=LH-rom, #2=LH-qual, #3=RH-rom, #4=RH-qual,
        # #5=LH-fig, #6=RH-fig, #7=Mood
        lh_rom, lh_qual, rh_rom, rh_qual = args[0], args[1], args[2], args[3]
        lh_fig, rh_fig, mood = args[4], args[5], args[6]
        entry = _TypedEntry(
            lh_roman=_make_roman(_tex_to_plain(lh_rom), _tex_to_plain(lh_qual)),
            rh_roman=_make_roman(_tex_to_plain(rh_rom), _tex_to_plain(rh_qual)),
            lh_figure=_tex_to_plain(lh_fig),
            rh_figure=_tex_to_plain(rh_fig),
        )
        out.append((entry, _tex_to_plain(mood)))
    return out


# ───────────────────────── Serialisation ────────────────────────────────

def _roman_to_string(r: Roman) -> str:
    """Concatenate Roman back into the legacy string form.

    Inversion is always ``None`` for pool entries, so this is simply
    numeral + quality (when present).
    """
    return r.numeral + (r.quality or '')


def _jazz_row_to_dict(row: _JazzRow) -> dict:
    e = row.entry
    return {
        'cycle': row.cycle,
        'lh_roman': _roman_to_string(e.lh_roman),
        'lh_figure': e.lh_figure,
        'rh_roman': _roman_to_string(e.rh_roman),
        'rh_figure': e.rh_figure,
        'cw_label': row.cw_label,
        'ccw_label': row.ccw_label,
    }


def _pool_entry_to_dict(entry: _TypedEntry, mood: str) -> dict:
    return {
        'lh_roman': _roman_to_string(entry.lh_roman),
        'lh_figure': entry.lh_figure,
        'rh_roman': _roman_to_string(entry.rh_roman),
        'rh_figure': entry.rh_figure,
        'mood': mood,
    }


# ───────────────────────────── Top-level rebuild ────────────────────────

def rebuild(tex_path: Path, prose_json_path: Path) -> dict:
    """Parse ``tex_path`` + inherit prose from ``prose_json_path`` → full JSON dict.

    Returns the rebuilt dict; caller decides where to write it.
    """
    tex = Path(tex_path).read_text(encoding='utf-8')
    with open(prose_json_path, encoding='utf-8') as f:
        existing = json.load(f)

    jazz_rows = extract_jazz_entries(tex)
    pool_rows = extract_pool_entries(tex)

    existing_sv = existing.get('schema_version')
    schema_version = existing_sv + 1 if isinstance(existing_sv, int) else 2

    rebuilt = {
        'schema_version': schema_version,
        'title': existing.get('title', 'Harp Chord System — JSON reference'),
        'source': 'HarpTrefoil.tex (byte-exact mirror of HarpChordSystem.tex) via trefoil/rebuild.py',
        '_rebuilt_from_tex': True,
        '_pedagogy_reference': 'See TREFOIL.md at repo root for the complete pedagogical model.',
        'how_to_use': existing.get('how_to_use', {}),
        'conventions': existing.get('conventions', {}),
        'instrument': existing.get('instrument', {}),
        'patterns': existing.get('patterns', []),
        'chords_by_pattern_and_degree': existing.get('chords_by_pattern_and_degree', {}),
        'cycles': existing.get('cycles', {}),
        'jazz_progressions': {
            'description': (
                'Paired LH/RH voicings along the three diatonic cycles. '
                'CW ascends, CCW descends. 42 entries (3 cycles × 14 rows).'
            ),
            '_canonical_name': 'complex chord cycles',
            'entries': [_jazz_row_to_dict(r) for r in jazz_rows],
        },
        'stacked_chords': {
            'description': (
                'Single-sonority two-handed fractions (LH over RH). Each has '
                'one mood name. 76 entries. Together with the 42 '
                'jazz_progressions entries these form the 118 legal chord '
                'fractions on the harp.'
            ),
            '_canonical_name': 'chord fractions pool',
            'entries': [_pool_entry_to_dict(e, m) for e, m in pool_rows],
        },
    }
    return rebuilt


def write_rebuilt(rebuilt: dict, out_path: Path) -> None:
    """Serialise ``rebuilt`` to ``out_path``, creating parent dirs if needed."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(rebuilt, f, indent=2, ensure_ascii=False)
