# Manuscript map

This repository verifies the finite computer-assisted assertions in *The four-speed Lonely Runner spectrum below 1/4*.

| Manuscript item | Verification entry point | Checked invariant |
| --- | --- | --- |
| Proposition 2.4 / Table 1 | `python src/verify_relation_types.py` | 23 first-relation types; 22 non-additive |
| Proposition 2.6 | `python src/verify_second_certificate.py` | least `k`: twenty at 3, one at 4, one at 9 |
| Proposition 2.8 (coverage) | `python src/enumerate_planes.py` | `83842 -> 37612 -> 538 -> 37074 -> 6866`, exact generated/certified set equality |
| Proposition 2.8 (certificates) | `python src/verify_plane_bound.py` | 6866 rows; margin `>=1/28`; denominator `<=17`; bound `<=290` |
| Lemma 2.9 | `python src/verify_endpoint_counts.py` | `|E_290|=34205`, `|E_445|=80381` |
| Proposition 2.10 | `python src/verify_nonadditive_290.py` | 282,669,864 non-additive quadruples; 0 failures |
| Proposition 3.2 | `python src/verify_additive_region.py` | 815,970 triples; 7,149 low; 7,148 family-(B); exception `{1,3,4,14}` |

Run `python src/verify_all.py --full` to execute all proof-critical finite checks.
