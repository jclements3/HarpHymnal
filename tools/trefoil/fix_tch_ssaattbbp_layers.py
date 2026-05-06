#!/usr/bin/env python3
"""Post-process Tch-SSAATTBBP MEI to fix moving/sustained layer assignment.

The Claude API composes good harmonies but puts everything in layer 1.
This script:
1. Parses each measure's staff 2 (RH) and staff 3 (LH) chord events
2. At each beat, compares pitches with the previous beat
3. Unchanged pitches → layer 2 (sustained, stems down) as held notes
4. Changed pitches → layer 1 (moving, stems up)
5. Removes duplicate pitches between layers
6. The pedal note (lowest LH note) always goes in layer 2

Input:  handout/tch_ssaattbbp_out/NNNN.mei  (raw AI output)
Output: handout/tch_ssaattbbp_out/NNNN.mei  (overwritten with fixed layers)
        app/tch_ssaattbbp_mei.json           (combined JSON for app)
"""

import json, re, sys
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / 'handout' / 'tch_ssaattbbp_out'
LEAD_SHEETS = ROOT / 'app' / 'lead_sheets.json'
COMBINED_OUTPUT = ROOT / 'app' / 'tch_ssaattbbp_mei.json'

NS = 'http://www.music-encoding.org/ns/mei'
ET.register_namespace('', NS)


def ns(tag):
    return f'{{{NS}}}{tag}'


def pitch_key(note_el):
    """Return a hashable pitch tuple (pname, oct, accid_ges) from a <note>."""
    p = note_el.get('pname', '')
    o = note_el.get('oct', '')
    a = note_el.get('accid.ges', '')
    return (p, o, a)


def make_note_el(pitch, dur, dots=0, xml_id=None, extra_attribs=None):
    """Create a new <note> element."""
    el = ET.Element(ns('note'))
    el.set('pname', pitch[0])
    el.set('oct', pitch[1])
    if pitch[2]:
        el.set('accid.ges', pitch[2])
    el.set('dur', str(dur))
    if dots:
        el.set('dots', str(dots))
    if xml_id:
        el.set('{http://www.w3.org/XML/1998/namespace}id', xml_id)
    if extra_attribs:
        for k, v in extra_attribs.items():
            el.set(k, v)
    return el


def make_chord_el(notes_els, dur, dots=0, xml_id=None):
    """Create a <chord> element containing <note> children."""
    ch = ET.Element(ns('chord'))
    ch.set('dur', str(dur))
    if dots:
        ch.set('dots', str(dots))
    if xml_id:
        ch.set('{http://www.w3.org/XML/1998/namespace}id', xml_id)
    for n in notes_els:
        ch.append(n)
    return ch


def extract_beat_events(layer_el):
    """Extract a list of beat events from a layer.

    Each event is a dict:
      {'pitches': set of pitch_key tuples,
       'dur': str, 'dots': int,
       'notes': list of note elements (from chord or standalone),
       'element': the original chord or note element}
    """
    events = []
    for child in layer_el:
        tag = child.tag.replace(f'{{{NS}}}', '')
        if tag == 'chord':
            notes = list(child.iter(ns('note')))
            pitches = set(pitch_key(n) for n in notes)
            events.append({
                'pitches': pitches,
                'dur': child.get('dur', '4'),
                'dots': int(child.get('dots', '0')),
                'notes': notes,
                'element': child,
            })
        elif tag == 'note':
            pk = pitch_key(child)
            events.append({
                'pitches': {pk},
                'dur': child.get('dur', '4'),
                'dots': int(child.get('dots', '0')),
                'notes': [child],
                'element': child,
            })
        elif tag == 'rest' or tag == 'mRest':
            events.append({
                'pitches': set(),
                'dur': child.get('dur', '4'),
                'dots': int(child.get('dots', '0')),
                'notes': [],
                'element': child,
            })
    return events


def dur_to_quarters(dur_str, dots):
    """Convert MEI dur + dots to duration in quarter notes."""
    base = {'1': 4.0, '2': 2.0, '4': 1.0, '8': 0.5, '16': 0.25, '32': 0.125}
    d = base.get(dur_str, 1.0)
    dot_add = d
    for _ in range(dots):
        dot_add /= 2
        d += dot_add
    return d


