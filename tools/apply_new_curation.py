#!/usr/bin/env python3
"""
apply_new_curation.py — rewrite HarpChordSystem.tex with the new 118-entry
curation produced by tools/analyze_chord_system.py.

What it does:
  1. Loads the analysis picks (42 cycle + 76 pool, inversion-biased, hex alphabet)
  2. Replaces the page-2 Jazz Progressions table rows
  3. Replaces the page-2 Stacked Chords table rows
  4. Trims the interval-from-tonic legend to remove G and H
  5. Writes HarpChordSystem.tex in place (makes a .bak backup first)

Usage:
    python3 tools/apply_new_curation.py
"""
import json
import os
import re
import sys

# Make analyze_chord_system importable from tools/ dir
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze_chord_system import (load_vocab, figure_info, roman_quality,
                                   roman_root_deg, enumerate_candidates,
                                   pick_cycle_winners, pick_pool_winners)

TEX_PATH = 'HarpChordSystem.tex'
JSON_PATH = 'HarpChordSystem.json'


def split_roman(rn):
    """Split a unicode roman-numeral+quality string (e.g. 'IΔ³') into
    (roman_numerals, tex_quality_code) for the \\rn / \\sexc macros.

    Returns macro-ready strings. The quality is converted to the
    macro's expected form:
      ¹ → i, ² → ii, ³ → iii,  ⁷ → 7,  Δ unchanged, ø unchanged, ° unchanged.
    """
    m = re.match(r'^([#b]?[ivIV]+)(.*)$', rn)
    if not m:
        return rn, ''
    roman = m.group(1)
    qual = m.group(2)
    qual = qual.replace('⁷', '7')
    qual = qual.replace('¹', 'i').replace('²', 'ii').replace('³', 'iii')
    return roman, qual


def make_sexc_call(macro_letter, cand, cw, ccw):
    """Produce a \\sexcA/B/C macro invocation.

    Macro signature: \\sexc{rh_rom}{rh_qual}{lh_rom}{lh_qual}{cw}{ccw}{lh_fig}{rh_fig}
    (the macro then renders LH first, RH second visually).
    """
    lh_rom, lh_qual = split_roman(cand['lh']['roman'])
    rh_rom, rh_qual = split_roman(cand['rh']['roman'])
    return (f"\\sexc{macro_letter}"
            f"{{{rh_rom}}}{{{rh_qual}}}{{{lh_rom}}}{{{lh_qual}}}"
            f"{{{cw}}}{{{ccw}}}"
            f"{{{cand['lh_fig']}}}{{{cand['rh_fig']}}}")


def make_spt_call(cand, mood):
    """\\spt{lh_rom}{lh_qual}{rh_rom}{rh_qual}{lh_fig}{rh_fig}{mood}"""
    lh_rom, lh_qual = split_roman(cand['lh']['roman'])
    rh_rom, rh_qual = split_roman(cand['rh']['roman'])
    return (f"\\spt{{{lh_rom}}}{{{lh_qual}}}{{{rh_rom}}}{{{rh_qual}}}"
            f"{{{cand['lh_fig']}}}{{{cand['rh_fig']}}}{{{mood}}}")


# Pool mood names — 76 curated names covering a full range of feelings.
# Kept distinct from the 42 cycle CW/CCW labels (Cloudy, Grounding, Drifting,
# Stepping, Brooding, etc.) so the handout's two vocabularies don't collide.
# Mix of preserved-from-original (Warm, Soulful, Crystalline, etc.), strong
# revivals (Sultry, Commanding, Haunting, Wistful), and new evocatives.
POOL_MOOD_ORDER = [
    # warmth & comfort
    'Warm', 'Soulful', 'Mellow', 'Velvety', 'Plush', 'Sultry', 'Pastoral',
    # brightness & light
    'Bright', 'Radiant', 'Glowing', 'Gilded', 'Shimmering', 'Silvered',
    'Crystalline', 'Sparkling', 'Prismatic', 'Halo',
    # dark & mystery
    'Dark', 'Nocturnal', 'Haunting', 'Mysterious', 'Arcane', 'Veiled',
    'Foggy', 'Shadowed', 'Wistful',
    # motion & flow
    'Cascading', 'Pendular', 'Rustling', 'Floating', 'Wafting', 'Spinning',
    'Curling', 'Ascending', 'Lifted', 'Melting',
    # stillness & breath
    'Still', 'Quiet', 'Settled', 'Anchored', 'Poised', 'Thoughtful',
    'Breathing', 'Resonant',
    # nature & seasons
    'Autumnal', 'Oceanic', 'Tidal', 'Misty', 'Frosted', 'Dewy',
    'Dappled',
    # texture & character
    'Lush', 'Rich', 'Spacious', 'Hollow', 'Airy', 'Soft', 'Open',
    'Hazy', 'Woven', 'Carved', 'Arched', 'Layered', 'Tangled',
    # sound & music
    'Bluesy', 'Jazzy', 'Modal', 'Pealing', 'Ringing', 'Brass',
    # emphasis
    'Commanding', 'Ancient', 'Elegant', 'Ethereal', 'Dreamy', 'Mournful',
]
assert len(POOL_MOOD_ORDER) == 76, f"Need exactly 76 moods, have {len(POOL_MOOD_ORDER)}"


