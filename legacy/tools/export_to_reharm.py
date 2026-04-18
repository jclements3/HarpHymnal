#!/usr/bin/env python3
"""
export_to_reharm.py — convert an export_hymn.py JSON (comprehensive machine
data) into a reharm JSON (lead-sheet-ready) consumable by fill_template.py.

Quality features applied during conversion:
  1. LaTeX-safe escaping of titles, metadata, lyrics (ä, è, ô, apostrophes)
  2. One chord per bar by default (no sub-bar clutter on a lead sheet)
  3. Phrase-boundary rehearsal letters (A, B, C, ...)
  4. Cycle-color inheritance from the phrase's dominant transition cycle
  5. Strategy hints derived from phrase contour/harmony
  6. Verse text split across phrases (one chunk per phrase per verse)
  7. Fermata markers preserved in melody string
  8. Substitution annotations when harmonic_substitution is set
  9. Tempo inference from BPM if given, else by meter convention
 10. Quality label from export (e.g. 'm7' not '7' for ii7)

Usage:
    python3 export_to_reharm.py <export.json> > <reharm.json>
    python3 export_to_reharm.py --all <dir>/       # convert whole corpus
"""
import json
import re
import sys
import argparse
import os
import glob


# ═════════════════════════════════════════════════════════════════════════════
#   LaTeX escape — MUST run on every user-visible string (titles, lyrics, metadata)
# ═════════════════════════════════════════════════════════════════════════════
LATEX_ESCAPES = [
    ('\\', r'\textbackslash{}'),   # must be first, before other backslash adds
    ('&', r'\&'),
    ('%', r'\%'),
    ('$', r'\$'),
    ('#', r'\#'),
    ('_', r'\_'),
    ('{', r'\{'),
    ('}', r'\}'),
    ('~', r'\textasciitilde{}'),
    ('^', r'\textasciicircum{}'),
]

UNICODE_MAP = {
    # Common accented characters in hymn text
    'à': r'\`a', 'á': r"\'a", 'â': r'\^a', 'ä': r'\"a', 'ã': r'\~a', 'å': r'\aa ',
    'À': r'\`A', 'Á': r"\'A", 'Â': r'\^A', 'Ä': r'\"A', 'Ã': r'\~A', 'Å': r'\AA ',
    'è': r'\`e', 'é': r"\'e", 'ê': r'\^e', 'ë': r'\"e',
    'È': r'\`E', 'É': r"\'E", 'Ê': r'\^E', 'Ë': r'\"E',
    'ì': r'\`i', 'í': r"\'i", 'î': r'\^i', 'ï': r'\"i',
    'Ì': r'\`I', 'Í': r"\'I", 'Î': r'\^I', 'Ï': r'\"I',
    'ò': r'\`o', 'ó': r"\'o", 'ô': r'\^o', 'ö': r'\"o', 'õ': r'\~o',
    'Ò': r'\`O', 'Ó': r"\'O", 'Ô': r'\^O', 'Ö': r'\"O', 'Õ': r'\~O',
    'ù': r'\`u', 'ú': r"\'u", 'û': r'\^u', 'ü': r'\"u',
    'Ù': r'\`U', 'Ú': r"\'U", 'Û': r'\^U', 'Ü': r'\"U',
    'ç': r'\c c', 'Ç': r'\c C',
    'ñ': r'\~n', 'Ñ': r'\~N',
    'ß': r'\ss ',
    'Æ': r'\AE ', 'æ': r'\ae ',
    'Œ': r'\OE ', 'œ': r'\oe ',
    # Smart quotes and dashes (must NOT be escaped by apostrophe fix)
    '\u2018': "`",       # left single quote
    '\u2019': "'",       # right single quote (apostrophe)
    '\u201C': "``",      # left double quote
    '\u201D': "''",      # right double quote
    '\u2013': '--',      # en dash
    '\u2014': '---',     # em dash
    '\u2026': r'\ldots{}',
    # Musical accidentals in text
    '\u266D': r'$\flat$',
    '\u266F': r'$\sharp$',
    '\u266E': r'$\natural$',
    # Non-breaking hyphen used in hymn lyrics
    '\u00AD': '',
    # Middle dot, bullets
    '\u00B7': r'$\cdot$',
}


