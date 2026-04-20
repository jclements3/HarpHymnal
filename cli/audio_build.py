"""Render harp-timbre audio (m4a/AAC) from every hymn's .midi.

Pipeline:  data/scores/tech_full/<slug>.midi
             --fluidsynth FluidR3/MuseScore SoundFont-->  <slug>.wav (temp)
             --ffmpeg AAC mono 48k-->                      data/audio/tech_full/<slug>.m4a

The LilyPond template sets ``\\set Staff.midiInstrument = "orchestral harp"``
on both staves, so the MIDI already carries program 46 (Orchestral Harp);
fluidsynth just maps that to the soundfont's harp sample.  We use mono
48 kbps AAC (HE-AAC isn't in this ffmpeg build) to keep the bundle small:
~250 KB per hymn, ~70 MB for the full 279-hymn corpus.

Usage:
    python3 -m cli.audio_build --all                 # render every hymn
    python3 -m cli.audio_build --title amazing_grace # render one
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DEFAULT_MIDI_DIR = REPO / 'data' / 'scores' / 'tech_full'
DEFAULT_OUT_DIR = REPO / 'data' / 'audio' / 'tech_full'
DEFAULT_SF = Path('/tmp/MuseScore_General.sf3')


def render_one(midi_path: Path, out_dir: Path, sf_path: Path,
               stagger_ms: float) -> tuple[str, bool, str]:
    """Strum-post-process MIDI, then fluidsynth -> WAV -> AAC m4a.

    Returns ``(slug, ok, error_msg)``.
    """
    from renderers.midi_strum import strum_midi
    slug = midi_path.stem
    out_path = out_dir / f'{slug}.m4a'
    try:
        with tempfile.NamedTemporaryFile(suffix='.midi', delete=False) as tmp_m:
            strummed = Path(tmp_m.name)
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_w:
            wav_path = Path(tmp_w.name)
        # Step 0: strum-stagger the MIDI (LilyPond emits blocks; harp needs a roll).
        strum_midi(midi_path, strummed, stagger_ms=stagger_ms)
        # Step 1: fluidsynth -> WAV
        r1 = subprocess.run(
            ['fluidsynth', '-ni', '-g', '1.0',
             '-F', str(wav_path), '-r', '22050',
             str(sf_path), str(strummed)],
            capture_output=True, text=True, timeout=120,
        )
        if r1.returncode != 0:
            return (slug, False, f'fluidsynth: {r1.stderr[-200:]}')
        # Step 2: ffmpeg WAV -> AAC m4a (mono, 48k)
        r2 = subprocess.run(
            ['ffmpeg', '-y', '-i', str(wav_path),
             '-ac', '1', '-c:a', 'aac', '-b:a', '48k',
             str(out_path)],
            capture_output=True, text=True, timeout=60,
        )
        strummed.unlink(missing_ok=True)
        wav_path.unlink(missing_ok=True)
        if r2.returncode != 0:
            return (slug, False, f'ffmpeg: {r2.stderr[-200:]}')
        return (slug, True, '')
    except Exception as e:
        return (slug, False, f'{type(e).__name__}: {e}')


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog='python -m cli.audio_build',
        description='Render harp audio (AAC m4a) from hymn MIDI files.',
    )
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument('--all', action='store_true',
                   help='Render every .midi under --midi-dir.')
    g.add_argument('--title',
                   help='Render one hymn by slug or title-substring match.')
    p.add_argument('--midi-dir', type=Path, default=DEFAULT_MIDI_DIR)
    p.add_argument('--out-dir', type=Path, default=DEFAULT_OUT_DIR)
    p.add_argument('--soundfont', type=Path, default=DEFAULT_SF,
                   help='.sf2/.sf3 soundfont file (default: %(default)s).')
    p.add_argument('--jobs', type=int, default=None,
                   help='Parallel workers (default: CPU count).')
    p.add_argument('--stagger-ms', type=float, default=20.0,
                   help='Per-note strum delta in milliseconds (default: %(default)s).')
    args = p.parse_args(argv)

    if not args.soundfont.exists():
        print(f'error: soundfont not found at {args.soundfont}', file=sys.stderr)
        return 2
    args.out_dir.mkdir(parents=True, exist_ok=True)

    midis = sorted(args.midi_dir.glob('*.midi'))
    if args.title:
        needle = args.title.lower()
        midis = [m for m in midis if needle in m.stem.lower()]
        if not midis:
            print(f'no MIDI matching {args.title!r} in {args.midi_dir}',
                  file=sys.stderr)
            return 1

    jobs = args.jobs or max(1, os.cpu_count() or 1)
    ok = 0
    fail = 0
    with ProcessPoolExecutor(max_workers=jobs) as ex:
        futures = {
            ex.submit(render_one, m, args.out_dir, args.soundfont,
                      args.stagger_ms): m
            for m in midis
        }
        for fut in as_completed(futures):
            slug, good, err = fut.result()
            if good:
                ok += 1
            else:
                fail += 1
                print(f'FAIL {slug}: {err}', file=sys.stderr)
    total = ok + fail
    print(f'done: {ok}/{total} ok, {fail} failed')
    return 0 if fail == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
