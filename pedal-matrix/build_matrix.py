"""Build pedal matrix as 2-page Letter landscape PDF, families 1-2 / 3-4."""

from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont('FreeMono', '/usr/share/fonts/truetype/freefont/FreeMono.ttf'))
pdfmetrics.registerFont(TTFont('FreeMonoBold', '/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf'))

PARENTS = {
    1: [0, 2, 4, 5, 7, 9, 11],
    2: [0, 2, 3, 5, 7, 9, 11],
    3: [0, 2, 3, 5, 7, 8, 11],
    4: [0, 2, 4, 5, 7, 8, 11],
}

def rotate(parent, i):
    base = parent[i]
    return [(parent[(i + k) % 7] - base) % 12 for k in range(7)]

MODES = ['Ionian', 'Dorian', 'Phrygian', 'Lydian', 'Mixolydian', 'Aeolian', 'Locrian']

# Map (family, mode_name) -> rotation index of the parent scale.
# F1 parent = Ionian: rotations directly produce Ionian, Dorian, ..., Locrian
# F2 parent = melodic minor (Dorian #7): rotation 0 = Dorian #7
# F3 parent = harmonic minor (Aeolian #7): rotation 0 = Aeolian #7
# F4 parent = harmonic major (Ionian b6): rotation 0 = Ionian b6
ROTATION_INDEX = {
    1: {'Ionian':0,'Dorian':1,'Phrygian':2,'Lydian':3,'Mixolydian':4,'Aeolian':5,'Locrian':6},
    2: {'Dorian':0,'Phrygian':1,'Lydian':2,'Mixolydian':3,'Aeolian':4,'Locrian':5,'Ionian':6},
    3: {'Aeolian':0,'Locrian':1,'Ionian':2,'Dorian':3,'Phrygian':4,'Lydian':5,'Mixolydian':6},
    4: {'Ionian':0,'Dorian':1,'Phrygian':2,'Lydian':3,'Mixolydian':4,'Aeolian':5,'Locrian':6},
}

# Alteration label for each (family, mode) combination
ALTERATION = {
    1: {m: '' for m in MODES},
    2: {'Ionian':' #1','Dorian':' #7','Phrygian':' #6','Lydian':' #5',
        'Mixolydian':' #4','Aeolian':' #3','Locrian':' #2'},
    3: {'Ionian':' #5','Dorian':' #4','Phrygian':' #3','Lydian':' #2',
        'Mixolydian':' #1','Aeolian':' #7','Locrian':' #6'},
    4: {'Ionian':' b6','Dorian':' b5','Phrygian':' b4','Lydian':' b3',
        'Mixolydian':' b2','Aeolian':' b1','Locrian':' b7'},
}

# Compact-notation digit per (family, mode): 0 = unaltered (F1),
# else the altered scale degree relative to F1 (sharp in F2/F3, flat in F4).
DIGIT = {
    1: {mode: 0 for mode in MODES},
    2: {'Ionian':1,'Dorian':7,'Phrygian':6,'Lydian':5,'Mixolydian':4,'Aeolian':3,'Locrian':2},
    3: {'Ionian':5,'Dorian':4,'Phrygian':3,'Lydian':2,'Mixolydian':1,'Aeolian':7,'Locrian':6},
    4: {'Ionian':6,'Dorian':5,'Phrygian':4,'Lydian':3,'Mixolydian':2,'Aeolian':1,'Locrian':7},
}

LETTERS = ['C', 'D', 'E', 'F', 'G', 'A', 'B']
LETTER_PC = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
ACC_OFF = {'f': -1, 'n': 0, 's': 1}

COLUMNS = [
    ('C', 'n'), ('G', 'n'), ('D', 'n'), ('A', 'n'),
    ('E', 'n'), ('B', 'n'), ('F', 's'),
    ('F', 'n'), ('B', 'f'), ('E', 'f'), ('A', 'f'),
    ('D', 'f'), ('G', 'f'),
]

