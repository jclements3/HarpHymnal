#!/usr/bin/env python3
"""Render a hymn as a Chopin-treatment piano arrangement.

Output is a normal grand-staff piano score:
  - RH (treble): melody at the source's actual rhythm + alto held beneath
  - LH (bass):   tenor + bass voice-led, held as one block per chord change

The harmony is the voice-led version, not the original SATB. Every bar's
inner voicing comes from `voice_lead.solve_next_voicing` with the soprano
fixed to the melody's first note of the bar.

Usage:
  python3 render_chopin_piano.py <slug>
       writes shapes/chopin/piano/<slug>.html (with inline SVG)
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import tempfile
from pathlib import Path

from voice_lead import (
    Voice, Voicing, chord_letters, initial_voicing_with_melody,
    solve_next_voicing,
)

REPO = Path(__file__).resolve().parents[1]
SHAPES = REPO / 'shapes'


def _abc_pitch(letter: str, accidental: str, octave: int) -> str:
    acc = {'#': '^', 'b': '_', '': ''}.get(accidental, '')
    if octave >= 5:
        return acc + letter.lower() + ("'" * (octave - 5))
    return acc + letter.upper() + ("," * (4 - octave))


def _norm_acc(a) -> str:
    if a in (None, ''): return ''
    if a in ('#', '♯'): return '#'
    if a in ('b', '♭'): return 'b'
    return ''


def _melody_pitches(bar: dict) -> list[Voice]:
    out = []
    for ev in bar.get('melody') or []:
        if ev.get('kind') != 'note':
            continue
        p = ev['pitch']
        out.append(Voice(p['letter'], _norm_acc(p.get('accidental')), p['octave']))
    return out


def _melody_to_abc(bar: dict, sixteenths_per_beat: int) -> str:
    """Render the bar's melody as an ABC token sequence under L:1/16.

    Durations in the JSON are in quarter-note lengths; convert each to an
    integer count of sixteenth-notes and emit `<pitch><count>`. Rests inside
    the melody are emitted as `z<count>`.
    """
    parts = []
    for ev in bar.get('melody') or []:
        dur_q = ev.get('duration') or 0
        n = max(1, round(dur_q * sixteenths_per_beat))
        if ev.get('kind') == 'rest':
            parts.append(f'z{n}')
            continue
        if ev.get('kind') != 'note':
            continue
        p = ev['pitch']
        parts.append(_abc_pitch(p['letter'], _norm_acc(p.get('accidental')), p['octave']) + str(n))
    return ' '.join(parts)


def _bar_chord_pcs(bar: dict, key_root: str) -> list[str]:
    ch = bar.get('chord') or {}
    num = ch.get('numeral') or 'I'
    qual = ch.get('quality') or ''
    return chord_letters(num, qual, key_root)


def _chord_token(voices: list[Voice], count: int) -> str:
    pitches = [_abc_pitch(v.letter, v.accidental, v.octave) for v in
               sorted(voices, key=lambda x: x.midi())]
    return '[' + ''.join(pitches) + ']' + str(count)


def _bar_units(beats: int, unit: int) -> int:
    """Sixteenth-note count for one full bar at the given meter."""
    return int(beats * 4 * (4 / unit))


def build_phrase_abc(phrase_bars: list[dict], voicings: list[Voicing],
                     key_root: str, mode: str, beats: int, unit: int,
                     title: str = '') -> str:
    """ABC for a single phrase: melody at original rhythm + voice-led ATB pad.

    `phrase_bars` and `voicings` are 1:1 — each bar's voicing supplies the
    A/T/B pitches for that bar. Empty/melody-less bars get rests."""
    bar_units = _bar_units(beats, unit)
    abc_key = key_root + ('m' if mode == 'minor' else '')

    soprano_lines, alto_lines, tenor_lines, bass_lines = [], [], [], []
    for bar, v in zip(phrase_bars, voicings):
        soprano_lines.append(_melody_to_abc(bar, 4) or f'z{bar_units}')
        if v is None:
            alto_lines.append(f'z{bar_units}')
            tenor_lines.append(f'z{bar_units}')
            bass_lines.append(f'z{bar_units}')
        else:
            alto_lines.append(_chord_token([v.a], bar_units))
            tenor_lines.append(_chord_token([v.t], bar_units))
            bass_lines.append(_chord_token([v.b], bar_units))

    return (
        'X: 1\n'
        f'T: {title}\n'
        f'M: {beats}/{unit}\n'
        'L: 1/16\n'
        f'K: {abc_key}\n'
        '%%staves [(S A) (T B)]\n'
        '%%scale 0.7\n'
        '%%staffsep 22\n'
        '%%musicspace 4\n'
        '%%maxshrink 1.0\n'
        'V: S clef=treble\n'
        'V: A clef=treble\n'
        'V: T clef=bass\n'
        'V: B clef=bass\n'
        '[V: S] ' + (' | '.join(soprano_lines) + ' |') + '\n'
        '[V: A] ' + (' | '.join(alto_lines) + ' |') + '\n'
        '[V: T] ' + (' | '.join(tenor_lines) + ' |') + '\n'
        '[V: B] ' + (' | '.join(bass_lines) + ' |') + '\n'
    )


def render_phrase_piano_svg(phrase_bars: list[dict], voicings: list[Voicing],
                            key_root: str, mode: str, beats: int, unit: int) -> str:
    """Render one phrase as an inline-SVG piano arrangement."""
    if not phrase_bars or not voicings:
        return ''
    abc = build_phrase_abc(phrase_bars, voicings, key_root, mode, beats, unit)
    return render_svg(abc)


def build_abc(hymn: dict) -> str:
    title = hymn.get('title') or 'Untitled'
    key = hymn.get('key') or {}
    key_root = key.get('root') or 'C'
    mode = (key.get('mode') or 'major').lower()
    meter = hymn.get('meter') or {}
    beats = meter.get('beats') or 4
    unit = meter.get('unit') or 4
    bars = hymn.get('bars') or []

    bar_units = _bar_units(beats, unit)
    abc_key = key_root + ('m' if mode == 'minor' else '')

    # Voice-leading chain: soprano fixed to each bar's first melody note.
    chain: list[Voicing] = []
    for i, bar in enumerate(bars):
        mel = _melody_pitches(bar)
        if not mel:
            if chain:
                chain.append(chain[-1])
            continue
        soprano = mel[0]
        pcs = _bar_chord_pcs(bar, key_root)
        if i == 0:
            v = initial_voicing_with_melody(pcs, soprano)
        else:
            v = solve_next_voicing(chain[-1], pcs, fixed_s=soprano)
        chain.append(v)

    soprano_lines, alto_lines, tenor_lines, bass_lines = [], [], [], []
    for i, bar in enumerate(bars):
        if i >= len(chain):
            break
        v = chain[i]
        soprano_lines.append(_melody_to_abc(bar, 4) or f'z{bar_units}')
        alto_lines.append(_chord_token([v.a], bar_units))
        tenor_lines.append(_chord_token([v.t], bar_units))
        bass_lines.append(_chord_token([v.b], bar_units))

    soprano_body = ' | '.join(soprano_lines) + ' |'
    alto_body = ' | '.join(alto_lines) + ' |'
    tenor_body = ' | '.join(tenor_lines) + ' |'
    bass_body = ' | '.join(bass_lines) + ' |'

    return (
        'X: 1\n'
        f'T: {title}\n'
        f'M: {beats}/{unit}\n'
        'L: 1/16\n'
        'Q: 1/4=80\n'
        f'K: {abc_key}\n'
        '%%staves [(S A) (T B)]\n'
        '%%scale 0.85\n'
        '%%staffsep 30\n'
        '%%musicspace 6\n'
        'V: S clef=treble name="RH"\n'
        'V: A clef=treble\n'
        'V: T clef=bass name="LH"\n'
        'V: B clef=bass\n'
        f'[V: S] {soprano_body}\n'
        f'[V: A] {alto_body}\n'
        f'[V: T] {tenor_body}\n'
        f'[V: B] {bass_body}\n'
    )


def render_svg(abc: str) -> str:
    with tempfile.TemporaryDirectory() as td:
        td_path = Path(td)
        in_path = td_path / 'tune.abc'
        in_path.write_text(abc)
        out_prefix = td_path / 'tune'
        result = subprocess.run(
            ['abcm2ps', '-g', '-O', str(out_prefix), str(in_path)],
            capture_output=True,
        )
        svgs = sorted(td_path.glob('tune*.svg'))
        if not svgs:
            return f'<pre>abcm2ps failed:\n{result.stderr.decode()}\n\nABC:\n{abc}</pre>'
        parts = []
        for s in svgs:
            t = s.read_text()
            t = re.sub(r'^<\?xml[^>]*\?>\s*', '', t)
            t = re.sub(r'<!DOCTYPE[^>]*>\s*', '', t)
            parts.append(t)
        return '\n'.join(parts)


def render_page(slug: str) -> str:
    hymn = json.loads((REPO / 'data' / 'hymns' / f'{slug}.json').read_text())
    abc = build_abc(hymn)
    svg = render_svg(abc)
    title = hymn.get('title') or slug
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        f'<title>{title} — Chopin piano</title>'
        '<link rel="stylesheet" href="../../style.css">'
        '<style>'
        '  .score { background: #fff; padding: 1rem; border: 1px solid var(--rule); }'
        '  pre.abc { background: var(--code-bg); padding: 0.6rem; '
        '            font-size: 0.85rem; overflow-x: auto; }'
        '</style></head><body>'
        '<nav class="shape-nav">'
        '<a href="../../index.html">index</a>'
        '<a href="../../QRG.html">QRG</a>'
        '<a href="../../README.html">README</a>'
        f'<a href="../{slug}.html">← shape table</a>'
        '<a href="../index.html">Chopin index</a>'
        '</nav>'
        f'<h1>{title} — Chopin piano arrangement</h1>'
        '<p>Melody at original rhythm on top; voice-led inner voices held '
        'as a Chopin-style pad. Inner voices re-strike at every bar but '
        'each bar\'s harmony is the voice-leading solver\'s output, not '
        'the source SATB.</p>'
        f'<div class="score">{svg}</div>'
        '<details><summary>ABC source</summary>'
        f'<pre class="abc">{abc}</pre></details>'
        '</body></html>'
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('slug')
    args = ap.parse_args()
    out_dir = SHAPES / 'chopin' / 'piano'
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f'{args.slug}.html'
    out.write_text(render_page(args.slug))
    print(f'wrote {out}')


if __name__ == '__main__':
    main()
