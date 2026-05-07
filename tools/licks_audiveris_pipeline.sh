#!/usr/bin/env bash
# End-to-end pipeline: 101_licks_Dmi.pdf -> Audiveris MusicXML -> per-lick ABC.
#
# Inputs:
#   $1 = path to 101_licks_Dmi.pdf  (default: ./101_licks_Dmi.pdf)
#   $2 = output ABC dir            (default: ./tablet_app/app/src/main/assets/licks/abc_audiveris)
#
# Side effects:
#   /tmp/licks_jpg/      - extracted JPEG strips (one per lick)
#   /tmp/audiveris-out/  - Audiveris MusicXML + .omr book files
#
# Requires: flatpak install of org.audiveris.audiveris, music21 (pip).
set -euo pipefail

PDF="${1:-$(pwd)/101_licks_Dmi.pdf}"
OUT="${2:-$(pwd)/tablet_app/app/src/main/assets/licks/abc_audiveris}"
META_DIR="$(pwd)/tablet_app/app/src/main/assets/licks"
JPG_DIR=/tmp/licks_jpg
MXL_DIR=/tmp/audiveris-out

mkdir -p "$JPG_DIR" "$MXL_DIR" "$OUT"

echo "[1/3] extracting JPEGs from $PDF"
rm -f "$JPG_DIR"/lick-*.jpg
pdfimages -j "$PDF" "$JPG_DIR/lick"
N=$(ls "$JPG_DIR"/lick-*.jpg | wc -l)
echo "      got $N strips"

echo "[2/3] running Audiveris on all strips"
flatpak run --filesystem=host org.audiveris.audiveris \
    -batch -export -output "$MXL_DIR" "$JPG_DIR"/lick-*.jpg \
    2>&1 | tail -20

echo "[3/3] converting MusicXML -> ABC"
i=0
for jpg in "$JPG_DIR"/lick-*.jpg; do
    base=$(basename "$jpg" .jpg)
    mxl="$MXL_DIR/${base}.mxl"
    n=$(printf '%03d' $((i + 1)))
    out_abc="$OUT/lick_${n}.abc"
    meta="$META_DIR/lick_${n}.json"

    if [ ! -f "$mxl" ]; then
        echo "  SKIP lick_${n}: no MusicXML"
        i=$((i + 1))
        continue
    fi

    level="?"
    if [ -f "$meta" ]; then
        level=$(python3 -c "import json,sys; print(json.load(open('$meta'))['level_word'])" 2>/dev/null || echo "?")
    fi

    python3 tools/audiveris_to_abc.py "$mxl" "$out_abc" \
        --lick "$((i + 1))" --level "$level" 2>/dev/null \
        || echo "  FAIL lick_${n}"
    i=$((i + 1))
done

echo "wrote $(ls "$OUT"/lick_*.abc | wc -l) ABC files to $OUT"
