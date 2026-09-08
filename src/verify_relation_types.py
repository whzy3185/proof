#!/usr/bin/env python3
"""Verify the 23 first-relation absolute types used in Proposition 2.4 / Table 1.

Only Python arbitrary-precision integers are used.
"""
from __future__ import annotations
import csv
from itertools import product
from math import gcd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "first_relation_types.csv"
ADD = (0, 1, 1, 1)

def enumerate_types() -> list[tuple[int, int, int, int]]:
    out: set[tuple[int, int, int, int]] = set()
    for r in product(range(-4, 5), repeat=4):
        if not any(r):
            continue
        if sum(abs(x) == 4 for x in r) > 1:
            continue
        if sum(r) % 2 == 0 or gcd(*r) != 1:
            continue
        if sum(x != 0 for x in r) < 2:
            continue
        out.add(tuple(sorted(abs(x) for x in r)))
    return sorted(out)

def read_expected() -> dict[tuple[int, int, int, int], str]:
    out = {}
    with DATA.open(newline="") as f:
        for rec in csv.DictReader(f):
            r = tuple(int(rec[f"r{i}"]) for i in range(1, 5))
            out[r] = rec["classification"]
    return out

def main() -> None:
    got = enumerate_types()
    expected = read_expected()
    if set(got) != set(expected):
        raise SystemExit({"status": "FAIL", "missing": sorted(set(expected) - set(got)), "extra": sorted(set(got) - set(expected))})
    if len(got) != 23 or expected.get(ADD) != "additive":
        raise SystemExit({"status": "FAIL", "count": len(got), "additive_type": expected.get(ADD)})
    nonadditive = [r for r in got if r != ADD]
    if len(nonadditive) != 22:
        raise SystemExit({"status": "FAIL", "nonadditive_count": len(nonadditive)})
    print("Proposition 2.4 / Table 1: PASS")
    print("first relation types = 23")
    print("immediately additive type = (0,1,1,1)")
    print("non-additive types = 22")

if __name__ == "__main__":
    main()