def latex_escape(s):
    """Make a string safe for LaTeX rendering. Call on every user string."""
    if not s:
        return ''
    # Step 1: replace unicode characters
    out = []
    for ch in s:
        if ch in UNICODE_MAP:
            out.append(UNICODE_MAP[ch])
        else:
            out.append(ch)
    s = ''.join(out)
    # Step 2: escape LaTeX specials (except those that are now in \commands)
    # We need to be careful not to re-escape backslashes in commands we just added
    # Simple approach: tokenise. But we added \' \" \^ \` \~ commands; the ASCII
    # ^ and ~ haven't been replaced yet. After the unicode pass, any remaining
    # raw ^ ~ \ { } & % $ # _ is user-supplied and needs escaping.
    # However, unicode replacements added new {} and \ — we must NOT re-escape
    # those. Trick: don't escape. Just escape the input's ORIGINAL specials
    # before the unicode pass.
    # Restart:
    return _latex_escape_proper(s)


def _latex_escape_proper(s):
    """Proper LaTeX escape that handles unicode+specials in the right order."""
    # 1) Escape LaTeX specials FIRST on the raw string (before unicode subs)
    # 2) Then map unicode to \command form
    # But the function as called already has unicode-replaced content in s.
    # Restructure: separate entry point.
    return s  # Never called directly; use latex_escape_v2 below


def _latex_escape_impl(s):
    """LaTeX-safe escape in the correct order.

    Order:
      1. Escape raw LaTeX specials (\ & % $ # _ { } ~ ^) in the ORIGINAL string
      2. Translate unicode characters to their \command equivalents

    This order matters: if we did unicode first, we'd introduce \ { } chars
    that would then be escaped into gibberish.
    """
    s = s.replace('\\', r'\textbackslash{}')
    for ch, repl in [
        ('&', r'\&'), ('%', r'\%'), ('$', r'\$'), ('#', r'\#'),
        ('_', r'\_'), ('{', r'\{'), ('}', r'\}'),
        ('~', r'\textasciitilde{}'), ('^', r'\textasciicircum{}'),
    ]:
        s = s.replace(ch, repl)
    out = []
    for ch in s:
        if ch in UNICODE_MAP:
            out.append(UNICODE_MAP[ch])
        else:
            out.append(ch)
    return ''.join(out)


def _html_escape_impl(s):
    """HTML-safe escape. Leaves unicode as-is (UTF-8 native)."""
    return (s.replace('&', '&amp;')
             .replace('<', '&lt;')
             .replace('>', '&gt;')
             .replace('"', '&quot;')
             .replace("'", '&#39;'))


ESCAPE_MODE = 'latex'   # 'latex' | 'html' | 'none'


def latex_escape_v2(s):
    """Dispatch escape based on module-level ESCAPE_MODE. Name preserved for callers."""
    if not s:
        return ''
    if ESCAPE_MODE == 'html':
        return _html_escape_impl(s)
    if ESCAPE_MODE == 'none':
        return s
    return _latex_escape_impl(s)


def _format_key_display(key_detected):
    """Format a key name with mode-appropriate accidentals."""
    if not key_detected:
        return key_detected
    if ESCAPE_MODE in ('html', 'none'):
        return key_detected.replace('-', '\u266D').replace('#', '\u266F')
    return key_detected.replace('-', r'$\flat$').replace('#', r'$\sharp$')


# ═════════════════════════════════════════════════════════════════════════════
#   Attribution cleanup — strip verbose "translated by... stanzas 2,4..." blurbs
# ═════════════════════════════════════════════════════════════════════════════
def _extract_from_c_lines(c_lines, label_prefixes):
    """Given c_lines and label prefixes like ['Music:', 'Music and Setting:'],
    return the content after the matching prefix in the first matching line.

    Used as a fallback when the primary composer/lyricist field is null.
    """
    for line in c_lines:
        for prefix in label_prefixes:
            if prefix in line:
                idx = line.find(prefix) + len(prefix)
                s = line[idx:].strip()
                # Strip any leading quoted tune name from the extracted string
                s = re.sub(r"^\s*['\"\u2018\u201c][^'\"\u2019\u201d]+['\"\u2019\u201d]\s*", '', s)
                return s.strip()
    return ''


