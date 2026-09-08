#!/usr/bin/env python3
"""Independently reconstruct the finite Pluecker-plane reduction in Proposition 2.8.

The script generates all candidate relation pairs, canonicalizes rational
rank-two relation planes by primitive Pluecker coordinates, removes planes
containing a forbidden short relation, reduces by signed coordinate
permutations, and finally compares the generated class set with
`data/plane_classes_6866.csv`.
"""
from __future__ import annotations
import csv
from itertools import product, permutations, combinations
from math import gcd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "plane_classes_6866.csv"
EDGES = ((0,1),(0,2),(0,3),(1,2),(1,3),(2,3))
EDGE_INDEX = {e:i for i,e in enumerate(EDGES)}

def primitive(v):
    v = tuple(v)
    g = gcd(*v)
    if not g:
        return v
    if next(x for x in v if x) < 0:
        g = -g
    return tuple(x // g for x in v)

def pluecker(r, s):
    return primitive(r[i] * s[j] - r[j] * s[i] for i, j in EDGES)

def first_types():
    roots = set()
    for r in product(range(-4, 5), repeat=4):
        if not any(r) or sum(abs(x) == 4 for x in r) > 1:
            continue
        if sum(r) % 2 == 0 or gcd(*r) != 1 or sum(x != 0 for x in r) < 2:
            continue
        roots.add(tuple(sorted(abs(x) for x in r)))
    if len(roots) != 23 or (0,1,1,1) not in roots:
        raise ValueError("first-relation type enumeration failed")
    roots.remove((0,1,1,1))
    return sorted(roots)

def normalized_short(m):
    return [s for s in product(range(-m, m + 1), repeat=4)
            if sum(s) % 2 and gcd(*s) == 1 and next(x for x in s if x) > 0]

def forbidden_vectors():
    out = []
    for k in (1,2,3):
        for inds in combinations(range(4), k):
            for sig in product((-1, 1), repeat=k - 1):
                f = [0] * 4
                f[inds[0]] = 1
                for i, a in zip(inds[1:], sig):
                    f[i] = a
                out.append(tuple(f))
    return out
FORBIDDEN = forbidden_vectors()

def contains(p, f):
    def P(a, b):
        if a < b:
            return p[EDGE_INDEX[(a,b)]]
        return -p[EDGE_INDEX[(b,a)]]
    for i, j, k in combinations(range(4), 3):
        if f[i] * P(j,k) - f[j] * P(i,k) + f[k] * P(i,j):
            return False
    return True

def transform(p, perm, sig):
    def P(a, b):
        if a < b:
            return p[EDGE_INDEX[(a,b)]]
        return -p[EDGE_INDEX[(b,a)]]
    return primitive(sig[i] * sig[j] * P(perm[i], perm[j]) for i, j in EDGES)

def generated_classes():
    roots = first_types()
    shorts = {m: normalized_short(m) for m in (4,5,10)}
    planes = set()
    pairs = 0
    for r in roots:
        m = 10 if r == (0,0,1,2) else 5 if r == (1,1,1,2) else 4
        for s in shorts[m]:
            p = pluecker(r, s)
            if not any(p):
                continue
            pairs += 1
            planes.add(p)
    admissible = {p for p in planes if not any(contains(p, f) for f in FORBIDDEN)}
    perms = tuple(permutations(range(4)))
    signs = tuple((1,) + x for x in product((-1,1), repeat=3))
    reps = {min(transform(p, perm, sig) for perm in perms for sig in signs) for p in admissible}
    return shorts, pairs, planes, admissible, reps

def read_certified_classes():
    fields = ("p12","p13","p14","p23","p24","p34")
    rows = []
    with DATA.open(newline="") as f:
        for rec in csv.DictReader(f):
            rows.append(tuple(int(rec[k]) for k in fields))
    return rows

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--write-canonical", default="", help="Write canonical Pluecker tuples to this CSV path.")
    ap.add_argument("--no-compare", action="store_true", help="Generate/count classes without comparing to checked-in plane data.")
    args = ap.parse_args()
    shorts, pairs, planes, admissible, reps = generated_classes()
    got = (pairs, len(planes), len(planes) - len(admissible), len(admissible), len(reps))
    want = (83842, 37612, 538, 37074, 6866)
    if got != want:
        raise SystemExit({"status":"FAIL", "got":got, "expected":want})
    if args.write_canonical:
        path = Path(args.write_canonical)
        with path.open("w", newline="") as f:
            wr = csv.writer(f)
            wr.writerow(("p12","p13","p14","p23","p24","p34"))
            wr.writerows(sorted(reps))
    if not args.no_compare:
        rows = read_certified_classes()
        cert = set(rows)
        if len(rows) != 6866 or len(cert) != 6866:
            raise SystemExit({"status":"FAIL", "certificate_rows":len(rows), "unique":len(cert)})
        missing, extra = reps - cert, cert - reps
        if missing or extra:
            raise SystemExit({"status":"FAIL", "missing":len(missing), "extra":len(extra)})
    print("Proposition 2.8 plane enumeration: PASS")
    print("N4 =", len(shorts[4]))
    print("N5 =", len(shorts[5]))
    print("N10 =", len(shorts[10]))
    print("independent relation pairs =", pairs)
    print("distinct rational relation planes =", len(planes))
    print("forbidden planes =", len(planes) - len(admissible))
    print("admissible planes =", len(admissible))
    print("signed-permutation classes =", len(reps))
    if not args.no_compare:
        print("generated/certified class-set equality = PASS")
        print("missing classes = 0")
        print("extra classes = 0")

if __name__ == "__main__":
    main()
