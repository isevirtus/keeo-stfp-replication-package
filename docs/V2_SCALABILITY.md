# V2 scalability: design, interpretation, and data quality

## What is being scaled?

| Experiment | Candidates | Team sizes | Configurations | GA runs |
|---|---:|---|---:|---:|
| B0 team-size | 510 | 5,6,7,8,9,10,12 | 84 | 2,520 |
| B1 candidate-pool | 1,000 | 4 | 12 | 360 |

Both use project labels P1–P12, the refined V2 evaluator and a compatible MILP.
B1 is an enlarged experimental pool, not evidence of a 1,000-person deployed
workforce. The construction of its additional profiles and edges remains an
end-to-end reproduction requirement. This is not a full factorial experiment:
large teams on B1 were not tested.

The separate B0 k=4 baseline remains in `optimization_summary.csv` as reported
aggregate evidence. It is not reverified by the new B0 sheet, which starts at k=5.

## Input and derived records

The released MILP and GA configuration summaries preserve supplied numeric
precision and recorded booleans. Project IDs are de-identified. Team membership
and timestamps are omitted. The source results contain no formula or error
cells; source text is treated as experiment documentation, not instructions.

Derived `comparison.csv`, `summary.csv` and B0 `team_size_summary.csv` are
recomputed with `scripts/analyze_v2_scalability.py`. MILP AE scores have six
decimal places and GA best scores generally eight. Ties use an absolute
1e-5 threshold on score differences. Numeric matches concern scores, not
identical team membership or managerial indifference.

B0: 80 certificates, four feasible uncertified results; 65 GA matches, 19
MILP-higher results, none GA-higher. The 65 matches include 63 certificates and
two uncertified incumbents. The uncertified configurations are P10/k=8,
P2/k=10, P2/k=12 and P8/k=12; the first and third are ties.

B1: no certificates. P5 has GA AE 0.69315561 versus MILP AE 0.689629.
The signed MILP-minus-GA difference is **-0.00352661**. P3 and P12 favor MILP;
the remaining nine are ties. This is an incumbent comparison, not proof of
GA optimality. Signed relative difference is not renamed optimality gap.

## Time accounting and protocol exception

The nominal MILP limit is 7,200 seconds per configuration, split between two
subproblems. GA quality uses the best of 30 runs. For timing, `time_total_s`
sums their recorded durations; it excludes orchestration outside those
timings. MILP `time_s` is the recorded invocation duration.

B1 mean MILP duration is 7,206.0392 s (range 7,202.33–7,209.43 s).
GA mean duration is 9.2057 s per run and 276.1696 s per 30 runs.
The ratio of mean recorded MILP duration to mean GA total is 26.0928.
It is descriptive, not a controlled speedup or equal-time quality comparison.
No causal cross-pool runtime estimate is made; hardware and execution controls
for the new runs must be confirmed from their environment records.

B0 P10/k=8 has recorded duration **14,390.14 s**. The source timing is retained.
It exceeds the nominal limit and needs execution-log review; no cause is
assumed. Its derived `runtime_review_required=1` flags the observation.
The B0 k=8 mean includes it (1,505.2833 s), while the median is 383.415 s.
Do not cap it at 7,200, silently remove it, or use it as a controlled speedup.

## Why reported solver bounds/gaps are not global AE bounds

The exact formulation solves two branches. The complete B0 implementation
extracts an internal objective bound for the chosen branch and reports the
maximum of the branch relative gaps; the internal objective omits a constant
included in final AE. These fields therefore do not form a global AE
incumbent/bound pair. The B1 excerpt is truncated, so implementation identity
is not assumed from similarity.

The literal `best_bound` and `mip_gap_pct` fields are retained for diagnostic
audit only. The released analysis does not use either to calculate a global
optimality gap. Such a calculation requires the upper bound for **each**
branch after restoration of its objective constant, followed by a valid bound
for their union and the best common-scale incumbent. Missing branch values
are not synthesized.

An exact `Optimal` combined status is interpreted as solver certification
within numerical tolerances, not a guarantee that every displayed diagnostic
is exactly zero. Four certified B0 rows contain small nonzero reported gaps
(P4/k=6, P1/k=8, P2/k=8, P1/k=9); this fact is retained, not erased.

## Reproduction boundary

The public script reproduces the configuration-level analysis. It does not
execute the original optimizers, recover individual GA runs or validate all
input transformations. Best seeds are released, but they do not replace the
complete seed-by-run logs. GA score means/medians/SDs are recorded summaries.
The B1 source code cells each end at 32,767 characters and terminate mid-code;
these truncated excerpts are not released as runnable source.