def build_jazz_table_body(cycle_winners):
    """Produce the body of the Jazz Progressions tabular (14 data rows).

    Organized as: rows 1-7 plain (cycle edges in CW walk order),
                  rows 8-14 enriched (same edges).
    Each row has 3 \\sexc calls (one per cycle column).
    """
    # Group by (cycle, variant, edge-from, edge-to)
    by_cycle = {'2nds': {'plain': {}, 'enriched': {}},
                '3rds': {'plain': {}, 'enriched': {}},
                '4ths': {'plain': {}, 'enriched': {}}}
    for variant, (cname, f, t), (score, cand) in cycle_winners:
        by_cycle[cname][variant][(f, t)] = cand

    # Cycle edges in CW traversal order (from the JSON)
    vocab = load_vocab(JSON_PATH)
    edge_order = {
        cname: [(e['from'], e['to']) for e in vocab['cycles'][cname]['edges']]
        for cname in by_cycle
    }

    cycle_colors = {'2nds': 'leafcyan!80!black',
                    '3rds': 'leafred',
                    '4ths': 'leafyellow!80!black'}
    macro_letter = {'2nds': 'A', '3rds': 'B', '4ths': 'C'}

    lines = []
    for variant in ('plain', 'enriched'):
        for row_idx, (edge_2, edge_3, edge_4) in enumerate(
                zip(edge_order['2nds'], edge_order['3rds'], edge_order['4ths'])):
            # Last plain row gets the rotated cycle-label cells
            is_label_row = (variant == 'plain' and row_idx == 6)
            row_parts = []
            for cname, edge in [('2nds', edge_2), ('3rds', edge_3), ('4ths', edge_4)]:
                cand = by_cycle[cname][variant].get(edge)
                if cand is None:
                    # Fallback: use a placeholder; shouldn't happen with 42/42 coverage
                    continue
                cell = f"\\cellcolor{{{cycle_colors[cname]}}}"
                if is_label_row:
                    cyc_num = {'2nds': '2nd', '3rds': '3rd', '4ths': '4th'}[cname]
                    cell += ("\\smash{\\rotatebox{90}{\\color{white}\\scshape "
                             + cyc_num + " cycle}}")
                call = make_sexc_call(macro_letter[cname], cand,
                                      cand.get('cw_label') or '',
                                      cand.get('ccw_label') or '')
                # Pull CW/CCW from the original edge definition in the vocab
                for e in vocab['cycles'][cname]['edges']:
                    if e['from'] == edge[0] and e['to'] == edge[1]:
                        cw = e['cw_label']
                        ccw = e['ccw_label']
                        break
                call = make_sexc_call(macro_letter[cname], cand, cw, ccw)
                row_parts.append(f"{cell} & {call}")
            lines.append(' & '.join(row_parts) + ' \\\\')
    return '\n'.join(lines)


