#!/usr/bin/env python3
"""
rebuild_chord_system_json.py — rebuild HarpChordSystem.json by parsing the
authoritative HarpChordSystem.tex source.

The TeX \sexcA/\sexcB/\sexcC macros take args in order:
    {#1 = RH-rom}{#2 = RH-qual}{#3 = LH-rom}{#4 = LH-qual}
    {#5 = CW-label}{#6 = CCW-label}
    {#7 = LH-figure}{#8 = RH-figure}

The prior Claude's JSON swapped LH/RH because it extracted positionally.
This script does it right by encoding the macro's actual argument order.

The \spt macro (pool entries) takes:
    {#1 = LH-rom}{#2 = LH-qual}{#3 = RH-rom}{#4 = RH-qual}
    {#5 = LH-figure}{#6 = RH-figure}{#7 = Name/Mood}

Usage:
    python3 tools/rebuild_chord_system_json.py \
        HarpChordSystem.tex HarpChordSystem.json \
        -o HarpChordSystem.rebuilt.json
"""
import argparse
import json
import re


def parse_braced_args(s, start, n):
    """From s[start:] read n brace-balanced {...} args and return (list, new_pos).
    Handles nested braces. Returns (None, start) if parse fails."""
    args = []
    pos = start
    for _ in range(n):
        # Skip whitespace
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


def tex_to_plain(s):
    """Strip common LaTeX artifacts from captured cells."""
    if not s:
        return ''
    # \inv{1} → ¹ (keep unicode for JSON readability)
    s = re.sub(r'\\inv\{1\}', '\u00b9', s)
    s = re.sub(r'\\inv\{2\}', '\u00b2', s)
    s = re.sub(r'\\inv\{3\}', '\u00b3', s)
    # \halfdim → ø
    s = s.replace(r'\halfdim', '\u00f8')
    # \rp{} or \rp → +
    s = re.sub(r'\\rp\{\}', '+', s)
    s = s.replace(r'\rp', '+')
    # \osf{x} → x  (iterate because can be nested)
    prev = None
    while prev != s:
        prev = s
        s = re.sub(r'\\osf\{([^{}]*)\}', r'\1', s)
    s = s.strip()
    return s


def extract_jazz(tex):
    """Parse all \\sexcA/B/C calls. Assign cycle by macro letter variant.
    Uses brace-balanced arg parsing so nested {\\halfdim\\osf{7}} works."""
    entries = []
    cycle_by_letter = {'A': '2nds', 'B': '3rds', 'C': '4ths'}
    for m in re.finditer(r'\\sexc([ABC])', tex):
        letter = m.group(1)
        args, _end = parse_braced_args(tex, m.end(), 8)
        if args is None:
            continue
        # Macro args: #1=RH-rom, #2=RH-qual, #3=LH-rom, #4=LH-qual,
        #             #5=CW-label, #6=CCW-label, #7=LH-fig, #8=RH-fig
        rh_rom, rh_qual, lh_rom, lh_qual = args[0], args[1], args[2], args[3]
        cw_label, ccw_label = args[4], args[5]
        lh_fig, rh_fig = args[6], args[7]
        entries.append({
            'cycle': cycle_by_letter[letter],
            'lh_roman': tex_to_plain(lh_rom) + tex_to_plain(lh_qual),
            'lh_figure': tex_to_plain(lh_fig),
            'rh_roman': tex_to_plain(rh_rom) + tex_to_plain(rh_qual),
            'rh_figure': tex_to_plain(rh_fig),
            'cw_label': tex_to_plain(cw_label),
            'ccw_label': tex_to_plain(ccw_label),
        })
    return entries


def extract_pool(tex):
    """Parse all \\spt calls (stacked/pool entries)."""
    entries = []
    for m in re.finditer(r'\\spt', tex):
        args, _end = parse_braced_args(tex, m.end(), 7)
        if args is None:
            continue
        # #1=LH-rom, #2=LH-qual, #3=RH-rom, #4=RH-qual,
        # #5=LH-fig, #6=RH-fig, #7=Mood
        lh_rom, lh_qual, rh_rom, rh_qual = args[0], args[1], args[2], args[3]
        lh_fig, rh_fig, mood = args[4], args[5], args[6]
        entries.append({
            'lh_roman': tex_to_plain(lh_rom) + tex_to_plain(lh_qual),
            'lh_figure': tex_to_plain(lh_fig),
            'rh_roman': tex_to_plain(rh_rom) + tex_to_plain(rh_qual),
            'rh_figure': tex_to_plain(rh_fig),
            'mood': tex_to_plain(mood),
        })
    return entries


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('tex', help='HarpChordSystem.tex (authoritative source)')
    ap.add_argument('existing_json', help='Existing HarpChordSystem.json (for prose)')
    ap.add_argument('-o', '--output', required=True)
    args = ap.parse_args()

    with open(args.tex) as f:
        tex = f.read()
    with open(args.existing_json) as f:
        existing = json.load(f)

    # Keep prose/conventions/patterns/cycles/how_to_use from existing; replace entries
    jazz_entries = extract_jazz(tex)
    pool_entries = extract_pool(tex)

    print(f'Extracted {len(jazz_entries)} complex-cycle entries (expected 42)')
    print(f'Extracted {len(pool_entries)} pool entries (expected 76)')

    # Count by cycle
    by_cyc = {}
    for e in jazz_entries:
        by_cyc[e['cycle']] = by_cyc.get(e['cycle'], 0) + 1
    print(f'Complex-cycle breakdown: {by_cyc}')

    rebuilt = {
        'schema_version': existing.get('schema_version', 1) + 1 if isinstance(existing.get('schema_version'), int) else 2,
        'title': existing.get('title', 'Harp Chord System — JSON reference'),
        'source': 'HarpChordSystem.tex (authoritative) via tools/rebuild_chord_system_json.py',
        '_rebuilt_from_tex': True,
        '_pedagogy_reference': 'See HARP_CHORD_SYSTEM.md at repo root for the complete pedagogical model.',
        'how_to_use': existing.get('how_to_use', {}),
        'conventions': existing.get('conventions', {}),
        'instrument': existing.get('instrument', {}),
        'patterns': existing.get('patterns', []),
        'chords_by_pattern_and_degree': existing.get('chords_by_pattern_and_degree', {}),
        'cycles': existing.get('cycles', {}),
        'jazz_progressions': {
            'description': 'Paired LH/RH voicings along the three diatonic cycles. CW ascends, CCW descends. 42 entries (3 cycles × 14 rows).',
            '_canonical_name': 'complex chord cycles',
            'entries': jazz_entries,
        },
        'stacked_chords': {
            'description': 'Single-sonority two-handed fractions (LH over RH). Each has one mood name. 76 entries. Together with the 42 jazz_progressions entries these form the 118 legal chord fractions on the harp.',
            '_canonical_name': 'chord fractions pool',
            'entries': pool_entries,
        },
    }

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(rebuilt, f, indent=2, ensure_ascii=False)
    print(f'Wrote {args.output}')


if __name__ == '__main__':
    main()
