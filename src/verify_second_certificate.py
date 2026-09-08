#!/usr/bin/env python3
"""Verify the finite second-Fourier-certificate data in Proposition 2.6.

The computation uses Python integers and math.comb only.
"""
from __future__ import annotations
import csv
from math import comb
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALUES = ROOT / "data" / "second_certificate_values.csv"
EXCEPTIONS = ROOT / "data" / "second_certificate_exception_sequences.csv"

def J(k: int, r: tuple[int, int, int, int]) -> int:
    total = 0
    for j in range(-k - 1, k + 2):
        prod = 1
        for ri in r:
            n = k + j * ri
            if n < 0 or n > 2 * k:
                prod = 0
                break
            prod *= comb(2 * k, n)
        if prod:
            total += (-1 if (j * sum(r)) % 2 else 1) * prod
    return total

def C(k: int, r: tuple[int, int, int, int]) -> int:
    return J(k + 1, r) - 128 * J(k, r)

def read_values():
    out = {}
    with VALUES.open(newline="") as f:
        for rec in csv.DictReader(f):
            r = tuple(int(rec[f"r{i}"]) for i in range(1, 5))
            out[r] = (int(rec["least_k"]), int(rec["C_k"]))
    exc = {}
    with EXCEPTIONS.open(newline="") as f:
        for rec in csv.DictReader(f):
            r = tuple(int(rec[f"r{i}"]) for i in range(1, 5))
            exc.setdefault(r, {})[int(rec["k"])] = int(rec["C_k"])
    return out, exc

def main() -> None:
    values, exceptions = read_values()
    if len(values) != 22:
        raise SystemExit({"status": "FAIL", "types": len(values)})
    counts = {3: 0, 4: 0, 9: 0}
    for r, (least_k, stored) in sorted(values.items()):
        if C(least_k, r) != stored or stored <= 0:
            raise SystemExit({"status": "FAIL", "type": r, "least_k": least_k, "stored": stored, "recomputed": C(least_k, r)})
        for k in range(3, least_k):
            if C(k, r) > 0:
                raise SystemExit({"status": "FAIL", "type": r, "unexpected_positive_k": k})
        counts[least_k] = counts.get(least_k, 0) + 1
    if counts != {3: 20, 4: 1, 9: 1}:
        raise SystemExit({"status": "FAIL", "least_k_counts": counts})
    for r, seq in exceptions.items():
        for k, stored in seq.items():
            if C(k, r) != stored:
                raise SystemExit({"status": "FAIL", "exception": r, "k": k, "stored": stored, "recomputed": C(k, r)})
    if exceptions.get((0, 0, 1, 2), {}).keys() != set(range(3, 10)):
        raise SystemExit("missing full k=3,...,9 exceptional sequence")
    if exceptions.get((1, 1, 1, 2), {}).keys() != {3, 4}:
        raise SystemExit("missing k=3,4 exceptional sequence")
    print("Proposition 2.6: PASS")
    print("least k = 3 for 20 types")
    print("least k = 4 for (1,1,1,2)")
    print("least k = 9 for (0,0,1,2)")

if __name__ == "__main__":
    main()