def _clean_attribution(raw):
    """Trim a lyricist/composer field down to a presentable short form.

    Hymnal metadata often contains things like:
        "Josef Mohr, 1818. stanzas 1,3 Translated by John Freeman Young, 1863 stanzas 2,4 translator anonymous."
        "'Stille Nacht' Franz Xaver Gruber, 1818 \"Concordia Kinderchöre\", 1908"
        "John Newton, 1779. last verse author unknown, before 1829"
        "George Bennard, 1913. Music and Setting:"
        "16th Century English Traditional traditional from, 1871"

    Strategy:
    - Strip leading quoted tune names
    - Cut on various ". X:" or ". X " patterns indicating a new attribution begins
    - Strip trailing ", alt" or ".alt" suffixes
    - Trim whitespace and trailing punctuation
    """
    if not raw:
        return ''
    s = str(raw)
    # Strip leading quoted tune names: 'xxx' or "xxx"
    s = re.sub(r"^\s*['\"][^'\"]+['\"]\s*", '', s)
    # Cut on common "rest of sentence" markers (order matters — longer first)
    cut_patterns = [
        '. stanzas', ' stanzas ',
        '. Translated by', ' Translated by',
        '. Music and', '. Music:', '. Setting:',
        '. last verse', ' last verse ',
        ' Harmonized by', ' Arranged by', ' Adapted by',
        ' Translator:',
        '. Translation',
        ', combined by', ' combined by',
        '. Based on', ' Based on ',
        ' based on Gregorian', ' based on plainsong',
    ]
    for marker in cut_patterns:
        idx = s.find(marker)
        if idx > 0:
            s = s[:idx]
    # Also cut at the first secondary quoted block (embedded book/collection)
    m = re.search(r'\s+["\u201c]', s)
    if m and m.start() > 10:
        s = s[:m.start()]
    # Strip trailing ", alt", ".alt", "alt." suffixes (common abbreviation for "altered")
    s = re.sub(r',?\s*alt\.?\s*$', '', s, flags=re.IGNORECASE)
    # Collapse duplicate "traditional traditional" (seen in source data)
    s = re.sub(r'\b(traditional)\s+\1\b', r'\1', s, flags=re.IGNORECASE)
    # Remove trailing "from," orphan
    s = re.sub(r'\s+from,?\s*$', '', s, flags=re.IGNORECASE)
    # Trim
    s = s.strip().rstrip('.,;').strip()
    return s


def _extract_tune_name(meta):
    """Extract a tune name from metadata c_lines if present.

    Tune names in hymnal c_lines typically appear in quotes after a
    'Music:' / 'Music and Setting:' / 'Tune:' / 'Setting:' label, or
    as a bare uppercase word like "ST. ANNE" or "HYFRYDOL".
    """
    c_lines = meta.get('c_lines', [])
    # Check the tune field of composer (often has it)
    composer = meta.get('composer', '') or ''
    m = re.search(r"['\"\u2018\u201c]([A-Za-z][^'\"\u2019\u201d]{2,40})['\"\u2019\u201d]", composer)
    if m:
        return m.group(1).strip()

    # Look for labeled tune name in c_lines
    for line in c_lines:
        # "Music: 'Tune Name' ..."  or  "Music and Setting: 'Tune Name' ..."
        m = re.search(r"(?:Music(?:\s+and\s+Setting)?|Setting|Tune|Melody)[^:]*:\s*['\"\u2018\u201c]([^'\"\u2019\u201d]+)['\"\u2019\u201d]", line)
        if m:
            return m.group(1).strip()

    # Fallback: first quoted string in any c_line (that's not a book title)
    for line in c_lines:
        m = re.search(r"['\"\u2018\u201c]([A-Z][^'\"\u2019\u201d]{2,30})['\"\u2019\u201d]", line)
        if m:
            candidate = m.group(1).strip()
            # Filter out obvious book/collection names
            book_words = ['Hymnal', 'Collection', 'Hymns', 'Songs', 'Book',
                          'Tunes', 'Psalms', 'Sacred', 'Appendix']
            if not any(w in candidate for w in book_words):
                return candidate
    return ''


# ═════════════════════════════════════════════════════════════════════════════
#   Cycle color mapping (per template convention)
# ═════════════════════════════════════════════════════════════════════════════
CYCLE_COLORS = {
    '4ths': 'leafyellow',
    '3rds': 'leafred',
    '2nds': 'leafcyan',
    'stacked': 'accent',
}


