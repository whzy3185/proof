# Verification notes for referees

This document records the mathematical role of each finite computation in the manuscript *The four-speed Lonely Runner spectrum below 1/4*.

The repository is intentionally organized as a **verification repository**, not as a development history. Internal experiments, mutation tests, old manuscript versions, submission metadata, and revision logs are omitted.

## 1. What the manuscript proves analytically

The manuscript proves the reductions that make the finite checks complete:

1. the first Fourier certificate forces one primitive relation with bounded coefficients;
2. the second Fourier certificate forces a second linearly independent bounded relation;
3. the saturated span of the two relations confines the speed vector to one of finitely many rational two-planes;
4. a strict safe point on such a plane bounds the primitive direction parameters;
5. Lemma 2.9 reduces the remaining one-dimensional safe-time problem to exact finite endpoint checks;
6. the additive branch is reduced analytically to a bounded parameter region plus explicit large-parameter families.

The code here verifies only the finite statements left after those reductions.

## 2. Proposition 2.4 / Table 1

`src/verify_relation_types.py` enumerates all primitive integer relations satisfying the support and parity restrictions from the first Fourier certificate. It then compares the generated set with `data/first_relation_types.csv`.

The exact result is 23 absolute types. The unique immediately additive type is `(0,1,1,1)`, leaving 22 non-additive types.

## 3. Proposition 2.6

`src/verify_second_certificate.py` computes the exact integers

`C_k(r) = J_{k+1}(r) - 128 J_k(r)`

from the binomial-coefficient formula in the manuscript. It proves the minimal choices:

- `k=3` for 20 relation types;
- `k=4` for `(1,1,1,2)`;
- `k=9` for `(0,0,1,2)`.

The exceptional negative-to-positive sequences are stored explicitly in `data/second_certificate_exception_sequences.csv`.

## 4. Proposition 2.8: complete plane coverage

`src/enumerate_planes.py` reconstructs the complete plane list independently of the safe-point certificates.

A rank-two rational relation plane is identified by its primitive Pluecker six-tuple. The script:

1. generates all normalized second relations allowed by Proposition 2.6;
2. forms every independent relation pair;
3. primitive-normalizes the Pluecker tuple;
4. removes planes containing a forbidden relation of support at most three;
5. quotients by signed coordinate permutations using the lexicographically least transformed primitive Pluecker tuple;
6. compares the generated class set with the class set in `data/plane_classes_6866.csv`.

The set comparison, not merely the count, is required to pass. Expected output:

`83842 -> 37612 -> 538 -> 37074 -> 6866`, with zero missing and zero extra classes.

## 5. Proposition 2.8: safe-point certificates

`data/plane_classes_6866.csv` contains the canonical class identifier and a final reduced saturated basis `(u,w)`.

`data/plane_safe_points.csv` contains, for the same class identifier,

- `(p/q,r/q)`;
- all four exact margins;
- `A_P,B_P`.

`src/verify_plane_bound.py` is deliberately a verifier rather than a search program. It checks:

- primitive/decomposable Pluecker data;
- saturation of `(u,w)` through the gcd of all `2x2` minors;
- agreement between the basis and the relation plane;
- `q <= 17`;
- exact recomputation of all four safety margins;
- each margin at least `1/28`;
- exact strict rounding that defines `A_P,B_P`;
- the final coordinate bound at most `290`.

The separate `src/generate_plane_certificates.py` performs the finite search for safe points. The verifier does not invoke the generator.

## 6. Lemma 2.9 and Proposition 2.10

`src/verify_endpoint_counts.py` reconstructs the canonical endpoint universes `E_290` and `E_445`.

`src/verify_nonadditive_290.py` invokes the exact C++17 core for the complete bounded non-additive check. The mathematical safety test for `t=p/q` is the integer inequality

`q <= 4 (vp mod q) <= 3q`.

Any interval witness returned by the finite core is rechecked by this modular inequality. The full result is:

- 288,641,640 increasing positive quadruples;
- 5,971,776 additive quadruples;
- 282,669,864 non-additive quadruples;
- 0 non-additive failures.

## 7. Proposition 3.2

`src/verify_additive_region.py` invokes the same exact C++17 core in the bounded additive mode. The result is:

- 815,970 parameter triples;
- 7,149 with no common `1/4`-safe time;
- 7,148 in family (B);
- one sporadic speed set `{1,3,4,14}`;
- 0 unclassified cases.

## 8. Arithmetic and independence of checks

All theorem-deciding Python computations use arbitrary-precision integers or `fractions.Fraction`. The C++ core represents rational endpoints by integer numerator/denominator pairs and uses integer cross-multiplication and modular inequalities. No floating-point tolerance is used.

The main independence built into the repository is structural:

- plane enumeration is separate from safe-point certificate verification;
- the certificate generator searches, while the certificate verifier only checks;
- the two bounded classifications do not use the relation-plane enumeration.

## 9. Quick versus full verification

`python src/verify_all.py --quick` is an environment/data smoke test and is **not** the full proof verification.

`python src/verify_all.py --full` runs all proof-critical finite checks.

## 10. Regenerating the checked-in plane data from definitions

The checked-in plane class and safe-point files can be regenerated without using the existing CSV data:

```bash
python src/enumerate_planes.py --no-compare --write-canonical /tmp/canonical_pluecker.csv
g++ -O3 -std=c++17 src/generate_plane_data.cpp -o /tmp/generate_plane_data
/tmp/generate_plane_data /tmp/canonical_pluecker.csv data/plane_classes_6866.csv data/plane_safe_points.csv
python src/verify_plane_bound.py
```

`generate_plane_data.cpp` constructs a saturated speed-plane basis from each primitive relation-plane Pluecker tuple, applies deterministic two-dimensional Gauss reduction, searches the exact rational grid with denominator at most 17, and writes the two checked-in CSV files. The subsequent Python verifier is independent of this search routine.
