"""PROTOTYPE jazz-hymnal arranger: hymn melody (RH) + Somerset-style LH comp,
with a key-agnostic Larsen altered ii-V-I lick as the cadential tag.
Major keys only for this prototype.  Emits grand-staff ABC."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from jazz.larsen_licks import LICKS, clean_licks, render as render_lick

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
    """Somerset LH comp for one bar in a chosen texture (all pedal-diatonic, safe durs)."""
    d=numeral_degree(numeral); r,f,t,r2=_tones(key_root,d)
    root="[%s]"%r; block="[%s%s]"%(f,t); full="[%s%s%s]"%(r,f,t)
    even = (B>=4 and B%2==0)
    if texture=="block":                 # held 1-5-10 block
        return safe_dur(full, B)
    if texture=="oompah" and even:       # bass | chord  x2
        q=B//2; return "%s %s %s %s"%(safe_dur(root,1),safe_dur(block,q-1),safe_dur(root,1),safe_dur(block,q-1))
    if texture=="stride" and B>=8 and B%4==0:   # bass chord bass chord (quarters)
        u=B//4; return " ".join([safe_dur(root,u),safe_dur(block,u)]*2)
    if texture=="arp" and even:          # 1-5-10-8 arpeggio across the bar
        u=B//4 if B%4==0 else B//2
        return " ".join(safe_dur("[%s]"%x,u) for x in [r,f,t,r2][:B//u])
    if texture=="waltz" and B==6:        # oom-pah-pah (3/4)
        return "%s %s %s"%(safe_dur(root,2),safe_dur(block,2),safe_dur(block,2))
    # fallback: held block
    return safe_dur(full, B)

def arrange(hymn_path):
    h=json.load(open(hymn_path)); key=h["key"]["root"]; minor=(h["key"].get("mode")=="minor"); bars=h["bars"]
    mt=h.get("meter") or {}
    meter=("%d/%d"%(mt.get("beats",4),mt.get("unit",4))) if isinstance(mt,dict) else str(mt or "4/4")
    ksig=key+("m" if minor else "")
    mult=2                                          # eighths
    out=["X:1","T:%s  -  jazz (Somerset LH x Larsen licks)"%h["title"],
         "C:trad., jazz arr. pedal harp","M:"+meter,"L:1/8","Q:1/4=92",
         "%%scale 0.62","%%nowrap true","%%score {1 | 2}","V:1 clef=treble name=\"RH\"","V:2 clef=bass name=\"LH\"","K:"+ksig]
    # map each bar to its phrase so the LH texture changes phrase-to-phrase
    bar2phr={}
    for pi,p in enumerate(h.get("phrases") or []):
        for ib in (p.get("ibars") or []): bar2phr[ib-1]=pi
    TEX=["oompah","stride","block","arp"]
    is34=(mt.get("beats")==3)
    rh=[]; lh=[]
    for bi,b in enumerate(bars):
        be=sum(max(1,round(e["duration"]*mult)) for e in b["melody"])
        rh.append(" ".join(mel_tok(e,mult) for e in b["melody"]))
        tex="waltz" if is34 else TEX[bar2phr.get(bi,bi//4)%len(TEX)]
        lh.append(som_lh(key, (b["chord"] or {}).get("numeral","I"), be, tex))
    # group ~4 bars per system
    for i in range(0,len(bars),4):
        rg=rh[i:i+4]; lg=lh[i:i+4]
        out.append("[V:1] "+" | ".join(rg)+" |")
        out.append("[V:2] "+" | ".join(lg)+" |")
    # --- Larsen cadential tag: a pedal-clean lick as a ii-V-I turnaround coda ---
    lick=clean_licks()[0]                            # Lick 1, transposed to this key
    tag_rh=render_lick(lick, ksig)
    out.append("%% --- Larsen ii-V-I tag ---")
    out.append('[V:1] '+tag_rh+' |]')
    # tag LH: ii root, rootless altered shell, I block
    d2=deg_to_abc(key,1,2); d5=deg_to_abc(key,4,2); d1=deg_to_abc(key,0,2)
    out.append('[V:2] [%s]8 | [%s]8 | [%s]8 |]'%(d2,d5,d1))
    return "\n".join(out)+"\n"

if __name__=="__main__":
    h=sys.argv[1] if len(sys.argv)>1 else "data/hymns/praise_god_from_whom_all_blessings_flow.json"
    abc=arrange(h)
    open("/tmp/jazz_arr.abc","w").write(abc)
    print(abc[:600])
