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

## NOT done (needs you / a device)
- **Tablet install is pending** — the tablet disconnected mid-run (you took it / it slept),
  so `./gradlew installDebug` failed with "No connected devices." **To get it on the tablet:**
  reconnect it, then from `tablet_app/`: `./gradlew installDebug`. Everything is already in the APK source.
- **Quality refinement:** the arranger is a solid, reliable *baseline*. A parallel-agent review
  pass was run (12 sampled hymns) to surface the top improvements; results land in this session's
  workflow output and should be applied to `jazz/arrange.py`, then `python3 jazz/build_jazz_hymnal.py`
  to regenerate, then commit. (Honest note: the Larsen lick is currently a cadential *tag*, not woven
  into internal cadences — that was the safe choice to avoid melody/altered-dominant clashes per hymn.)

## To regenerate after any change
```
cd ~/projects/HarpHymnal
python3 jazz/build_jazz_hymnal.py        # re-arrange + re-render all 279
cd tablet_app && ./gradlew installDebug  # push to a connected tablet
```

## Commits (HarpHymnal main)
- `00a50bc3` Jazz Hymnal baseline (arranger + 279 SVGs + viewer + tile)
- `4bf50457` vary Somerset LH texture per phrase
