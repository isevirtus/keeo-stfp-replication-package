# Experimental environments

The study used two machines and version-specific software environments. V1
and V2 optimization runs used the same reported hardware but different software
versions. Runtime values must not be compared across versions or machines as
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

## V2 GA/MILP comparison on 510 profiles (primary RQ3 and RQ4)

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
solver parameters and time limit, seeds, and thread/load controls have not been
included with the aggregate results. The V1 settings above must not silently be
reused as a verified V2 execution record. No pinned V2 environment file is
provided until these versions and settings can be checked against the original
execution environment.
