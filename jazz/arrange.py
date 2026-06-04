"""PROTOTYPE jazz-hymnal arranger: hymn melody (RH) + Somerset-style LH comp,
with a key-agnostic Larsen altered ii-V-I lick as the cadential tag.
Major keys only for this prototype.  Emits grand-staff ABC."""
import json, os, sys, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

KERN = 165   # target per-bar width in abc units; staffwidth = BPL*KERN sets the
             # note "kerning" (density). Larger = more air between notes.
def pick_bpl(n):
    """Bars per system: ~aspect-match a landscape screen so fit-to-screen fills it."""
    return max(4, round(1.55 * math.sqrt(max(1, n))))
from jazz.larsen_licks import (LICKS, clean_licks, render as render_lick,
                               spell_flat, keysig_acc, spell_chord, spell_note, beam)

LETTERS = "CDEFGAB"
ACC = {"♯":"^","♭":"_","sharp":"^","flat":"_","natural":"=", None:""}
MAJ_STEPS = [0,2,4,5,7,9,11]                      # semitone of each scale degree
NUM = {"I":0,"II":1,"III":2,"IV":3,"V":4,"VI":5,"VII":6}
_SAFE = {1,2,3,4,6,8,12,16,24,32}                # ABC durations abcm2ps accepts (no >2 dots)

def safe_dur(tok, n):
    """Render token at duration n eighths, splitting unsafe values into tied
    (notes/chords) or space-separated (rests) legal pieces."""
    if n <= 0: return ""
    if n in _SAFE: return tok if n == 1 else tok + str(n)
    join = " " if tok.startswith("z") else "-"
    for c in sorted(_SAFE, reverse=True):
        if c < n:
            head = tok if c == 1 else tok + str(c)
            return head + join + safe_dur(tok, n - c)
    return tok + str(n)

def deg_to_abc(key_root, degree, octave):
    ti = LETTERS.index(key_root[0])
    letter = LETTERS[(ti+degree)%7]; oa=(ti+degree)//7; o=octave+oa
    return (letter.lower()+"'"*(o-5)) if o>=5 else (letter.upper()+","*(4-o))

def mel_tok(ev, mult):
    d = max(1, round(ev["duration"]*mult))
    if ev["kind"]!="note": return safe_dur("z", d)
    p=ev["pitch"]; letter=p["letter"]; o=p["octave"]
    pre=ACC.get(p.get("accidental"),"")
    s=(letter.lower()+"'"*(o-5)) if o>=5 else (letter.upper()+","*(4-o))
    return safe_dur(pre+s, d)

def numeral_degree(numeral):
    import re
    m=re.match(r'([b#]?)([IViv]+)', numeral or "I")
    return NUM.get((m.group(2) if m else "I").upper(),0)

def _tones(key_root, d):
    return (deg_to_abc(key_root,d,2),    # root (octave 2)
            deg_to_abc(key_root,d+4,2),  # 5th
            deg_to_abc(key_root,d+2,3),  # 10th (3rd up an octave)
            deg_to_abc(key_root,d,3))    # root up an octave

