# KESO-STFP Replication Package

Supplementary material for **“Knowledge Engineering for Search and Optimization: From Expert Knowledge to Auditable and Executable Models.”**

The paper introduces **Knowledge Engineering for Search and Optimization (KESO)** and instantiates it for the Software Team Formation Problem (STFP). Package version **1.2.1** contains de-identified experimental results, a versioned knowledge-change record, reference benchmark runners, a sanitized solver log, and verification scripts.

KESO engineers domain knowledge into explicit variables, constraints, preferences,
and executable evaluation models; it does not prescribe an evolutionary algorithm.
The study evaluates a GA and an exact MILP formulation. Either can be the
operational optimizer, selected according to deadline, workload, instance
difficulty, and required assurance. Using MILP as the GA's quality reference was
an experimental choice, not a requirement of KESO. Other compatible engines,
such as simulated annealing, are design options, not implementations evaluated
in this package. Evaluator choice (BN, direct lightweight model, or optional
surrogate) is separate from optimizer choice.

**Naming and compatibility:** KESO replaces the former method name KEEO.
Version 1.2.1 updates documentation and citation metadata only; all experimental
data and analysis code are unchanged. The repository URL and the
data/keeo_traceability/ directory retain their existing names to preserve links
and script compatibility.

The authoritative artifact is the **knowledge specification**, not the BN. The
BN is a V1 reference implementation; replacing it with a V1 surrogate is an
optional representation choice. V2 refines AT and AC independently of that
choice. The main optimization evidence uses V2 on **510 candidates with varying team sizes** and **1,000 candidates at fixed team size four**. These are distinct experiments; the historical V1 1,000-candidate experiment is not included.

## What this package supports

The public release supports the following forms of result inspection and reproduction:

1. **Semantic traceability:** inspect eight documented construct dispositions: six operational traces and two explicit exclusions (OSF and SLF).
2. **Surrogate fidelity (RQ1):** inspect pointwise and decision-level V1 fidelity on training, controlled-holdout, and semisynthetic end-to-end evaluations.
3. **Surrogate versus Bayesian Network runtime (RQ2):** recompute descriptive statistics and the reported 19.69x and 21.69x speedups from 100 timing measurements.
4. **Historical GA versus exact MILP evidence (RQ3 lineage):** regenerate the V1 12-project comparison from 12 MILP executions and 360 GA runs.
5. **Historical team-size evidence (RQ4 lineage):** inspect the V1 84 project/team-size comparisons on the organization-derived 510-profile base.
6. **Knowledge refinement:** inspect the V1-to-V2 AT/AC changes, reported coefficients, and preference-order coverage (13/14 to 14/14).
7. **Primary V2 optimization evidence (RQ3/RQ4):** inspect the separate 510-candidate size-four baseline; recompute 84 larger-team comparisons on 510 candidates and 12 size-four comparisons on 1,000 candidates.
8. **Package integrity:** verify released counts, V1 seed grids, comparison conventions, de-identification checks, and SHA-256 checksums.

The package is an **analysis-reproduction package**, not a self-contained
end-to-end execution environment. Organizational inputs, original semantic
elicitation records, and the complete STFP implementation are not included.
V1 includes timing and candidate-score records, plus historical optimization
records. V2 includes **MILP configuration records and GA configuration summaries**
for scalability, plus reported baseline and refinement aggregates. It does not
include individual GA runs or a complete evaluator. The scripts reproduce
analyses from these records, not the original optimization experiments. See the
[article-to-artifact map and outstanding artifacts](docs/REPRODUCIBILITY.md).

## Quick verification

Only the Python standard library is required to verify the public package:

```bash
python scripts/verify_package.py
```

Expected output:

```text
All replication-package checks passed.
```

The verification covers released row counts, V1 seed grids and comparison
rules, V2 instance-level classifications, signed differences, timing arithmetic, semantic exclusions, canonical values,
de-identification checks, and file hashes. Run without Python's `-O` option.

## Repository structure

```text
.
|-- README.md
|-- CHANGELOG.md
|-- CITATION.cff
|-- MANIFEST.sha256
|-- data/
|   |-- keeo_traceability/
|   |   |-- semantic_traceability_audit.csv
|   |   `-- semantic_traceability_summary.csv
|   |-- surrogate/
|   |   |-- decision_fidelity_per_team.csv
|   |   |-- decision_fidelity_by_project.csv
|   |   |-- decision_fidelity_summary.csv
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
|   `-- v2/
|       |-- optimization_summary.csv
|       |-- runtime_summary.csv
|       |-- refinement_summary.csv
|       |-- parameters.csv
|       |-- scalability_b0/  # V2: 510 candidates, k=5,6,7,8,9,10,12
|       `-- scalability_b1/  # V2: 1000 candidates, k=4
|-- docs/
|   |-- DATA_DICTIONARY.md
|   |-- ENVIRONMENT.md
|   |-- SEMANTIC_TRACEABILITY.md
|   |-- KNOWLEDGE_VERSIONS.md
|   `-- REPRODUCIBILITY.md
|-- scripts/
|   |-- verify_package.py
|   |-- analyze_decision_fidelity.py
|   |-- regenerate_tables.py
|   |-- summarize_v2.py
|   |-- analyze_v2_scalability.py
|   |-- benchmark_surrogate_vs_bn.py
|   |-- benchmark_scalability.py
|   `-- generate_manifest.py
`-- solver_logs/
    `-- P2_k12_B0_sanitized.txt