def quarters_to_dur(q):
    """Find the best MEI dur + dots for a duration in quarters."""
    candidates = [
        (4.0, '1', 0), (3.0, '2', 1), (2.0, '2', 0), (1.5, '4', 1),
        (1.0, '4', 0), (0.75, '8', 1), (0.5, '8', 0), (0.375, '16', 1),
        (0.25, '16', 0), (0.125, '32', 0),
    ]
    for val, dur, dots in candidates:
        if abs(q - val) < 0.01:
            return dur, dots
    # Fallback: closest
    best = min(candidates, key=lambda c: abs(q - c[0]))
    return best[1], best[2]


def fix_staff_layers(staff_el, prev_pitches, is_lh=False, id_counter=[0]):
    """Rewrite a staff's layers into proper moving (L1) / sustained (L2).

    Returns the set of pitches sounding at the end of this measure
    for use as prev_pitches in the next measure.
    """
    # Collect all events from all existing layers
    all_events = []
    for layer in list(staff_el.iter(ns('layer'))):
        all_events.extend(extract_beat_events(layer))

    if not all_events:
        return prev_pitches

    # Remove all existing layers
    for layer in list(staff_el.findall(ns('layer'))):
        staff_el.remove(layer)

    # Build moving and sustained event streams
    moving_events = []    # layer 1, stems up
    sustained_events = [] # layer 2, stems down
    current_sustained = set(prev_pitches)  # pitches being held from previous measure

    for ev in all_events:
        if not ev['pitches']:
            # Rest — add to both layers
            moving_events.append(('rest', ev['dur'], ev['dots'], []))
            sustained_events.append(('rest', ev['dur'], ev['dots'], []))
            current_sustained = set()
            continue

        new_pitches = ev['pitches'] - current_sustained  # moving
        held_pitches = ev['pitches'] & current_sustained  # sustained

        # For LH: pedal = lowest pitch, always in sustained layer
        if is_lh and ev['pitches']:
            sorted_p = sorted(ev['pitches'], key=lambda p: (int(p[1]), p[0]))
            pedal_pitch = sorted_p[0]
            # Ensure pedal is in sustained, not moving
            if pedal_pitch in new_pitches:
                new_pitches.discard(pedal_pitch)
                held_pitches.add(pedal_pitch)

        # If this is the first beat (no prior sustained), everything is moving
        if not current_sustained and not held_pitches:
            new_pitches = ev['pitches']

        # Build note elements for each layer
        def build_notes(pitch_set):
            notes = []
            for pk in sorted(pitch_set, key=lambda p: (int(p[1]), p[0])):
                id_counter[0] += 1
                n = make_note_el(pk, ev['dur'], ev['dots'],
                                 xml_id=f'fx{id_counter[0]}')
                notes.append(n)
            return notes

        if new_pitches:
            mnotes = build_notes(new_pitches)
            moving_events.append(('notes', ev['dur'], ev['dots'], mnotes))
        else:
            moving_events.append(('rest', ev['dur'], ev['dots'], []))

        if held_pitches:
            snotes = build_notes(held_pitches)
            sustained_events.append(('notes', ev['dur'], ev['dots'], snotes))
        else:
            sustained_events.append(('rest', ev['dur'], ev['dots'], []))

        # Update sustained set for next beat
        current_sustained = ev['pitches']

    # Now try to merge consecutive sustained events with the same pitches into
    # longer tied notes. This is the key stacking optimization.
    def merge_sustained(events):
        """Merge consecutive events with identical pitch sets into one longer note."""
        if not events:
            return events
        merged = [events[0]]
        for ev in events[1:]:
            prev = merged[-1]
            if (prev[0] == 'notes' and ev[0] == 'notes' and
                set(pitch_key(n) for n in prev[3]) == set(pitch_key(n) for n in ev[3])):
                # Same pitches — extend duration
                prev_q = dur_to_quarters(prev[1], prev[2])
                ev_q = dur_to_quarters(ev[1], ev[2])
                total_q = prev_q + ev_q
                new_dur, new_dots = quarters_to_dur(total_q)
                # Rebuild with merged duration
                new_notes = []
                id_counter[0] += 1
                for n in prev[3]:
                    nn = make_note_el(pitch_key(n), new_dur, new_dots,
                                      xml_id=f'fx{id_counter[0]}')
                    id_counter[0] += 1
                    new_notes.append(nn)
                merged[-1] = ('notes', new_dur, new_dots, new_notes)
            else:
                merged.append(ev)
        return merged

    sustained_events = merge_sustained(sustained_events)

    # Emit layer 1 (moving)
    layer1 = ET.SubElement(staff_el, ns('layer'))
    layer1.set('n', '1')
    has_moving = False
    for etype, dur, dots, notes in moving_events:
        if etype == 'rest' or not notes:
            r = ET.SubElement(layer1, ns('rest'))
            r.set('dur', dur)
            if dots:
                r.set('dots', str(dots))
        elif len(notes) == 1:
            layer1.append(notes[0])
            has_moving = True
        else:
            id_counter[0] += 1
            ch = make_chord_el(notes, dur, dots, xml_id=f'fxc{id_counter[0]}')
            layer1.append(ch)
            has_moving = True

    # Emit layer 2 (sustained)
    has_sustained = any(e[0] == 'notes' and e[3] for e in sustained_events)
    if has_sustained:
        layer2 = ET.SubElement(staff_el, ns('layer'))
        layer2.set('n', '2')
        for etype, dur, dots, notes in sustained_events:
            if etype == 'rest' or not notes:
                r = ET.SubElement(layer2, ns('rest'))
                r.set('dur', dur)
                if dots:
                    r.set('dots', str(dots))
                r.set('visible', 'false')
            elif len(notes) == 1:
                layer2.append(notes[0])
            else:
                id_counter[0] += 1
                ch = make_chord_el(notes, dur, dots, xml_id=f'fxc{id_counter[0]}')
                layer2.append(ch)

    # If no moving notes at all, swap: make the sustained layer be layer 1
    if not has_moving and has_sustained:
        staff_el.remove(layer1)
        layer2.set('n', '1')

    return current_sustained