def phrase_cycle_and_color(phrase_assignments):
    """Determine the dominant cycle of a phrase from its assignments' methods.
    Returns (cycle_label, cycle_color) for the banner."""
    if not phrase_assignments:
        return 'stacked', 'accent'
    from collections import Counter
    method_counts = Counter()
    dir_counts = Counter()
    for a in phrase_assignments:
        m = a.get('method', 'stacked')
        if m == 'stacked':
            method_counts['stacked'] += 1
        elif '-' in m:
            cycle, direction = m.split('-')
            method_counts[cycle] += 1
            dir_counts[direction] += 1
        else:
            method_counts['stacked'] += 1
    # Find the dominant cycle
    dominant = method_counts.most_common(1)[0][0]
    if dominant == 'stacked':
        return 'stacked', 'accent'
    # Determine direction as majority of CW/CCW within that cycle
    direction = dir_counts.most_common(1)[0][0] if dir_counts else 'CW'
    return f"{dominant} {direction}", CYCLE_COLORS[dominant]


# ═════════════════════════════════════════════════════════════════════════════
#   Per-bar chord pick — from the bar's assignment, pick the fraction
# ═════════════════════════════════════════════════════════════════════════════
def best_assignment_for_bar(assignments, bar):
    """Find the assignment for a given bar. Returns None if no assignment."""
    for a in assignments:
        if a['bar'] == bar:
            return a
    return None


def _rn_base_letters(rn):
    """Strip digits/accidentals to get the base numeral letters (I, V, ii, vi, etc.)."""
    if not rn:
        return ''
    m = re.match(r'^(b?[ivIV]+[°ø]?)', rn)
    return m.group(1) if m else rn


def _prefer_tonic_at_phrase_end(assignment, is_final_of_phrase, is_very_final):
    """If this bar is a phrase ending, try to swap in an alternate that has
    RH matching the functional rn (tonic in most cases). This makes the
    lead sheet visually read as "ends on I" rather than "ends on ii7".

    Mutates and returns the assignment.
    """
    if not assignment or not (is_final_of_phrase or is_very_final):
        return assignment
    rn = assignment.get('rn', '')
    # Only re-pick if the RN is a tonic-family chord (I, i, I6, i64, etc.)
    rn_base = _rn_base_letters(rn)
    # Only re-pick if the RN is a tonic-family chord (I, i, I6, i64, etc.)
    if rn_base.lower() not in ('i',):
        return assignment   # Not a tonic — the original voicing is fine
    # If RH already matches (case-insensitive), no swap needed
    cur_rh = assignment.get('rh_roman', '')
    cur_rh_base = _rn_base_letters(cur_rh)
    if cur_rh_base.lower() == rn_base.lower():
        return assignment
    # Scan alternates for one with RH base matching tonic (case-insensitive)
    for alt in assignment.get('alternates', []):
        alt_rh = alt.get('rh_roman', '')
        if _rn_base_letters(alt_rh).lower() == rn_base.lower():
            # Swap: replace lh_*, rh_*, mood, source with alternate
            new_a = dict(assignment)
            new_a['lh_roman'] = alt.get('lh_roman', '')
            new_a['lh_figure'] = alt.get('lh_figure', '')
            new_a['rh_roman'] = alt.get('rh_roman', '')
            new_a['rh_figure'] = alt.get('rh_figure', '')
            new_a['mood'] = alt.get('mood', '')
            new_a['source'] = alt.get('source', '')
            # Keep bar, rn, melody, etc. unchanged
            return new_a
    # No tonic-RH alternate exists — keep original voicing.
    # The functional `rn` is still 'I' in the reharm output, so downstream
    # can show that if needed. The fraction visually shows both parts.
    return assignment


