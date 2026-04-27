#!/usr/bin/env python3
"""Render a phrase of 4-voice voicings to a compact inline SVG snippet.

Constraint per the user: no chord symbols, no key signature, no time
signature, no bar lines — just the notes, packed tight on a grand staff.

Pipeline:
  voicings  → minimal ABC string  → abcm2ps -g -  → SVG bytes  → inline string
"""
from __future__ import annotations

import re
import subprocess
import tempfile
from pathlib import Path

from voice_lead import Voicing


def _abc_pitch(letter: str, accidental: str, octave: int) -> str:
    """Convert (letter, accidental, octave) to ABC notation.

    ABC convention: 'C' = middle C (C4); lowercase = C5+ octave; ',' lowers,
    "'" raises by an octave. So C3 = 'C,', C5 = 'c', etc.
    """
    acc = {'#': '^', 'b': '_', '': ''}[accidental]
    if octave >= 5:
        base = letter.lower()
        ups = octave - 5
        return acc + base + ("'" * ups)
    base = letter.upper()
    downs = 4 - octave
    return acc + base + ("," * downs)


def _voicing_to_abc_chord(v: Voicing) -> tuple[str, str]:
    """Split a SATB voicing into (treble_chord, bass_chord) ABC tokens.

    Soprano + alto go on the treble staff; tenor + bass go on the bass staff.
    Each chord renders as a whole note via the `4` duration suffix (with the
    snippet's L:1/4 default that's 4 quarter-notes = a whole note).
    """
    treble = sorted(
        [(v.a.midi(), _abc_pitch(v.a.letter, v.a.accidental, v.a.octave)),
         (v.s.midi(), _abc_pitch(v.s.letter, v.s.accidental, v.s.octave))],
        key=lambda x: x[0],
    )
    bass = sorted(
        [(v.b.midi(), _abc_pitch(v.b.letter, v.b.accidental, v.b.octave)),
         (v.t.midi(), _abc_pitch(v.t.letter, v.t.accidental, v.t.octave))],
        key=lambda x: x[0],
    )
    return ('[' + ''.join(p for _, p in treble) + ']4',
            '[' + ''.join(p for _, p in bass) + ']4')


def _abc_for_phrase(voicings: list[Voicing]) -> str:
    """Build the minimal ABC tune body for one phrase's voicings."""
    treble_chords = []
    bass_chords = []
    for v in voicings:
        t, b = _voicing_to_abc_chord(v)
        treble_chords.append(t)
        bass_chords.append(b)
    # Use quarter notes (L:1/4) packed without bar lines. M:none suppresses
    # the time signature display; K:C with explicit accidentals avoids any
    # key signature rendering. %%scale 0.65 shrinks the whole snippet.
    return (
        'X: 1\n'
        'T:\n'
        'M: none\n'
        'L: 1/4\n'
        'K: C\n'
        '%%staves [(V1) (V2)]\n'
        '%%musicspace 0\n'
        '%%maxshrink 1.0\n'
        '%%scale 0.7\n'
        '%%staffsep 25\n'
        'V: V1 clef=treble\n'
        'V: V2 clef=bass\n'
        '[V: V1] ' + ' '.join(treble_chords) + '\n'
        '[V: V2] ' + ' '.join(bass_chords) + '\n'
    )


def render_phrase_svg(voicings: list[Voicing]) -> str:
    """Run abcm2ps on the phrase ABC and return the resulting <svg> tag.

    Returns an empty string if rendering fails."""
    if not voicings:
        return ''
    abc = _abc_for_phrase(voicings)
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        in_path = td_path / 'phrase.abc'
        in_path.write_text(abc)
        out_prefix = td_path / 'phrase'
        # abcm2ps may emit non-fatal warnings + still produce a file; don't
        # `check=True` since exit-code-non-zero on warning would skip the SVG.
        subprocess.run(
            ['abcm2ps', '-g', '-O', str(out_prefix), str(in_path)],
            capture_output=True,
        )
        svg_path = td_path / 'phrase001.svg'
        if not svg_path.exists():
            # abcm2ps sometimes emits phrase.svg vs phrase001.svg
            for cand in td_path.glob('phrase*.svg'):
                svg_path = cand
                break
        if not svg_path.exists():
            return ''
        svg = svg_path.read_text()
    # Strip the XML declaration & DOCTYPE so it inlines cleanly.
    svg = re.sub(r'^<\?xml[^>]*\?>\s*', '', svg)
    svg = re.sub(r'<!DOCTYPE[^>]*>\s*', '', svg)
    return svg


if __name__ == '__main__':
    # Smoke-test against Amazing Grace phrase 1.
    from voice_lead import (
        chord_letters, initial_voicing_for, solve_next_voicing,
    )
    chords = [('I', ''), ('I', ''), ('V', '7'), ('IV', '')]
    key = 'G'
    v = initial_voicing_for(chord_letters(*chords[0], key))
    voicings = [v]
    for n, q in chords[1:]:
        pcs = chord_letters(n, q, key)
        v = solve_next_voicing(v, pcs)
        voicings.append(v)
    svg = render_phrase_svg(voicings)
    print(f'svg length: {len(svg)} bytes')
    print(svg[:200])
