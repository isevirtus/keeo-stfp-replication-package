# Experimental environments

The earlier study records describe two machines and version-specific software
environments. Prior V1 and V2 optimization runs used the same reported hardware
but different software versions. Hardware for the newly supplied V2 scalability
executions, especially B1, must be confirmed from their execution manifests. Runtime values must not be compared across versions or machines as
if they were paired measurements.

## V1 surrogate-versus-BN benchmark (RQ2)

- Windows 10 Pro, 64-bit
- Intel Core i3-3217U at 1.80 GHz
- 6 GB RAM
- Python 3.13.3
- pgmpy 1.0.0
- NumPy 2.2.6
- BN inference: `VariableElimination`
- One Python process; no explicit threading, multiprocessing, or parallel evaluator calls
- NumPy/backend thread counts were not explicitly constrained

Conditions ran in fixed order for each project: surrogate without GA, surrogate with GA, BN without GA, and BN with GA. Five consecutive rounds were executed per condition. The benchmark used a warm-up, matching seeds across corresponding conditions, suppressed console output in timed regions, disabled caching and early stopping, and measured time with `time.perf_counter()`.

CPU affinity, background load, and pauses between conditions were not controlled.

## Historical V1 GA/MILP exact comparison and team-size analysis

- Windows 11 Home Single Language, build 26200
- Intel Core i5-1334U, 10 physical cores and 12 logical processors
- 8 GB RAM
- Python 3.11.9
- PuLP 3.3.2
- Gurobi 13.0.2
- GA: Python standard library; no third-party evolutionary framework

Explicit Gurobi settings:

- relative gap target: 0
- `MIPFocus=1`
- `Threads=0`, which allowed use of up to the 12 logical processors recorded by the solver
- presolve, heuristics, cuts, and numerical tolerances: Gurobi defaults

The 7,200-second per-instance budget was divided equally between the two MILP subproblems. GA and MILP were invoked sequentially by the same benchmark runner.

## Prior V2 GA/MILP environment record

- Windows 11
- Intel Core i5-1334U
- 8 GB RAM
- Python 3.12.14 (reported version; environment lock not yet released)
- Gurobi 13.0.3 (reported version)
- Same reported optimization hardware as the earlier runs

The V2 record reports 30 GA runs per project/team-size configuration. At team
size four, mean times were 121.0 seconds per MILP project and 9.21 seconds per
GA run. The latter is not the elapsed time for a 30-run batch.

The V2 operating-system build, PuLP version if used, exact software revision,
and thread/load controls require an environment lock. The new scalability
protocol specifies 30 runs and a nominal 7,200-s MILP limit; this does not
establish all historical execution settings. The V1 settings above must not silently be
reused as a verified V2 execution record. No pinned V2 environment file is
provided until these versions and settings can be checked against the original
execution environment.

## New V2 scalability records (package 1.2.0)

Both experiments specify a nominal 7,200-s MILP budget and 30 GA repetitions.
The complete B0 runner constructs seeds 1–30 for a 30-run invocation. The
configuration summaries preserve each best seed but not all per-run seeds.
B1's truncated runner is not sufficient for independent end-to-end verification.

No new hardware or pinned environment manifest accompanies these configuration
records. Do not silently assign the prior machine/software record to B1, or
infer a hardware-controlled cross-pool speedup. The package reports computation
times descriptively. The nominal limit and recorded duration differ: B1
invocations are 2.33–9.43 s above the limit, and B0 P10/k=8 is 14,390.14 s.
See [V2_SCALABILITY.md](V2_SCALABILITY.md) for the unchanged observations and
comparison rules.
