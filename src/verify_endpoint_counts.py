#!/usr/bin/env python3
"""Verify the exact endpoint-universe counts used in Lemma 2.9."""
from fractions import Fraction

def count(N):
    E=set([Fraction(0), Fraction(1,2)])
    for v in range(1,N+1):
        j=0
        while True:
            lo=Fraction(4*j+1,4*v); hi=Fraction(4*j+3,4*v)
            if lo>Fraction(1,2):break
            E.add(lo)
            if hi<=Fraction(1,2):E.add(hi)
            j+=1
    return len(E)

def main():
    a,b=count(290),count(445)
    if (a,b)!=(34205,80381):raise SystemExit({"status":"FAIL","E290":a,"E445":b})
    print("Lemma 2.9 endpoint universes: PASS")
    print("|E_290| = 34205")
    print("|E_445| = 80381")
if __name__=='__main__':main()
