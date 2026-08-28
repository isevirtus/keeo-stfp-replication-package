# KEEO-STFP Replication Package

Supplementary material for **“Knowledge Engineering for Evolutionary Optimization: From Expert Knowledge to Auditable and Executable Search Models.”**

The paper introduces **Knowledge Engineering for Evolutionary Optimization (KEEO)** and instantiates it for the Software Team Formation Problem (STFP). This repository contains de-identified experimental results, reference benchmark runners, a synthetic-base generator, a sanitized solver log, and verification scripts.

## What this package supports

The public release supports four forms of result inspection and reproduction:

1. **Surrogate fidelity (RQ1):** inspect the reported training, controlled-holdout, and organization-derived end-to-end fidelity summaries.
2. **Surrogate versus Bayesian Network runtime (RQ2):** recompute descriptive statistics and the reported 19.69x and 21.69x speedups from 100 timing measurements.
3. **GA versus exact MILP (RQ3):** regenerate the 12 project-level comparisons and aggregate results from 12 MILP executions and 360 GA runs.
4. **Scalability (RQ4):** inspect the 84 project/team-size comparisons on the 510-profile base and regenerate the 12 project-level comparisons on the 1,000-profile base from 360 corrected GA runs and 12 time-limited MILP runs.

The package is an **analysis-reproduction package**, not yet a fully self-contained end-to-end execution environment. The organization-derived developer profiles, collaboration graph, prediction-level fidelity records, and complete STFP implementation are not included in this public release. Consequently, the supplied scripts can verify and regenerate the reported result tables, while rerunning every optimization and BN evaluation from original organizational inputs requires additional private artifacts.

## Quick verification

Only the Python standard library is required to verify the public package:

```bash
python scripts/verify_package.py
```

Expected output:

```text
All replication-package checks passed.
```

The verification covers row counts, seed grids, solver-status interpretation, tie classification, canonical aggregate values, corrected B1 results, synthetic-profile membership flags, and de-identification checks.

## Repository structure

```text
.
|-- README.md
|-- CITATION.cff
|-- MANIFEST.sha256
|-- data/
|   |-- surrogate/
|   |   |-- fidelity_summary.csv
|   |   |-- runtime_raw.csv
|   |   |-- runtime_summary_by_project.csv
|   |   |-- runtime_summary_overall.csv
|   |   `-- surrogate_parameters.csv
|   |-- rq3_exact_vs_ga/
|   |   |-- ilp.csv
|   |   |-- ga_runs.csv
|   |   |-- comparison.csv
|   |   `-- summary.csv
|   |-- scalability_b0/
|   |   |-- project_level.csv
|   |   `-- team_size_summary.csv
|   `-- scalability_b1/
|       |-- ilp.csv
|       |-- ga_runs.csv
|       |-- comparison.csv
|       |-- summary.csv
|       |-- best_team_synthetic_membership.csv
|       `-- synthetic_generation_summary.csv
|-- docs/
|   |-- DATA_DICTIONARY.md
|   `-- ENVIRONMENT.md
|-- scripts/
|   |-- verify_package.py
|   |-- regenerate_tables.py
|   |-- benchmark_surrogate_vs_bn.py
|   |-- benchmark_scalability.py
|   |-- generate_synthetic_bases.py
|   `-- generate_manifest.py
`-- solver_logs/
    `-- P2_k12_B0_sanitized.txt
