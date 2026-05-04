#!/bin/bash
# Bootstrap EasyABC + vi mode on a fresh box.
#
# Clones jwdj/EasyABC into TARGET (default ~/projects/HarpHymnal/tmp/EasyABC),
# drops in our vi modules, patches easy_abc.py, and installs a shim at
# ~/.local/bin/easyabc that launches the patched copy.
#
# Re-runnable. The patch step is idempotent.
#
# Requirements:
#   - python3 with wxPython 4.x  (sudo apt install python3-wxgtk4.0)
#   - git
#   - ~/.local/bin on PATH

set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
TARGET="${1:-$HOME/projects/HarpHymnal/tmp/EasyABC}"
SHIM="$HOME/.local/bin/easyabc"

echo "==> EasyABC + vi mode install"
echo "    source : $HERE"
echo "    target : $TARGET"
echo "    shim   : $SHIM"

if [ ! -d "$TARGET/.git" ]; then
    echo "==> Cloning jwdj/EasyABC into $TARGET"
    mkdir -p "$(dirname "$TARGET")"
    git clone --depth 1 https://github.com/jwdj/EasyABC.git "$TARGET"
else
    echo "==> Existing EasyABC clone found at $TARGET (skipping clone)"
fi

echo "==> Copying vi modules"
cp "$HERE"/vi_motions.py    "$TARGET"/
cp "$HERE"/vi_operators.py  "$TARGET"/
cp "$HERE"/vi_search.py     "$TARGET"/
cp "$HERE"/vi_mode.py       "$TARGET"/
cp "$HERE"/aui_compat.py    "$TARGET"/
cp "$HERE"/test_vi.py       "$TARGET"/

echo "==> Patching $TARGET/easy_abc.py"
python3 "$HERE"/patch.py "$TARGET"/easy_abc.py

echo "==> Installing shim at $SHIM"
mkdir -p "$(dirname "$SHIM")"
cat > "$SHIM" <<EOF
#!/bin/bash
exec /usr/bin/python3 $TARGET/easy_abc.py "\$@"
EOF
chmod +x "$SHIM"

echo
echo "==> Done."
echo "    Run: easyabc            # press F12 in editor pane to toggle vi off"
echo "    Test: python3 $TARGET/test_vi.py"