```

## Data and experiments

### Semantic traceability audit

`data/keeo_traceability/semantic_traceability_audit.csv` records the eight
elicited constructs and their execution or exclusion paths through the
knowledge specification, evaluator, optimizer, and recommendation artifacts.
OSF and SLF are not inputs to the operational collaboration graph. The aggregate counts are
in `semantic_traceability_summary.csv`, and the audit protocol and
interpretation boundary are documented in `docs/SEMANTIC_TRACEABILITY.md`.

### RQ1: surrogate fidelity

`data/surrogate/fidelity_summary.csv` contains the three reported evaluations:

| Phase | n | Brier score | MAE |
|---|---:|---:|---:|
| Training/calibration | 20,930 | 0.0155264 | 0.0382722 |
| Controlled holdout | 5,320 | 0.0155735 | 0.0385423 |
| Semisynthetic end-to-end teams | 1,200 | 0.0328372 | 0.0495603 |

The controlled training and holdout partitions come from the same enumerated
scenario space. The semisynthetic end-to-end evaluation used 192
organization-derived developer profiles and six synthetic project profiles,
sampling 200 teams per project with seed 42. De-identified prediction-level
scores are released in `decision_fidelity_per_team.csv`; project-level ranking,
top-k, and regret results are in `decision_fidelity_by_project.csv` and
`decision_fidelity_summary.csv`. The analysis script accepts both the public
six-decimal scores and the original private evaluator format. Public-score
recalculation may differ slightly from original-precision summaries.

`data/surrogate/surrogate_parameters.csv` reports the V1 analytical-surrogate
parameters. These are not a complete V2 configuration.

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

### RQ3 lineage: V1 GA against a certified exact reference

`data/rq3_exact_vs_ga/` contains the pre-refinement V1 evidence: 12 certified MILP solutions and 360 GA runs, using seeds 1-30 for each of 12 projects at team size four. The GA best-of-30 reached eight certified optima and remained within 2.26104% on the other four projects. Across all 360 runs, 73 reached a certified optimum within the absolute raw-AE tolerance of `1e-5`. These records preserve evidence lineage; they are not the V2 aggregate result foregrounded in the paper.

The public files omit project descriptions, developer identifiers, selected-team identifiers, and timestamps. These fields are not required to reproduce the reported quality and runtime analyses.

### RQ4 lineage: V1 team-size evidence on B0

`data/scalability_b0/project_level.csv` contains the pre-refinement V1 evidence:
84 project/team-size comparisons, with 12 projects for each of
`k = 5, 6, 7, 8, 9, 10, 12`. `team_size_summary.csv` contains the corresponding
historical aggregates. The V2 B0 series now uses the same team-size set, but a different
knowledge version. Do not merge or relabel the historical observations as V2.

The MILP certified 83 of 84 instances. The exception is P2 at `k=12`; its sanitized solver output is provided in `solver_logs/P2_k12_B0_sanitized.txt`. Across all B0 instances, 65 comparisons were ties under the raw-AE tolerance, the mean absolute relative difference was approximately 0.3221%, and the maximum was 3.961952%.

Only project-level best-of-30 results are available for this historical V1 team-size analysis; its 2,520 individual GA run records are not included in the current source material.

### V1-to-V2 refinement

[The knowledge-version record](docs/KNOWLEDGE_VERSIONS.md) documents the
independent Must-gated Should/Could terms, useful Must redundancy levels,
and global AC compression. It links each change to affected evaluators,
optimization formulations, and validation evidence. `data/v2/` includes
reported parameters and the six-scenario preference-order aggregates, with
unavailable parameters explicitly distinguished from zero.

### Primary RQ3/RQ4: V2 baseline and two scalability dimensions

| Pool / team sizes | Configurations | MILP certified | Feasible, uncertified | GA ties | MILP higher | GA higher | Valid GA runs | Mean absolute AE difference |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 510 / k=4 (RQ3 baseline) | 12 | 12 | 0 | 9 | 3 | 0 | 360/360 | 0.0028 |
| 510 / k=5,6,7,8,9,10,12 | 84 | 80 | 4 | 65 | 19 | 0 | 2,520/2,520 | 0.00127472 |
| 1000 / k=4 | 12 | 0 | 12 | 9 | 2 | 1 | 360/360 | 0.00298195 |

The same 12 project contexts recur. The first row remains a **reported
aggregate**, not newly reconstructed raw data. The two scalability rows are
**recomputed from released configuration records**. The B0 series excludes
the RQ3 k=4 baseline and does not contain k=11. Do not pool versions or count
the baseline twice. The earlier V2 k=5..10 subset is confirmed by the new
records: 72 configurations, 70 certificates, 55 ties, and mean absolute AE
difference rounded to 0.0014.

Each scalability folder contains de-identified MILP records, GA summaries
(best, mean, median, standard deviation, best seed, and timing), and canonical
derived comparisons. The GA quality comparison always uses **best-of-30**.
Ties use an absolute tolerance of **1e-5 AE units**, applied before conversion
to percentages. Differences retain their sign. Of the 65 B0 matches, 63 are
to certified optima and two to uncertified incumbents.

On B1, **none of the MILP results is certified**. The GA exceeds the returned
incumbent on P5, trails on P3 and P12, and ties on the other nine projects.
This does not prove GA optimality. Mean MILP duration is **7,206.04 s**;
mean total computation for **all 30 GA runs is 276.17 s** (descriptive ratio
26.09). These are not equal-time budgets or a hardware-controlled speedup
experiment. The 9.21-s mean single-run GA time must not be attached to
best-of-30 quality.

The B0 P10/k=8 MILP duration is **14,390.14 s**, above the nominal 7,200-s
budget. It is retained and flagged, not silently capped or dropped.
Reported solver bounds/gaps describe internal branch diagnostics and must
not be used as global AE bounds. See [scalability interpretation and
data-quality notes](docs/V2_SCALABILITY.md).

The size-four B0 baseline retains mean relative gap 0.3879%, maximum 2.5986%
(P3), mean MILP time 121.0 s, and mean GA run time 9.21 s. Its approximate
30-run cost is 276.3 s from the rounded mean, not a recorded batch duration.

## Regenerating public analyses

Decision fidelity from released candidate-score pairs:

```bash
python scripts/analyze_decision_fidelity.py
```

V2 baseline/scalability summary (Markdown and LaTeX, `reproduced/v2/`):

```bash
python scripts/summarize_v2.py
```

V2 configuration-level comparisons, per-size quality, and timing summaries:

```bash
python scripts/analyze_v2_scalability.py
```

Outputs go to `reproduced/v2_scalability/` and match the canonical derived
CSV files under `data/v2/scalability_b0/` and `data/v2/scalability_b1/`.

The historical V1 comparison script uses only the Python standard library and
applies a single absolute raw-AE tie tolerance of `1e-5`.

Historical V1 RQ3:

```bash
python scripts/regenerate_tables.py \
  --ilp data/rq3_exact_vs_ga/ilp.csv \
  --ga-runs data/rq3_exact_vs_ga/ga_runs.csv \
  --dataset-label B0_k4_certified \
  --output-dir reproduced/rq3