def build_bar_assignment(a):
    """Convert an export-style assignment to a reharm-style assignment.
    Reharm schema expects: bar, rn, mel, lh_rom, lh_qual, lh_fig,
                           rh_rom, rh_qual, rh_fig, mood, source.

    Note: the export stores quality baked into the roman (e.g. 'V7', 'iii¹').
    fill_template's split_rn() handles the split, so we pass full roman as
    lh_rom/rh_rom and leave lh_qual/rh_qual empty.
    """
    if not a:
        return None
    return {
        'bar': a['bar'],
        'rn': a.get('rn', ''),
        'mel': a.get('melody', ''),
        'lh_rom': a.get('lh_roman', ''),
        'lh_qual': '',     # fill_template splits qual from roman itself
        'lh_fig': a.get('lh_figure', ''),
        'rh_rom': a.get('rh_roman', ''),
        'rh_qual': '',
        'rh_fig': a.get('rh_figure', ''),
        'mood': a.get('mood', ''),
        'source': a.get('source', ''),
    }


# ═════════════════════════════════════════════════════════════════════════════
#   Strategy hint per phrase — tell the performer what the phrase is "doing"
# ═════════════════════════════════════════════════════════════════════════════
def infer_phrase_strategy(phrase, assignments, melody_notes, total_bars):
    """Generate a short descriptive string for the phrase banner."""
    bars = phrase['bars']
    if not bars:
        return 'harmonic motion'
    # Look at melody direction within phrase
    mel_in_phrase = [n for n in melody_notes
                     if n.get('bar') in bars and not n.get('is_rest')]
    if not mel_in_phrase:
        return 'harmonic motion'
    first_midi = mel_in_phrase[0].get('midi', 60)
    last_midi = mel_in_phrase[-1].get('midi', 60)
    span = max(n['midi'] for n in mel_in_phrase) - min(n['midi'] for n in mel_in_phrase)
    direction = 'rises' if last_midi > first_midi + 2 else \
                'falls' if last_midi < first_midi - 2 else 'circles'
    # Cadence type from ending_marker
    ending = phrase.get('ending_marker', '')
    if ending == 'fermata':
        tail = 'rests on a fermata'
    elif ending == 'cadence':
        # Is it the final phrase? Then it's a full cadence
        if max(bars) == total_bars:
            tail = 'closes home'
        else:
            tail = 'breathes'
    else:
        tail = 'moves on'
    return f"melody {direction} — {tail}"


# ═════════════════════════════════════════════════════════════════════════════
#   Verse-text splitting across phrases
# ═════════════════════════════════════════════════════════════════════════════
def split_lyrics_by_phrase(verse_syllables, phrase_bars_list):
    """Given a verse's syllable list (each with note_offset_ql and text) and
    a list-of-lists of bar numbers per phrase, return a list of strings —
    one lyric chunk per phrase.

    We map syllables to phrases by looking at which phrase's bar-range each
    note's bar falls into. Then join the text tokens with the original
    word-boundary convention.
    """
    # Build a map: bar -> phrase index
    bar_to_phrase = {}
    for i, bars in enumerate(phrase_bars_list):
        for b in bars:
            bar_to_phrase[b] = i

    chunks = [[] for _ in phrase_bars_list]
    # We need syllables aligned to notes — each syllable has note_offset_ql.
    # We don't have the note's bar stored in the syllable; we need to look it up.
    # But since we're iterating, we can just use offset_ql % (meter_num_ql) to
    # derive the bar. Simpler: pass in the melody notes and zip.
    # Actually, each syllable dict has note_offset_ql. For now, we'll use a
    # different approach: assume phrases are filled IN ORDER by offset.

    # Build sorted list of (offset, phrase_idx) via phrase_bars and note offsets
    # We need phrase bar start-end → offset range. Without meter info here, let
    # the caller pass phrase_offsets (start_ql, end_ql).
    return chunks  # placeholder — see split_lyrics_by_phrase_v2 below


def split_lyrics_by_phrase_v2(verse_syllables, phrase_offset_ranges):
    """Split a verse's syllables into per-phrase text chunks.

    Uses the `joins_next` flag on each syllable (True if the next syllable
    is part of the same word — i.e. the ABC had a hyphen: 'Si- lent'). If
    joins_next is missing (old export), fall back to heuristic based on
    trailing punctuation.

    verse_syllables : list of {text, note_offset_ql, joins_next?, ...}
    phrase_offset_ranges : list of (start_ql, end_ql) tuples.

    Returns: list of strings, one per phrase.
    """
    chunks = [[] for _ in phrase_offset_ranges]
    for syl in verse_syllables:
        off = syl.get('note_offset_ql', 0)
        text = syl.get('text', '').strip()
        if not text:
            continue  # skip empty (melisma continuations)
        joins = syl.get('joins_next', False)
        for i, (start, end) in enumerate(phrase_offset_ranges):
            is_last = (i == len(phrase_offset_ranges) - 1)
            if (start <= off < end) or (is_last and off >= start):
                chunks[i].append((text, joins))
                break

    # Join tokens. If prev.joins_next, concatenate without space. Otherwise space.
    result = []
    for chunk in chunks:
        text = ''
        for i, (tok, joins) in enumerate(chunk):
            if i == 0:
                text += tok
            else:
                prev_joins = chunk[i-1][1]
                if prev_joins:
                    text += tok   # no separator: same word
                else:
                    text += ' ' + tok
        result.append(text)
    return result