def som_lh(key_root, numeral, B, texture):
    """Somerset LH comp for one bar in a chosen texture (all pedal-diatonic, safe durs).
    Every texture re-articulates within the bar -- no dead held whole-notes, which
    decay to silence on a harp and violate the repo's 'sustain -> vary every chord' rule."""
    d=numeral_degree(numeral); r,f,t,r2=_tones(key_root,d)
    root="[%s]"%r; block="[%s%s]"%(f,t); full="[%s%s%s]"%(r,f,t)
    even = (B>=4 and B%2==0)
    if texture=="oompah" and even:       # bass | chord  x2
        q=B//2; return "%s %s %s %s"%(safe_dur(root,1),safe_dur(block,q-1),safe_dur(root,1),safe_dur(block,q-1))
    if texture=="stride" and B>=8 and B%4==0:   # bass chord bass chord (quarters)
        u=B//4; return " ".join([safe_dur(root,u),safe_dur(block,u)]*2)
    if texture=="arp" and even:          # 1-5-10-8 arpeggio across the bar
        u=B//4 if B%4==0 else B//2
        return " ".join(safe_dur("[%s]"%x,u) for x in [r,f,t,r2][:B//u])
    if texture=="waltz" and B==6:        # oom-pah-pah (3/4)
        return "%s %s %s"%(safe_dur(root,2),safe_dur(block,2),safe_dur(block,2))
    if texture=="block" and even:        # 1-5-10 re-articulated on each half (not a dead whole-note)
        h=B//2; return "%s %s"%(safe_dur(full,h),safe_dur(full,B-h))
    # fallback: bass then chord, re-articulated -- never a held whole-note
    if B>=2:
        h=B//2; return "%s %s"%(safe_dur(root,h),safe_dur(block,B-h))
    return safe_dur(full, B)

def arrange(hymn_path, bpl=None):
    h=json.load(open(hymn_path)); key=h["key"]["root"]; minor=(h["key"].get("mode")=="minor"); bars=h["bars"]
    mt=h.get("meter") or {}
    meter=("%d/%d"%(mt.get("beats",4),mt.get("unit",4))) if isinstance(mt,dict) else str(mt or "4/4")
    ksig=key+("m" if minor else "")
    mult=2                                          # eighths
    out=["X:1","T:%s  -  jazz (Somerset LH x Larsen licks)"%h["title"],
         "C:trad., jazz arr. pedal harp","M:"+meter,"L:1/8","Q:1/4=92",
         "%%scale 0.62","%%score {1 | 2}","V:1 clef=treble name=\"RH\"","V:2 clef=bass name=\"LH\"","K:"+ksig]
    # map each bar to its phrase so the LH texture changes phrase-to-phrase
    bar2phr={}
    for pi,p in enumerate(h.get("phrases") or []):
        for ib in (p.get("ibars") or []): bar2phr[ib-1]=pi
    TEX=["oompah","stride","block","arp"]
    is34=(mt.get("beats")==3)
    # beat length in eighths -> beam eighth notes by beat (compound 6/8 etc. by 3)
    unit=mt.get("unit",4) if isinstance(mt,dict) else 4
    nbeats=mt.get("beats",4) if isinstance(mt,dict) else 4
    mbeat=3 if (unit==8 and nbeats%3==0) else (4 if unit==2 else 2)
    rh=[]; lh=[]
    for bi,b in enumerate(bars):
        be=sum(max(1,round(e["duration"]*mult)) for e in b["melody"])
        rh.append(beam([(mel_tok(e,mult), max(1,round(e["duration"]*mult)), e.get("kind")=="note")
                        for e in b["melody"]], mbeat))
        tex="waltz" if is34 else TEX[bar2phr.get(bi,bi//4)%len(TEX)]
        lh.append(som_lh(key, (b["chord"] or {}).get("numeral","I"), be, tex))
    # Group bars per system in the SOURCE (one source line = one rendered system).
    # The renderer uses NO wrap option, so abcjs keeps its natural sqrt(duration)
    # note spacing instead of justify-stretching each row -- that stretch is what
    # spreads notes apart. Bars/line is chosen so the whole block's aspect ratio
    # ~matches a landscape tablet (BPL ~ 1.3*sqrt(bars)); fit-to-screen then scales
    # it up to fill BOTH dimensions, maximizing note size on one screen.
    BPL = bpl or pick_bpl(len(bars))
    L = max(1, math.ceil(len(bars) / BPL))               # number of systems
    base, extra = divmod(len(bars), L)                   # spread bars EVENLY across them
    idx = 0
    for li in range(L):
        n = base + (1 if li < extra else 0)
        out.append("[V:1] " + " | ".join(rh[idx:idx+n]) + " |")
        out.append("[V:2] " + " | ".join(lh[idx:idx+n]) + " |")
        idx += n
    # --- Larsen cadential tag: ii7 - V7alt - I, voiced as a real turnaround coda ---
    # RH keeps the Larsen altered ii7/V7alt line, but the resolution is a true tonic
    # arpeggio (I-maj7 / i-min7), NOT the lick's bare 5th.  The LH gives each chord a
    # real voicing: ii7 shell, an altered-dominant shell carrying the leading tone, and
    # a full tonic chord.  Forced to 4/4 so the 8-eighth lick never overflows a 3/4 bar.
    lick=clean_licks()[0]
    cells=render_lick(lick, ksig).split(" | ")       # '"ii7" ..' / '"V7alt" ..' / '"Imaj7" ..'
    ii_rh, v_rh = cells[0], cells[1]
    tonic=[0,3,7,10] if minor else [0,4,7,11]        # i-min7 / I-maj7
    lab='"i"' if minor else '"Imaj7"'
    flat=spell_flat(ksig); ks=keysig_acc(ksig)
    # Each tag bar carries its own accidental state, so within a bar the repeated chord
    # inherits the first statement's accidentals (no redundant re-spelling).
    sr={}; res_rh=lab+" "+" ".join(spell_note(ksig,s,4,sr,ks,flat)+"2" for s in tonic)  # tonic arpeggio
    s1={}; ii_a=spell_chord(ksig,[2,5,9,12],2,s1,ks,flat);  ii_b=spell_chord(ksig,[2,5,9,12],2,s1,ks,flat)
    s2={}; v_a =spell_chord(ksig,[7,11,15,17],2,s2,ks,flat); v_b=spell_chord(ksig,[7,11,15,17],2,s2,ks,flat)
    s3={}; i_a =spell_chord(ksig,tonic,2,s3,ks,flat)        # full tonic chord under the arrival
    # Larsen ii-V-I coda. The lick cells are 8 eighths each; we DON'T emit an inline
    # [M:4/4] meter change because the abcjsharp renderer breaks the grand-staff brace
    # across it. abcjs renders the (technically overfull, in <4/4 hymns) tag bars fine
    # since the barlines are explicit -- they read as a free cadenza-style coda.
    out.append("%% --- Larsen ii-V-I tag (coda) ---")
    out.append('[V:1] %s | %s | %s |]'%(ii_rh, v_rh, res_rh))
    out.append('[V:2] %s4 %s4 | %s4 %s4 | %s8 |]'%(ii_a,ii_b,v_a,v_b,i_a))
    return "\n".join(out)+"\n"

if __name__=="__main__":
    h=sys.argv[1] if len(sys.argv)>1 else "data/hymns/praise_god_from_whom_all_blessings_flow.json"
    abc=arrange(h)
    open("/tmp/jazz_arr.abc","w").write(abc)
    print(abc[:600])
