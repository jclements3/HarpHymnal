"""Multi-page improv guide, organized by Prehn's 4 families.

Cover + TOC + 4 family chapters + appendix.
"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont('FreeMono', '/usr/share/fonts/truetype/freefont/FreeMono.ttf'))
pdfmetrics.registerFont(TTFont('FreeMonoBold', '/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf'))
pdfmetrics.registerFont(TTFont('FreeMonoOblique', '/usr/share/fonts/truetype/freefont/FreeMonoOblique.ttf'))

PAGE = letter  # portrait, easier for multi-page reading
W, H = PAGE
MARGIN = 50
LINE_H = 14
import os as _os
_outdir = _os.environ.get('PEDAL_OUT_DIR', '/mnt/user-data/outputs')
_os.makedirs(_outdir, exist_ok=True)
out_path = _os.path.join(_outdir, 'improv_guide.pdf')
c = canvas.Canvas(out_path, pagesize=PAGE)

# ============================================================
# Helper: pedal braille generator
# ============================================================
LETTERS = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
LETTER_PC = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}

PARENTS = {
    1: [0, 2, 4, 5, 7, 9, 11],
    2: [0, 2, 3, 5, 7, 9, 11],
    3: [0, 2, 3, 5, 7, 8, 11],
    4: [0, 2, 4, 5, 7, 8, 11],
}

ROTATION_INDEX = {
    1: {'Ionian':0,'Dorian':1,'Phrygian':2,'Lydian':3,'Mixolydian':4,'Aeolian':5,'Locrian':6},
    2: {'Dorian':0,'Phrygian':1,'Lydian':2,'Mixolydian':3,'Aeolian':4,'Locrian':5,'Ionian':6},
    3: {'Aeolian':0,'Locrian':1,'Ionian':2,'Dorian':3,'Phrygian':4,'Lydian':5,'Mixolydian':6},
    4: {'Ionian':0,'Dorian':1,'Phrygian':2,'Lydian':3,'Mixolydian':4,'Aeolian':5,'Locrian':6},
}

ALTERATION = {
    1: {m: '' for m in ['Ionian','Dorian','Phrygian','Lydian','Mixolydian','Aeolian','Locrian']},
    2: {'Ionian':' #1','Dorian':' #7','Phrygian':' #6','Lydian':' #5',
        'Mixolydian':' #4','Aeolian':' #3','Locrian':' #2'},
    3: {'Ionian':' #5','Dorian':' #4','Phrygian':' #3','Lydian':' #2',
        'Mixolydian':' #1','Aeolian':' #7','Locrian':' #6'},
    4: {'Ionian':' b6','Dorian':' b5','Phrygian':' b4','Lydian':' b3',
        'Mixolydian':' b2','Aeolian':' b1','Locrian':' b7'},
}

DIGIT = {
    1: {m: 0 for m in ['Ionian','Dorian','Phrygian','Lydian','Mixolydian','Aeolian','Locrian']},
    2: {'Ionian':1,'Dorian':7,'Phrygian':6,'Lydian':5,'Mixolydian':4,'Aeolian':3,'Locrian':2},
    3: {'Ionian':5,'Dorian':4,'Phrygian':3,'Lydian':2,'Mixolydian':1,'Aeolian':7,'Locrian':6},
    4: {'Ionian':6,'Dorian':5,'Phrygian':4,'Lydian':3,'Mixolydian':2,'Aeolian':1,'Locrian':7},
}

LEFT_DOT  = {'f': 0, 'n': 1, 's': 2}
RIGHT_DOT = {'f': 3, 'n': 4, 's': 5}

def pattern_string(pcs):
    pcs_oct = list(pcs) + [12]
    steps = [pcs_oct[i+1] - pcs_oct[i] for i in range(7)]
    return ' '.join({1:'H', 2:'W', 3:'W+H'}.get(s, '?') for s in steps)

def rotate(parent, i):
    base = parent[i]
    return [(parent[(i + k) % 7] - base) % 12 for k in range(7)]

def pc_to_pos(letter_, pc):
    natural = LETTER_PC[letter_]
    diff = (pc - natural) % 12
    if diff == 0:   return 'n'
    if diff == 1:   return 's'
    if diff == 11:  return 'f'
    return None

def scale_at_C(fam, mode):
    rot_idx = ROTATION_INDEX[fam][mode]
    pcs = rotate(PARENTS[fam], rot_idx)
    accs = {}
    for k, interval in enumerate(pcs):
        L = LETTERS[k]
        target_pc = interval
        a = pc_to_pos(L, target_pc)
        accs[L] = a
    return accs, pcs

def best_tonic_spelling(fam, mode):
    """Find a tonic spelling that gives a clean (no-? letter) scale.
    Prefer C; fall back to C#, then any tonic that works.
    Returns (tonic_label, accs_dict, pcs)."""
    rot_idx = ROTATION_INDEX[fam][mode]
    pcs = rotate(PARENTS[fam], rot_idx)
    # Try C first
    accs, _ = scale_at_C(fam, mode)
    if all(a in ('f','n','s') for a in accs.values()):
        return 'C', accs, pcs
    # Try C# next
    candidates = [('C','s',1), ('D','f',-1), ('D','n',0)]
    # Then everything else
    for tL in LETTERS:
        for ta, off in [('n',0),('s',1),('f',-1)]:
            cand = (tL, ta, off)
            if cand not in candidates:
                candidates.append(cand)
    for tL, ta, off in candidates:
        tpc = (LETTER_PC[tL] + off) % 12
        start = LETTERS.index(tL)
        accs2 = {}
        ok = True
        for k, interval in enumerate(pcs):
            L = LETTERS[(start+k)%7]
            target = (tpc + interval) % 12
            a = pc_to_pos(L, target)
            if a is None:
                ok = False
                break
            accs2[L] = a
        if ok:
            label = tL + ('\u266f' if ta=='s' else '\u266d' if ta=='f' else '')
            return label, accs2, pcs
    return 'C', accs, pcs  # shouldn't reach here

def braille_cell(left_pos, right_pos, separator=False):
    bits = 0
    if left_pos is not None and left_pos != '?':
        bits |= 1 << LEFT_DOT[left_pos]
    if right_pos is not None and right_pos != '?':
        bits |= 1 << RIGHT_DOT[right_pos]
    if separator:
        bits |= (1 << 3) | (1 << 4) | (1 << 5)
    return chr(0x2800 + bits)

def braille_pedal(accs):
    if any(a == '?' or a is None for a in accs.values()):
        return '(needs respelling)'
    c1 = braille_cell(accs['D'], accs['C'])
    c2 = braille_cell(accs['B'], None, separator=True)
    c3 = braille_cell(accs['E'], accs['F'])
    c4 = braille_cell(accs['G'], accs['A'])
    return c1 + c2 + c3 + c4

def notes_for_scale(accs, tonic_letter):
    """Return note names with accidentals, starting from tonic letter."""
    start = LETTERS.index(tonic_letter)
    out = []
    for k in range(7):
        L = LETTERS[(start+k)%7]
        a = accs[L]
        if a == 'n': out.append(L)
        elif a == 's': out.append(L + '\u266f')
        elif a == 'f': out.append(L + '\u266d')
        else: out.append(L + '?')
    return out

def notes_at_C(fam, mode):
    """Return note names with accidentals for this scale on C."""
    accs, pcs = scale_at_C(fam, mode)
    return notes_for_scale(accs, 'C')

# ============================================================
# Drawing helpers
# ============================================================
def text(x, y, s, font='FreeMono', size=10):
    c.setFont(font, size)
    c.drawString(x, y, s)

def hline(y):
    c.line(MARGIN, y, W - MARGIN, y)

def newpage():
    c.showPage()
    return H - MARGIN

# Page footer
def footer(page_num):
    c.setFont('FreeMono', 8)
    c.drawString(W - MARGIN - 20, 30, f'p. {page_num}')

# ============================================================
# DATA: per-mode descriptions
# ============================================================
MODE_DESC = {
    'Ionian': {
        'pop':  'major scale',
        'pat':  'W W H W W W H',
        'char': 'natural 7 (leading tone resolves up to tonic)',
        'sound':'happy, resolved, classic Western major',
        'use':  'pop, folk, classical, hymns; anything that wants to feel "settled"',
        'chord':'maj7  (C E G B on tonic C)',
        'tip':  'use the leading tone 7\u21921 cadence; avoid lingering on 4',
    },
    'Dorian': {
        'pop':  'Dorian mode',
        'pat':  'W H W W W H W',
        'char': 'natural 6 in a minor mode (the brightener)',
        'sound':'minor but optimistic; jazz, soul, Celtic music',
        'use':  '"So What" by Miles Davis; modal jazz; medieval-feeling minor',
        'chord':'m7   (C E\u266d G B\u266d on tonic C)',
        'tip':  'feature the natural 6 (A in C Dorian); IV chord is major',
    },
    'Phrygian': {
        'pop':  'Phrygian mode',
        'pat':  'H W W W H W W',
        'char': 'flat 2 (semitone above tonic)',
        'sound':'Spanish, exotic, dark minor',
        'use':  'flamenco, metal, anything with Iberian or Middle-Eastern flavor',
        'chord':'m7   (C E\u266d G B\u266d on tonic C)',
        'tip':  '\u266d2 is the signature; cadence \u266dII\u2192I; avoid V as arrival',
    },
    'Lydian': {
        'pop':  'Lydian mode',
        'pat':  'W W W H W W H',
        'char': 'sharp 4 (raised tritone above tonic)',
        'sound':'floating, dreamy, otherworldly',
        'use':  'film scores, cartoons, Joe Satriani; wonder/magic moments',
        'chord':'maj7  (C E G B on tonic C) but often play maj7\u266f11',
        'tip':  'land on \u266f4 as upper neighbor to 5; don\'t resolve \u266f4\u21925',
    },
    'Mixolydian': {
        'pop':  'Mixolydian mode',
        'pat':  'W W H W W H W',
        'char': 'flat 7 (no leading tone)',
        'sound':'rocky, swaggering, bluesy',
        'use':  'rock, blues, Celtic jigs, gospel',
        'chord':'7    (C E G B\u266d on tonic C, dominant 7)',
        'tip':  'feature \u266d7; cadence \u266dVII\u2192I instead of V\u2192I',
    },
    'Aeolian': {
        'pop':  'natural minor scale',
        'pat':  'W H W W H W W',
        'char': 'flat 6 and flat 7 (both flat in a minor mode)',
        'sound':'sad, brooding, the default minor',
        'use':  'pop ballads, folk laments, classical minor pieces',
        'chord':'m7   (C E\u266d G B\u266d on tonic C)',
        'tip':  'stay diatonic; raising 7 drifts into harmonic minor (F3)',
    },
    'Locrian': {
        'pop':  'Locrian mode',
        'pat':  'H W W H W W W',
        'char': 'flat 2 AND flat 5 (the only mode with diminished 5)',
        'sound':'unstable, tense, queasy',
        'use':  'rare as a tonic; appears in metal (Slayer), some Bartok',
        'chord':'m7\u266d5 / \u00f8 (half-diminished)',
        'tip':  '\u266d5 makes the tonic chord diminished; use as color, not as home',
    },
}

# Per-(family, mode) overrides. Alterations significantly change a mode's
# character; these entries describe the *altered* scale, not the base mode.
ALTERED_DESC = {
    # F2: melodic minor modes
    (2, 'Ionian'): {  # Ionian #1 = altered scale = super Locrian
        'pop':  'altered scale / super Locrian',
        'char': 'every chord tone altered (\u266d2 \u266d3 \u266d4 \u266d5 \u266d6 \u266d7)',
        'sound':'maximum tension; alien, jazz "outside"',
        'use':  'over altered dominants in jazz (V7alt resolving to I)',
        'chord':'7alt (dominant with all alterations)',
        'tip':  'every note clashes; lean into the dissonance',
    },
    (2, 'Dorian'): {  # Dorian #7 = melodic minor (ascending)
        'pop':  'melodic minor (ascending)',
        'char': 'minor scale with raised 7 (leading tone) AND raised 6',
        'sound':'minor with classical pull-to-tonic',
        'use':  'classical minor pieces ascending; jazz minor harmony',
        'chord':'mMaj7 (minor with major 7th)',
        'tip':  'the raised 7 wants to resolve up to tonic; combine with natural 6',
    },
    (2, 'Phrygian'): {  # Phrygian #6
        'pop':  'Dorian b2 (also called Phrygian #6)',
        'char': 'Dorian-bright minor with a flat 2',
        'sound':'minor with bright 6 plus dark \u266d2 — both characters at once',
        'use':  'jazz over minor chords needing extra color',
        'chord':'m7 (with \u266d9 tension available)',
        'tip':  'feature both natural 6 (Dorian color) and \u266d2 (Phrygian color)',
    },
    (2, 'Lydian'): {  # Lydian #5 = Lydian augmented
        'pop':  'Lydian augmented',
        'char': 'Lydian with raised 5 (augmented chord at the root)',
        'sound':'floating Lydian plus augmented-chord tension',
        'use':  'maj7#5 chords; whole-tone-adjacent moments in jazz',
        'chord':'maj7#5',
        'tip':  'land on \u266f4 and \u266f5; both push outward from the major triad',
    },
    (2, 'Mixolydian'): {  # Mixolydian #4 = Lydian dominant
        'pop':  'Lydian dominant / acoustic scale',
        'char': 'Mixolydian (\u266d7) but with \u266f4 as well',
        'sound':'dominant 7 chord with bright Lydian color',
        'use':  'common over 7\u266f11 chords in jazz; "Simpsons theme"',
        'chord':'7\u266f11',
        'tip':  'feature \u266d7 AND \u266f4 — the trademark "Lydian dominant" pair',
    },
    (2, 'Aeolian'): {  # Aeolian #3 — but Aeolian #3 makes it major... wait
        'pop':  '(unusual; sharpening 3 in Aeolian creates a Mixolydian-like scale with \u266d6)',
        'char': 'natural minor with raised 3 — turns minor into a major-with-flat-6',
        'sound':'major sound with sad \u266d6 hanging over it',
        'use':  'rare; sometimes over altered dominants',
        'chord':'7\u266d13 (dominant with flat 13)',
        'tip':  'feels like a clouded major; lean on \u266d6',
    },
    (2, 'Locrian'): {  # Locrian #2 = half-diminished
        'pop':  'Locrian \u266e2 / half-diminished scale',
        'char': 'Locrian but with natural 2 (less alien than plain Locrian)',
        'sound':'softer than plain Locrian; the standard "half-dim" sound',
        'use':  'over m7\u266d5 chords in jazz minor 2-5-1',
        'chord':'m7\u266d5 / \u00f8 (half-diminished 7)',
        'tip':  'works wonderfully over half-diminished chords; \u266d5 is the marker',
    },

    # F3: harmonic minor modes
    (3, 'Ionian'): {  # Ionian #5 = harmonic major (no, that's F4)... wait
        # F3 Ionian #5 = Ionian augmented = Ionian with #5
        'pop':  'Ionian #5 / harmonic major mode',
        'char': 'major scale with raised 5 (augmented chord at the root)',
        'sound':'major with augmented-chord tension',
        'use':  'over maj7#5 chords; rare in tonal music',
        'chord':'maj7#5',
        'tip':  'the raised 5 sits between 5 and 6 of the major scale',
    },
    (3, 'Dorian'): {  # Dorian #4 = Romanian minor
        'pop':  'Romanian minor / Ukrainian Dorian',
        'char': 'Dorian with raised 4 (the wide step from \u266d3 to \u266f4)',
        'sound':'minor with an exotic raised 4; Eastern European flavor',
        'use':  'klezmer, Romani music, some film scores',
        'chord':'m7 (with \u266f11 color available)',
        'tip':  'feature the wide step \u266d3 \u2192 \u266f4 — the signature interval',
    },
    (3, 'Phrygian'): {  # Phrygian #3 = Phrygian dominant
        'pop':  'Phrygian dominant / Spanish gypsy',
        'char': 'Phrygian with raised 3 — produces dominant 7 chord at the root',
        'sound':'flamenco, Andalusian, Middle-Eastern',
        'use':  'Spanish music, klezmer, metal (Yngwie Malmsteen); over V7\u266d9 in minor keys',
        'chord':'7\u266d9',
        'tip':  'the wide step from \u266d2 to natural 3 is the signature; lean on \u266d2 and natural 3',
    },
    (3, 'Lydian'): {  # Lydian #2
        'pop':  'Lydian #2',
        'char': 'Lydian with raised 2 (gives a wide step from root to \u266f2)',
        'sound':'Lydian dreaminess plus a sharp opening interval',
        'use':  'jazz over maj7#9 or maj7#11 chords; rare elsewhere',
        'chord':'maj7 (with \u266f9 color)',
        'tip':  'the wide root-to-\u266f2 step gives this its character',
    },
    (3, 'Mixolydian'): {  # Mixolydian #1
        'pop':  '(sometimes called altered dominant variant)',
        'char': 'Mixolydian with raised root — creates exotic intervals',
        'sound':'unusual; rarely used except as theoretical curiosity',
        'use':  'mostly appears as the 5th mode of harmonic minor',
        'chord':'\u00b07 (diminished 7, since the root is altered)',
        'tip':  'rarely used as a standalone scale',
    },
    (3, 'Aeolian'): {  # Aeolian #7 = harmonic minor
        'pop':  'harmonic minor',
        'char': 'natural minor with raised 7 (leading tone)',
        'sound':'classical minor; dramatic, "European" minor',
        'use':  'Bach, Mozart, classical minor cadences; metal; flamenco modulations',
        'chord':'mMaj7 (minor with major 7th)',
        'tip':  'the raised 7 creates the V\u2192i cadence missing in plain Aeolian',
    },
    (3, 'Locrian'): {  # Locrian #6
        'pop':  'Locrian #6 / Locrian \u266e6',
        'char': 'Locrian but with natural 6 (raised from plain Locrian\'s \u266d6)',
        'sound':'half-diminished feel with extra brightness on 6',
        'use':  'jazz over m7\u266d5 chords as alternative to Locrian \u266e2',
        'chord':'m7\u266d5 (half-diminished)',
        'tip':  'similar to Locrian \u266e2 in use; pick by which extension you want',
    },

    # F4: harmonic major modes
    (4, 'Ionian'): {  # Ionian b6 = harmonic major
        'pop':  'harmonic major',
        'char': 'major scale with flat 6 (borrowed from minor)',
        'sound':'major with a darkened 6th; "wistful major"',
        'use':  'film scores; some classical (Brahms); modal jazz',
        'chord':'maj7 (with \u266d13 color available)',
        'tip':  'the \u266d6 is the modal marker; use it to add wistfulness to major',
    },
    (4, 'Dorian'): {  # Dorian b5
        'pop':  'Dorian b5 / Locrian #2 #6',
        'char': 'Dorian with flat 5 — turns the minor into a half-diminished color',
        'sound':'half-diminished feel with Dorian\'s natural 6',
        'use':  'jazz over m7\u266d5 with bright extensions',
        'chord':'m7\u266d5',
        'tip':  'natural 6 brightens this half-dim variant',
    },
    (4, 'Phrygian'): {  # Phrygian b4
        'pop':  'Phrygian b4',
        'char': 'Phrygian with flat 4 — creates wide step from 4 to 5',
        'sound':'darker Phrygian; ultra-exotic',
        'use':  'rare; appears in flamenco and some Bartok',
        'chord':'m7 (with \u266d11 dissonance)',
        'tip':  'the \u266d2 + \u266d4 combination is unusual; treat as color',
    },
    (4, 'Lydian'): {  # Lydian b3
        'pop':  'Lydian b3 / Lydian diminished',
        'char': 'Lydian with flat 3 — turns the major into minor with \u266f4',
        'sound':'minor mode with raised 4 — exotic minor',
        'use':  'jazz fusion; some film score textures',
        'chord':'m(maj7) with \u266f11',
        'tip':  '\u266f4 in a minor mode creates a haunting quality',
    },
    (4, 'Mixolydian'): {  # Mixolydian b2 — note: this is the same as Phrygian dominant from F3? No.
        # Mixolydian b2 = Phrygian dominant in F3 was #3, here it's b2. Let me check.
        # F4 Mix b2 pcs: [0, 1, 4, 5, 7, 9, 10]
        # F3 Phr #3 pcs: [0, 1, 4, 5, 7, 8, 10]
        # Different (8 vs 9 at index 5). Good.
        'pop':  'Mixolydian b2',
        'char': 'Mixolydian (\u266d7) with flat 2',
        'sound':'dominant 7 chord with Phrygian-flavored upper structure',
        'use':  'jazz over 7\u266d9 chords resolving to I',
        'chord':'7\u266d9',
        'tip':  'similar to Phrygian dominant but with natural 6',
    },
    (4, 'Aeolian'): {  # Aeolian b1 — flattening the root
        'pop':  '(rare; root altered)',
        'char': 'Aeolian with flattened root creates unusual intervals',
        'sound':'used as a rotation rather than as a tonic scale',
        'use':  'mostly theoretical; appears as 6th mode of harmonic major',
        'chord':'(no clean chord-scale match)',
        'tip':  'rarely used as standalone; usually a passing rotation',
    },
    (4, 'Locrian'): {  # Locrian b7 (which would be Locrian bb7 traditionally)
        'pop':  'Locrian b7 / Locrian \u266d\u266d7',
        'char': 'Locrian with further-flattened 7 — creates diminished 7 chord',
        'sound':'fully diminished, very dark',
        'use':  'over diminished 7 chords in jazz and classical',
        'chord':'\u00b07 (diminished 7)',
        'tip':  'the \u266d\u266d7 is enharmonically a 6 — but in this naming, the chord built up is dim7',
    },
}

def get_desc(fam, mode):
    """Get description, preferring family-specific override."""
    if (fam, mode) in ALTERED_DESC:
        merged = dict(MODE_DESC[mode])
        merged.update(ALTERED_DESC[(fam, mode)])
        return merged
    return MODE_DESC[mode]


FAMILY_DESC = {
    1: {
        'name':    'Family 1: the major modes',
        'parent':  'Ionian',
        'popular': 'major scale',
        'pattern': 'W W H W W W H',
        'short':   'F1',
        'about':   'The 7 unaltered modes. The "white-key" scales. Every other family is built by altering one note in one of these modes.',
        'use':     'Most tonal music lives here. If you don\'t know which family to pick, start in F1.',
    },
    2: {
        'name':    'Family 2: the melodic minor modes',
        'parent':  'Dorian #7',
        'popular': 'ascending melodic minor',
        'pattern': 'W H W W W W H',
        'short':   'F2',
        'about':   'F1 with one sharp added. The alteration is different in each mode (Ionian #1, Dorian #7, etc.) but they all share the same 7-note set.',
        'use':     'Jazz harmony lives here. Modern, sophisticated, "outside" colors over standard chord types.',
    },
    3: {
        'name':    'Family 3: the harmonic minor modes',
        'parent':  'Aeolian #7',
        'popular': 'harmonic minor',
        'pattern': 'W H W W H W+H H',
        'short':   'F3',
        'about':   'F1 with a different sharp. Contains a wide whole-and-a-half step that gives this family its distinctive "exotic" sound.',
        'use':     'Classical minor cadences (Bach), flamenco, klezmer, Middle-Eastern flavors, metal.',
    },
    4: {
        'name':    'Family 4: the harmonic major modes',
        'parent':  'Ionian b6',
        'popular': 'harmonic major',
        'pattern': 'W W H W H W+H H',
        'short':   'F4',
        'about':   'F1 with one flat added. Like F3 but built from a major (Ionian) base instead of minor (Aeolian). Contains the same wide whole-and-a-half step.',
        'use':     'Mysterious major-key colors; film scores; Hollywood "Eastern" pastiche; some 20th-century classical.',
    },
}

# Mode order from brightest to darkest (Prehn's ordering, applies within each family)
BRIGHTNESS_ORDER = ['Lydian', 'Ionian', 'Mixolydian', 'Dorian', 'Aeolian', 'Phrygian', 'Locrian']

# ============================================================
# Page tracking
# ============================================================
toc_entries = []  # list of (title, page_num)
page_num = 1

def begin_page():
    global page_num
    return H - MARGIN

def end_page():
    global page_num
    footer(page_num)
    page_num += 1
    c.showPage()

# ============================================================
# COVER PAGE
# ============================================================
y = begin_page()
y -= 30
text(MARGIN, y, "Pedal harp improv guide", 'FreeMonoBold', 22)
y -= 26
text(MARGIN, y, "28 scales, 4 families, 7 modes each", 'FreeMono', 14)
y -= 60

text(MARGIN, y, "How to use this guide", 'FreeMonoBold', 14)
y -= 22
intro = [
    "This guide walks through Oliver Prehn's 28-scale system, organized by his",
    "4 families. Within each family, the 7 modes are presented in order from",
    "brightest (Lydian) to darkest (Locrian).",
    "",
    "For each scale you'll find:",
    "  - what it sounds like and where you might hear it",
    "  - its characteristic tone (the note that defines its mood)",
    "  - the 7th chord that pairs with it",
    "  - a tip for improvising",
    "  - the pedal setting on tonic C, written in 4-cell braille",
    "",
    "To play a scale on a different tonic, look up the row + column in the",
    "companion pedal matrix.",
    "",
    "All 28 scales are equal in this system. You don't need to memorize any",
    "particular scale as more important than another. Browse by family,",
    "find scales whose sound you like, and add them to your vocabulary",
    "as you encounter them in pieces or improvisations.",
]
for line in intro:
    text(MARGIN, y, line, 'FreeMono', 11)
    y -= 14

y -= 14
text(MARGIN, y, "Pedal braille notation", 'FreeMonoBold', 14)
y -= 20
braille_intro = [
    "Each pedal setting is shown as 4 braille cells:",
    "",
    "  cell 1: D pedal (left dots) + C pedal (right dots)",
    "  cell 2: B pedal (left dots) + separator (always shows three vertical dots)",
    "  cell 3: E pedal (left dots) + F pedal (right dots)",
    "  cell 4: G pedal (left dots) + A pedal (right dots)",
    "",
    "Within each cell, the dot row tells you the pedal position:",
    "  top    = flat",
    "  middle = natural",
    "  bottom = sharp",
    "",
    "Example: \u2812\u283A\u2812\u2812 = all naturals (C major scale).",
]
for line in braille_intro:
    text(MARGIN, y, line, 'FreeMono', 11)
    y -= 14

end_page()

# ============================================================
# FAMILY CHAPTERS
# ============================================================
def draw_family_overview(fam, y):
    """Draw the family overview block. Returns new y."""
    info = FAMILY_DESC[fam]
    # Estimate space needed: header (30) + parent (90) + about (60) + modes (150) = ~330
    needed = 330
    if y < MARGIN + needed:
        end_page()
        y = begin_page()

    toc_entries.append((info['name'], page_num))

    text(MARGIN, y, info['name'], 'FreeMonoBold', 18)
    y -= 24

    text(MARGIN, y, "Parent scale", 'FreeMonoBold', 12)
    y -= 18
    text(MARGIN + 20, y, f"Premise:    {info['parent']}", 'FreeMono', 11)
    y -= 14
    text(MARGIN + 20, y, f"Popular:    {info['popular']}", 'FreeMono', 11)
    y -= 14
    text(MARGIN + 20, y, f"Pattern:    {info['pattern']}", 'FreeMono', 11)
    y -= 14
    text(MARGIN + 20, y, "(W=whole step, H=half step, W+H=whole-and-a-half step)", 'FreeMono', 9)
    y -= 20

    text(MARGIN, y, "About this family", 'FreeMonoBold', 12)
    y -= 18
    import textwrap
    for para in [info['about'], info['use']]:
        for line in textwrap.wrap(para, width=80):
            text(MARGIN + 20, y, line, 'FreeMono', 11)
            y -= 14
        y -= 4

    y -= 4
    text(MARGIN, y, "The 7 modes (brightest to darkest)", 'FreeMonoBold', 12)
    y -= 18

    text(MARGIN + 20, y, '{:<18} {:<18} {}'.format('mode', 'pattern', 'character'),
         'FreeMonoBold', 10)
    y -= 13
    for mode in BRIGHTNESS_ORDER:
        full_name = f'{mode}{DIGIT[fam][mode]}'
        rot_idx = ROTATION_INDEX[fam][mode]
        pcs = rotate(PARENTS[fam], rot_idx)
        pat = pattern_string(pcs)
        desc = get_desc(fam, mode)
        text(MARGIN + 20, y, '{:<18} {:<18} {}'.format(full_name, pat, desc['sound']),
             'FreeMono', 10)
        y -= 13

    y -= 12
    return y


def draw_mode_entry(fam, mode, y):
    """Draw a single mode entry. Page-break if not enough room.
    Avoid orphan headers: only place the title when room exists for at least
    the title + 4 body lines."""
    desc = get_desc(fam, mode)
    tonic_label, accs, pcs = best_tonic_spelling(fam, mode)
    full_name = f'{mode}{DIGIT[fam][mode]}{tonic_label.lower()}'
    tonic_letter = tonic_label[0]
    notes = notes_for_scale(accs, tonic_letter)
    pedal = braille_pedal(accs)
    pat = pattern_string(pcs)

    # An entry needs ~145pt. If less is available, page-break.
    needed = 145
    if y < MARGIN + needed:
        end_page()
        y = begin_page()

    # Mode name + parent reference
    text(MARGIN, y, full_name, 'FreeMonoBold', 14)
    if ALTERATION[fam][mode]:
        offset = len(full_name) * 8.4 + 10
        text(MARGIN + offset, y, f"(rotation of F{fam} parent at the {mode} degree)", 'FreeMonoOblique', 9)
    y -= 18

    col1_x = MARGIN + 20
    val_x = col1_x + 75

    text(col1_x, y, "sound:",   'FreeMonoBold', 10)
    text(val_x, y,  desc['sound'], 'FreeMono', 10)
    y -= 13

    text(col1_x, y, "use:",     'FreeMonoBold', 10)
    text(val_x, y,  desc['use'], 'FreeMono', 10)
    y -= 13

    text(col1_x, y, "mark tone:", 'FreeMonoBold', 10)
    text(val_x, y,  desc['char'], 'FreeMono', 10)
    y -= 13

    text(col1_x, y, "improv:",  'FreeMonoBold', 10)
    text(val_x, y,  desc['tip'], 'FreeMonoOblique', 10)
    y -= 13

    text(col1_x, y, "chord:",   'FreeMonoBold', 10)
    text(val_x, y,  desc['chord'], 'FreeMono', 10)
    y -= 13

    text(col1_x, y, "pattern:", 'FreeMonoBold', 10)
    text(val_x, y,  pat, 'FreeMono', 10)
    y -= 13

    text(col1_x, y, "on " + tonic_label + ":",    'FreeMonoBold', 10)
    text(val_x, y,  ' '.join(notes), 'FreeMono', 10)
    y -= 14

    text(col1_x, y, tonic_label + " pedals:", 'FreeMonoBold', 10)
    text(val_x, y,   pedal, 'FreeMono', 16)
    y -= 18

    # Separator
    c.setStrokeGray(0.7)
    c.line(MARGIN, y, W - MARGIN, y)
    c.setStrokeGray(0)
    y -= 10
    return y


# Walk through all 4 families continuously
y = H - MARGIN  # start fresh after cover page
# (cover already ended; we're on page 2 now)
y = begin_page()

for fam in [1, 2, 3, 4]:
    y = draw_family_overview(fam, y)
    for mode in BRIGHTNESS_ORDER:
        y = draw_mode_entry(fam, mode, y)
    y -= 6

end_page()

# ============================================================
# APPENDIX: brightness ordering
# ============================================================
appendix_page = page_num
toc_entries.append(("Appendix: brightness ordering", page_num))
y = begin_page()
text(MARGIN, y, "Appendix: brightness ordering", 'FreeMonoBold', 18)
y -= 26
text(MARGIN, y, "Within each family, modes go brightest (Lydian) to darkest (Locrian).", 'FreeMono', 11)
y -= 14
text(MARGIN, y, "Across families, brightness depends on which alterations cancel or compound.", 'FreeMono', 11)
y -= 24

text(MARGIN, y, "Sequence within each family:", 'FreeMonoBold', 12)
y -= 18
text(MARGIN + 20, y, "Lydian \u2192 Ionian \u2192 Mixolydian \u2192 Dorian \u2192 Aeolian \u2192 Phrygian \u2192 Locrian", 'FreeMono', 11)
y -= 24

text(MARGIN, y, "Family character (rough):", 'FreeMonoBold', 12)
y -= 18
fc = [
    ("F1", "neutral; the unaltered diatonic baseline"),
    ("F2", "brighter where alteration sharps a note (Lydian #5 is very bright);"),
    ("",   "         darker where alteration is in already-dark mode (Locrian #2)"),
    ("F3", "exotic; the wide W+H step adds a 'foreign' color"),
    ("F4", "darker than F1 because adding a flat darkens"),
]
for label, descr in fc:
    text(MARGIN + 20, y, '{:<5} {}'.format(label, descr), 'FreeMono', 11)
    y -= 14

end_page()

# ============================================================
# APPENDIX: pedal matrix (2 landscape pages)
# ============================================================
def draw_matrix_page(families):
    """Draw the pedal matrix for given families on a landscape page."""
    # Switch to landscape for this page
    c.setPageSize(landscape(letter))
    LW, LH = landscape(letter)
    margin_l = 30
    fs = 10
    braille_size = 16
    line_h = 22
    scale_col_w = 95
    tonic_col_w = 49

    y = LH - margin_l

    fam_label = '/'.join(f'F{f}' for f in families)
    c.setFont('FreeMonoBold', fs + 2)
    c.drawString(margin_l, y, f"Appendix: pedal matrix \u2014 {fam_label} x 12 tonics")
    y -= line_h
    c.setFont('FreeMono', fs - 1)
    c.drawString(margin_l, y, "Cells: D-C \u2016 B-sep \u2016 E-F \u2016 G-A     Per cell: top=flat, middle=natural, bottom=sharp     * = enharmonic respelling")
    y -= line_h * 1.2

    # Headers
    from reportlab.pdfbase.pdfmetrics import stringWidth
    c.setFont('FreeMonoBold', fs)
    glyph_w = braille_size * 0.6
    sep_center_offset = 1.5 * glyph_w
    for j, col in enumerate(MATRIX_COLUMNS):
        cx = margin_l + scale_col_w + j * tonic_col_w
        label = col_label_matrix(col)
        label_w = stringWidth(label, 'FreeMonoBold', fs)
        c.drawString(cx + sep_center_offset - label_w / 2, y, label)
    y -= line_h * 0.3
    c.line(margin_l, y, margin_l + scale_col_w + len(MATRIX_COLUMNS) * tonic_col_w, y)
    y -= line_h

    for fam in families:
        fam_name = {1:'F1 major', 2:'F2 melodic minor',
                    3:'F3 harmonic minor', 4:'F4 harmonic major'}[fam]
        c.setFont('FreeMonoBold', fs)
        c.drawString(margin_l, y, fam_name)
        y -= line_h
        for mode in ['Ionian','Dorian','Phrygian','Lydian','Mixolydian','Aeolian','Locrian']:
            rot_idx = ROTATION_INDEX[fam][mode]
            pcs = rotate(PARENTS[fam], rot_idx)
            row_label = f'{mode}{DIGIT[fam][mode]}'
            c.setFont('FreeMono', fs)
            c.drawString(margin_l, y, row_label)
            for j, col in enumerate(MATRIX_COLUMNS):
                cx = margin_l + scale_col_w + j * tonic_col_w
                tL, tA, accs2 = matrix_spell_for_column(pcs, col)
                if accs2 is None:
                    c.setFont('FreeMono', fs)
                    c.drawString(cx, y, '----')
                else:
                    bp = matrix_braille_pedal(accs2)
                    c.setFont('FreeMono', braille_size)
                    c.drawString(cx, y, bp)
                    if (tL, tA) != col:
                        c.setFont('FreeMono', fs)
                        star_x = cx + braille_size * 0.6 * 4 + 1
                        c.drawString(star_x, y, '*')
            y -= line_h
        y -= line_h * 0.4

# Matrix data
from reportlab.lib.pagesizes import landscape
MATRIX_COLUMNS = [
    ('C', 'n'), ('G', 'n'), ('D', 'n'), ('A', 'n'),
    ('E', 'n'), ('B', 'n'), ('F', 's'),
    ('F', 'n'), ('B', 'f'), ('E', 'f'), ('A', 'f'),
    ('D', 'f'), ('G', 'f'),
]
MATRIX_ENHARMONIC = {
    ('C', 'n'): [('B', 's'), ('D', 'f')],
    ('G', 'n'): [('F', 's'), ('A', 'f')],
    ('D', 'n'): [('C', 's'), ('E', 'f')],
    ('A', 'n'): [('G', 's'), ('B', 'f')],
    ('E', 'n'): [('D', 's'), ('F', 'f')],
    ('B', 'n'): [('A', 's'), ('C', 'f')],
    ('F', 's'): [('G', 'f'), ('E', 's')],
    ('F', 'n'): [('E', 's')],
    ('B', 'f'): [('A', 's')],
    ('E', 'f'): [('D', 's')],
    ('A', 'f'): [('G', 's')],
    ('D', 'f'): [('C', 's')],
    ('G', 'f'): [('F', 's')],
}
MATRIX_ACC_OFF = {'f': -1, 'n': 0, 's': 1}

def matrix_try_spell(scale_pcs, tonic_letter, tonic_acc):
    tonic_pc = (LETTER_PC[tonic_letter] + MATRIX_ACC_OFF[tonic_acc]) % 12
    start_idx = LETTERS.index(tonic_letter)
    accs = {}
    for k, interval in enumerate(scale_pcs):
        L = LETTERS[(start_idx + k) % 7]
        target_pc = (tonic_pc + interval) % 12
        a = pc_to_pos(L, target_pc)
        if a is None:
            return None
        accs[L] = a
    return accs

def matrix_spell_for_column(scale_pcs, col):
    candidates = [col] + MATRIX_ENHARMONIC.get(col, [])
    for tL, tA in candidates:
        result = matrix_try_spell(scale_pcs, tL, tA)
        if result is not None:
            return tL, tA, result
    return None, None, None

def col_label_matrix(col):
    L, A = col
    return L + {'f': '\u266d', 'n': '', 's': '\u266f'}[A]

def matrix_braille_pedal(accs):
    c1 = braille_cell(accs['D'], accs['C'])
    c2 = braille_cell(accs['B'], None, separator=True)
    c3 = braille_cell(accs['E'], accs['F'])
    c4 = braille_cell(accs['G'], accs['A'])
    return c1 + c2 + c3 + c4

# Draw matrix appendix pages
toc_entries.append(("Appendix: pedal matrix (F1/F2)", page_num))
draw_matrix_page([1, 2])
footer(page_num)
page_num += 1
c.showPage()

toc_entries.append(("Appendix: pedal matrix (F3/F4)", page_num))
draw_matrix_page([3, 4])
footer(page_num)
page_num += 1
c.showPage()

# Switch back to portrait (in case anything follows)
c.setPageSize(letter)

c.save()
print('Wrote', out_path, 'pages:', page_num - 1)
