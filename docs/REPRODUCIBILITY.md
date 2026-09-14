# Reproduction scope and artifact status

This is an analysis-reproduction package. Passing the verifier establishes
internal consistency of released records and checksums, not an independent
replication of the original organizational experiments.

## Article-to-artifact map

| Evidence | Knowledge version | Public records | Supported operation |
|---|---|---|---|
| Semantic traceability | V1 core construct audit; V2 changes separately documented | Eight-construct audit and coverage counts | Inspect six operational traces and two explicit exclusions |
| RQ1 pointwise fidelity | V1 | Three aggregate rows | Inspect reported errors; no training/holdout raw predictions |
| RQ1 decision fidelity | V1 | 1,200 candidate-score pairs and project summaries | Recompute ranking, overlap, regret, and score error |
| RQ2 runtime | V1 | 100 timing records | Recompute condition summaries and ratios |
| Earlier RQ3 comparison | V1 historical lineage | 12 MILP records and 360 GA run records | Regenerate project comparisons with the signed-difference convention |
| Earlier team-size analysis | V1 historical lineage | 84 project-level comparisons | Recompute aggregates; individual GA runs not released |
| Knowledge refinement | V1 to V2 | Reported coefficients, change record, 13/14 and 14/14 counts | Inspect rules and aggregate calibration evidence; not rerun calibration |
| Primary RQ3 and RQ4 | V2 | Two non-overlapping stratum aggregates on 510 candidates | Regenerate the aggregate table and verify count arithmetic; not reanalyze original runs |

## V2 aggregation rules

`data/v2/optimization_summary.csv` separates `k=4` (12 configurations) from
`k=5..10` (72). Both use the **same 12 projects**. Their union is 84 unique
project/team-size configurations, not 84 independent projects. The RQ3 `k=4`
baseline is reused in RQ4 and must not be counted twice.

The 82 certified optima and two feasible but uncertified MILP solutions have
different evidential status. The 64 GA matches refer to the **returned MILP
value**, not necessarily to 64 certified optima: the cross-tabulation of ties
and certification for the two uncertified configurations is not released.
Best-of-30 quality must not be attributed to an average single GA run.

The mean absolute differences 0.0028 and 0.0014 are in AE score units.
Only the `k=4` stratum has released mean and maximum relative gaps (0.3879%
and 2.5986%). No pooled mean is calculated from rounded subgroup means.
No per-team-size runtime trend, confidence interval, equivalence test, or
per-project V2 comparison can be reconstructed from these aggregates.

The `k=4` mean times are 121.0 seconds per MILP project and 9.21 seconds per
GA run. Their ratio is approximately 13.1. Thirty sequential GA runs cost
approximately `30 * 9.21 = 276.3` seconds per project using the rounded mean,
excluding additional orchestration costs. This is a derived estimate, not a
recorded best-of-30 batch time or evidence of a 13-fold best-of-30 speedup.

Tie counts in the V2 aggregate file are reported classifications. The historical
V1 scripts implement an absolute raw-AE tolerance of `1e-5`; the V2 classifier,
full-precision scores, and tolerance still need to accompany the V2 raw release
before those classifications can be independently recomputed.

## Still needed for full V2 reproduction

- Version-matched evaluator, feature extraction, GA and MILP implementations,
  with software revisions and full-precision parameters.
- Original six elicitation scenarios, the 14 explicit preference relations,
  calibration script, and a precise fitting-error definition.
- A 510-profile instance manifest and approved input-release policy. If
  original inputs remain restricted, a small sanitized runnable example can
  demonstrate the pipeline, but cannot reproduce the industrial results.
- All 2,520 V2 GA run outputs, their seeds, feasibility flags and times, and
  the 84 project/team-size MILP outputs with bounds, statuses, times, and gaps.
- Identification and logs for the two feasible uncertified MILP configurations.
- V2 tie convention, aggregation script, and environment lock including solver
  parameters, time limits, thread settings, and dependencies.

No missing raw rows or experimental scenarios have been synthesized in this
package. Older V1 files are retained as explicitly labeled historical evidence,
not substituted for V2. The primary optimization scope is the 510-profile pool.

## Running the public analyses

All commands below use only the Python standard library:

```bash
python scripts/verify_package.py
python scripts/analyze_decision_fidelity.py
python scripts/summarize_v2.py
```

The decision-fidelity command recomputes the public summaries by default; use
`--help` for its output options. The V2 command writes
`reproduced/v2/optimization_table.md` and `optimization_table.tex`; both label
the inputs as reported aggregates. Generated outputs and Python caches are
excluded from the release manifest.

Decision-fidelity scores are published to six decimal places. The script
supports the public schema without private inputs; the canonical project and
overall decision summaries match recalculation from these released scores at
their reported precision. This does not recover the unreleased probability
vectors needed to recompute the end-to-end Brier score.