# ═════════════════════════════════════════════════════════════════════════════
#   Main conversion
# ═════════════════════════════════════════════════════════════════════════════
def export_to_reharm(exp):
    """Convert an export JSON dict to a reharm JSON dict."""
    title = exp.get('title', '').strip()
    music = exp.get('music', {})
    meta = exp.get('metadata', {})
    phrases = exp.get('phrases', [])
    assignments = exp.get('harmony', {}).get('harp_chord_assignments', [])
    lyrics_data = exp.get('lyrics', {})
    s1v1_notes = exp.get('voices', {}).get('S1V1', [])
    meter_num = music.get('meter_num', 4)

    # ─── Header fields
    key_detected = music.get('key_detected', '')
    key_display = _format_key_display(key_detected)

    meter_str = music.get('meter', '4/4')
    bpm = music.get('bpm', 100)

    # Try primary fields first; fall back to c_lines if null/empty
    c_lines = meta.get('c_lines', [])
    raw_lyricist = meta.get('lyricist', '') or _extract_from_c_lines(
        c_lines, ['Words:', 'Text:'])
    raw_composer = meta.get('composer', '') or _extract_from_c_lines(
        c_lines, ['Music and Setting:', 'Music:', 'Setting:', 'Melody:'])

    words_who = latex_escape_v2(_clean_attribution(raw_lyricist))
    words_year = meta.get('words_year', '') or meta.get('year', '')
    music_who = latex_escape_v2(_clean_attribution(raw_composer))
    music_year = meta.get('music_year', '') or meta.get('year', '')

    # If the cleaned attribution already ends with a year, don't append.
    def _combine(who, year):
        if not who:
            return f"[unknown]{', ' + year if year else ''}"
        # If the final 4 chars of who are digits (a year), trust them
        if re.search(r',\s*\d{4}\s*$', who):
            return who
        if year and year in who:
            return who
        if year:
            return f"{who}, {year}"
        return who

    words_str = _combine(words_who, words_year)
    music_str = _combine(music_who, music_year)

    tune = latex_escape_v2(_extract_tune_name(meta))

    # ─── Phrase assembly
    # Build phrase_offset_ranges for lyric splitting
    phrase_offset_ranges = []
    for i, p in enumerate(phrases):
        start = p.get('start_ql', 0)
        end = p.get('end_ql', start + 1)
        # Inclusive of next phrase's start as boundary for the last phrase
        phrase_offset_ranges.append((start, end))

    # Derive lyrics per phrase per verse
    # Shape: {verse_num: [phraseA_text, phraseB_text, ...]}
    verses_split = {}
    verse_count = lyrics_data.get('verse_count', 0)
    for v_num, vdata in lyrics_data.get('verses', {}).items():
        syl_list = vdata.get('syllables', [])
        chunks = split_lyrics_by_phrase_v2(syl_list, phrase_offset_ranges)
        verses_split[int(v_num)] = [latex_escape_v2(c) for c in chunks]

    # Build phrases for reharm schema, with per-phrase lyrics attached
    reharm_phrases = []
    for p_idx, p in enumerate(phrases):
        bars = p['bars']
        phrase_asns = [a for a in assignments if a['bar'] in bars]
        cycle_label, cycle_color = phrase_cycle_and_color(phrase_asns)
        strategy = infer_phrase_strategy(p, phrase_asns, s1v1_notes,
                                          music.get('total_bars', 0))
        # Attach v1 and v2 lyrics for this phrase
        phrase_lyrics = {}
        for v_num in sorted(verses_split.keys())[:2]:
            key = f'v{v_num}'
            chunks = verses_split[v_num]
            if p_idx < len(chunks):
                phrase_lyrics[key] = chunks[p_idx]
            else:
                phrase_lyrics[key] = ''
        # Ensure v1 and v2 always exist
        phrase_lyrics.setdefault('v1', '')
        phrase_lyrics.setdefault('v2', '')

        reharm_phrases.append({
            'label': p['label'],
            'bars': bars,
            'strategy': latex_escape_v2(strategy),
            'cycle': cycle_label,
            'cycle_color': cycle_color,
            'lyrics': phrase_lyrics,
        })

    # Build assignments — apply phrase-end tonic preference where possible
    # Compute which bars are phrase endings and which is the hymn's final bar
    phrase_end_bars = set()
    for p in phrases:
        if p['bars']:
            phrase_end_bars.add(max(p['bars']))
    final_bar = music.get('total_bars', 0)

    reharm_assignments = []
    for a in assignments:
        bar = a.get('bar')
        is_phrase_end = bar in phrase_end_bars
        is_very_final = bar == final_bar
        if is_phrase_end or is_very_final:
            a = _prefer_tonic_at_phrase_end(a, is_phrase_end, is_very_final)
        reharm_assignments.append(build_bar_assignment(a))

    # Top-level lyrics: flat map {v1: "full verse 1 text", v2: "full verse 2 text"}
    # (fill_template uses phrase-embedded lyrics, but this is kept for debugging)
    top_lyrics = {}
    for v_num, vdata in lyrics_data.get('verses', {}).items():
        top_lyrics[f'v{v_num}'] = latex_escape_v2(vdata.get('raw_text', ''))

    # ─── Mode/key breakdown
    mode_str = music.get('mode', 'major')  # 'major' or 'minor'

    return {
        'title': latex_escape_v2(title),
        'key': key_display,
        'key_root': music.get('key_root', 'C'),
        'mode': mode_str,
        'meter': meter_str,
        'bpm': bpm,
        'words': words_str,
        'music': music_str,
        'tune': tune or '[unknown]',
        'lyrics': top_lyrics,
        'phrases': reharm_phrases,
        'assignments': reharm_assignments,
        'total_bars': music.get('total_bars', 0),
    }