```

The regenerated `comparison.csv` and `summary.csv` files should match their canonical counterparts in `data/`.

### Historical V1 difference convention

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

The V2 scalability classifier is implemented separately in
`analyze_v2_scalability.py` with decimal arithmetic over the released scores.
The size-four B0 baseline remains an aggregate classification; it is not
recomputed from individual V2 runs.

## Reference benchmark scripts

The following scripts document the historical V1 benchmark logic:

- `benchmark_surrogate_vs_bn.py`: controlled 210-call evaluator benchmark;
- `benchmark_scalability.py`: parameterized GA/MILP scalability benchmark.

They are included for auditability but are not standalone because they import the complete STFP pipeline and require files that are not public in this release, including the organization-derived candidate base, collaboration graph, target-project definitions, BN evaluator, surrogate evaluator, GA engine, and MILP implementation.

## Privacy and de-identification

This public package intentionally removes:

- project descriptions;
- developer and selected-team identifiers;
- local filesystem paths;
- solver-license identifiers and registered-user information;
- execution timestamps that are not analytically required.

Project identifiers in the released data range from P1 to P12. V1 tables
preserve the available seeds, scores, solver statuses, MIP gaps, execution
times and GA configurations. V2 scalability tables preserve configuration-level
scores, dispersion, best seeds, timing and status fields while omitting team
membership and timestamps. No individual GA runs have been synthesized.

## Experimental environments

See [`docs/ENVIRONMENT.md`](docs/ENVIRONMENT.md) for version-specific hardware,
software and solver records, including V2 confirmation gaps. Table fields and
interpretation rules are in [`docs/DATA_DICTIONARY.md`](docs/DATA_DICTIONARY.md).

## Integrity manifest

`MANIFEST.sha256` records SHA-256 checksums for the public files and is checked
by `verify_package.py`. Git preserves exact file bytes, including line endings.
Generated `reproduced/` outputs and caches are excluded. Regenerate the
manifest only after an intentional release change, not to hide an unexpected
verification failure:

```bash
python scripts/generate_manifest.py
```

## Citation

Use the metadata in `CITATION.cff`. The paper is currently under preparation for submission to *Knowledge-Based Systems*; final bibliographic metadata and a permanent archive DOI should be added after acceptance or archival release.

## License

No reuse license has been selected for this initial release. Until the repository owners add one, the contents remain under default copyright. Code and data licensing should be finalized before archival publication.
