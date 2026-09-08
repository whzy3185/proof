#!/usr/bin/env python3
"""Standalone exact verifier for Proposition 2.8 plane certificates.

This program does not enumerate relation pairs and does not search for safe
points.  It joins `plane_classes_6866.csv` and `plane_safe_points.csv` by their
primitive Pluecker tuple and verifies the published certificate conditions.
"""
from __future__ import annotations
import csv
from fractions import Fraction
from itertools import combinations
from math import gcd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLASSES = ROOT / "data" / "plane_classes_6866.csv"
SAFE = ROOT / "data" / "plane_safe_points.csv"
EDGES = tuple(combinations(range(4), 2))
PFIELDS = ("p12","p13","p14","p23","p24","p34")

def primitive(v):
    v = tuple(v); g = gcd(*v)
    if not g: return v
    if next(x for x in v if x) < 0: g = -g
    return tuple(x // g for x in v)

def row_space(a, b):
    a, b = tuple(a), tuple(b)
    p = next((i for i in range(4) if a[i] or b[i]), None)
    if p is None: return None
    if not a[p]: a, b = b, a
    bb = primitive(a[p] * b[i] - b[p] * a[i] for i in range(4))
    if not any(bb): return None
    q = next(i for i in range(4) if bb[i])
    aa = primitive(bb[q] * a[i] - a[q] * bb[i] for i in range(4))
    return aa, bb

def nullspace_rows(u, w):
    a, b = row_space(u, w)
    p = next(i for i in range(4) if a[i])
    q = next(i for i in range(4) if b[i])
    basis = []
    for j in range(4):
        if j in (p, q): continue
        z = [0] * 4
        z[j] = a[p] * b[q]
        z[p] = -a[j] * b[q]
        z[q] = -b[j] * a[p]
        basis.append(primitive(z))
    return row_space(*basis)

def exterior(rows):
    a, b = rows
    return primitive(a[i] * b[j] - a[j] * b[i] for i, j in EDGES)

def ceil_minus_one(x: Fraction) -> int:
    return (x.numerator - 1) // x.denominator

def read_rows(path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))

def key(rec):
    return tuple(int(rec[k]) for k in PFIELDS)

def main():
    class_rows = read_rows(CLASSES)
    safe_rows = read_rows(SAFE)
    classes = {key(r): r for r in class_rows}
    safe = {key(r): r for r in safe_rows}
    if len(class_rows) != 6866 or len(classes) != 6866 or len(safe_rows) != 6866 or len(safe) != 6866:
        raise SystemExit("expected 6866 unique class and safe-point rows")
    if set(classes) != set(safe):
        raise SystemExit({"status":"FAIL", "missing_safe":len(set(classes)-set(safe)), "extra_safe":len(set(safe)-set(classes))})
    maxspeed = 0
    mingap = Fraction(1, 1)
    maxden = 0
    for n, pvec in enumerate(sorted(classes), 1):
        c, s = classes[pvec], safe[pvec]
        if primitive(pvec) != pvec:
            raise ValueError(f"row {n}: nonprimitive Pluecker tuple")
        if pvec[0]*pvec[5] - pvec[1]*pvec[4] + pvec[2]*pvec[3] != 0:
            raise ValueError(f"row {n}: nondecomposable Pluecker tuple")
        u = tuple(int(c[f"u{i}"]) for i in range(1,5))
        w = tuple(int(c[f"w{i}"]) for i in range(1,5))
        minors = [u[i]*w[j] - u[j]*w[i] for i,j in EDGES]
        if gcd(*minors) != 1:
            raise ValueError(f"row {n}: unsaturated basis")
        if exterior(nullspace_rows(u, w)) != pvec:
            raise ValueError(f"row {n}: basis/plane mismatch")
        xn, yn, q = int(s["x_num"]), int(s["y_num"]), int(s["den"])
        if not (1 <= q <= 17 and 0 <= xn < q and 0 <= yn < q):
            raise ValueError(f"row {n}: parameter range")
        gaps = []
        for i in range(4):
            phase = (u[i]*xn + w[i]*yn) % q
            gap = Fraction(min(phase, q-phase), q) - Fraction(1,4)
            stored = Fraction(int(s[f"delta{i+1}_num"]), int(s[f"delta{i+1}_den"]))
            if gap != stored or gap < Fraction(1,28):
                raise ValueError(f"row {n}: safety margin")
            gaps.append(gap)
        alpha = max(Fraction(abs(w[i]),2)/gaps[i] for i in range(4))
        beta  = max(Fraction(abs(u[i]),2)/gaps[i] for i in range(4))
        A, B = ceil_minus_one(alpha), ceil_minus_one(beta)
        if (A, B) != (int(s["A_bound"]), int(s["B_bound"])):
            raise ValueError(f"row {n}: parameter bound mismatch")
        speed = max(A*abs(u[i]) + B*abs(w[i]) for i in range(4))
        if speed > 290:
            raise ValueError(f"row {n}: speed bound {speed}")
        maxspeed = max(maxspeed, speed)
        mingap = min(mingap, *gaps)
        maxden = max(maxden, q)
    print("Proposition 2.8 plane certificates: PASS")
    print("certificate rows = 6866")
    print("maximum certified speed bound =", maxspeed)
    print("minimum safety margin =", mingap)
    print("maximum denominator =", maxden)

if __name__ == "__main__":
    main()
