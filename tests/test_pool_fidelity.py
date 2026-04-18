"""Fidelity gate: HarpTrefoil.tex must stay byte-exact to HarpChordSystem.tex.

The legacy TeX is the canonical pedagogical source.  The new-name mirror
exists so every downstream script can reference the new brand without
modifying the legacy file.  Any drift is detected here.
"""
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
LEGACY_TEX  = ROOT / 'source' / 'HarpChordSystem.tex'
TREFOIL_TEX = ROOT / 'source' / 'HarpTrefoil.tex'


def test_legacy_tex_exists():
    assert LEGACY_TEX.is_file(), f"missing canonical source: {LEGACY_TEX}"


def test_trefoil_tex_exists():
    assert TREFOIL_TEX.is_file(), f"missing trefoil mirror: {TREFOIL_TEX}"


def test_trefoil_matches_legacy_byte_for_byte():
    """HarpTrefoil.tex is a pure rename mirror.  No content changes allowed.

    If an edit to the pedagogy is needed, it must land in HarpChordSystem.tex
    first (the canonical source), and this mirror is regenerated with `cp`.
    """
    a = LEGACY_TEX.read_bytes()
    b = TREFOIL_TEX.read_bytes()
    assert a == b, (
        "HarpTrefoil.tex has drifted from HarpChordSystem.tex.\n"
        "To update pedagogy: edit HarpChordSystem.tex, then "
        "`cp source/HarpChordSystem.tex source/HarpTrefoil.tex`."
    )