```

## Data and experiments

### RQ1: surrogate fidelity

`data/surrogate/fidelity_summary.csv` contains the three reported evaluations:

| Phase | n | Brier score | MAE |
|---|---:|---:|---:|
| Training/calibration | 20,930 | 0.0155264 | 0.0382722 |
| Controlled holdout | 5,320 | 0.0155735 | 0.0385423 |
| Organization-derived teams | 1,200 | 0.0328372 | 0.0495603 |

The controlled training and holdout partitions come from the same enumerated scenario space. The end-to-end evaluation sampled 200 teams for each of six projects with seed 42. The file contains aggregate metrics; prediction-level BN and surrogate outputs are not part of this release, so these metrics can be inspected and validated against the paper but not recomputed from individual predictions.

`data/surrogate/surrogate_parameters.csv` reports the calibrated analytical-surrogate parameters used in the study.

### RQ2: evaluator runtime

`data/surrogate/runtime_raw.csv` contains 100 measurements:

- 4 conditions;
- 5 projects (P1-P5);
- 5 consecutive rounds per condition and project;
- 210 evaluator calls per measurement.

The conditions are:

| ID | Evaluator | Search |
|---|---|---|
| `C1_Sur_noGA` | Surrogate | Direct evaluation of 210 sampled teams |
| `C2_Sur_withGA` | Surrogate | GA, population 10, initialization plus 20 complete generations |
| `C3_BN_noGA` | Bayesian Network | Direct evaluation of 210 sampled teams |
| `C4_BN_withGA` | Bayesian Network | GA, population 10, initialization plus 20 complete generations |

Caching and early stopping were disabled. A warm-up evaluation of both evaluators preceded timing. Matching project-round combinations used the same seed, conditions ran in a fixed order, console output was suppressed in timed regions, and elapsed time was measured with `time.perf_counter()`.

The benchmark used one Python process without explicit parallel evaluation. The operating system did not constrain threads that might be used internally by NumPy or its numerical backend.

### RQ3: GA against a certified exact reference

`data/rq3_exact_vs_ga/` contains 12 certified MILP solutions and 360 GA runs: seeds 1-30 for each of 12 projects at team size four. The GA best-of-30 reached eight certified optima and remained within 2.26104% on the other four projects. Across all 360 runs, 73 reached a certified optimum within the absolute raw-AE tolerance of `1e-5`.

The public files omit project descriptions, developer identifiers, selected-team identifiers, and timestamps. These fields are not required to reproduce the reported quality and runtime analyses.

### RQ4: scalability on B0

`data/scalability_b0/project_level.csv` contains 84 project/team-size comparisons: 12 projects for each of `k = 5, 6, 7, 8, 9, 10, 12`. `team_size_summary.csv` contains the aggregates reported in the paper.

The MILP certified 83 of 84 instances. The exception is P2 at `k=12`; its sanitized solver output is provided in `solver_logs/P2_k12_B0_sanitized.txt`. Across all B0 instances, 65 comparisons were ties under the raw-AE tolerance, the mean absolute relative difference was approximately 0.3221%, and the maximum was 3.961952%.

Only project-level best-of-30 results are available for this scalability dimension; the 2,520 individual GA run records are not included in the current source material.

### RQ4: scalability on B1

B1 expands B0 from 510 to 1,000 candidate profiles by adding 490 synthetic profiles with seed 42. The generator samples feature-list sizes, feature frequencies, collaboration-edge density, and edge-weight frequencies from B0. The resulting graph contains 37,272 edges and has density 0.074619, compared with 9,685 edges and density 0.074618 on B0.

`data/scalability_b1/` contains the final corrected execution:

- 12 time-limited MILP incumbents;
- 360 GA runs, seeds 1-30 per project;
- 7 ties;
- 2 cases in which the MILP incumbent was higher;
- 3 cases in which the GA reported value was higher than the time-limited incumbent;
- mean absolute incumbent difference: 1.174941%;
- maximum absolute incumbent difference: 4.332014%;
- total GA time: 2,140.810299 seconds.

None of the 360 recorded run-best teams contained a synthetic profile. `best_team_synthetic_membership.csv` preserves this check without exposing team identifiers. It does not establish that synthetic profiles were never evaluated during a run.

All B1 MILP solutions were feasible but uncertified. Therefore, a GA value above an MILP incumbent is not a value above the unknown optimum. B1 results are comparisons with time-limited incumbents, not optimality comparisons.

## Regenerating comparison tables

The standalone regeneration script uses only the Python standard library and applies a single absolute raw-AE tie tolerance of `1e-5`.

RQ3:

```bash
python scripts/regenerate_tables.py \
  --ilp data/rq3_exact_vs_ga/ilp.csv \
  --ga-runs data/rq3_exact_vs_ga/ga_runs.csv \
  --dataset-label B0_k4_certified \
  --output-dir reproduced/rq3
```

B1 scalability:

```bash
python scripts/regenerate_tables.py \
  --ilp data/scalability_b1/ilp.csv \
  --ga-runs data/scalability_b1/ga_runs.csv \
  --dataset-label B1_k4_time_limited_incumbents \
  --output-dir reproduced/b1
```

The regenerated `comparison.csv` and `summary.csv` files should match their canonical counterparts in `data/`.

### Difference convention

For MILP score `AE_ILP` and GA score `AE_GA`:

```text
raw_difference       = AE_ILP - AE_GA
signed_difference_%  = 100 * raw_difference / AE_ILP
absolute_difference_% = abs(signed_difference_%)
```

A comparison is a tie when:

```text
abs(AE_ILP - AE_GA) <= 1e-5
```

Negative signed differences are preserved: they indicate that the GA reported value exceeded the available MILP value. The sign must not be truncated before aggregation.

## Reference benchmark scripts

The following scripts document the executed benchmark logic:

- `benchmark_surrogate_vs_bn.py`: controlled 210-call evaluator benchmark;
- `benchmark_scalability.py`: parameterized GA/MILP scalability benchmark;
- `generate_synthetic_bases.py`: B1/B2/B3 profile and graph generator.

They are included for auditability but are not standalone because they import the complete STFP pipeline and require files that are not public in this release, including the organization-derived candidate base, collaboration graph, target-project definitions, BN evaluator, surrogate evaluator, GA engine, and MILP implementation.

## Privacy and de-identification

This public package intentionally removes:

- project descriptions;
- developer and selected-team identifiers;
- local filesystem paths;
- solver-license identifiers and registered-user information;
- execution timestamps that are not analytically required.

Projects are represented only as P1-P12. The de-identified data preserve seeds, scores, solver status, MIP gaps, execution times, GA configurations, and other fields required by the analyses.

## Experimental environments

See [`docs/ENVIRONMENT.md`](docs/ENVIRONMENT.md) for the two execution environments and solver settings. Table fields and interpretation rules are documented in [`docs/DATA_DICTIONARY.md`](docs/DATA_DICTIONARY.md).

## Integrity manifest

`MANIFEST.sha256` records SHA-256 checksums for the public files. Regenerate it after an intentional release change with:

```bash
python scripts/generate_manifest.py
```

## Citation

Use the metadata in `CITATION.cff`. The paper is currently under preparation for submission to *Knowledge-Based Systems*; final bibliographic metadata and a permanent archive DOI should be added after acceptance or archival release.

## License

No reuse license has been selected for this initial release. Until the repository owners add one, the contents remain under default copyright. Code and data licensing should be finalized before archival publication.

