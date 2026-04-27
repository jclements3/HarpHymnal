#!/usr/bin/env python3
"""Render a phrase of 4-voice voicings to a MIDI file.

One whole-note chord per bar, all four voices sounding simultaneously,
at a slow tempo so each voicing is hearable. The output is a standard
.mid file the page can fetch and play via the vendored midi-player-js +
soundfont-player libraries.
"""
from __future__ import annotations

from pathlib import Path

from music21 import chord, duration, instrument, stream, tempo

from voice_lead import Voicing


def _voice_to_m21_pitch(letter: str, accidental: str, octave: int) -> str:
    """Voice's accidental (`''` / `'#'` / `'b'`) → music21 pitch string
    (uses `-` for flat, `#` for sharp)."""
    acc = '#' if accidental == '#' else '-' if accidental == 'b' else ''
    return f'{letter}{acc}{octave}'


def render_phrase_midi(voicings: list[Voicing], out_path: Path,
                       bpm: int = 60) -> Path:
    """Write one whole-note-per-bar 4-voice MIDI to `out_path`."""
    sc = stream.Score()
    part = stream.Part()
    part.insert(0, instrument.Piano())
    part.insert(0, tempo.MetronomeMark(number=bpm))

    for v in voicings:
        pitches = [
            _voice_to_m21_pitch(v.b.letter, v.b.accidental, v.b.octave),
            _voice_to_m21_pitch(v.t.letter, v.t.accidental, v.t.octave),
            _voice_to_m21_pitch(v.a.letter, v.a.accidental, v.a.octave),
            _voice_to_m21_pitch(v.s.letter, v.s.accidental, v.s.octave),
        ]
        c = chord.Chord(pitches)
        c.duration = duration.Duration(4.0)  # whole note in 4/4
        part.append(c)

    sc.append(part)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sc.write('midi', fp=str(out_path))
    return out_path


if __name__ == '__main__':
    from voice_lead import (
        chord_letters, initial_voicing_with_melody, solve_next_voicing, Voice,
    )
    chords = [('I', ''), ('I', ''), ('V', '7'), ('IV', '')]
    melody = [Voice('G', '', 4), Voice('B', '', 4),
              Voice('G', '', 4), Voice('D', '', 4)]
    pcs0 = chord_letters(*chords[0], 'G')
    v = initial_voicing_with_melody(pcs0, melody[0])
    voicings = [v]
    for (n, q), s in zip(chords[1:], melody[1:]):
        pcs = chord_letters(n, q, 'G')
        v = solve_next_voicing(v, pcs, fixed_s=s)
        voicings.append(v)
    out = Path('/tmp/test_phrase.mid')
    render_phrase_midi(voicings, out)
    print(f'wrote {out} ({out.stat().st_size} bytes)')