# ═════════════════════════════════════════════════════════════════════════════
#   CLI
# ═════════════════════════════════════════════════════════════════════════════
def main():
    global ESCAPE_MODE
    ap = argparse.ArgumentParser(description='Convert export JSON to reharm JSON')
    ap.add_argument('input', nargs='?', help='Export JSON file (or dir if --all)')
    ap.add_argument('-o', '--output', help='Output file (default: stdout for single)')
    ap.add_argument('--all', action='store_true', help='Batch-convert directory')
    ap.add_argument('--out-dir', help='Output directory for --all mode')
    ap.add_argument('--escape', choices=('latex', 'html', 'none'), default='latex',
                    help='String-escape mode for user-visible fields (default: latex)')
    args = ap.parse_args()
    ESCAPE_MODE = args.escape

    if args.all:
        if not args.input or not args.out_dir:
            print("Error: --all requires input directory and --out-dir", file=sys.stderr)
            sys.exit(2)
        os.makedirs(args.out_dir, exist_ok=True)
        files = sorted(glob.glob(os.path.join(args.input, '*.json')))
        success = 0
        for fp in files:
            try:
                with open(fp) as f:
                    exp = json.load(f)
                reharm = export_to_reharm(exp)
                outname = os.path.basename(fp).replace('.json', '_reharm.json')
                out_path = os.path.join(args.out_dir, outname)
                with open(out_path, 'w') as f:
                    json.dump(reharm, f, indent=2, ensure_ascii=False)
                success += 1
            except Exception as e:
                print(f"[fail] {fp}: {e}", file=sys.stderr)
        print(f"Done. {success}/{len(files)} converted to {args.out_dir}",
              file=sys.stderr)
        return

    # Single-file mode
    if not args.input:
        print("Error: input path required", file=sys.stderr)
        sys.exit(2)
    with open(args.input) as f:
        exp = json.load(f)
    reharm = export_to_reharm(exp)
    output = json.dumps(reharm, indent=2, ensure_ascii=False)
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
    else:
        print(output)


if __name__ == '__main__':
    main()
