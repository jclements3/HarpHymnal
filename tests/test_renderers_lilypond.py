"""Tests for renderers/lilypond.py — piano-score LilyPond emission.

Scope:
  - render_piano_score() returns a non-empty LilyPond source string
    containing the expected structural markers.
  - pick_style() dispatches bars correctly: bar 1 and last → grand_chord,
    interior phrase-ending → cadence_arp, everything else → strum_pickup.
  - build_score() is wired end-to-end up to (but not including) LilyPond:
    writes a .ly file when compile=False.
  - Pedal MIDI clamp: for every key/mode/chord-root combo, the pedal stays
    ≥ HARP_LOW_MIDI (31).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from grammar.types import (  # noqa: E402
    Bar,
    Key,
    Meter,
    Note,
    Phrase,
    Pitch,
    Roman,
    Song,
    Tempo,
)
from renderers.lilypond import (  # noqa: E402
    HARP_LOW_MIDI,
    build_score,
    diatonic_neighbor,
    pick_style,
    render_piano_score,
    rn_to_root_degree,
    string_to_midi,
)
from trefoil.pool import load_pool  # noqa: E402


@pytest.fixture(scope='module')
def pool():
    return load_pool()


# ──────────────────────────────────────────────────────────────────────────
# Fixture factories
# ──────────────────────────────────────────────────────────────────────────

def _bar(chord_rn: Roman, *melody_pitches: tuple) -> Bar:
    """Build a Bar with a melody of one note per pitch (each 1 beat)."""
    notes = []
    for p in melody_pitches:
        pitch = Pitch(letter=p[0], accidental=p[1] if len(p) > 1 else None,
                      octave=p[2] if len(p) > 2 else 4)  # type: ignore[arg-type]
        notes.append(Note(pitch=pitch, duration=1.0))
    return Bar(melody=tuple(notes), chord=chord_rn, voicing=None)


def _tiny_song(n_bars: int = 2) -> Song:
    """Build a minimal 2-bar C-major song with a simple I/V progression."""
    C_I = Roman(numeral='I', quality=None, inversion=None)
    C_V = Roman(numeral='V', quality=None, inversion=None)
    bars = [
        _bar(C_I, ('C', None, 4), ('E', None, 4), ('G', None, 4)),
        _bar(C_V, ('D', None, 4), ('F', None, 4), ('G', None, 4)),
    ]
    if n_bars > 2:
        for _ in range(n_bars - 2):
            bars.append(_bar(C_I, ('C', None, 4), ('E', None, 4), ('G', None, 4)))
    return Song(
        title='Test Song',
        key=Key(root='C', mode='major'),
        meter=Meter(beats=3, unit=4),  # type: ignore[arg-type]
        tempo=Tempo(value=90, unit=4),  # type: ignore[arg-type]
        bars=tuple(bars),
        phrases=(Phrase(ibars=tuple(range(1, n_bars + 1)), path=None),),
        verses=(),
    )


# ──────────────────────────────────────────────────────────────────────────
# render_piano_score — source structure
# ──────────────────────────────────────────────────────────────────────────

def test_render_piano_score_returns_nonempty_string(pool):
    song = _tiny_song()
    ly = render_piano_score(song, pool)
    assert isinstance(ly, str)
    assert len(ly) > 100


def test_render_piano_score_contains_version(pool):
    song = _tiny_song()
    ly = render_piano_score(song, pool)
    assert '\\version' in ly


def test_render_piano_score_contains_score_block(pool):
    song = _tiny_song()
    ly = render_piano_score(song, pool)
    assert '\\score' in ly
    assert '\\new PianoStaff' in ly


def test_render_piano_score_emits_chord_label(pool):
    """First bar's assignment should surface in a \\markup block — at minimum
    the \\concat/\\bold construction from chord_label_markup appears."""
    song = _tiny_song()
    ly = render_piano_score(song, pool)
    # A chord-fraction label attaches via ``^\markup { ... }``.
    assert '\\markup' in ly
    # And the bold roman is the signature piece of render_rn_markup.
    assert '\\bold' in ly


def test_render_piano_score_uses_title(pool):
    song = _tiny_song()
    song.title = 'Little Test Waltz'
    ly = render_piano_score(song, pool)
    assert 'Little Test Waltz' in ly


def test_render_piano_score_emits_meter_and_key(pool):
    song = _tiny_song()
    ly = render_piano_score(song, pool)
    assert '3/4' in ly
    assert 'c \\major' in ly


# ──────────────────────────────────────────────────────────────────────────
# pick_style — dispatch rules
# ──────────────────────────────────────────────────────────────────────────

def test_pick_style_bar_one_is_grand_chord():
    # bar 1 → grand_chord, no matter what else is going on.
    assert pick_style(1, phrase_end_bars={4}, is_last_bar=False) == 'grand_chord'


def test_pick_style_last_bar_is_grand_chord():
    # Last bar of the piece → grand_chord (overrides phrase-ender rule).
    assert pick_style(8, phrase_end_bars={4, 8}, is_last_bar=True) == 'grand_chord'


def test_pick_style_phrase_ender_interior_is_cadence_arp():
    # Phrase-ending bar that isn't the last → cadence_arp.
    assert pick_style(4, phrase_end_bars={4, 8}, is_last_bar=False) == 'cadence_arp'


def test_pick_style_interior_is_strum_pickup():
    # Non-special bar → strum_pickup.
    assert pick_style(3, phrase_end_bars={4, 8}, is_last_bar=False) == 'strum_pickup'
    assert pick_style(5, phrase_end_bars={4, 8}, is_last_bar=False) == 'strum_pickup'


def test_pick_style_phrase_opener_is_strum_pickup():
    # First bar of a new phrase (not bar 1 of the piece) → strum_pickup.
    assert pick_style(5, phrase_end_bars={4, 8}, is_last_bar=False) == 'strum_pickup'


# ──────────────────────────────────────────────────────────────────────────
# build_score — end-to-end smoke (no compile)
# ──────────────────────────────────────────────────────────────────────────

def test_build_score_writes_ly_without_compiling(pool, tmp_path):
    """Build a tiny Song, write .ly, do NOT invoke lilypond."""
    song = _tiny_song()
    # Persist the song as a data/hymns-style JSON first — build_score reads
    # from that path.
    hymn_dir = tmp_path / 'hymns'
    hymn_dir.mkdir()
    hymn_json_path = hymn_dir / 'test_song.json'
    _dump_song_to_json(song, hymn_json_path)

    out_dir = tmp_path / 'scores'
    result = build_score(hymn_json_path, out_dir, pool, compile=False)

    assert 'ly' in result
    ly_path = Path(result['ly'])
    assert ly_path.exists()
    assert ly_path.suffix == '.ly'
    content = ly_path.read_text(encoding='utf-8')
    assert '\\version' in content
    assert '\\score' in content
    # With compile=False, no PDF/SVG/MIDI keys in the result.
    assert 'pdf' not in result
    assert 'svg' not in result
    assert 'midi' not in result


def test_build_score_slug_matches_title(pool, tmp_path):
    song = _tiny_song()
    song.title = 'My Weird/Hymn  Title!!'
    hymn_dir = tmp_path / 'hymns'
    hymn_dir.mkdir()
    hymn_json_path = hymn_dir / 'my_weird_hymn_title.json'
    _dump_song_to_json(song, hymn_json_path)

    out_dir = tmp_path / 'scores'
    result = build_score(hymn_json_path, out_dir, pool, compile=False)
    assert result['slug'] == 'my_weird_hymn_title'
    assert Path(result['ly']).name == 'my_weird_hymn_title.ly'


# ──────────────────────────────────────────────────────────────────────────
# Pedal MIDI regression guard — always >= HARP_LOW_MIDI
# ──────────────────────────────────────────────────────────────────────────

_EIGHT_KEYS = [
    ('C', 'major'), ('G', 'major'), ('D', 'major'), ('A', 'major'),
    ('F', 'major'), ('Bb', 'major'), ('Eb', 'major'), ('Ab', 'major'),
]

_CHORD_ROOTS = ['I', 'ii', 'iii', 'IV', 'V', 'vi', 'vii○']


def _pedal_midi_for(rn: str, key_root: str, mode: str) -> int:
    """Reproduce the pedal-grace clamp logic from layout_bar_grand."""
    root_degree = rn_to_root_degree(rn)
    assert root_degree is not None, f'root_degree None for {rn!r}'
    pedal_midi = string_to_midi(root_degree, key_root, mode, base_octave=1)
    while pedal_midi < HARP_LOW_MIDI:
        pedal_midi += 12
    return pedal_midi


def test_pedal_midi_stays_above_harp_low_midi_across_keys():
    """For every key × common chord root, the clamped pedal MIDI is ≥ 31 (G1)."""
    for key_root, mode in _EIGHT_KEYS:
        for rn in _CHORD_ROOTS:
            midi = _pedal_midi_for(rn, key_root, mode)
            assert midi >= HARP_LOW_MIDI, (
                f'pedal MIDI {midi} below HARP_LOW_MIDI ({HARP_LOW_MIDI}) '
                f'for {rn!r} in {key_root} {mode}'
            )


def test_pedal_midi_stays_below_bass_staff_top():
    """Soft upper-bound: pedal should land below the top of the bass staff
    (A3 = MIDI 57).  It lives in the ~Bb1–G#2 range after clamp — never a
    mid-register pop.  This is the roadmap's 'always below the bass staff'
    guarantee, with slack for sharp keys' vii° landing a semitone high.
    """
    for key_root, mode in _EIGHT_KEYS:
        for rn in _CHORD_ROOTS:
            midi = _pedal_midi_for(rn, key_root, mode)
            # A3 (bass-staff top) is MIDI 57; the clamp keeps us a full
            # octave below that.
            assert midi < 48, (
                f'pedal MIDI {midi} is too high (expected sub-C3 range) '
                f'for {rn!r} in {key_root} {mode}'
            )


# ──────────────────────────────────────────────────────────────────────────
# diatonic_neighbor — sanity
# ──────────────────────────────────────────────────────────────────────────

def test_diatonic_neighbor_up_in_c_major():
    # C (MIDI 60) → D (62) going up in C major.
    assert diatonic_neighbor(60, 'C', 'major', +1) == 62


def test_diatonic_neighbor_down_in_c_major():
    # G (MIDI 67) → F (65) going down in C major.
    assert diatonic_neighbor(67, 'C', 'major', -1) == 65


# ──────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────

def _dump_song_to_json(song: Song, path: Path) -> None:
    """Emit a data/hymns-style JSON record for a Song.

    Mirrors parsers.abc.song_to_json, but without the ABC-source sidecar —
    we only need the fields renderers/lilypond.py::_song_from_hymn_json
    reads back.
    """
    import json

    def pitch_d(p):
        return {'letter': p.letter, 'accidental': p.accidental, 'octave': p.octave}

    def mel_d(ev):
        if isinstance(ev, Note):
            return {'kind': 'note', 'pitch': pitch_d(ev.pitch),
                    'duration': ev.duration, 'ornaments': []}
        return {'kind': 'rest', 'duration': ev.duration, 'ornaments': []}

    def bar_d(b):
        return {
            'melody': [mel_d(e) for e in b.melody],
            'chord': {'numeral': b.chord.numeral,
                       'quality': b.chord.quality,
                       'inversion': b.chord.inversion},
            'voicing': None,
            'technique': b.technique,
        }

    d = {
        'title': song.title,
        'key': {'root': song.key.root, 'mode': song.key.mode},
        'meter': {'beats': song.meter.beats, 'unit': song.meter.unit},
        'tempo': {'value': song.tempo.value, 'unit': song.tempo.unit},
        'bars': [bar_d(b) for b in song.bars],
        'phrases': [{'ibars': list(p.ibars), 'path': p.path}
                     for p in song.phrases],
        'verses': [],
    }
    with path.open('w', encoding='utf-8') as f:
        json.dump(d, f, indent=2)
