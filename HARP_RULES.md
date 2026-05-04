# HarpHymnal pedal-harp composition rules

> **Read this when composing for the 47-string pedal harp in this project.** The same rules are also embedded in:
> - the `abccomposer/index.html` `DEFAULT_SYSTEM` prompt (so the tablet's built-in Claude chat has them automatically)
> - Claude Code's local auto-memory at `~/.claude/projects/.../memory/project_pedal_harp_composition.md` (per-machine, NOT version-controlled — this file is the portable copy that travels with the repo)
>
> If you change a rule, update **all three** places so they don't drift.

Rules for composing 47-string pedal-harp music in HarpHymnal projects (Boddie, Nicene Creed, future). Source: project conventions + the user's curated cheatsheet (originally `~/Downloads/pedal-harp-rules.md`, 2026-05-04).

# Project-specific constraints (Boddie / Nicene Creed)

- **Range:** 47-string pedal harp, **C1..G7** inclusive (MIDI 24..103). Out-of-range pitches are illegal.
- **Three vertical zones — DON'T cross them:**
  - **C1..B1 (lowest harp octave, 7 strings) — DRONE ZONE.** Reserved exclusively for *single-pitch* organ-pedal drones that reinforce the church mode. **NEVER place chord notes here**, not even open-spread voicings. A chord with even one note in C1..B1 (e.g. `[C,,,G,,,C,,E,,]` = C1 G1 C2 E2) violates the rule. Drones go in as `"drone"X,,,` where X is the modal centre (D under Dorian, E under Phrygian, etc.).
  - **C2..C6 (~36 strings around middle C) — PRIMARY ACTION.** This is where the bulk of the music lives — chords, melody, voice leading, harmonic motion. Most LH and RH activity happens here.
  - **C6..G7 (top harp octave-plus, ~12 strings) — FLUFF / ANGEL ZONE.** Rare for chords. Reserved for sparkle: glissandi, ascending flourishes, climactic arpeggios, "angel-sounding" runs and trills. Chord usage up here is exceptional (e.g. a climax) — not the default.
- **Diatonic only** for these compositions — no lever flips, no accidentals during play. All notes drawn from the key signature. (Rules out chromatic alterations, secondary dominants, harmonic-minor V; substitution strategies live in `harp_mapper.py`.)
- **The user uses SCIENTIFIC octave numbering throughout — NOT harp numbering.** When the user says "C1" they mean scientific C1 = lowest bass pitch on the harp (MIDI 24); "C6" = treble; "middle C" = C4. The harp-octave-from-the-top numbering (harp 1 = highest) was background information, *not* the user's working frame. Always think in scientific. **Harp C1 ≠ user's C1.**
- **Stripchart orientation = standard music-staff orientation.** C1 (bass / lowest pitch) at the BOTTOM of the chart, C7/G7 (treble / highest pitch) at the TOP, middle C (C4) in the middle (red, matching the harp's red middle-C string). Ascending pitches visually ascend. Gutter labels are SCIENTIFIC: C1, C2, C3, C4 (red), C5, C6, C7 from bottom up. The chord-symbol track sits at the bottom of the pane (below the C1 lane).
- **ABC source uses scientific octave numbering matching what's on screen:** `C,,, = C1`, `C,, = C2`, `C, = C3`, `C = C4` (middle C), `c = C5`, `c' = C6`, `c'' = C7`. Apostrophes raise an octave from lowercase; commas lower an octave from uppercase. A "scale above C6" written in ABC is `c'/8 d'/8 e'/8 ... c''/8` for C6→C7, or `g'/8 ... g''/8` for G6→G7. Lowercase + commas (e.g. `c,,`) is valid but confusing — prefer uppercase + commas (`C,`) for octaves below middle C and lowercase + apostrophes (`c'`) for octaves above.

# Stripchart color scheme — discussing notes by color + octave

The stripchart's `colorForDegree()` function paints each scale-degree (in the current key) a Dracula-palette color. Lane backgrounds carry the color at ~10% opacity; individual note bars use the color at full saturation. So a note's color *is* its scale-degree at a glance, and the user often refers to notes by **color + octave** (e.g. "pink-4" = B4, "red-2" = C2).

| Degree | Pitch class (C major) | Color  | Hex       |
|--------|-----------------------|--------|-----------|
| 1      | C (tonic)             | red    | `#ff5555` |
| 2      | D                     | orange | `#ffb86c` |
| 3      | E                     | yellow | `#f1fa8c` |
| 4      | F                     | green  | `#50fa7b` |
| 5      | G                     | cyan   | `#8be9fd` |
| 6      | A                     | purple | `#bd93f9` |
| 7      | B                     | pink   | `#ff79c6` |

- **Colors are SCALE-DEGREE, not absolute pitch class.** They shift with the key. For C major / A minor (and any other key whose tonic is C), C = red (degree 1). In G major, G = red because G is degree 1 there; D = orange because D is degree 2; etc.
- `colorForDegree()` snaps non-diatonic notes to the nearest scale degree, so an accidental still renders in one of the seven colors (no extra hue for chromatic tones).
- Examples (in C major / A minor):
  - **pink-4** = B4
  - **red-1** = C1 (drone-zone tonic)
  - **purple-6** = A6 (top of fluff zone before the C–G7 octave)
  - **cyan-3** = G3, **yellow-5** = E5, **green-2** = F2
- When the user says something like "pink whole notes" while looking at the stripchart, they mean **B-pitched whole notes specifically** (in C major / A minor) — translate color + register back to pitch before acting.

# Hand & chord limits

- **4 notes per hand** (thumb + 3 fingers — no pinky). **8 notes total** across both hands.
- **Span: 10th comfortable, 11th max.** Every chord (treble or bass) must span ≤ 10 diatonic strings (≈ octave + a 3rd).
- **Open spacing** (10th outer, inner notes filling) sounds bigger than close position. Idiomatic two-hand voicing: LH 10th + RH 10th + ~1-octave gap between hands = ~3 octaves of chord.
- **Two-hand chords:** stagger reaches so neither hand exceeds a 10th; a 13th *between* hands is trivial.
- **Same letter can't sound together** unless enharmonically respelled (C♯ + D♭ OK — different strings). Diatonic projects can't exploit this; chromatic projects can.

# Pedals (chromatic projects only — diatonic projects ignore)

- 7 pedals, 3 positions (♭ ♮ ♯). Left foot: D C B. Right foot: E F G A.
- ~1/4 sec between notes on that letter for a change. Max 2 simultaneous changes (one per foot).
- Notate at the moment of foot movement.
- Enharmonics are *free strings* — respell to dodge a change (C♯ = D♭ are different strings).
- **C♭-major is rest position** (all flats). Modulations cost pedal changes — budget them.
- C/G/F cycle moves are all single-pedal: F→C needs B♭→♮, C→G needs F♮→♯, G→F reverses both.

# Sustain & drones (C1–B1)

- Harp strings ring naturally; **re-striking the same chord/voicing in succession smears into a muddy column**. Vary chord and/or voicing on every strike, even within a phrase. Use inversions for stepwise voice leading instead of root-position throughout.
- **Drone-only zone: C1..B1** (lowest harp octave). Wire-wound strings, longest sustain (8–15 sec). Use sparingly — one drone per phrase or per modal section is plenty. **Strict rule: only single-pitch drones in C1..B1, no multi-note voicings.** The earlier "open root+5+octave" pattern (e.g. `C1 G1 C2 E2`) is *not* allowed — that's a chord and chords are forbidden in C1..B1.
- Drones are **slow to speak** — give them downbeats, not pickups.
- Damp by laying the palm on strings at harmony changes, or write rests with explicit étouffé.
- Best as **pedal points under modal sections**: low D under Dorian, low E under Phrygian, etc. — the drone defines the mode for the listener.
- Avoid drones in fast harmonic rhythm — overlapping bass strings create mush. One drone, let it bloom, damp, next.
- Drone notation in ABC: `"drone"X,,,` for the C1..B1 zone (e.g. `"drone"E,,,` = E1, `"drone"A,,,` = A1, `"drone"C,,,` = C1).

# Harmony — what works

- **Quartal/quintal voicings (4ths, 5ths)** ring beautifully and avoid the muddy-thirds problem in low register.
- **Avoid closely-voiced thirds below C2**; 5ths or wider sound clearer down there.
- **7th chords:** spread voicings (1-5-7-3 or 1-7-3-5) sound idiomatic; root-position close voicings sound stiff.
- **Add9 / sus2 / sus4** voicings exploit open-string resonance and need fewer pedals.
- **Modal harmony favors the harp** — minimizes accidentals, set pedals once per section.
- **Parallel triads / quartal chords** with hands in oblique or contrary motion are pure harp.

# Glissandi

- Pedal-tune all 7 strings to scale/chord, sweep. Diatonic, pentatonic, whole-tone, dim7, dom7 are all standard.
- Notate the pedal setting above the gliss.
- **Modal glissandi:** set pedals to the mode for instant character (Lydian gliss, Phrygian gliss…).
- **Above G7 = glissando-only zone** in this project — never melodic notes.

# Modal melody — register strategy

| Mode       | LH melody character                              | RH melody character                            |
|------------|--------------------------------------------------|------------------------------------------------|
| Lydian     | bright tonic + raised-4 drone ringing under      | sparkling top; ♯4 stands out at C5–C6          |
| Ionian     | warm, around C2–C4                               | standard treble                                |
| Mixolydian | ♭7 colors well at C3–C4, sub-tonic feel          | RH ♭7 against tonic drone is the sound         |
| Dorian     | minor with bright IV — LH around D2–D3 strong    | major IV chord in middle register, classic    |
| Aeolian    | natural minor, full register works               | RH plaintive — top octave thin, stay C5–G6     |
| Phrygian   | ♭2 needs LH emphasis to sell the mode            | RH ♭2 as upper neighbor to tonic               |
| Locrian    | unstable — treat as color, not home              | rare, use as transient                         |

(Mode terminology uses harp/scientific note names. For diatonic projects, "♭7" etc. read as the relevant scale degree of the diatonic mode rather than literal lever flips.)

# General melodic placement

- **LH melody best C2–C4** (resonant, articulate).
- **RH melody best C4–C6** (heart of the instrument).
- Above C6 thins quickly — reserve for sparkle and accent, not sustained line.
- Below C2 = drone territory, not melody.

# Color effects

- **Harmonics:** sound 8va above written; one per hand practical; middle register only.
- **Bisbigliando:** whispered tremolo on enharmonic unisons.
- **Près de la table:** near soundboard, guitar-like.
- **Xylophonic:** muted, percussive.

# Polychords (`upper~lower` notation)

Two triads stacked, each clearly its own chord. The harp is unusually well-suited because two hands hold two distinct voicings cleanly.

**Why the harp fits:** LH/RH separate naturally into two harmonic strata. 8 notes available — enough for two full triads (3+3) or two 7ths sharing a tone (4+4 with overlap). Pedal setting locks all 7 letters at once, so any diatonic polychord costs zero extra pedal work. Sustain is the point — both chords ring together.

**Voicing rules:**
- Separate the two triads by **at least an octave** — closer than that, the ear fuses them into a cluster.
- LH = lower triad, root position or open. RH = upper triad, any inversion.
- Common spacing: LH root + 5th + 10th; RH triad above C5. The gap sells the polychord.
- Don't double the shared tone in both hands — collapses the stack.
- If the two triads share a pitch class, voice it only once (in the upper structure).

**Idiomatic diatonic pairs (zero pedal cost):**
| Pair      | Sound                                                |
|-----------|------------------------------------------------------|
| I/V       | C/G — bright, suspended, common                      |
| ii/I      | Dm/C — warm, Lydian-ish color                        |
| IV/I      | F/C — plagal shimmer                                 |
| V/IV      | G/F — Mixolydian, ♭7 implied                         |
| vi/IV     | Am/F — minor color over major root                   |
| ♭VII/I    | B♭/C in C-Mixolydian — rock/folk                     |
| II/I      | D/C — hard Lydian                                    |

**Modal pairings:**
- **Lydian:** II/I (D/C) is *the* sound — raised 4 in upper structure.
- **Dorian:** IV/i (F/Dm) — bright IV is the modal marker; LH holds minor tonic.
- **Phrygian:** ♭II/i (E♭/Dm or F/E) — flat 2 over minor tonic, unmistakable.
- **Mixolydian:** ♭VII/I (F/G) — flat 7 triad over tonic.
- **Aeolian:** ♭VI/i (F/Am) or ♭VII/i (G/Am).

**Practical limits:**
- Don't change polychords faster than ~quarter note at moderate tempo — ear needs time to parse two triads.
- Damping matters more with polychords; ringing previous-stack notes muddy the new one fast.
- Polychords in the bottom octave turn to mud — keep LH triad C2 or higher.
- Don't arpeggiate both triads simultaneously — pick one to roll, hold the other as block.

**Notation:** project-wide convention is `upper~lower` (e.g. `IV~I`, `II~I`). Stripchart chord track renders the upper label on top with a divider, lower in purple beneath. Modal pairings (II/I, ♭VII/I) map directly — the difference is voicing intent, not symbol.

# Meta-principles for pedal-harp writing

1. **Resonance is the instrument.** Write to let strings ring, not to suppress them. Fight this and you're writing piano music on a harp.
2. **Pedal economy.** Plan harmonic motion to minimize pedal changes per bar. One change/beat is busy; two is risky; three needs careful staging.
3. **Hands are independent strata.** LH bass + RH treble with a real gap between. Closed-position chords sound choked.
4. **Open intervals beat closed ones.** 4ths, 5ths, 10ths, 13ths sound bigger and clearer than 3rds and 6ths.
5. **Idiomatic = arpeggios, rolled chords, glissandi, parallel motion.** Block chords are a tool, not the texture.
6. **Damping is composition.** Where you stop sound matters as much as where you start it. Notate étouffé, rests with damping, palm mutes.
7. **Modal > chromatic.** Every accidental beyond the key signature costs a pedal. Modal writing exploits this; chromatic writing fights it.
8. **Register has function.** Bass = drone/anchor; mid = harmony/melody; top = sparkle. Don't ask the bottom octave to carry counterpoint or the top to sustain a line.
9. **Plan from the rest position.** C♭-major is home. Travel outward from home, don't demand all-sharps from bar 1.
10. **Write what the hands can reach without crossing or contorting.** If RH has to leap C3→C6 in a sixteenth, rewrite.

# References

- Salzedo, *Modern Study of the Harp*
- Inglefield & Neill, *Writing for the Pedal Harp*
- `~/Downloads/pedal-harp-rules.md` (user-curated cheatsheet)

**Why:** Reason: harp idiom (sustain, hand reach, pedal mechanics, modal-register sweet spots) materially shapes what voicings work musically. Generic piano-style voicings smear, fight pedal logic, or simply can't be reached. **How to apply:** Apply on every chord placement when composing, reharmonising, or translating from non-harp sources. Reject voicings that violate range / hand-span / sustain / register-strategy rules even if they would sound fine on a piano. For Boddie + Nicene Creed: stay diatonic, ignore pedal-mechanics rules; for future chromatic projects, plan modulations around pedal-change budget.
