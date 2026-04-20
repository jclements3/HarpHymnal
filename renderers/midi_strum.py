"""Post-process a LilyPond-emitted .midi to add harp-strum articulation.

LilyPond's ``\\arpeggio`` is purely a visual wavy line — the MIDI plays the
chord as a simultaneous block.  A harp physically can't do that; the
characteristic harp sound is a quick roll from bass upward.  This module
rewrites a .midi so that every simultaneous note-on group of ≥2 pitches
is staggered by a configurable millisecond delta per note (lowest pitch
first, mimicking a real harp's bass-to-treble strum).

Note-offs are left untouched, so the strummed notes all release together
(arpeggiated attack, sustained ring — the harp idiom).

Usage:
    from renderers.midi_strum import strum_midi
    strum_midi(Path('amazing_grace.midi'),
               Path('amazing_grace.strummed.midi'),
               stagger_ms=20.0)
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import mido


DEFAULT_STAGGER_MS = 20.0  # harp-natural pluck interval
DEFAULT_MIN_CHORD = 2      # stagger chords of >= 2 notes (include dyads)


def _tempo_us_per_beat(mid: mido.MidiFile) -> int:
    """Return the microseconds-per-beat from the first set_tempo meta,
    defaulting to 500000 (120 BPM) if none is present."""
    for trk in mid.tracks:
        for msg in trk:
            if msg.type == 'set_tempo':
                return int(msg.tempo)
    return 500000


def _ms_to_ticks(ms: float, ticks_per_beat: int, us_per_beat: int) -> int:
    """Convert milliseconds to MIDI ticks under the given tempo."""
    ms_per_beat = us_per_beat / 1000.0
    return max(1, int(round(ms * ticks_per_beat / ms_per_beat)))


def _strum_track(track: mido.MidiTrack,
                 stagger_ticks: int,
                 min_chord: int) -> mido.MidiTrack:
    """Re-emit ``track`` with simultaneous note-ons staggered by tick delta.

    Notes are sorted low-pitch-first within each chord so the strum rolls
    upward (standard harp/arpeggio direction).  Note-offs are untouched,
    so notes release together.
    """
    # Absolute-time event list.
    abs_events: list[tuple[int, int, mido.Message]] = []
    # ^ (abs_tick, original_index, msg) — original_index preserves the
    #   stable order of events that share an abs_tick but aren't note-ons.
    t = 0
    for i, msg in enumerate(track):
        t += msg.time
        abs_events.append((t, i, msg))

    # Group note-ons by absolute tick.
    chord_groups: dict[int, list[int]] = {}  # abs_tick -> list of abs_events indices
    for idx, (at, _, msg) in enumerate(abs_events):
        if msg.type == 'note_on' and getattr(msg, 'velocity', 0) > 0:
            chord_groups.setdefault(at, []).append(idx)

    # Stagger each chord: sort ascending by pitch, offset each by k*stagger_ticks.
    for at, indices in chord_groups.items():
        if len(indices) < min_chord:
            continue
        indices.sort(key=lambda i: abs_events[i][2].note)
        for k, i in enumerate(indices):
            if k == 0:
                continue
            new_at = at + k * stagger_ticks
            at_old, orig, m = abs_events[i]
            abs_events[i] = (new_at, orig, m)

    # Stable sort by (abs_tick, original_index) to preserve order within a tick.
    abs_events.sort(key=lambda t: (t[0], t[1]))

    # Rebuild delta-time track.
    new_track = mido.MidiTrack()
    prev_t = 0
    for abs_t, _orig, msg in abs_events:
        delta = max(0, abs_t - prev_t)
        new_track.append(msg.copy(time=delta))
        prev_t = abs_t
    return new_track


def strum_midi(src: Path, dst: Optional[Path] = None,
               *, stagger_ms: float = DEFAULT_STAGGER_MS,
               min_chord: int = DEFAULT_MIN_CHORD) -> Path:
    """Read ``src``, strum-stagger its chords, write to ``dst`` (or overwrite).

    Returns the path that was written to.  ``stagger_ms`` is per-note delta
    (20 ms → a 4-note chord spans 60 ms of attack; a 5-note chord spans 80 ms).
    """
    src = Path(src)
    dst = Path(dst) if dst is not None else src
    mid = mido.MidiFile(str(src))
    us_per_beat = _tempo_us_per_beat(mid)
    stagger_ticks = _ms_to_ticks(stagger_ms, mid.ticks_per_beat, us_per_beat)
    new_tracks = [_strum_track(trk, stagger_ticks, min_chord)
                  for trk in mid.tracks]
    out = mido.MidiFile(ticks_per_beat=mid.ticks_per_beat, type=mid.type)
    out.tracks = new_tracks
    out.save(str(dst))
    return dst


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description='Add harp-strum to a .midi file.')
    p.add_argument('src', type=Path)
    p.add_argument('dst', type=Path, nargs='?', default=None,
                   help='Output path (default: overwrite src).')
    p.add_argument('--stagger-ms', type=float, default=DEFAULT_STAGGER_MS)
    p.add_argument('--min-chord', type=int, default=DEFAULT_MIN_CHORD)
    args = p.parse_args()
    out = strum_midi(args.src, args.dst,
                     stagger_ms=args.stagger_ms, min_chord=args.min_chord)
    print(f'wrote {out}')