def fix_mei(mei_text):
    """Fix all staves in the MEI, returning the corrected MEI text."""
    tree = ET.ElementTree(ET.fromstring(mei_text))
    root = tree.getroot()

    # Find all measures
    measures = list(root.iter(ns('measure')))

    prev_rh_pitches = set()
    prev_lh_pitches = set()

    for measure in measures:
        staffs = list(measure.findall(ns('staff')))
        for staff in staffs:
            n = staff.get('n')
            if n == '2':  # RH
                prev_rh_pitches = fix_staff_layers(
                    staff, prev_rh_pitches, is_lh=False)
            elif n == '3':  # LH
                prev_lh_pitches = fix_staff_layers(
                    staff, prev_lh_pitches, is_lh=True)
            # Staff 1 (melody) is left unchanged

    # Serialize back to string
    ET.indent(tree, space='  ')
    return ET.tostring(root, encoding='unicode', xml_declaration=True)


def main():
    mei_files = sorted(OUTPUT_DIR.glob('*.mei'))
    if not mei_files:
        print('No MEI files found in', OUTPUT_DIR)
        return

    # Optional: process single file
    single_n = None
    for arg in sys.argv[1:]:
        if arg.isdigit():
            single_n = arg

    processed = 0
    for fp in mei_files:
        n = fp.stem
        if single_n and n != single_n:
            continue
        print(f'Fixing {fp.name}...', end=' ', flush=True)
        try:
            mei_text = fp.read_text()
            fixed = fix_mei(mei_text)
            fp.write_text(fixed)
            print(f'OK ({len(fixed)} chars)')
            processed += 1
        except Exception as e:
            print(f'ERROR: {e}')

    print(f'\nFixed {processed} files')

    # Rebuild combined JSON
    print('Combining MEI files...')
    lead_sheets = json.loads(LEAD_SHEETS.read_text())
    ls_map = {str(ls['n']): ls for ls in lead_sheets}
    results = []
    for fp in sorted(OUTPUT_DIR.glob('*.mei')):
        n = fp.stem
        if n not in ls_map:
            continue
        ls = ls_map[n]
        mei_text = fp.read_text()
        if len(mei_text) > 200:
            results.append({
                'n': n,
                't': ls['t'],
                'key': ls['key'],
                'tempo': 100,
                'mei': mei_text,
            })
    COMBINED_OUTPUT.write_text(json.dumps(results, ensure_ascii=False))
    print(f'Combined {len(results)} hymns → {COMBINED_OUTPUT} ({COMBINED_OUTPUT.stat().st_size // 1024} KB)')


if __name__ == '__main__':
    main()
