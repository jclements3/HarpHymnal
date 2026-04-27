#!/usr/bin/env python3
"""Extract SATB downbeat pitches per bar from a hymn's ABC source.

The hymn pipeline's per-bar JSON keeps only the soprano (`melody` field).
Tenor / alto / bass live only in the raw ABC under `_abc_source`. This
module parses the four `[V: S1V1]` / `[V: S1V2]` / `[V: S2V1]` / `[V: S2V2]`
voice lines, splits each by `|`, and returns the first note of each
ABC segment (= downbeat of the original bar) for every voice.

The output is a list of `(soprano, alto, tenor, bass)` Pitch tuples,
one per ABC bar (skipping the pickup if any).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Pitch:
    letter: str          # 'A'..'G'
    accidental: str      # '#' '' 'b'
    octave: int          # MIDI-style octave: middle C = C4

    def name(self) -> str:
        return f'{self.letter}{self.accidental}'

    def with_key(self, sharps: list[str], flats: list[str]) -> 'Pitch':
        if self.accidental:
            return self
        if self.letter in sharps:
            return Pitch(self.letter, '#', self.octave)
        if self.letter in flats:
            return Pitch(self.letter, 'b', self.octave)
        return self


# ABC note token: optional accidental, letter, optional ,/'+ octave shifts.
NOTE_RE = re.compile(r"([\^_=]?)([A-Ga-g])([,']*)")


def _parse_abc_pitch(token: str) -> Pitch:
    m = NOTE_RE.match(token)
    if not m:
        raise ValueError(f'not a note token: {token!r}')
    acc_raw, letter, oct_shift = m.groups()
    acc = {'^': '#', '_': 'b', '=': '', '': ''}[acc_raw]
    base_octave = 5 if letter.islower() else 4
    octave = base_octave + oct_shift.count("'") - oct_shift.count(',')
    return Pitch(letter.upper(), acc, octave)


def _strip_decorations(body: str) -> str:
    """Remove ABC inline directives, decorations, slurs, ties, and bar-line
    markers other than `|`, leaving just notes + the bar separators."""
    body = re.sub(r'\[[^\]]*\]', '', body)         # [Q:1/4=100] etc.
    body = re.sub(r'!\w+!', '', body)              # !fermata! !sintro!
    body = re.sub(r'\{[^}]*\}', '', body)          # {grace} notes
    body = re.sub(r'"[^"]*"', '', body)            # "chord names" if any
    body = re.sub(r'[()]', '', body)               # slurs
    body = re.sub(r'-+', '', body)                 # ties
    body = body.replace('|]', '|').replace('[|', '|').replace(':|', '|').replace('|:', '|')
    return body


def _voice_lines(abc: str, voice_id: str) -> str:
    """Concatenate every line that opens with `[V: <voice_id>]` and
    return the joined music body (with decorations stripped)."""
    parts: list[str] = []
    for line in abc.splitlines():
        s = line.strip()
        prefix = f'[V: {voice_id}]'
        if s.startswith(prefix):
            content = s[len(prefix):].strip()
            parts.append(content)
    return _strip_decorations(' '.join(parts))


def _first_note(segment: str) -> Optional[Pitch]:
    """Return the first pitched note in an ABC bar segment, or None."""
    m = NOTE_RE.search(segment)
    if not m:
        return None
    # Normalise to a single-token slice from the match position
    token = segment[m.start():m.end()]
    return _parse_abc_pitch(token)


# Major-key sharp/flat order, copied from retab_hymnal.py (kept in sync).
KEY_SIG = {
    'C':  ([], []),
    'G':  (['F'], []),
    'D':  (['F', 'C'], []),
    'A':  (['F', 'C', 'G'], []),
    'E':  (['F', 'C', 'G', 'D'], []),
    'B':  (['F', 'C', 'G', 'D', 'A'], []),
    'F#': (['F', 'C', 'G', 'D', 'A', 'E'], []),
    'F':  ([], ['B']),
    'Bb': ([], ['B', 'E']),
    'Eb': ([], ['B', 'E', 'A']),
    'Ab': ([], ['B', 'E', 'A', 'D']),
    'Db': ([], ['B', 'E', 'A', 'D', 'G']),
    'Gb': ([], ['B', 'E', 'A', 'D', 'G', 'C']),
}


def extract_satb_per_bar(
    abc: str,
    key_root: str,
    has_anacrusis: bool = True,
) -> list[tuple[Optional[Pitch], Optional[Pitch], Optional[Pitch], Optional[Pitch]]]:
    """Return one `(soprano, alto, tenor, bass)` tuple per ABC bar.

    Each pitch is the first note of that voice's |-segment, which is
    conventionally the downbeat of the bar. When a voice has no note
    in that segment (e.g. a tied-over rest), its slot is None.

    `has_anacrusis=True` skips the first segment of each voice, so the
    output indexes line up with the original (1-based) bar numbers.
    """
    sharps, flats = KEY_SIG.get(key_root, ([], []))
    voices = ['S1V1', 'S1V2', 'S2V1', 'S2V2']
    voice_segs: list[list[str]] = []
    for vid in voices:
        body = _voice_lines(abc, vid)
        segs = [s.strip() for s in body.split('|') if s.strip()]
        if has_anacrusis:
            segs = segs[1:]
        voice_segs.append(segs)

    n_bars = max(len(s) for s in voice_segs)
    out = []
    for i in range(n_bars):
        bar_pitches = []
        for segs in voice_segs:
            if i < len(segs):
                p = _first_note(segs[i])
                bar_pitches.append(p.with_key(sharps, flats) if p else None)
            else:
                bar_pitches.append(None)
        # Voice order in ABC: S1V1=Sop, S1V2=Alto, S2V1=Tenor, S2V2=Bass.
        s, a, t, b = bar_pitches
        out.append((s, a, t, b))
    return out
