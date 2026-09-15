# Reproduction scope and artifact status

This is an **analysis-reproduction package**, not a complete optimization
execution environment. Verification establishes consistency of the released
records and checksums, not independent replication of organizational experiments.

## Article-to-artifact map

| Evidence | Version | Public records | Supported operation |
|---|---|---|---|
| Semantic traceability | V1 core audit; V2 changes separately documented | Eight-construct audit and counts | Inspect six operational traces and two explicit exclusions |
| RQ1 pointwise fidelity | V1 | Three aggregates | Inspect errors; no raw training/holdout predictions |
| RQ1 decision fidelity | V1 | 1,200 candidate-score pairs and summaries | Recompute rankings, overlap, regret and score error |
| RQ2 runtime | V1 | 100 timings | Recompute condition summaries and ratios |
| Earlier RQ3 | V1 lineage | 12 MILP records, 360 GA runs | Regenerate signed project comparisons |
| Earlier team-size analysis | V1 lineage | 84 project summaries | Recompute aggregates; no individual GA runs |
| Knowledge refinement | V1 to V2 | Coefficients, change record, 13/14 and 14/14 counts | Inspect aggregate calibration evidence, not rerun it |
| Primary RQ3 | V2, B0, k=4 | Reported aggregate | Inspect 12 certificates, nine GA matches and reported gaps |
| RQ4 team-size scalability | V2, B0 | 84 MILP records and 84 GA configuration summaries | Recompute ties, score differences, per-size summaries and times |
| RQ4 candidate-pool scalability | V2, B1 | 12 MILP records and 12 GA configuration summaries | Recompute incumbent comparisons, dispersion and times |

## Versions and denominators

B0 has 510 candidates. The new V2 team-size series uses k=5,6,7,8,9,10,12:
84 configurations, 80 certificates, 65 returned-score matches, 2,520 valid GA
runs. B1 has 1,000 candidates and k=4: 12 configurations, no certificates,
nine matches, two MILP-higher and one GA-higher result, 360 valid GA runs.
The same 12 project contexts recur in both experiments.

The separate B0 k=4 RQ3 baseline is not included in either RQ4 denominator.
It remains an aggregate: 12 certificates, nine GA matches and 360 valid runs.
The old V2 k=5..10 aggregates are confirmed by their 72 matching configurations
in the new B0 data; do not add them again. The historical V1 B0 series is a
different knowledge version even though its size set matches the new V2 series.
No historical V1 B1 data are included or relabeled.

## Analysis convention

The V2 analysis uses decimal arithmetic on released score precision.
A tie is abs(MILP_AE - GA_best_AE) <= 1e-5 in AE score units. Signed differences
are never truncated. Best-of-30 quality is paired with the sum of the 30 run
durations, not the mean time of one run. GA means, medians and standard
deviations are retained as recorded summary statistics, not re-estimated from
unreleased individual runs. See [V2_SCALABILITY.md](V2_SCALABILITY.md) for
solver bounds, protocol exceptions and interpretive limits.

## Running and verifying

All core commands use only the Python standard library:

```bash
python scripts/verify_package.py
python scripts/analyze_decision_fidelity.py
python scripts/summarize_v2.py
python scripts/analyze_v2_scalability.py
```

The V2 scalability command writes comparisons and summaries under
`reproduced/v2_scalability/`; the canonical counterparts are released under
`data/v2/scalability_b0/` and `data/v2/scalability_b1/`. The verifier checks
their exact correspondence to recomputation, as well as negative-difference,
tolerance, non-contiguous-size, status and runtime-anomaly regressions.

The summary command renders the separate baseline and scalability strata
under `reproduced/v2/`. It does not pool rounded means. Generated outputs and
caches are excluded from the release manifest.

V1 decision-fidelity scores are released to six decimal places. Recalculation
matches the canonical summaries at reported precision; it does not recover the
probability vectors needed for the Brier score.

## Remaining end-to-end requirements

- Complete, version-matched feature extraction, evaluator, GA and MILP code,
  full-precision parameters and software revisions.
- Original six elicitation scenarios, 14 preference relations, calibration
  code and the precise fitting-error definition.
- Approved B0/B1 input manifests and graph construction procedures; the
  additional B1 profiles and edges require an explicit construction record.
- Individual V2 GA outputs and seed logs: 2,880 runs in the two scalability
  series, plus 360 in the separate B0 k=4 baseline.
- Original B0 k=4 MILP records; complete branch-level logs for scalability,
  including objective offsets and both bounds on the common AE scale.
- Explanation of B0 P10/k=8 timing and a verified environment lock for each
  experiment, including B1 hardware and thread/load controls.
- Sanitized preparation records and privacy-compatible inputs or a small
  runnable example if industrial inputs cannot be released.

The V2 script text received for B1 was truncated. It is not included as a
runnable implementation, and complete-looking B0 excerpts are not substituted
for it. No missing run rows, bounds, inputs, or calibration cases are fabricated.
