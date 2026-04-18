"""The 118-fraction pool: load, index, look up.

Wraps `data/trefoil/HarpTrefoil.json` behind a small grammar-native API.
Every entry in the pool is a two-hand `Bishape` (LH Shape + RH Shape); the
canonical index `001..118` walks `jazz_progressions.entries` (001..042) and
then `stacked_chords.entries` (043..118) in document order.

Public surface:
    load_pool(path) -> Pool
    Pool.get(ipool) -> PoolEntry
    Pool.all_voicings_of(chord) -> tuple[PoolEntry, ...]
    Pool.ipool_of(bishape) -> str | None
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from grammar.parse import parse_figure, parse_roman
from grammar.types import Bishape, Roman, Shape


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_POOL_PATH = ROOT / 'data' / 'trefoil' / 'HarpTrefoil.json'


@dataclass(frozen=True)
class PoolEntry:
    """One of the 118 fractions, typed.

    `source` is either 'jazz_progressions' (cycle-annotated) or
    'stacked_chords' (single-sonority). The `meta` dict carries
    source-specific fields verbatim: mood/cw_label/ccw_label/cycle.
    """
    ipool: str                 # '001'..'118'
    source: str                # 'jazz_progressions' | 'stacked_chords'
    bishape: Bishape
    lh_chord: Roman
    rh_chord: Roman
    lh_figure: str             # e.g. '133'
    rh_figure: str             # e.g. '933'
    meta: dict                 # mood / cw_label / ccw_label / cycle


class Pool:
    """Indexed view over the 118 fractions."""

    def __init__(self, entries: tuple[PoolEntry, ...]):
        self._entries = entries
        self._by_ipool = {e.ipool: e for e in entries}
        self._by_bishape: dict[tuple, PoolEntry] = {}
        for e in entries:
            self._by_bishape[_bishape_key(e.bishape)] = e

    def __len__(self) -> int:
        return len(self._entries)

    def __iter__(self):
        return iter(self._entries)

    @property
    def entries(self) -> tuple[PoolEntry, ...]:
        return self._entries

    def get(self, ipool: str) -> PoolEntry:
        """Look up by canonical '001'..'118' index."""
        key = ipool.zfill(3) if isinstance(ipool, str) else f"{int(ipool):03d}"
        if key not in self._by_ipool:
            raise KeyError(f"ipool {ipool!r} not in pool (valid: 001..{len(self):03d})")
        return self._by_ipool[key]

    def all_voicings_of(self, chord) -> tuple[PoolEntry, ...]:
        """Every pool entry whose LH chord matches `chord`.

        `chord` can be a Roman dataclass or a string like 'I', 'V7', 'vi'.
        Matching is by numeral + quality + inversion after `parse_roman`
        normalization; entries whose LH *or* RH chord matches are returned.
        """
        target = chord if isinstance(chord, Roman) else parse_roman(chord)
        return tuple(
            e for e in self._entries
            if _roman_eq(e.lh_chord, target) or _roman_eq(e.rh_chord, target)
        )

    def ipool_of(self, bishape: Bishape) -> Optional[str]:
        """Inverse lookup: shape→ipool, or None if not in the pool."""
        return self._by_bishape.get(_bishape_key(bishape), None) and \
               self._by_bishape[_bishape_key(bishape)].ipool


def load_pool(path: Path | str = DEFAULT_POOL_PATH) -> Pool:
    """Load and index `data/trefoil/HarpTrefoil.json`."""
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    entries: list[PoolEntry] = []
    idx = 1
    for raw in data['jazz_progressions']['entries']:
        entries.append(_build_entry(raw, idx, 'jazz_progressions'))
        idx += 1
    for raw in data['stacked_chords']['entries']:
        entries.append(_build_entry(raw, idx, 'stacked_chords'))
        idx += 1
    return Pool(tuple(entries))


# ─────────────────── internals ───────────────────

def _build_entry(raw: dict, idx: int, source: str) -> PoolEntry:
    lh_fig, rh_fig = raw['lh_figure'], raw['rh_figure']
    lh_anchor, lh_ivals = parse_figure(lh_fig)
    rh_anchor, rh_ivals = parse_figure(rh_fig)
    lh_chord = _parse_pool_roman(raw['lh_roman'])
    rh_chord = _parse_pool_roman(raw['rh_roman'])
    bishape = Bishape(
        lh=Shape(degree=lh_anchor, intervals=lh_ivals),   # type: ignore[arg-type]
        rh=Shape(degree=rh_anchor, intervals=rh_ivals),   # type: ignore[arg-type]
    )
    meta = {k: v for k, v in raw.items()
            if k not in ('lh_roman', 'lh_figure', 'rh_roman', 'rh_figure')}
    return PoolEntry(
        ipool=f"{idx:03d}",
        source=source,
        bishape=bishape,
        lh_chord=lh_chord,
        rh_chord=rh_chord,
        lh_figure=lh_fig,
        rh_figure=rh_fig,
        meta=meta,
    )


def _parse_pool_roman(s: str) -> Roman:
    """Parse a pool roman, tolerating concatenated legacy forms.

    The pool TeX sometimes carries compound strings like 'V7i' or 'Δiii'
    that don't match grammar.parse._QUALITIES. Fall through to a dataclass
    built directly so we never lose data on load.
    """
    try:
        return parse_roman(s)
    except ValueError:
        return Roman(numeral=s, quality=None, inversion=None)


def _roman_eq(a: Roman, b: Roman) -> bool:
    return (a.numeral == b.numeral
            and (a.quality or '') == (b.quality or '')
            and (a.inversion or '') == (b.inversion or ''))


def _bishape_key(bs: Bishape) -> tuple:
    return (bs.lh.degree, tuple(bs.lh.intervals),
            bs.rh.degree, tuple(bs.rh.intervals))
