"""Shared helper: render a batch of (abc, output-path) items to SVG through the
abcjsharp fork (jazz/fork_render.js) -- harp grand-staff stems + middle-C alignment.
Used by the jazz, reharm and retab hymnal builds so they all match.

    from jazz.fork_batch import fork_render
    n_ok, fails = fork_render(outdir, items)   # items: [{abc, out, staffwidth?}, ...]
"""
import json, os, re, subprocess, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
FORK_RENDER = os.path.join(HERE, "fork_render.js")
JSDOM_MODULES = os.path.join(os.path.expanduser("~"), "projects", "hymnal", "node_modules")

def strip_abcm2ps(abc):
    """Drop abcm2ps-only markup abcjs doesn't understand: $N font-switch escapes
    inside annotations (else they print literally as '$1vi$0')."""
    return re.sub(r"\$\d", "", abc)

def fork_render(outdir, items):
    """items: list of {abc, out (path rel to outdir), staffwidth?}. Returns (ok, fails)."""
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as jf:
        json.dump({"outdir": outdir, "items": items}, jf)
        jobpath = jf.name
    env = dict(os.environ, NODE_PATH=JSDOM_MODULES)
    res = subprocess.run(["node", FORK_RENDER, jobpath], capture_output=True, text=True, env=env)
    os.unlink(jobpath)
    if res.returncode != 0:
        raise RuntimeError("fork_render failed:\n" + res.stderr[-2000:])
    rep = json.loads(res.stdout.strip().splitlines()[-1])
    return rep["ok"], rep["fail"]
