#!/usr/bin/env python3
"""Build ``tablet_app/app/src/main/assets/harphymnal_drills.json``.

Two data sources feed the tablet drills app:

1. **Pool cards** — one per pool fraction (all 118). Source: ``data/trefoil/HarpTrefoil.json``.
   Each card carries ipool, source (``paths``/``reserve``), LH/RH roman labels,
   LH/RH figures, rendered note-letter strings (key of C: LH lowercase, RH
   UPPERCASE), and the cycle / mood / CW-CCW metadata.

2. **Technique drill cards** — from→to pairs per technique. Source: the
   §3.6.1 technique inventory in ``SDD.md``. That inventory already has the
   three filters pre-applied (duplicate pattern-pair dedup, MIN_GAP=0 same-
   string-overlap reject, MAX_GAP=6 wide-spread reject — from
   ``grammar/constants.py``). Parsing it keeps us one-to-one with the
   pedagogical handout.

Run:

    python3 tablet_app/build_drill_data.py

Writes ``tablet_app/app/src/main/assets/harphymnal_drills.json``.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Pull the bounds from the single source of truth in the repo (imported for
# the record-in-JSON side-effect — the SDD inventory has already applied them
# but we want to assert the numbers match).
from grammar.constants import MIN_GAP, MAX_GAP, POOL_SIZE  # noqa: E402
from grammar.parse import parse_figure  # noqa: E402


POOL_JSON = ROOT / 'data' / 'trefoil' / 'HarpTrefoil.json'
SDD_MD = ROOT / 'SDD.md'
OUT_PATH = Path(__file__).resolve().parent / 'app' / 'src' / 'main' / 'assets' / 'harphymnal_drills.json'


# ─────────────────────── Figure → note-letters (key of C) ────────────────
#
# String positions 1..15 on the harp map deterministically to pitch letters in
# the key of C:
#
#     1  2  3  4  5  6  7  8  9  10 11 12 13 14 15
#     c  d  e  f  g  a  b  c  d  e  f  g  a  b  c
#
# A "figure" such as ``133`` means: start on position 1 (c), add intervals
# 3, 3. Interval N = "jump N-1 string steps forward". So from c, +2 → e, +2 → g.
# Result: ``ceg``. This matches the handout's rendering and the SDD inventory's
# note-string form.

_DIATONIC_LETTERS = 'cdefgabcdefgabc'  # positions 1..15 (0-indexed 0..14)


# Lever-harp accessible keys in the standard raise order from the
# Eb-stored tuning (no levers raised) up to E (seven levers raised).
# Each value is the 7-note diatonic scale starting on that tonic.
KEYS: list[tuple[str, list[str]]] = [
    ('Eb', ['Eb','F', 'G', 'Ab','Bb','C', 'D']),
    ('Bb', ['Bb','C', 'D', 'Eb','F', 'G', 'A']),
    ('F',  ['F', 'G', 'A', 'Bb','C', 'D', 'E']),
    ('C',  ['C', 'D', 'E', 'F', 'G', 'A', 'B']),
    ('G',  ['G', 'A', 'B', 'C', 'D', 'E', 'F#']),
    ('D',  ['D', 'E', 'F#','G', 'A', 'B', 'C#']),
    ('A',  ['A', 'B', 'C#','D', 'E', 'F#','G#']),
    ('E',  ['E', 'F#','G#','A', 'B', 'C#','D#']),
]


def figure_to_notes(fig: str, *, upper: bool, key: str = 'C') -> str:
    """Render a figure as pitch letters in `key`.

    A figure like ``'133'`` means: start on scale-position 1, then intervals
    3, 3 (interval N = skip N-1 diatonic steps).  In the key of C the result
    is ``ceg``; in G ``gbd``; in Eb ``EbGBb`` (RH) or ``ebgbb`` (LH).

    ``upper=True`` → RH style (pitch letter UPPERCASE); ``upper=False`` → LH
    style (pitch letter lowercase).  Accidentals (``#`` / ``b``) always stay
    lowercase and keep their position after the letter — so "Ab" in LH form
    becomes ``ab`` (note: both lowercase) while in RH form it stays ``Ab``.
    """
    anchor, intervals = parse_figure(fig)
    scale = dict(KEYS)[key]
    positions = [anchor]
    cur = anchor
    for ivl in intervals:
        cur += ivl - 1
        positions.append(cur)

    out = []
    for p in positions:
        pitch = scale[(p - 1) % 7]    # e.g. "Eb", "F#", "C"
        letter, acc = pitch[0], pitch[1:]
        out.append((letter.upper() if upper else letter.lower()) + acc)
    return ''.join(out)


# ─────────────────────── Pool cards (all 118) ────────────────────────────

def build_pool_cards() -> list[dict]:
    """One card per pool fraction, walking paths then reserve in load order.

    Uses the same degree-prefixed ipool scheme as ``trefoil/pool.py`` so that
    the on-tablet IDs match every other tool in the repo.
    """
    data = json.loads(POOL_JSON.read_text(encoding='utf-8'))

    # Numeral → degree, matching trefoil.pool._NUMERAL_TO_DEGREE (longest-first
    # match so 'vii' beats 'vi').
    NUM_PREFIXES = ('vii', 'iii', 'iv', 'vi', 'v', 'ii', 'i',
                    'VII', 'III', 'IV', 'VI', 'V', 'II', 'I')
    NUM_TO_DEG = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7,
                  'i': 1, 'ii': 2, 'iii': 3, 'iv': 4, 'v': 5, 'vi': 6, 'vii': 7}

    def lh_degree(lh_roman: str) -> int:
        s = re.sub(r'^[b#]', '', lh_roman)
        for n in NUM_PREFIXES:
            if s.startswith(n):
                return NUM_TO_DEG[n]
        raise ValueError(f'no numeral in {lh_roman!r}')

    rank_per_degree = {d: 0 for d in range(1, 8)}
    base_entries: list[dict] = []    # (ipool, source, raw) before key explosion

    for raw in data['paths']['entries']:
        deg = lh_degree(raw['lh_roman'])
        rank_per_degree[deg] += 1
        ipool = f'{deg}{rank_per_degree[deg]:02d}'
        base_entries.append({'ipool': ipool, 'source': 'paths', 'raw': raw})

    for raw in data['reserve']['entries']:
        deg = lh_degree(raw['lh_roman'])
        rank_per_degree[deg] += 1
        ipool = f'{deg}{rank_per_degree[deg]:02d}'
        base_entries.append({'ipool': ipool, 'source': 'reserve', 'raw': raw})

    assert len(base_entries) == POOL_SIZE, \
        f'expected {POOL_SIZE} pool fractions, got {len(base_entries)}'

    # One pool card with all 118 fractions, interleaved with section
    # markers.  The card flows as a single grid: section header → that
    # degree's fractions → next section header → next fractions → ...
    DEG_NAMES = {1: 'I', 2: 'ii', 3: 'iii', 4: 'IV', 5: 'V', 6: 'vi', 7: 'vii°'}
    DEG_TONICS = {1: 'C', 2: 'D', 3: 'E', 4: 'F', 5: 'G', 6: 'A', 7: 'B'}

    by_deg: dict[int, list[dict]] = {d: [] for d in range(1, 8)}
    for entry in base_entries:
        raw = entry['raw']
        d = lh_degree(raw['lh_roman'])
        by_deg[d].append({
            'type': 'fraction',
            'ipool': entry['ipool'],
            'lh_notes': figure_to_notes(raw['lh_figure'], upper=False),
            'rh_notes': figure_to_notes(raw['rh_figure'], upper=True),
        })

    items: list[dict] = []
    for d in range(1, 8):
        items.append({
            'type': 'section',
            'chord': DEG_NAMES[d],
            'tonic': DEG_TONICS[d],
        })
        items.extend(by_deg[d])

    # Return the raw pool item stream; pagination happens globally in
    # build() so pool and techniques share flash card pages.
    return items


# ─────────────────── Technique-drill cards (from SDD.md) ─────────────────
#
# SDD §3.6.1 headers look like:
#     #### Third sub   *(slide both hands down 2 degrees; same pattern)*
# and each bullet like:
#     * **I-vi**   bcegABDF gaceFGBD, gceFAD eacDFB, ...
#
# Parsing rules:
#   - Split at `####` headers. The header name is the substring between
#     `####` and the first opening `*(`. Strip trailing whitespace.
#   - Each bullet inside a header section is one function-pair (or single
#     function — e.g. Inversion's `**I**` means the I chord slot).
#   - The comma-separated sequence after the function label is a list of
#     from-to pairs: each pair is exactly two whitespace-separated tokens,
#     e.g. `bcegABDF gaceFGBD` = (from, to).

_HEADER_RE = re.compile(r'^####\s+(?P<name>[^*\n]+?)\s+\*\((?P<rule>[^*]+)\)\*\s*$')
_BULLET_RE = re.compile(r'^\*\s+\*\*(?P<label>[^*]+?)\*\*\s+(?P<body>.+)$')

# Family colors for the header banner (matches handout SDD colors).
_FAMILY_COLOR = {
    'substitution': '#C0605A',
    'approach':     '#4080A0',
    'voicing':      '#50A050',
    'placement':    '#7B4A9E',
}

# Which family each displayed header belongs to. Mirrors drills/build.py's
# _FAMILY, with Density split into (drop)/(extend) the way SDD shows them.
_TECHNIQUE_FAMILY: dict[str, str] = {
    'Third sub':           'substitution',
    'Quality sub':         'substitution',
    'Modal reframing':     'substitution',
    'Deceptive sub':       'substitution',
    'Common-tone pivot':   'substitution',
    'Step approach':       'approach',
    'Third approach':      'approach',
    'Dominant approach':   'approach',
    'Suspension approach': 'approach',
    'Double approach':     'approach',
    'Inversion':           'voicing',
    'Density (drop)':      'voicing',
    'Density (extend)':    'voicing',
    'Stacking':            'voicing',
    'Pedal':               'voicing',
    'Voice leading':       'voicing',
    'Open/closed spread':  'voicing',
    'Anticipation':        'placement',
    'Delay':               'placement',
}

# Drillable techniques = those with at least one concrete pattern-pair entry
# in the SDD inventory. Build order matches the SDD reading order; empty
# techniques (Modal reframing, Dominant approach, Suspension approach, Double
# approach, Voice leading, Anticipation, Delay) are still represented in
# the output JSON with empty ``cards`` so the tablet UI can show them but
# grey them out. That way all 14 techniques the task mentions remain
# present — 12 with content + 2 (Modal reframing, Voice leading) without.


def parse_sdd_inventory() -> dict[str, dict]:
    """Parse SDD §3.6.1 into ``{name: {name, rule, family, color, cards}}``."""
    text = SDD_MD.read_text(encoding='utf-8')

    # Limit to section 3.6.1 — bail out once section 3.7 starts.
    start = text.find('### 3.6.1')
    end = text.find('### 3.7', start)
    body = text[start:end] if (start != -1 and end != -1) else text

    sections: dict[str, dict] = {}
    current: dict | None = None
    for line in body.splitlines():
        hm = _HEADER_RE.match(line)
        if hm:
            name = hm.group('name').strip()
            rule = hm.group('rule').strip()
            family = _TECHNIQUE_FAMILY.get(name, 'voicing')
            current = {
                'name':   name,
                'rule':   rule,
                'family': family,
                'color':  _FAMILY_COLOR[family],
                # Each bullet (function-pair) becomes ONE card; the card's
                # body is a list of from/to pairs that flow as a paragraph
                # on the tablet, same way the pool card flows its fractions.
                'cards':  [],
            }
            sections[name] = current
            continue
        if current is None:
            continue
        bm = _BULLET_RE.match(line)
        if not bm:
            continue
        label = bm.group('label').strip()
        pairs_body = bm.group('body').strip()
        pairs: list[dict] = []
        for raw_pair in pairs_body.split(','):
            tokens = raw_pair.strip().split()
            if len(tokens) == 2:
                pairs.append({'from': tokens[0], 'to': tokens[1]})
            elif len(tokens) == 1:
                # Single-token entries (Pedal-style) render as a fraction
                # with only the from-side, mirroring the pool card's
                # ipool/notes stack.
                pairs.append({'from': tokens[0], 'to': ''})
        if pairs:
            current['cards'].append({
                'label': label,
                'pairs': pairs,
            })
    return sections


# ─────────────────────── Card-balancing pass ────────────────────────────
#
# Some function-pair bullets only contain 1 or 2 pairs (rare gestures).
# One-pair cards are wasteful as flash cards, so merge adjacent small cards
# into a single combined card per technique.  Merge rule:
#
#   while any card.pairs.length < SMALL_THRESHOLD:
#       merge that card with its neighbour (prefer the smaller-total neighbour
#       so merged cards stay balanced).  Labels are joined with "/" so the
#       banner reads e.g. "vi-IV / ii-vii°".
#
# Cards with pair-count >= SMALL_THRESHOLD stay as-is.

SMALL_THRESHOLD = 5     # fewer pairs than this triggers a merge

def _balance_cards(cards: list[dict]) -> list[dict]:
    cs = [dict(c) for c in cards]
    changed = True
    while changed and len(cs) > 1:
        changed = False
        # Find the smallest card below the threshold.
        sizes = [len(c['pairs']) for c in cs]
        min_size = min(sizes)
        if min_size >= SMALL_THRESHOLD:
            break
        i = sizes.index(min_size)
        # Pick neighbour with the smaller total pair-count.
        left  = sizes[i - 1] if i - 1 >= 0 else float('inf')
        right = sizes[i + 1] if i + 1 < len(cs) else float('inf')
        if left == float('inf') and right == float('inf'):
            break
        j = i - 1 if left <= right else i + 1
        a, b = sorted([i, j])
        merged = {
            'label': cs[a]['label'] + ' / ' + cs[b]['label'],
            'pairs': cs[a]['pairs'] + cs[b]['pairs'],
        }
        cs[a:b + 1] = [merged]
        changed = True
    return cs


# ─────────────────────────── Assembly ────────────────────────────────────

CARD_CAPACITY = 42     # 7 rows × 6 cols cells per flash card


def _paginate(items: list[dict]) -> list[dict]:
    """Pack a linear item stream into 6×6 flash cards.

    When a page starts mid-section (no section/label marker as first item),
    a synthetic continuation marker is prepended so the reader always sees
    what section the cells belong to.
    """
    pages: list[dict] = []
    i = 0
    current_marker: dict | None = None
    SECTION_TYPES = ('section', 'tech_label')
    while i < len(items):
        page_items: list[dict] = []
        # Continuation marker at top of page if first item isn't one.
        if i > 0 and items[i]['type'] not in SECTION_TYPES and current_marker is not None:
            page_items.append(current_marker)
        while i < len(items) and len(page_items) < CARD_CAPACITY:
            it = items[i]
            if it['type'] in SECTION_TYPES:
                current_marker = it
            page_items.append(it)
            i += 1
        pages.append({'items': page_items})
    return pages


def build() -> dict:
    # ── Collect pool items (section markers + fractions) ─────
    pool_items = build_pool_cards()          # now returns a flat item list

    # ── Collect technique items (bullet labels + pairs) ──────
    techniques = parse_sdd_inventory()
    for t in techniques.values():
        t['cards'] = _balance_cards(t['cards'])

    tech_items: list[dict] = []
    for name in techniques:
        t = techniques[name]
        if not t['cards']:
            continue
        for c in t['cards']:
            tech_items.append({
                'type':      'tech_label',
                'technique': t['name'],
                'label':     c['label'],
                'family':    t['family'],
            })
            for p in c['pairs']:
                tech_items.append({
                    'type': 'tech_pair',
                    'from': p['from'],
                    'to':   p['to'],
                    'family': t['family'],
                })

    # Flow pool + techniques as one long stream, paginate into 7×6 cards.
    all_items = pool_items + tech_items
    cards = _paginate(all_items)

    # Build the "jumps" index — one entry per navigable section (pool + each
    # technique) with the card-number where that section first appears in the
    # flow and the count of practiceable fractions/pairs in that section.

    # Count items per section from the raw (unpaginated) item stream so
    # continuation markers in the paginated cards don't inflate counts.
    section_counts: dict[tuple, int] = {}
    current_pool_chord: str | None = None
    current_tech: str | None = None
    for it in all_items:
        if it['type'] == 'section':
            current_pool_chord = it['chord']
            current_tech = None
            section_counts.setdefault(('pool', current_pool_chord), 0)
        elif it['type'] == 'tech_label':
            current_tech = it['technique']
            current_pool_chord = None
            section_counts.setdefault(('tech', current_tech), 0)
        elif it['type'] == 'fraction' and current_pool_chord:
            section_counts[('pool', current_pool_chord)] += 1
        elif it['type'] == 'tech_pair' and current_tech:
            section_counts[('tech', current_tech)] += 1

    jumps: list[dict] = []
    seen_sections = set()
    for card_idx, card in enumerate(cards):
        for it in card['items']:
            if it['type'] == 'section':
                key = ('pool', it['chord'])
                if key not in seen_sections:
                    seen_sections.add(key)
                    jumps.append({
                        'kind':   'pool',
                        'title':  'Pool',
                        'label':  it['chord'],
                        'family': 'pool',
                        'card':   card_idx,
                        'count':  section_counts.get(key, 0),
                    })
            elif it['type'] == 'tech_label':
                key = ('tech', it['technique'])
                if key not in seen_sections:
                    seen_sections.add(key)
                    jumps.append({
                        'kind':   'technique',
                        'title':  it['technique'],
                        'label':  it['label'],
                        'family': it['family'],
                        'card':   card_idx,
                        'count':  section_counts.get(key, 0),
                    })

    return {
        'schema_version': 3,
        'source': 'HarpTrefoil.json + SDD.md §3.6.1',
        'filters': {
            'MIN_GAP': MIN_GAP,
            'MAX_GAP': MAX_GAP,
            'CARD_CAPACITY': CARD_CAPACITY,
            'note': 'Pool and technique items flow in a single paginated deck; '
                    f'each card holds up to {CARD_CAPACITY} cells (7 rows × 6 cols). '
                    'Continuation markers repeat the current section/bullet at the '
                    'top of mid-flow pages.',
        },
        'cards': cards,
        'jumps': jumps,
        'summary': {
            'pool_item_count':  len(pool_items),
            'tech_item_count':  len(tech_items),
            'total_item_count': len(all_items),
            'card_count':       len(cards),
            'jump_count':       len(jumps),
        },
    }


def main() -> int:
    data = build()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + '\n',
        encoding='utf-8',
    )
    # Also emit as a JS global so the WebView can <script src>-load it
    # without triggering file:// CORS on fetch().
    js_path = OUT_PATH.with_suffix('.js')
    js_path.write_text(
        'window.DRILL_DATA = ' + json.dumps(data, ensure_ascii=False) + ';\n',
        encoding='utf-8',
    )
    s = data['summary']
    print(f'wrote {OUT_PATH.relative_to(ROOT)}')
    print(f'wrote {js_path.relative_to(ROOT)}')
    print(f'  pool items:   {s["pool_item_count"]}')
    print(f'  tech items:   {s["tech_item_count"]}')
    print(f'  total items:  {s["total_item_count"]}')
    print(f'  flash cards:  {s["card_count"]}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
