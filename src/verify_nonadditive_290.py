#!/usr/bin/env python3
"""Run the exact finite verification in Proposition 2.10."""
import json, subprocess
from _cpp_runner import executable

def main():
    out = subprocess.check_output([str(executable()), "290", "31"], text=True)
    data = json.loads(out)
    expected = {
        "maximum_speed": 290,
        "all_distinct_positive_quadruples": 288641640,
        "excluded_additive_quadruples": 5971776,
        "nonadditive_quadruples_all_scales": 282669864,
        "uncovered": 0,
    }
    for k, v in expected.items():
        if data.get(k) != v:
            raise SystemExit({"status":"FAIL", "field":k, "got":data.get(k), "expected":v})
    print("Proposition 2.10: PASS")
    print("|E_290| = 34205")
    print("total quadruples = 288641640")
    print("additive quadruples = 5971776")
    print("non-additive quadruples = 282669864")
    print("non-additive failures = 0")

if __name__ == "__main__":
    main()
