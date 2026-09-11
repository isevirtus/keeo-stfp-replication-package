# Experimental environments

The study used two machines/environments. Runtime values should not be compared across them as if they were paired measurements.

## Surrogate-versus-BN benchmark

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

## GA/MILP exact comparison and scalability

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