def build_stacked_table_body(pool_winners):
    """Produce the body of the Stacked Chords tabular.

    Existing layout: 4 columns of \\spt calls per row, with \\cellcolor
    separators. The 76 picks produce 19 rows of 4 columns.
    """
    # Sort pool picks for presentation: by LH root, then quality class, then score
    def sort_key(item):
        _score, cand = item
        return (roman_root_deg(cand['lh']['roman']) or 99,
                roman_quality(cand['lh']['roman']))
    sorted_picks = sorted(pool_winners, key=sort_key)

    lines = []
    row = []
    for i, (score, cand) in enumerate(sorted_picks):
        mood = (POOL_MOOD_ORDER[i] if i < len(POOL_MOOD_ORDER)
                else f"Color{i}")
        row.append(make_spt_call(cand, mood))
        if len(row) == 4:
            lines.append(' & \\cellcolor{headerbg} & '.join(row) + ' \\\\')
            row = []
    # Flush partial last row (pad with empty cells if needed)
    if row:
        while len(row) < 4:
            row.append('')
        lines.append(' & \\cellcolor{headerbg} & '.join(row) + ' \\\\')
    return '\n'.join(lines)


def rewrite_tex(original_tex, jazz_body, stacked_body):
    """Perform the three substitutions in the TeX source:
       1. Jazz Progressions tabular data rows
       2. Stacked Chords tabular data rows
       3. Trim interval alphabet (remove G and H rows)
    """
    out = original_tex

    # -------- Interval alphabet trim --------
    # The alphabet in the Interval-from-Tonic legend has one line per letter,
    # like:   \osf{G} & 16 \\
    #         \osf{H} & 17 \\
    # Drop just those two lines.
    out = re.sub(r'\n\\osf\{G\}\s*&\s*16\s*\\\\', '', out)
    out = re.sub(r'\n\\osf\{H\}\s*&\s*17\s*\\\\', '', out)

    # -------- Jazz Progressions tabular --------
    # The existing table begins with the rowcolor+header line and ends with \end{tabular}.
    # We look for the tabular block enclosing \sexcA calls.
    pattern = re.compile(
        r'(\\begin\{tabular\}[^\n]*\n'              # start of tabular
        r'\\rowcolor\{headerbg\}[\s\S]*?\\\\)'      # header row through its \\
        r'[\s\S]*?'                                  # existing body (non-greedy)
        r'(\n\\end\{tabular\})',                    # end
        re.MULTILINE)
    # Find the matching block containing \sexcA to disambiguate from others.
    matches = list(pattern.finditer(out))
    for m in matches:
        if '\\sexcA' in m.group(0):
            replacement = m.group(1) + '\n' + jazz_body + m.group(2)
            out = out[:m.start()] + replacement + out[m.end():]
            break

    # -------- Stacked Chords tabular --------
    matches = list(pattern.finditer(out))
    for m in matches:
        if '\\spt' in m.group(0):
            replacement = m.group(1) + '\n' + stacked_body + m.group(2)
            out = out[:m.start()] + replacement + out[m.end():]
            break

    return out


def main():
    # Load analysis
    vocab = load_vocab(JSON_PATH)
    cbd = vocab['chords_by_pattern_and_degree']
    patterns = [p['id'] for p in vocab['patterns']]
    cycle_edges = {cname: c['edges'] for cname, c in vocab['cycles'].items()}
    candidates = enumerate_candidates(cbd, patterns)
    cycle_winners = pick_cycle_winners(candidates, cycle_edges)
    cycle_pairs = set((w[2][1]['lh_fig'], w[2][1]['rh_fig']) for w in cycle_winners)
    pool_winners = pick_pool_winners(candidates, n=76, excluded_pairs=cycle_pairs)

    print(f"Loaded {len(cycle_winners)} cycle + {len(pool_winners)} pool picks")

    with open(TEX_PATH) as f:
        original = f.read()
    with open(TEX_PATH + '.bak-pre-curation', 'w') as f:
        f.write(original)
    print(f"Backup saved to {TEX_PATH}.bak-pre-curation")

    jazz_body = build_jazz_table_body(cycle_winners)
    stacked_body = build_stacked_table_body(pool_winners)
    new_tex = rewrite_tex(original, jazz_body, stacked_body)

    with open(TEX_PATH, 'w') as f:
        f.write(new_tex)
    print(f"Wrote {TEX_PATH} ({len(new_tex)} bytes)")
    print()
    print("Next steps:")
    print(f"  pdflatex {TEX_PATH}  # verify it compiles")
    print(f"  python3 tools/rebuild_chord_system_json.py {TEX_PATH} {JSON_PATH} -o {JSON_PATH}")


if __name__ == '__main__':
    main()
