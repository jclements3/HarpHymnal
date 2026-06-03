"""Harmonic accuracy audit of the key-agnostic Larsen licks (key-independent)."""
import json, os
LIB = json.load(open(os.path.join(os.path.dirname(__file__), "larsen_keyagnostic.json")))
II = {0,2,4,5,7,9,11}                 # F dorian (= Eb major): ii7 + Imaj7 cells
V  = {1,2,3,5,7,8,10,11}              # Bb7 chord tones + altered tensions
CHTONE = {0,4,7,11}                   # Ebmaj7 chord tones (resolution targets)
NAME = ['Eb','E','F','Gb','G','Ab','A','Bb','B','C','Db','D']
AVOID = {'V7alt': {0:'11/sus',4:'nat-13',6:'?',9:'nat-9'},
         'ii7':   {1:'b9',3:'#9',6:'b5',8:'b6',10:'b3'}}
def run():
    for L in LIB:
        bad, alt = [], False
        for c in L['cells']:
            al = V if c['func'] == 'V7alt' else II
            for semi, _ in c['notes']:
                pc = semi % 12
                if c['func'] == 'V7alt' and pc in {8,10,1,3}: alt = True
                if pc not in al and c['func'] != 'Imaj7':
                    tag = AVOID.get(c['func'], {}).get(pc, '')
                    bad.append("%s:%s%s" % (c['func'], NAME[pc], '('+tag+')' if tag else ''))
        land = L['cells'][2]['notes'][-1][0] % 12
        fl = []
        if bad: fl.append("outside-scale " + ", ".join(sorted(set(bad))))
        if not alt: fl.append("no altered tension in V")
        if land not in CHTONE: fl.append("lands on %s (color)" % NAME[land])
        print("  #%-2d %-8s %-30s %s" % (L['id'], "OK" if not fl else "REVIEW", L['name'][:30], "; ".join(fl)))
if __name__ == "__main__":
    run()
