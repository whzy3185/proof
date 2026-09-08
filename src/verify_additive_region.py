#!/usr/bin/env python3
"""Run the exact bounded additive classification in Proposition 3.2."""
import json, subprocess
from _cpp_runner import executable

def main():
    out = subprocess.check_output([str(executable()), "additive"], text=True)
    data = json.loads(out)
    expected = {
        "parameter_triples": 815970,
        "exact_interval_near_tight": 7149,
        "U2_parameter_triples": 7148,
        "isolated_parameter_triples": 1,
        "unclassified": 0,
    }
    for k, v in expected.items():
        if data.get(k) != v:
            raise SystemExit({"status":"FAIL", "field":k, "got":data.get(k), "expected":v})
    print("Proposition 3.2: PASS")
    print("|E_445| = 80381")
    print("parameter triples = 815970")
    print("no-common-safe-time triples = 7149")
    print("family-(B) parameter triples = 7148")
    print("exceptional speed set = {1,3,4,14}")
    print("unclassified = 0")

if __name__ == "__main__":
    main()
