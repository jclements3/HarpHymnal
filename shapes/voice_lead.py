#!/usr/bin/env python3
"""Voice-leading-first shape selection (the "Chopin level").

Instead of picking a shape that covers the bar's chord, pick the 4-voice
voicing whose pitches are closest to the previous bar's voicing. The
chord is what the voices land on, not the input.

Algorithm per bar:
  1. Get the bar's chord pitch-classes (e.g. V7 = {D, F#, A, C}).
  2. Enumerate every assignment of 4 voices to the chord-tones (with
     voice-doubling allowed when the chord has fewer pcs than voices).
  3. For each assignment, find the closest octave for each voice such
     that voices stay ordered B < T < A < S (no crossings).
  4. Pick the assignment+octaves that minimise the total semitone
     distance from the previous voicing.

A "voice-leading distance" of zero means the same pitches; small
distances (1-2 semitones) are the smooth side-slips Chopin uses.
Bigger jumps are flagged so the player sees where the writing reaches
beyond pure voice-leading.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product

# Pitch-class names → semitone offset from C.
PC = {'C': 0, 'B#': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
      'E': 4, 'Fb': 4, 'F': 5, 'E#': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
      'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11, 'Cb': 11}


@dataclass(frozen=True)
class Voice:
    letter: str            # 'A'..'G'
    accidental: str        # '', '#', 'b'
    octave: int            # MIDI-style: middle C = C4

    def name(self) -> str:
        return f'{self.letter}{self.accidental}'

    def midi(self) -> int:
        return (self.octave + 1) * 12 + PC[self.name()]


@dataclass(frozen=True)
class Voicing:
    """4 voices in S, A, T, B order (top to bottom)."""
    s: Voice
    a: Voice
    t: Voice
    b: Voice

    def voices(self) -> tuple[Voice, Voice, Voice, Voice]:
        return (self.s, self.a, self.t, self.b)

    def midis(self) -> tuple[int, int, int, int]:
        return (self.s.midi(), self.a.midi(), self.t.midi(), self.b.midi())

    def is_ordered(self) -> bool:
        m = self.midis()
        return m[3] < m[2] < m[1] < m[0]


def voice_distance(v1: Voicing, v2: Voicing) -> int:
    """Sum of absolute semitone moves across all four voices."""
    return sum(abs(a - b) for a, b in zip(v1.midis(), v2.midis()))


# Diatonic chord pitch-classes in a major key, returned as letter names.
def chord_letters(numeral: str, quality: str, key_root: str) -> list[str]:
    """Roman numeral + quality → list of (letter, accidental) pitch classes."""
    SCALE_INDEX = {'C': 0, 'D': 1, 'E': 2, 'F': 3, 'G': 4, 'A': 5, 'B': 6}
    LETTERS = list('CDEFGAB')
    NUMERAL_DEG = {
        'I': 0, 'i': 0, 'II': 1, 'ii': 1, 'ii°': 1,
        'III': 2, 'iii': 2, 'IV': 3, 'iv': 3,
        'V': 4, 'v': 4, 'VI': 5, 'vi': 5,
        'VII': 6, 'vii': 6, 'vii°': 6,
    }
    deg0 = NUMERAL_DEG.get(numeral)
    if deg0 is None:
        return []
    base = SCALE_INDEX[key_root[0]]
    sharps, flats = _key_sig_letters(key_root)
    triad = [(base + deg0 + i * 2) % 7 for i in range(3)]
    if quality == '7':
        triad.append((base + deg0 + 6) % 7)
    out = []
    for idx in triad:
        L = LETTERS[idx]
        acc = '#' if L in sharps else 'b' if L in flats else ''
        out.append(f'{L}{acc}')
    return out


def _key_sig_letters(key_root: str) -> tuple[list[str], list[str]]:
    KEY_SIG = {
        'C':  ([], []),  'G':  (['F'], []),  'D':  (['F', 'C'], []),
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
    return KEY_SIG.get(key_root, ([], []))


def _split_pitch_name(pn: str) -> tuple[str, str]:
    return pn[0], pn[1:]


def voice_around(target_pc: str, near_midi: int) -> Voice:
    """Pick the octave for `target_pc` whose midi is closest to `near_midi`."""
    letter, acc = _split_pitch_name(target_pc)
    pc = PC[target_pc]
    target_oct = (near_midi // 12) - 1
    best: Voice | None = None
    best_dist = 10**9
    for oct_ in range(target_oct - 1, target_oct + 2):
        v = Voice(letter, acc, oct_)
        d = abs(v.midi() - near_midi)
        if d < best_dist:
            best_dist = d
            best = v
    assert best is not None
    return best


def solve_next_voicing(prev: Voicing, chord_pcs: list[str],
                       fixed_s: Voice | None = None) -> Voicing:
    """Voice-leading-first re-voicing.

    Each inner voice (alto / tenor / bass) independently picks the pitch
    with the smallest semitone move from its prior position, drawn only
    from the chord's pitch-classes. A voice that's already on a chord-tone
    holds; one that isn't slips by the smallest step to land on one.

    No "every chord pc must appear" constraint — the resulting voicing
    can omit chord-tones (V7 without the 5th, etc.). What matters is
    each voice's local motion, not that the voicing fully spells the
    label. Voice ordering (B < T < A < S) is enforced.
    """
    if not chord_pcs:
        return prev

    s = fixed_s if fixed_s is not None else prev.s
    s_midi = s.midi()

    def pick(prev_voice: Voice, ceiling_midi: int) -> Voice:
        prev_pc = f'{prev_voice.letter}{prev_voice.accidental}'
        prev_midi = prev_voice.midi()
        # If the voice is already on a chord-tone, it holds (zero motion).
        if prev_pc in chord_pcs:
            if prev_midi < ceiling_midi:
                return prev_voice
        # Otherwise pick the chord-tone whose closest octave is the
        # nearest pitch — i.e. the smallest semitone move.
        best: Voice | None = None
        best_dist = 10**9
        for pc in chord_pcs:
            cand = voice_around(pc, prev_midi)
            if cand.midi() >= ceiling_midi:
                cand = Voice(cand.letter, cand.accidental, cand.octave - 1)
                if cand.midi() >= ceiling_midi:
                    continue
            d = abs(cand.midi() - prev_midi)
            if d < best_dist:
                best_dist = d
                best = cand
        return best if best is not None else prev_voice

    a = pick(prev.a, s_midi)
    t = pick(prev.t, a.midi())
    b = pick(prev.b, t.midi())

    return Voicing(s=s, a=a, t=t, b=b)


def initial_voicing_with_melody(chord_pcs: list[str], melody_s: Voice) -> Voicing:
    """Pick a starting voicing where the soprano is the given melody pitch
    and A/T/B occupy reasonable SATB ranges below it.

    Bootstrap is a "pseudo-prev" voicing centred around stock SATB octaves
    (S=4, A=3, T=3, B=2); we then run the constrained solver against it so
    the result is a plausibly-distributed voicing rooted on the melody.
    """
    pseudo_prev = Voicing(
        s=Voice(melody_s.letter, melody_s.accidental, melody_s.octave),
        a=Voice('B', '', 3),
        t=Voice('G', '', 3),
        b=Voice('G', '', 2),
    )
    return solve_next_voicing(pseudo_prev, chord_pcs, fixed_s=melody_s)


def initial_voicing_for(chord_pcs: list[str], anchor_octaves=(4, 3, 3, 2)) -> Voicing:
    """Bootstrap voicing for the first bar: root-position close voicing
    around the given S/A/T/B target octaves."""
    if len(chord_pcs) < 3:
        return Voicing(
            Voice('C', '', 4), Voice('G', '', 3), Voice('E', '', 3), Voice('C', '', 2)
        )
    # SATB top-down: 5 / 3 / 1 / 1
    pc_for_voice = [chord_pcs[2 % len(chord_pcs)],   # S = 5
                    chord_pcs[1 % len(chord_pcs)],   # A = 3
                    chord_pcs[0 % len(chord_pcs)],   # T = 1
                    chord_pcs[0 % len(chord_pcs)]]   # B = 1 (octave below)
    voices = []
    for pc, oct_target in zip(pc_for_voice, anchor_octaves):
        letter, acc = _split_pitch_name(pc)
        # Force the voice into its target octave (raise/lower if pc is below/above).
        v = Voice(letter, acc, oct_target)
        voices.append(v)
    s, a, t, b = voices
    v = Voicing(s, a, t, b)
    # If voices crossed (rare for SATB defaults), nudge the bass down.
    while not v.is_ordered() and v.b.octave > 0:
        v = Voicing(v.s, v.a, v.t, Voice(v.b.letter, v.b.accidental, v.b.octave - 1))
    return v


def voicing_motion(prev: Voicing, curr: Voicing) -> dict[str, int]:
    """Return `{'S': dt, 'A': dt, 'T': dt, 'B': dt}` semitone deltas
    (positive = up)."""
    return {
        'S': curr.s.midi() - prev.s.midi(),
        'A': curr.a.midi() - prev.a.midi(),
        'T': curr.t.midi() - prev.t.midi(),
        'B': curr.b.midi() - prev.b.midi(),
    }


def voicing_to_shape_html(v: Voicing, key_root: str, deg_html_fn) -> str:
    """Render a voicing as a two-shape Chopin-style token:
    `<oct>L^<bass-deg><B-T-interval> <oct>R^<alto-deg><A-S-interval>`."""
    SCALE_INDEX = {'C': 0, 'D': 1, 'E': 2, 'F': 3, 'G': 4, 'A': 5, 'B': 6}

    def step(p1: Voice, p2: Voice) -> int:
        return (SCALE_INDEX[p2.letter] - SCALE_INDEX[p1.letter]) + (p2.octave - p1.octave) * 7

    def deg(letter: str) -> int:
        return ((SCALE_INDEX[letter] - SCALE_INDEX[key_root[0]]) % 7) + 1

    bt = step(v.b, v.t)
    asp = step(v.a, v.s)
    if bt <= 0 or asp <= 0:
        return ''
    bass_deg = deg(v.b.letter)
    alto_deg = deg(v.a.letter)
    return (
        f'{v.b.octave}L{deg_html_fn(bass_deg)}{(bt + 1):x} '
        f'{v.a.octave}R{deg_html_fn(alto_deg)}{(asp + 1):x}'
    )
