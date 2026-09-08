# Exact verification for *The four-speed Lonely Runner spectrum below 1/4*

This repository contains the exact verification code and finite certificates for the computer-assisted parts of the manuscript **The four-speed Lonely Runner spectrum below `1/4`**.

All proof-critical computations use **exact integer or rational arithmetic**. No floating-point tolerance and no randomized step is used to decide a mathematical statement.

The analytic reductions are proved in the manuscript. This repository addresses only the finite assertions used in the proof.

## Manuscript-to-code map

| Manuscript result | Main scripts | Expected result |
| --- | --- | --- |
| Proposition 2.4 / Table 1 | `src/verify_relation_types.py` | 23 first-relation types; one additive type; 22 non-additive types |
| Proposition 2.6 | `src/verify_second_certificate.py` | 20 types have least `k=3`, one has `k=4`, one has `k=9` |
| Proposition 2.8 | `src/enumerate_planes.py`, `src/generate_plane_certificates.py`, `src/verify_plane_bound.py` | `83842 -> 37612 -> 538 -> 37074 -> 6866`; all 6866 plane classes certified; bound `<= 290` |
| Lemma 2.9 | `src/verify_endpoint_counts.py` | `|E_290|=34205`, `|E_445|=80381` |
| Proposition 2.10 | `src/verify_nonadditive_290.py` | 282,669,864 non-additive quadruples; 0 failures |
| Proposition 3.2 | `src/verify_additive_region.py` | 815,970 triples; 7,149 low; 7,148 family-(B); unique exception `{1,3,4,14}` |

## Quick start

Requirements:

- Python 3.10 or newer;
- a C++17 compiler (`g++` or `clang++`);
- no third-party Python package is required for verification.

Clone the repository and run:

```bash
git clone https://github.com/whzy3185/proof.git
cd proof
python src/verify_all.py --quick
```

Quick mode checks the exact Fourier data, reconstructs all 6,866 Pluecker classes, verifies all 6,866 plane certificates, checks the endpoint counts, and compiles/runs a small exact C++ smoke test. It is **not** the complete proof verification.

For the full proof-critical finite checks:

```bash
python src/verify_all.py --full
```

A successful full run ends with

```text
ALL PROOF-CRITICAL CHECKS PASSED
```

## Individual checks

### Proposition 2.4 / Table 1

```bash
python src/verify_relation_types.py
```

Expected:

```text
first relation types = 23
immediately additive type = (0,1,1,1)
non-additive types = 22
```

### Proposition 2.6

```bash
python src/verify_second_certificate.py
```

Expected:

```text
least k = 3 for 20 types
least k = 4 for (1,1,1,2)
least k = 9 for (0,0,1,2)
```

The exact values used in this check are stored in
`data/second_certificate_values.csv` and
`data/second_certificate_exception_sequences.csv`.

### Proposition 2.8: plane enumeration and coverage

```bash
python src/enumerate_planes.py
```

Expected:

```text
N4 = 1620
N5 = 3620
N10 = 47844
independent relation pairs = 83842
distinct rational relation planes = 37612
forbidden planes = 538
admissible planes = 37074
signed-permutation classes = 6866
generated/certified class-set equality = PASS
missing classes = 0
extra classes = 0
```

`data/plane_classes_6866.csv` contains one canonical primitive Pluecker tuple and one final reduced saturated integer basis for each class.

### Proposition 2.8: safe-point certificates and bound 290

The supplied certificates are checked without any search by:

```bash
python src/verify_plane_bound.py
```

Expected:

```text
certificate rows = 6866
maximum certified speed bound = 290
minimum safety margin = 1/28
maximum denominator = 17
```

The certificate generator is deliberately separate:

```bash
python src/generate_plane_certificates.py --output generated_plane_safe_points.csv
```

It searches, for each fixed reduced basis in `plane_classes_6866.csv`, all

```text
1 <= q <= 17,  0 <= p,r < q
```

until it finds a strict safe point with margin at least `1/28` and certified bound at most `290`. The standalone verifier does not call this generator.

For an environment-only test of the generator:

```bash
python src/generate_plane_certificates.py --limit 25 --output generated_25.csv
```

### Lemma 2.9 endpoint sets

```bash
python src/verify_endpoint_counts.py
```

Expected:

```text
|E_290| = 34205
|E_445| = 80381
```

### Proposition 2.10

```bash
python src/verify_nonadditive_290.py
```

Expected:

```text
|E_290| = 34205
total quadruples = 288641640
additive quadruples = 5971776
non-additive quadruples = 282669864
non-additive failures = 0
```

The Python entry point compiles and runs `src/exact_box_core.cpp`. All theorem-deciding checks in the C++ core are integer/rational checks; each returned witness is rechecked independently by the modular inequality from Lemma 2.9.

### Proposition 3.2

```bash
python src/verify_additive_region.py
```

Expected:

```text
|E_445| = 80381
parameter triples = 815970
no-common-safe-time triples = 7149
family-(B) parameter triples = 7148
exceptional speed set = {1,3,4,14}
unclassified = 0
```

## Data files

- `data/first_relation_types.csv` — all 23 first-relation absolute types and the additive/non-additive classification.
- `data/second_certificate_values.csv` — least successful `k` and exact `C_k(r)` for the 22 non-additive types.
- `data/second_certificate_exception_sequences.csv` — the complete exceptional sign sequences proving minimal `k=4` and `k=9`.
- `data/plane_classes_6866.csv` — canonical Pluecker tuple and final reduced saturated basis for every plane class.
- `data/plane_safe_points.csv` — exact rational safe point, four exact margins, and `A_P,B_P` for every class.

## Generator / verifier separation

The plane computation is intentionally split:

- `src/enumerate_planes.py` regenerates the complete canonical Pluecker class set and checks exact set equality with `plane_classes_6866.csv`;
- `src/generate_plane_certificates.py` searches for safe-point certificates using the fixed reduced bases;
- `src/verify_plane_bound.py` is a standalone certificate verifier and performs no search.

Thus the short verifier does not rely on the certificate-generation search procedure.

## Exact arithmetic

No proof-critical comparison uses floating point. The Python checks use arbitrary-precision `int` and `fractions.Fraction`; the C++ finite classification uses exact integer modular inequalities and exact rational interval endpoints represented by integer numerator/denominator pairs.

In particular, there is no code of the form

```python
abs(x - 0.25) < 1e-10
```

in any theorem-deciding branch.

## Expected outputs

Human-readable expected outputs are in `expected_output/`. A referee can run a script and compare its final invariants directly with the corresponding file.

## Repository version

The intended manuscript correspondence is documented in `docs/verification_notes.md`. For a journal submission, the authors should create a frozen GitHub release (for example `v1.0-jcta-submission`) and cite that release/commit in submission metadata. The mathematical checks do not depend on a GitHub release mechanism.

## License and citation

See `LICENSE` and `CITATION.cff`.