ENHARMONIC = {
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

def pc_to_pos(letter_, pc):
    natural = LETTER_PC[letter_]
    diff = (pc - natural) % 12
    if diff == 0:   return 'n'
    if diff == 1:   return 's'
    if diff == 11:  return 'f'
    return None

def try_spell(scale_pcs, tonic_letter, tonic_acc):
    tonic_pc = (LETTER_PC[tonic_letter] + ACC_OFF[tonic_acc]) % 12
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

def spell_for_column(scale_pcs, col):
    candidates = [col] + ENHARMONIC.get(col, [])
    for tL, tA in candidates:
        result = try_spell(scale_pcs, tL, tA)
        if result is not None:
            return tL, tA, result
    return None, None, None

LEFT_DOT  = {'f': 0, 'n': 1, 's': 2}
RIGHT_DOT = {'f': 3, 'n': 4, 's': 5}

def braille_cell(left_pos, right_pos, separator=False):
    bits = 0
    if left_pos is not None:
        bits |= 1 << LEFT_DOT[left_pos]
    if right_pos is not None:
        bits |= 1 << RIGHT_DOT[right_pos]
    if separator:
        bits |= (1 << 3) | (1 << 4) | (1 << 5)
    return chr(0x2800 + bits)

def braille_pedal(accs):
    c1 = braille_cell(accs['D'], accs['C'])
    c2 = braille_cell(accs['B'], None, separator=True)
    c3 = braille_cell(accs['E'], accs['F'])
    c4 = braille_cell(accs['G'], accs['A'])
    return c1 + c2 + c3 + c4

ACC_SUFFIX = {'f': '\u266d', 'n': '', 's': '\u266f'}

def col_label(col):
    L, A = col
    return L + ACC_SUFFIX[A]

PAGE = landscape(letter)
W, H = PAGE

import os
_outdir = os.environ.get('PEDAL_OUT_DIR', '/mnt/user-data/outputs')
os.makedirs(_outdir, exist_ok=True)
out_path = os.path.join(_outdir, 'pedals_matrix.pdf')
c = canvas.Canvas(out_path, pagesize=PAGE)

margin = 30
font_size = 10
braille_size = 16
line_h = 22
scale_col_w = 95
tonic_col_w = 49  # 95 + 13*49 = 732, fits exactly

def draw_page(families):
    y = H - margin

    c.setFont('FreeMonoBold', font_size + 2)
    fam_label = '/'.join(f'F{f}' for f in families)
    c.drawString(margin, y, f"Pedal settings: {fam_label} x 12 tonics")
    y -= line_h

    c.setFont('FreeMono', font_size - 1)
    c.drawString(margin, y, "Cells: D-C \u2016 B-sep \u2016 E-F \u2016 G-A     Per cell: top=flat, middle=natural, bottom=sharp     * = enharmonic respelling")
    y -= line_h * 1.2

    c.setFont('FreeMonoBold', font_size)
    # Each braille glyph at braille_size has width ~= 0.6 * braille_size in monospace.
    # Cell 2 (separator) center is at offset 1.5 * glyph_w from start of braille string.
    glyph_w = braille_size * 0.6
    sep_center_offset = 1.5 * glyph_w
    for j, col in enumerate(COLUMNS):
        cx = margin + scale_col_w + j * tonic_col_w
        from reportlab.pdfbase.pdfmetrics import stringWidth
        label = col_label(col)
        label_w = stringWidth(label, 'FreeMonoBold', font_size)
        # Center label horizontally over the separator
        c.drawString(cx + sep_center_offset - label_w / 2, y, label)
    y -= line_h * 0.3
    c.line(margin, y, margin + scale_col_w + len(COLUMNS) * tonic_col_w, y)
    y -= line_h

    for fam in families:
        fam_name = {1:'F1 major', 2:'F2 melodic minor',
                    3:'F3 harmonic minor', 4:'F4 harmonic major'}[fam]
        c.setFont('FreeMonoBold', font_size)
        c.drawString(margin, y, fam_name)
        y -= line_h
        parent = PARENTS[fam]
        for mode in MODES:
            rot_idx = ROTATION_INDEX[fam][mode]
            pcs = rotate(parent, rot_idx)
            row_label = f'{mode}{DIGIT[fam][mode]}'
            c.setFont('FreeMono', font_size)
            c.drawString(margin, y, row_label)
            for j, col in enumerate(COLUMNS):
                cx = margin + scale_col_w + j * tonic_col_w
                tL, tA, accs = spell_for_column(pcs, col)
                if accs is None:
                    c.setFont('FreeMono', font_size)
                    c.drawString(cx, y, '----')
                else:
                    braille = braille_pedal(accs)
                    c.setFont('FreeMono', braille_size)
                    c.drawString(cx, y, braille)
                    if (tL, tA) != col:
                        c.setFont('FreeMono', font_size)
                        star_x = cx + braille_size * 0.6 * 4 + 1
                        c.drawString(star_x, y, '*')
            y -= line_h
        y -= line_h * 0.4

def draw_footer_p1():
    """Mode pattern + char tone, family identity (F1, F2), brightness order."""
    footer_y = 132
    fs = 11
    lh = 13

    c.setFont('FreeMonoBold', fs)
    c.drawString(margin, footer_y, "Mode reference (W=whole, H=half)")
    y2 = footer_y - lh
    c.setFont('FreeMono', fs)
    mode_info = [
        ('Lydian',     'W W W H W W H', '\u266f4    brightest major'),
        ('Ionian',     'W W H W W W H', 'nat 7  major scale'),
        ('Mixolydian', 'W W H W W H W', '\u266d7    dominant feel'),
        ('Dorian',     'W H W W W H W', 'nat 6  bright minor'),
        ('Aeolian',    'W H W W H W W', '\u266d6    natural minor'),
        ('Phrygian',   'H W W W H W W', '\u266d2    Spanish color'),
        ('Locrian',    'H W W H W W W', '\u266d2 \u266d5  darkest'),
    ]
    c.drawString(margin, y2, '{:<12}{:<16}{}'.format('mode','pattern','char tone'))
    y2 -= lh
    for name, pat, char in mode_info:
        c.drawString(margin, y2, '{:<12}{:<16}{}'.format(name, pat, char))
        y2 -= lh

    fam_x = margin + 344
    c.setFont('FreeMonoBold', fs)
    c.drawString(fam_x, footer_y, "Families")
    y3 = footer_y - lh
    c.setFont('FreeMono', fs)
    fam_info = [
        ('F1', 'Ionian',     'major scale'),
        ('F2', 'Dorian #7',  'melodic minor'),
        ('F3', 'Aeolian #7', 'harmonic minor'),
        ('F4', 'Ionian b6',  'harmonic major'),
    ]
    for fam, premise, popular in fam_info:
        c.drawString(fam_x, y3, '{:<5}{:<13}{}'.format(fam, premise, popular))
        y3 -= lh

    bright_x = margin + 624
    c.setFont('FreeMonoBold', fs)
    c.drawString(bright_x, footer_y, "Brightness")
    y4 = footer_y - lh
    c.setFont('FreeMono', fs)
    c.drawString(bright_x, y4, "Lyd (brightest)")
    y4 -= lh
    c.drawString(bright_x, y4, "Ion")
    y4 -= lh
    c.drawString(bright_x, y4, "Mix")
    y4 -= lh
    c.drawString(bright_x, y4, "Dor")
    y4 -= lh
    c.drawString(bright_x, y4, "Aeo")
    y4 -= lh
    c.drawString(bright_x, y4, "Phr")
    y4 -= lh
    c.drawString(bright_x, y4, "Loc (darkest)")


def draw_footer_p2():
    """Improv usage notes + family alteration cheat-sheet."""
    footer_y = 132
    fs = 11
    lh = 13

    c.setFont('FreeMonoBold', fs)
    c.drawString(margin, footer_y, "Improv tips per mode")
    y2 = footer_y - lh
    c.setFont('FreeMono', fs)
    tips = [
        ('Lydian',     'land on \u266f4 as upper neighbor to 5; don\'t resolve \u266f4\u21925'),
        ('Ionian',     'use 7\u21921 leading-tone cadence; avoid resting on 4'),
        ('Mixolydian', 'feature \u266d7; cadence \u266dVII\u2192I (no leading tone)'),
        ('Dorian',     'feature natural 6 (the modal marker); IV is major'),
        ('Aeolian',    'stay diatonic; raising 7 drifts into harmonic minor'),
        ('Phrygian',   '\u266d2 is the signature; cadence \u266dII\u2192I; avoid V'),
        ('Locrian',    '\u266d2 and \u266d5 as tension; unstable as tonic'),
    ]
    for name, tip in tips:
        c.drawString(margin, y2, '{:<11} {}'.format(name, tip))
        y2 -= lh

    fam_x = margin + 555
    c.setFont('FreeMonoBold', fs)
    c.drawString(fam_x, footer_y, "Family alterations")
    y3 = footer_y - lh
    c.setFont('FreeMono', fs)
    c.drawString(fam_x, y3, "(Ion-Dor-Phr-Lyd-")
    y3 -= lh
    c.drawString(fam_x, y3, "Mix-Aeo-Loc order)")
    y3 -= lh * 1.3
    c.drawString(fam_x, y3, "F2: #1 #7 #6 #5 #4 #3 #2"); y3 -= lh
    c.drawString(fam_x, y3, "F3: #5 #4 #3 #2 #1 #7 #6"); y3 -= lh
    c.drawString(fam_x, y3, "F4: b6 b5 b4 b3 b2 b1 b7"); y3 -= lh


draw_page([1, 2])
draw_footer_p1()
c.showPage()
draw_page([3, 4])
draw_footer_p2()
c.save()
print('Wrote', out_path)
