"""Generate one SVG per key signature, all using the same cell template
(arc borders, radial sides, curved staff, rotated clef) and Bravura sharp/flat
glyphs embedded as paths."""
import math

CX, CY = 80.82, 340
MIDDLE_R, SPACING = 291.54, 12.5  # staff_pos_r(p) = MIDDLE_R + p * SPACING/2

CELL_PATH = ('M 0 9.66 A 340 340 0 0 1 161.64 9.66 L 139.04 101.95 '
             'A 245 245 0 0 0 22.60 101.95 Z')
STAFF_PATHS = [
    'M 10.16 31.45 A 316.53 316.53 0 0 1 151.48 31.45',
    'M 13.11 43.60 A 304.04 304.04 0 0 1 148.53 43.60',
    'M 16.05 55.74 A 291.54 291.54 0 0 1 145.59 55.74',
    'M 19.03 67.90 A 279.04 279.04 0 0 1 142.61 67.90',
    'M 21.99 80.02 A 266.55 266.55 0 0 1 139.64 80.02',
]
CLEF = ('<text x="40" y="76.45" transform="rotate(-13.75 40 50)" '
        'font-family="FreeSerif, serif" font-size="75" text-anchor="middle" '
        'dominant-baseline="alphabetic">&#x1D11E;</text>')

SHARP_PATH = ('M237 118C244 121 249 129 249 135V206C249 211 246 214 242 214'
              'C240 214 239 214 237 213C237 213 217 205 212 204C205 204 198 209 198 217'
              'V339C198 345 192 350 184 350C174 350 168 345 168 339V209'
              'C167 199 164 186 155 180C143 173 109 159 92 155C83 155 80 167 80 175'
              'V295C80 301 73 306 66 306C56 306 50 301 50 295V160'
              'C50 146 44 136 38 133C32 130 12 122 12 122C5 120 0 112 0 106'
              'V35C0 29 3 26 9 26L11 27C12 27 27 33 35 37L36 38C44 38 50 28 50 20'
              'V-79C50 -90 45 -99 39 -102C33 -104 12 -113 12 -113C5 -115 0 -123 0 -129'
              'V-200C0 -206 3 -209 9 -209L11 -208C12 -208 26 -202 35 -199'
              'C36 -198 37 -198 38 -198C45 -198 50 -209 50 -214V-337'
              'C50 -343 56 -348 63 -348C73 -348 80 -343 80 -337V-198'
              'C80 -185 85 -178 90 -176L151 -151C151 -151 152 -151 152 -151L154 -150'
              'C163 -150 168 -162 168 -168V-293C168 -299 174 -304 181 -304'
              'C192 -304 198 -299 198 -293V-151C198 -143 202 -131 209 -128'
              'C216 -125 237 -117 237 -117C244 -114 249 -106 249 -100V-29'
              'C249 -24 246 -21 242 -21C240 -21 239 -21 237 -22L211 -32'
              'C205 -32 198 -26 198 -14V79C198 86 203 105 211 108Z'
              'M168 -45C162 -65 115 -85 92 -85C86 -85 81 -83 80 -80'
              'C78 -76 77 -54 77 -30C77 1 78 36 80 44C82 61 128 82 153 82'
              'C160 82 166 80 168 76C170 71 172 46 172 19C172 -8 170 -36 168 -45Z')
SHARP_CX = 6.225  # half of 249 * 0.05 (advance width / em * scale)
SHARP_SCALE = 0.05

FLAT_PATH = ('M12 -170C15 -174 18 -175 21 -175C24 -175 27 -173 27 -173'
             'C57 -156 81 -129 106 -112C195 -50 226 11 226 57'
             'C226 114 182 150 136 153C119 153 95 145 81 136'
             'C75 131 64 122 59 122C57 122 56 122 54 123C47 126 43 133 43 140'
             'C44 162 50 402 50 422C50 433 41 439 31 439C17 439 1 429 0 411'
             'C0 411 4 -160 12 -170Z'
             'M47 -81C47 -81 44 -21 44 19C44 35 45 47 46 51C53 71 93 100 116 100'
             'C145 100 157 67 157 42C157 -12 111 -66 68 -93C64 -95 61 -96 58 -96'
             'C49 -96 47 -86 47 -81Z')
# Flat glyph is taller: spans roughly y=-175 to y=439 (centered around y=130)
# For SMuFL convention, the glyph's "origin" (vertical center on staff line) is at
# the flat's bowl, near y=0. So we don't pre-translate vertically.
FLAT_CX = 0.05 * 226 / 2  # half of glyph horizontal extent at scale 0.05

SHARP_POS = {'F#': 4, 'C#': 1, 'G#': 5, 'D#': 2, 'A#': -1, 'E#': 3}
FLAT_POS = {'Bb': 0, 'Eb': 3, 'Ab': -1, 'Db': 2, 'Gb': -2, 'Cb': 1}
ORDER_SHARPS = ['F#', 'C#', 'G#', 'D#', 'A#', 'E#']
ORDER_FLATS = ['Bb', 'Eb', 'Ab', 'Db', 'Gb', 'Cb']

