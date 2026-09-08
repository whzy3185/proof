#!/usr/bin/env python3
"""Convenience entry point for referee verification.

Quick mode checks the exact Fourier and plane-certificate data and compiles the
finite verifier. Full mode additionally performs the two exhaustive finite
classifications used in Propositions 2.10 and 3.2.
"""
from __future__ import annotations
import argparse, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

def run(name, *args):
    cmd = [sys.executable, str(SRC / name), *map(str,args)]
    print("\n$", " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=ROOT, check=True)

def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--quick", action="store_true", help="Fast environment/data check; not the full proof verification.")
    g.add_argument("--full", action="store_true", help="Run all proof-critical finite checks.")
    args = ap.parse_args()
    full = args.full or not args.quick
    run("verify_relation_types.py")
    run("verify_second_certificate.py")
    run("enumerate_planes.py")
    run("verify_plane_bound.py")
    run("verify_endpoint_counts.py")
    if full:
        run("verify_nonadditive_290.py")
        run("verify_additive_region.py")
        print("\nALL PROOF-CRITICAL CHECKS PASSED")
    else:
        from _cpp_runner import executable
        import json
        out = subprocess.check_output([str(executable()), "30", "0"], text=True)
        data = json.loads(out)
        if data.get("status") != "PASS":
            raise SystemExit(data)
        print("\nC++17 exact verifier smoke test: PASS")
        print("Quick mode completed. Run `python src/verify_all.py --full` for the proof-critical exhaustive checks.")

if __name__ == "__main__":
    main()
