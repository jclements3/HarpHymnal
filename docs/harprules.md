# Harp voicing rules

Converting SATB hymns to harp. Start with 4 valid independent melodies that already harmonize. Reallocate wasted re-plucks into other voices.

## The principle

A SATB voice that repeats the same pitch on consecutive beats wastes a pluck on harp — the string is still ringing. Collapse the repeat to a sustain. The finger that would have re-plucked is now free for that beat. Decide what to do with it.

## The roster

8 voices defined. SATB = 4 of them. The other 4 are usually idle, populated only when fingers are freed.

|Voice|Range|Role                                         |
|-----|-----|---------------------------------------------|
|Dr   |C1–B1|Sub-bass drone (pedal harp only)             |
|B    |C2–C4|Bass. Root motion.                           |
|T2   |C3–E4|LH inner. Populated when LH finger is free.  |
|T1   |E3–G4|LH upper inner. SATB tenor lives here.       |
|A2   |G3–C5|RH lower inner. Populated when RH finger is free. |
|A1   |C4–E5|RH inner. SATB alto lives here.              |
|S2   |E4–G5|RH upper. Populated when RH finger is free.  |
|S1   |G4–C6|Melody. SATB soprano.                        |
|Gl   |B6–G7|Glissando (pedal harp only)                  |

Lever harp: drop Dr and Gl. Source SATB voices land in S1 (soprano), A1 (alto), T1 (tenor), B (bass). T2, A2, S2 are the "empty" voices available to receive freed-finger fills.

## Procedure

1. **Take the source SATB beat-by-beat.** S1 = soprano, A1 = alto, T1 = tenor, B = bass.
2. **Find repeats.** For each voice, scan consecutive beats. If voice V plays the same pitch at beat N and beat N+1, mark N+1 as a re-pluck of V.
3. **Collapse to sustains.** Replace the repeated beats with a single longer note in V.
4. **Each collapsed re-pluck frees one finger** at that beat in the hand that owns V (LH owns B/T1; RH owns A1/S1).
5. **For each freed finger, choose what to do with it.** Options below. Idle is always valid.

## Freed-finger fill options

|Option|What it does|When to use|
|------|------------|-----------|
|idle  |Do nothing. Finger rests. Texture thins.|Contemplative passages, phrase openings, after climaxes.|
|chord-tone fill|Pluck a chord tone not currently sounding, in the empty voice for that hand.|Most beats. Standard density-thickener.|
|neighbor decoration|Step away from a held pitch and back to it, in the empty voice.|Inner motion under sustained outer voices.|
|anticipation|Pluck the next beat's pitch from one of the SATB voices, an eighth or quarter early.|Approaching a strong beat or cadence.|
|octave-fill|Double an outer voice at the octave, in the empty voice.|Climax moments, final cadence, structural arrivals.|
|passing-tone|Step between two adjacent chord tones, in the empty voice.|Connect-the-dots inner line.|

## Hand mechanics

- 4 fingers per hand, no pinky. Max 4 plucks per hand per beat.
- Hand span ≤ 11 strings (octave + 4th). Anything wider needs a roll or hand split.
- LH covers B, T1, T2, (Dr). RH covers A1, A2, S1, S2, (Gl).
- Voice-to-hand assignment is the *default routing*. The player may cross hands when register makes it easier. Don't over-specify.
- Open voicing: when both hands hold chord shapes, leave ~2 strings between LH-top and RH-bottom. Closer placements require register-specific judgment.

## Sustain and damping

- Plucked strings ring. Decay times for lever harp: C2–B2 ~8 beats, C3–B3 ~4, C4–B4 ~2, C5–B5 ~1, above ~½.
- Re-plucking a string replaces its prior vibration. No separate damping needed for re-plucks.
- Damping is needed only when a ringing pitch is no longer wanted AND nothing will re-pluck that string. Mark with `!damp!` decoration. Most pieces need none.
- Default policy declared in the legend: "Let strings ring; damp only where indicated."

## Accidentals

- Each accidental costs a pedal change (pedal harp) or lever change (lever harp) on its pitch class.
- Lever changes during sustain on the same pitch class buzz. Schedule changes into rests in that pitch class.
- Prefer source keys with few accidentals. Lever harp tuned in Eb plays Eb/Bb/F/C/G/D/A/E major.
- Hymns with heavy chromaticism should be re-keyed or accept tactile breaks.

## SATB voice motion preserved

The SATB voices already follow good voice-leading. Don't override:

- No parallel 5ths or 8ves between SATB voices (the source got this right).
- Leading-tone resolves up; chordal 7th resolves down.
- The freed-finger fills are added *on top of* the SATB voices, not replacing them. They can reinforce or decorate but should not create parallels with existing voices.

## Texture by hymn character

|Character|Sustain density|Freed-finger fill rate|
|---------|---------------|----------------------|
|Contemplative / closing|High (collapse most repeats)|Low (most fingers idle)|
|Festive / opening|Medium|High (chord-tone and octave fills)|
|Stately / processional|Medium|Medium (passing tones, anticipations)|
|Pastoral|High|Low to medium (neighbor decorations)|

## Output format (ABC)

- Two voices: RH (treble) + LH (bass), grouped on grand staff `%%staves {RH LH}`.
- Within each voice: `[xy]` for chord-stacks (aligned rhythms), `&` for voice overlay (mixed rhythms within a beat group).
- Empty voices (T2, A2, S2) are *not separate ABC voices* — they appear as additional notes inside the relevant hand's chord-stacks or overlay segments at freed-finger beats.
- `%%MIDI program 46` per voice (orchestral harp).
- Render PDF with abcm2ps; render MIDI with abc2midi (use `-NFER` to suppress fermata-MIDI-desync).

## Audit checklist

1. SATB pitches preserved (no SATB voice was altered, only collapsed-to-sustain).
2. Voice totals match across all voices (no rhythmic desync).
3. Max simultaneous attacks per beat ≤ 8 (4 per hand).
4. Max hand span ≤ 11 strings.
5. Bass not below C2 (lever harp) or A0 (pedal harp).
6. Accidentals counted; lever changes scheduled into rests in that pitch class.
