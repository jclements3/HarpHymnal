"""Flask dev server for the SATB → pedal-harp arranger.

Run with::

    python3 -m tools.satb_to_harp.server

Endpoints:
    GET  /                – static/index.html
    GET  /static/<path>   – static asset (Flask default)
    GET  /api/hymns       – { titles: [...] }   (from source/OpenHymnal.abc)
    POST /api/arrange     – { title } → { abc, audits, beats }
    POST /api/midi        – { abc }   → audio/midi bytes (via abc2midi)

The analyzer/consolidator imports are deferred until the request hits so the
server still starts when those modules aren't ready yet. v1 = dev only.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import traceback
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory


REPO_ROOT = Path(__file__).resolve().parents[2]
PKG_DIR = Path(__file__).resolve().parent
STATIC_DIR = PKG_DIR / "static"
HYMNAL_ABC = REPO_ROOT / "source" / "OpenHymnal.abc"
ABC2MIDI = "/usr/bin/abc2midi"
FLUIDSYNTH = "/usr/bin/fluidsynth"
SOUNDFONT = "/usr/share/sounds/sf2/FluidR3_GM.sf2"

# Make sure the repo root is on sys.path so `parsers.abc` and
# `tools.satb_to_harp.*` resolve regardless of how the server was launched.
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


app = Flask(
    __name__,
    static_folder=str(STATIC_DIR),
    static_url_path="/static",
)


# ─────────────────────────────────────────────────────────────────────────────
#   Hymn title cache
# ─────────────────────────────────────────────────────────────────────────────
_TITLE_CACHE: list[str] | None = None


def _load_titles() -> list[str]:
    global _TITLE_CACHE
    if _TITLE_CACHE is not None:
        return _TITLE_CACHE
    try:
        from parsers.abc import iter_tunes
    except Exception as e:
        print(f"[server] parsers.abc import failed: {e}", file=sys.stderr)
        _TITLE_CACHE = []
        return _TITLE_CACHE
    if not HYMNAL_ABC.exists():
        print(f"[server] missing hymnal source: {HYMNAL_ABC}", file=sys.stderr)
        _TITLE_CACHE = []
        return _TITLE_CACHE
    text = HYMNAL_ABC.read_text(encoding="utf-8", errors="replace")
    titles = sorted({t for t, _ in iter_tunes(text)})
    _TITLE_CACHE = titles
    return _TITLE_CACHE


# Fallback ABC used when analyzer/consolidator aren't importable yet — so the
# browser can still render and play SOMETHING and we can verify the UI.
_FALLBACK_ABC = """X:1
T:Fallback C-major progression
M:4/4
L:1/4
Q:1/4=90
K:C
V:RH clef=treble
[CEG]4 | [FAc]4 | [GBd]4 | [CEG]4 |]
V:LH clef=bass
C,4 | F,4 | G,4 | C,4 |]
"""


# ─────────────────────────────────────────────────────────────────────────────
#   Routes
# ─────────────────────────────────────────────────────────────────────────────
@app.route("/")
def root():
    return send_from_directory(str(STATIC_DIR), "index.html")


@app.route("/api/hymns", methods=["GET"])
def hymns():
    try:
        titles = _load_titles()
        hymns_out = [
            {"n": i + 1, "label": f"{i+1:03d} {t}", "title": t}
            for i, t in enumerate(titles)
        ]
        return jsonify({"hymns": hymns_out})
    except Exception as e:
        return (
            jsonify({"error": str(e), "traceback": traceback.format_exc()}),
            500,
        )


@app.route("/api/patterns", methods=["GET"])
def patterns():
    try:
        from tools.satb_to_harp.somerset import AVAILABLE
        return jsonify({"patterns": AVAILABLE})
    except Exception as e:
        return jsonify({"error": str(e), "patterns": []}), 500


@app.route("/api/arrange", methods=["POST"])
def arrange():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    pattern = (data.get("pattern") or "").strip() or None
    if not title:
        return jsonify({"error": "missing 'title' in JSON body"}), 400

    try:
        try:
            from tools.satb_to_harp.analyzer import analyze
            from tools.satb_to_harp.consolidator import consolidate
        except ImportError as e:
            # Analyzer/consolidator not ready yet — return a usable fallback so
            # the UI can be exercised end-to-end.
            return (
                jsonify({
                    "title": title,
                    "abc": _FALLBACK_ABC,
                    "audits": [{
                        "beat": 0,
                        "severity": "info",
                        "message": (
                            f"analyzer/consolidator not yet importable "
                            f"({e}); serving fallback ABC."
                        ),
                    }],
                    "beats": 0,
                    "fallback": True,
                }),
                503,
            )

        ledger = analyze(title)
        result = consolidate(ledger, pattern=pattern)
        return jsonify({
            "title": title,
            "pattern": pattern,
            "abc": result.abc,
            "audits": [
                {"beat": a.beat, "message": a.message, "severity": a.severity}
                for a in result.audits
            ],
            "beats": len(ledger.beats),
        })
    except Exception as e:
        return (
            jsonify({"error": str(e), "traceback": traceback.format_exc()}),
            500,
        )


@app.route("/api/midi", methods=["POST"])
def midi():
    data = request.get_json(silent=True) or {}
    abc_text = data.get("abc") or ""
    if not abc_text.strip():
        return jsonify({"error": "missing 'abc' in JSON body"}), 400

    with tempfile.TemporaryDirectory() as td:
        in_path = Path(td) / "tune.abc"
        out_path = Path(td) / "tune.mid"
        in_path.write_text(abc_text, encoding="utf-8")
        try:
            proc = subprocess.run(
                [ABC2MIDI, str(in_path), "-NFER", "-o", str(out_path)],
                capture_output=True,
                text=True,
                timeout=20,
            )
        except FileNotFoundError:
            return jsonify({"error": f"abc2midi not found at {ABC2MIDI}"}), 500
        except subprocess.TimeoutExpired:
            return jsonify({"error": "abc2midi timed out"}), 500

        if not out_path.exists() or out_path.stat().st_size == 0:
            return (
                jsonify({
                    "error": "abc2midi produced no output",
                    "stdout": proc.stdout,
                    "stderr": proc.stderr,
                    "returncode": proc.returncode,
                }),
                500,
            )

        midi_bytes = out_path.read_bytes()

    return (
        midi_bytes,
        200,
        {
            "Content-Type": "audio/midi",
            "Content-Disposition": "inline; filename=tune.mid",
        },
    )


@app.route("/api/audio", methods=["POST"])
def audio():
    """ABC → MIDI (abc2midi) → WAV (fluidsynth). Browsers play WAV natively."""
    data = request.get_json(silent=True) or {}
    abc_text = data.get("abc") or ""
    if not abc_text.strip():
        return jsonify({"error": "missing 'abc' in JSON body"}), 400

    with tempfile.TemporaryDirectory() as td:
        in_path = Path(td) / "tune.abc"
        mid_path = Path(td) / "tune.mid"
        wav_path = Path(td) / "tune.wav"
        in_path.write_text(abc_text, encoding="utf-8")

        try:
            proc = subprocess.run(
                [ABC2MIDI, str(in_path), "-NFER", "-o", str(mid_path)],
                capture_output=True, text=True, timeout=20,
            )
        except FileNotFoundError:
            return jsonify({"error": f"abc2midi not found at {ABC2MIDI}"}), 500
        except subprocess.TimeoutExpired:
            return jsonify({"error": "abc2midi timed out"}), 500
        if not mid_path.exists() or mid_path.stat().st_size == 0:
            return jsonify({
                "error": "abc2midi produced no output",
                "stderr": proc.stderr,
            }), 500

        try:
            fs_proc = subprocess.run(
                [FLUIDSYNTH, "-ni", "-F", str(wav_path), SOUNDFONT, str(mid_path)],
                capture_output=True, text=True, timeout=60,
            )
        except FileNotFoundError:
            return jsonify({"error": f"fluidsynth not found at {FLUIDSYNTH}"}), 500
        except subprocess.TimeoutExpired:
            return jsonify({"error": "fluidsynth timed out"}), 500
        if not wav_path.exists() or wav_path.stat().st_size == 0:
            return jsonify({
                "error": "fluidsynth produced no output",
                "stderr": fs_proc.stderr,
            }), 500

        wav_bytes = wav_path.read_bytes()

    return (
        wav_bytes,
        200,
        {
            "Content-Type": "audio/wav",
            "Content-Disposition": "inline; filename=tune.wav",
        },
    )


# ─────────────────────────────────────────────────────────────────────────────
#   Entry
# ─────────────────────────────────────────────────────────────────────────────
def main() -> None:
    port = int(os.environ.get("FLASK_RUN_PORT", "5173"))
    print(f"[server] HarpHymnal SATB→Harp dev server: http://localhost:{port}/")
    print(f"[server] hymnal source: {HYMNAL_ABC}")
    print(f"[server] static dir:    {STATIC_DIR}")
    # Pre-warm the title cache so the first /api/hymns is fast (best-effort).
    try:
        n = len(_load_titles())
        print(f"[server] cached {n} hymn titles")
    except Exception as e:
        print(f"[server] title cache failed: {e}", file=sys.stderr)
    # debug=True enables auto-reload on Python file changes so the browser
    # refresh is all the user needs after edits.
    app.run(host="127.0.0.1", port=port, debug=True, use_reloader=True)


if __name__ == "__main__":
    main()
