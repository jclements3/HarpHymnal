# Jazz Hymnal — status (autonomous run while you were away)

## What exists now
A **third hymn corpus** alongside reharm/retab: a **jazz arrangement of all 279 hymns**
(Somerset-style LH × Larsen altered ii-V-I licks × the hymn melody), built from the same
`data/hymns/*.json`. Committed + pushed to `jclements3/HarpHymnal`.

- **Arranger:** `jazz/arrange.py` — deterministic. RH = the hymn melody; LH = a Somerset
  comp whose texture rotates per phrase (oom-pah / stride / block / arp; 3/4 → waltz);
  cadence = a key-agnostic Larsen altered ii-V-I lick as a tag, transposed into the hymn's key.
- **Lick toolkit:** `jazz/larsen_licks.py` (`render(lick, key)`, `clean_licks()` = the
  3 pedal-safe licks valid in every key), `jazz/larsen_keyagnostic.json` (built from the
  source `hymnal/altered_licks_Eb.abc` via `jazz/build_lib.py`), `jazz/audit.py` (harmonic check).
- **Build:** `jazz/build_jazz_hymnal.py` — renders all 279 to SVG with `abcm2ps -g`
  (matches reharm/retab) → `tablet_app/.../assets/jazz/hymns/*.svg` + `jazz_hymns.js` manifest.
- **Viewer + tile:** standalone `assets/jazz/index.html` (TOC + SVG, Home/Print) and a
  **"Jazz Hymnal"** tile in the hub (`assets/index.html`).

## Verified
- All 279 build, 0 failures (~6 s). Manifest = 279, SVG files = 279, no missing.
- Fork stem test (`hymnal/test_render.js`) passes on samples across major/minor & 4/4·3/4·6/8·2/2.
- APK **assembleDebug succeeds** with the jazz assets.

## Review + fix round (done autonomously)
A 12-agent parallel review (`jazz-hymnal-review` workflow) scored a diverse sample and returned
a "not shippable, fix the tag first" verdict (avg LH 2.3/5, lick integration 2.1/5). All mandatory
findings were then applied to `jazz/arrange.py` and the whole corpus regenerated (commit `ede323ab`):
- Tag resolves to a **real tonic chord** (I-maj7 arpeggio / i-min7), not the lick's bare 5th.
- **V7alt** LH carries the leading tone + altered shell (root-3-b13-b7) — functions as a dominant.
- Tag forced to `[M:4/4]` inline so the 8-eighth lick no longer overflows 3/4 hymns.
- Minor hymns resolve to a real minor `i` (labeled correctly), not a mislabeled major.
- Sharp-side minor keys (Em/Bm/F#m/C#m/G#m, 19 hymns) spell with sharps, not flat enharmonics.
- LH re-articulates every bar — removed the dead held-whole-note textures.

A focused 6-agent re-verify then confirmed the fixes: **4 of 6 worst hymns now "shippable"**
(were 0), tonic resolutions real, minor labeled `i`. It caught one more real bug — in **flat
keys** the lick's natural notes were bare letters the key signature re-flattened (`K:Ab` turned a
bare `B` into B♭), so the V7alt lost its leading tone. Fixed by emitting **explicit accidentals**
on every tag pitch (commit `a6dc220a`); V7alt now functions as a dominant in every key.

**Current state: broadly shippable.** Remaining known items are minor/out-of-scope:
- A few hymns have pre-existing body-meter quirks **in the parsed source data** (`blessed_assurance`
  bar 8 overflow; `o_that_the_lord` declares 3/2 but bars hold 3/4) — not the arranger; they play
  coherently and also affect reharm/retab. A separate `data/hymns/*.json` cleanup pass would fix them.
- Minor hymns use a Dorian `ii7` (not `iiø7`) into the altered V — a deliberate jazz choice.
- The lick is a cadential **coda tag**, not yet woven into the hymn's own final cadence (deferred).

## NOT done (needs you / a device)
- **Tablet install is pending** — the tablet disconnected mid-run, so `./gradlew installDebug`
  failed with "No connected devices." Reconnect it, then from `tablet_app/`: `./gradlew installDebug`.
  Everything is already baked into the APK source.
- **Optional further polish:** the Larsen lick is a cadential **coda tag**, not yet woven into the
  hymn's own final cadence (review improvement #5) — deferred as it needs per-hymn cadence detection.

## To regenerate after any change
```
cd ~/projects/HarpHymnal
python3 jazz/build_jazz_hymnal.py        # re-arrange + re-render all 279
cd tablet_app && ./gradlew installDebug  # push to a connected tablet
```

## Commits (HarpHymnal main)
- `00a50bc3` Jazz Hymnal baseline (arranger + 279 SVGs + viewer + tile)
- `4bf50457` vary Somerset LH texture per phrase
- `d20a0a36` this status doc
- `ede323ab` fix round from the 12-agent review (tag resolution, V7alt dominant, 3/4 meter, minor, spelling)
- `a6dc220a` explicit accidentals so flat keys keep the V7alt leading tone (caught by re-verify)
