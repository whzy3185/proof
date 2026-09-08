#!/usr/bin/env python3
"""Regenerate safe-point certificates for the 6,866 fixed reduced plane bases.

This generator reads the canonical plane and reduced saturated basis data in
`data/plane_classes_6866.csv`.  For each row it exhaustively searches
1 <= q <= 17 and 0 <= p,r < q for a strict safe point with margin at least
1/28 and certified speed bound at most 290.  It writes a new certificate CSV.

The independent verifier is `verify_plane_bound.py`; it does not call this
script or share its search routine.
"""
from __future__ import annotations
import argparse, csv
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLASSES = ROOT / "data" / "plane_classes_6866.csv"
OUT_FIELDS = ["p12","p13","p14","p23","p24","p34","x_num","y_num","den",
              "delta1_num","delta1_den","delta2_num","delta2_den",
              "delta3_num","delta3_den","delta4_num","delta4_den","A_bound","B_bound"]

def ceil_minus_one(x: Fraction) -> int:
    return (x.numerator - 1) // x.denominator

def search(u, w):
    target = Fraction(1, 28)
    for q in range(1, 18):
        for p in range(q):
            for r in range(q):
                gaps = []
                for i in range(4):
                    phase = (u[i] * p + w[i] * r) % q
                    gap = Fraction(min(phase, q - phase), q) - Fraction(1, 4)
                    if gap < target:
                        break
                    gaps.append(gap)
                if len(gaps) != 4:
                    continue
                alpha = max(Fraction(abs(w[i]), 2) / gaps[i] for i in range(4))
                beta  = max(Fraction(abs(u[i]), 2) / gaps[i] for i in range(4))
                A, B = ceil_minus_one(alpha), ceil_minus_one(beta)
                speed = max(A * abs(u[i]) + B * abs(w[i]) for i in range(4))
                if speed <= 290:
                    return p, r, q, gaps, A, B
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", default=str(ROOT / "generated_plane_safe_points.csv"))
    ap.add_argument("--limit", type=int, default=0, help="For environment testing only; 0 means all 6866 classes.")
    args = ap.parse_args()
    with CLASSES.open(newline="") as f:
        rows = list(csv.DictReader(f))
    if args.limit:
        rows = rows[:args.limit]
    out = Path(args.output)
    with out.open("w", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=OUT_FIELDS)
        wr.writeheader()
        for n, rec in enumerate(rows, 1):
            pvec = {k: rec[k] for k in ("p12","p13","p14","p23","p24","p34")}
            u = tuple(int(rec[f"u{i}"]) for i in range(1,5))
            w = tuple(int(rec[f"w{i}"]) for i in range(1,5))
            found = search(u, w)
            if found is None:
                raise SystemExit(f"no certificate found for row {n}")
            p, r, q, gaps, A, B = found
            row = dict(pvec, x_num=p, y_num=r, den=q, A_bound=A, B_bound=B)
            for i, gap in enumerate(gaps, 1):
                row[f"delta{i}_num"] = gap.numerator
                row[f"delta{i}_den"] = gap.denominator
            wr.writerow(row)
            if n % 500 == 0:
                print(f"generated {n}/{len(rows)}")
    print(f"generated certificates = {len(rows)}")
    print(f"output = {out}")

if __name__ == "__main__":
    main()