THETA_FIRST_SHARP = -4.25
THETA_FIRST_FLAT = -2.45
THETA_STEP = 3.0

# Designator (top-left) and braille (top-right) geometry, modeled on cof_top.py
TOP_LINE_R = 316.53
BOTTOM_LINE_R = 266.55
DESIGNATOR_R = (TOP_LINE_R + 340) / 2 + 2  # 330.27 (was 328.27)
MINOR_R = (BOTTOM_LINE_R + 245) / 2 - 2    # 253.78 (was 255.78)
DESIGNATOR_SIZE = (340 - TOP_LINE_R) * 0.85  # 19.95
MINOR_SIZE = (BOTTOM_LINE_R - 245) * 0.85    # 18.32
DESIGNATOR_DEG = -12.904  # angle for left edge of designator text (matches staff margin)
MINOR_DEG = 12.904        # mirror of major designator on the bottom-right
BRAILLE_DEG_CENTER = 8.45 # angle for pedal diagram midpoint (arc right end at staff margin)
BRAILLE_SPAN = 9.0        # angular span of pedal arc
BRAILLE_ARC_R = 337.0     # radius for pedal arc

KEYS = [
    # (filename, major, minor, kind, count, braille)
    ('C.svg',      'C',  'Am',  '#', 0, '⠒⠺⠒⠒'),
    ('G.svg',      'G',  'Em',  '#', 1, '⠒⠺⠢⠒'),
    ('D.svg',      'D',  'Bm',  '#', 2, '⠢⠺⠢⠒'),
    ('A.svg',      'A',  'F♯m', '#', 3, '⠢⠺⠢⠔'),
    ('E.svg',      'E',  'C♯m', '#', 4, '⠤⠺⠢⠔'),
    ('B.svg',      'B',  'G♯m', '#', 5, '⠤⠺⠢⠤'),
    ('fsharp.svg', 'F♯', 'D♯m', '#', 6, '⠤⠺⠤⠤'),
    ('F.svg',      'F',  'Dm',  'b', 1, '⠒⠹⠒⠒'),
    ('Bb.svg',     'B♭', 'Gm',  'b', 2, '⠒⠹⠑⠒'),
    ('Eb.svg',     'E♭', 'Cm',  'b', 3, '⠒⠹⠑⠊'),
    ('Ab.svg',     'A♭', 'Fm',  'b', 4, '⠑⠹⠑⠊'),
    ('Db.svg',     'D♭', 'B♭m', 'b', 5, '⠑⠹⠑⠉'),
]

def staff_r(p): return MIDDLE_R + p * SPACING / 2

def pol(theta_deg, r):
    th = math.radians(theta_deg)
    return CX + r * math.sin(th), CY - r * math.cos(th)

def glyph_defs():
    """Return the sharp and flat glyph definitions as a string."""
    sharp = (f'<g id="sharp" fill-rule="evenodd">'
             f'<g transform="translate(-{SHARP_CX} 0) scale({SHARP_SCALE} -{SHARP_SCALE})">'
             f'<path d="{SHARP_PATH}"/></g></g>')
    flat = (f'<g id="flat" fill-rule="evenodd">'
            f'<g transform="translate(-{FLAT_CX} 0) scale({SHARP_SCALE} -{SHARP_SCALE})">'
            f'<path d="{FLAT_PATH}"/></g></g>')
    return sharp + flat

def key_body(display, minor, kind, count, braille):
    """Return the SVG body content for a key cell — staff, clef, accidentals,
    designator, braille — without the cell border or <defs>. Coordinates use
    disc center (CX, CY) = (80.82, 340)."""
    order = ORDER_SHARPS if kind == '#' else ORDER_FLATS
    pos = SHARP_POS if kind == '#' else FLAT_POS
    glyph_id = 'sharp' if kind == '#' else 'flat'

    theta_first = THETA_FIRST_SHARP if kind == '#' else THETA_FIRST_FLAT
    accs = []
    for i in range(count):
        acc = order[i]
        theta = theta_first + i * THETA_STEP
        r = staff_r(pos[acc])
        x, y = pol(theta, r)
        accs.append(f'<use href="#{glyph_id}" '
                    f'transform="translate({x:.2f} {y:.2f}) rotate({theta:.2f})"/>')

    dx, dy = pol(DESIGNATOR_DEG, DESIGNATOR_R)
    designator = (f'<text x="{dx:.2f}" y="{dy:.2f}" '
                  f'transform="rotate({DESIGNATOR_DEG:.2f} {dx:.2f} {dy:.2f})" '
                  f'font-family="FreeSerif, serif" font-size="{DESIGNATOR_SIZE:.2f}" '
                  f'text-anchor="start" dominant-baseline="middle" '
                  f'font-weight="bold">{display}</text>')

    mdx, mdy = pol(MINOR_DEG, MINOR_R)
    minor_designator = (f'<text x="{mdx:.2f}" y="{mdy:.2f}" '
                        f'transform="rotate({MINOR_DEG:.2f} {mdx:.2f} {mdy:.2f})" '
                        f'font-family="FreeSerif, serif" font-size="{MINOR_SIZE:.2f}" '
                        f'text-anchor="end" dominant-baseline="middle" '
                        f'font-style="italic">{minor}</text>')

    # Decode pedal positions from braille (D C B | E F G A)
    # Cell 1: D (dots 1/2/3 = flat/nat/sharp), C (dots 4/5/6)
    # Cell 2: B (dots 1/2/3), split (right col ignored)
    # Cell 3: E (1/2/3), F (4/5/6)
    # Cell 4: G (1/2/3), A (4/5/6)
    def _decode_col(bits, base_bit):
        if bits & (1 << base_bit):       return 'flat'
        if bits & (1 << (base_bit + 1)): return 'natural'
        if bits & (1 << (base_bit + 2)): return 'sharp'
        return 'natural'
    b = [ord(c) - 0x2800 for c in braille]
    pedals = [
        _decode_col(b[0], 0), _decode_col(b[0], 3),  # D, C
        _decode_col(b[1], 0),                         # B
        _decode_col(b[2], 0), _decode_col(b[2], 3),  # E, F
        _decode_col(b[3], 0), _decode_col(b[3], 3),  # G, A
    ]

    # Arc pedal diagram: 7 short radial marks (3 + 4) on a reference arc,
    # with a longer radial divider between B and E.
    MARK_LEN = 6.0
    MARK_THICK = 1.8
    DIV_LEN = 10.0
    DIV_THICK = 0.5
    n_slots = 8  # 7 pedals + 1 divider
    slot_step = BRAILLE_SPAN / n_slots
    pedal_svg = []
    # Reference arc
    pa_start = BRAILLE_DEG_CENTER - BRAILLE_SPAN / 2
    pa_end = BRAILLE_DEG_CENTER + BRAILLE_SPAN / 2
    px1, py1 = pol(pa_start, BRAILLE_ARC_R)
    px2, py2 = pol(pa_end, BRAILLE_ARC_R)
    pedal_svg.append(
        f'<path d="M {px1:.2f} {py1:.2f} A {BRAILLE_ARC_R} {BRAILLE_ARC_R} 0 0 1 '
        f'{px2:.2f} {py2:.2f}" fill="none" stroke="#a83214" stroke-width="0.35"/>')
    # 7 pedal marks (slot 3 reserved for divider)
    for i, p in enumerate(pedals):
        slot_idx = i if i < 3 else i + 1
        theta = BRAILLE_DEG_CENTER - BRAILLE_SPAN / 2 + (slot_idx + 0.5) * slot_step
        if p == 'flat':
            r_in, r_out = BRAILLE_ARC_R, BRAILLE_ARC_R + MARK_LEN
        elif p == 'sharp':
            r_in, r_out = BRAILLE_ARC_R - MARK_LEN, BRAILLE_ARC_R
        else:  # natural
            r_in, r_out = BRAILLE_ARC_R - MARK_LEN / 2, BRAILLE_ARC_R + MARK_LEN / 2
        x1, y1 = pol(theta, r_in)
        x2, y2 = pol(theta, r_out)
        pedal_svg.append(
            f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
            f'stroke="#a83214" stroke-width="{MARK_THICK}" stroke-linecap="butt"/>')
    # Divider (longer thin radial line between B and E)
    theta_div = BRAILLE_DEG_CENTER - BRAILLE_SPAN / 2 + 3.5 * slot_step
    dx1, dy1 = pol(theta_div, BRAILLE_ARC_R - DIV_LEN / 2)
    dx2, dy2 = pol(theta_div, BRAILLE_ARC_R + DIV_LEN / 2)
    pedal_svg.append(
        f'<line x1="{dx1:.2f}" y1="{dy1:.2f}" x2="{dx2:.2f}" y2="{dy2:.2f}" '
        f'stroke="#a83214" stroke-width="{DIV_THICK}"/>')

    staff_lines = '\n'.join(f'<path d="{p}"/>' for p in STAFF_PATHS)
    accs_str = '\n'.join(accs)
    braille_str = '\n'.join(pedal_svg)
    return (f'<g stroke="#000" stroke-width="0.4" fill="none">\n{staff_lines}\n</g>\n'
            f'{CLEF}\n'
            f'<g>\n{accs_str}\n</g>\n'
            f'{designator}\n'
            f'{minor_designator}\n'
            f'{braille_str}\n')

def make_svg(display, minor, kind, count, braille):
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 161.64 102">
  <defs>{glyph_defs()}</defs>
  <path d="{CELL_PATH}" fill="white" stroke="#000" stroke-width="0.5"/>
  {key_body(display, minor, kind, count, braille)}
</svg>
'''

if __name__ == '__main__':
    for fname, display, minor, kind, count, braille in KEYS:
        svg = make_svg(display, minor, kind, count, braille)
        with open(fname, 'w') as f:
            f.write(svg)
        print(f'wrote {fname}')
