# benchmark.py
# Runtime experiment: 4 conditions x 5 projects x 5 rounds
#
# C1 - Surrogate without GA -> avaliar_equipe_surrogate  (Pipeline/evaluate_teams_sur.py)
# C2 - Surrogate with GA    -> run_ga_com_config with evaluator=surrogate
# C3 - BN without GA        -> avaliar_equipe            (Pipeline/evaluate_teams.py)
# C4 - BN with GA           -> run_ga_com_config with evaluator=BN
#
# Output: results_tempo.csv  (columns: condition, project, round, time_s)
# ---------------------------------------------------------------------------
from __future__ import annotations
import sys, os, csv, time, random, io, contextlib
from pathlib import Path
# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
THIS     = Path(__file__).resolve()
BASE_DIR = THIS.parents[1]          # .../STFP
sys.path.insert(0, str(BASE_DIR))
# ---------------------------------------------------------------------------
# Experiment parameters
# ---------------------------------------------------------------------------
N_ROUNDS   = 5      # rounds per (condition, project)
TEAM_SIZE  = 4
GA_POP_SIZE = 10
GA_GENS     = 20     # complete generations (early stopping disabled by stable_gens=9999)
SEED_BASE   = 42
# Teams evaluated per round in the without-GA conditions:
# must equal the total number of GA evaluations = pop_size x (gens + 1)
N_TEAMS_SEM_AG = GA_POP_SIZE * (GA_GENS + 1)   # 10 x 21 = 210
OUTPUT_CSV = THIS.parent / "results_tempo.csv"
# ---------------------------------------------------------------------------
# Target projects
# ---------------------------------------------------------------------------
PROJETOS = {
    "P1": {
        "dominio":     {"must": ["Desktop", "Web"], "should": ["Cloud"],  "could": ["Mobile"]},
        "ecossistema": {"must": [".NET"],            "should": ["React"],  "could": ["MongoDB"]},
        "linguagens":  {"must": ["C#"],              "should": ["JavaScript", "TypeScript"], "could": ["Python"]},
    },
    "P2": {
        "dominio":     {"must": ["Mobile"],                    "should": ["Web"],   "could": ["Cloud"]},
        "ecossistema": {"must": ["Android", "iOS/iPadOS"],     "should": ["React"], "could": [".NET"]},
        "linguagens":  {"must": ["Kotlin", "Swift"],           "should": ["JavaScript", "TypeScript"], "could": ["Java", "C#"]},
    },
    "P3": {
        "dominio":     {"must": ["IoT", "Cloud"],   "should": ["Web"],  "could": ["Desktop"]},
        "ecossistema": {"must": ["AWS Lambda"],     "should": ["React", "Angular", "MongoDB"], "could": ["Android"]},
        "linguagens":  {"must": ["Python", "C++"], "should": ["JavaScript"], "could": ["Java", "TypeScript"]},
    },
    "P4": {
        "dominio":     {"must": ["Web"],      "should": ["Cloud"],            "could": ["Desktop"]},
        "ecossistema": {"must": ["MongoDB"],  "should": ["Angular", "React"], "could": ["AWS Lambda"]},
        "linguagens":  {"must": ["JavaScript"], "should": ["TypeScript", "Python"], "could": ["Java", "C#"]},
    },
    "P5": {
        "dominio":     {"must": ["Web", "Cloud"],  "should": ["Mobile"], "could": ["Desktop"]},
        "ecossistema": {"must": ["React", "AWS Lambda", "MongoDB"], "should": [".NET"], "could": ["Android"]},
        "linguagens":  {"must": ["JavaScript", "TypeScript", "Python"], "should": ["C#", "Java"], "could": ["Kotlin", "Swift"]},
    },
}
# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
print("[INIT] Loading evaluators and engine...", flush=True)
from Pipeline.evaluate_teams     import avaliar_equipe            as _bn_eval
from Pipeline.evaluate_teams_sur import avaliar_equipe_surrogate  as _sur_eval
import Algorithms.GA.engine as _engine
CANDIDATOS_IDS: list[int] = list(_engine.CANDIDATOS_IDS)
print(f"[INIT] Candidates in the graph: {len(CANDIDATOS_IDS)}", flush=True)
if len(CANDIDATOS_IDS) < TEAM_SIZE:
    raise RuntimeError(
        f"Insufficient candidates in the graph ({len(CANDIDATOS_IDS)}) "
        f"to form teams of size {TEAM_SIZE}."
    )
# ---------------------------------------------------------------------------
# _NoCacheDict: dictionary that never reports hits -- disables FITNESS_CACHE
# ---------------------------------------------------------------------------
class _NoCacheDict(dict):
    """Replaces FITNESS_CACHE: accepts writes but never returns hits."""
    def __contains__(self, key):  # pragma: no branch
        return False
    def __getitem__(self, key):
        raise KeyError(key)
# ---------------------------------------------------------------------------
# _run_ga_full: reimplements the GA loop using engine internals,
#               with configurable stable_gens and FITNESS_CACHE disabled.
#               This avoids modifying any file outside this folder.
# ---------------------------------------------------------------------------
def _run_ga_full(projeto_externo: dict, team_size: int, pop_size: int,
                 geracoes: int, seed: int, stable_gens: int = 9999,
                 log_eval: bool = False) -> dict:
    """
    Runs the COMPLETE GA pipeline (all generations and individuals),
    without FITNESS_CACHE or early stopping (stable_gens=9999).
    Uses the internal engine operators (_build_next_population, avaliar_pop,
    gerador_cromossomo) while directly controlling STABLE_GENS and the cache.
    """
    import random as _rand
    _rand.seed(seed)
    _engine.RUN_SUMMARY.clear()
    # --- disables the cache for this run ---
    _engine.FITNESS_CACHE = _NoCacheDict()
    # --- configures engine globals used by the operators ---
    _engine.PROJETO_ALVO = dict(projeto_externo)
    _engine.PROJETO_ALVO["tamanhoEquipe"] = team_size
    _engine.TAM_POP = pop_size
    MIN_DELTA     = 1e-4
    STABLE_GENS   = stable_gens   # 9999 -> early stopping never triggers
    t0 = time.perf_counter()
    # Generation 0 -- initial population
    pop = [_engine.gerador_cromossomo() for _ in range(pop_size)]
    pop = _engine.avaliar_pop(pop, 0, log_eval=log_eval, verbose=False)
    best_ind       = max(pop, key=lambda x: x["fitness"])
    best_ever      = best_ind["fitness"]
    best_team_ever = list(best_ind["equipe"])
    stable_count   = 0
    stop_reason    = "max_gens"
    last_gen       = 0
    # Main loop
    for g in range(1, geracoes + 1):
        pop = _engine._build_next_population(pop, pop_size=pop_size,
                                             elitism_k=_engine.ELITISMO)
        pop = _engine.avaliar_pop(pop, g, log_eval=log_eval, verbose=False)
        best_gen = max(pop, key=lambda x: x["fitness"])
        if best_gen["fitness"] > best_ever + MIN_DELTA:
            best_ever      = best_gen["fitness"]
            best_team_ever = list(best_gen["equipe"])
            stable_count   = 0
        else:
            stable_count += 1
        if stable_count >= STABLE_GENS:
            stop_reason = "stable_gens_no_improve"
            last_gen    = g
            break
        last_gen = g
    dur = time.perf_counter() - t0
    return {
        "best_team":    best_team_ever,
        "best_fitness": best_ever,
        "duration_sec": dur,
        "gens_executed": last_gen,
        "stop_reason":  stop_reason,
    }
# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _silence():
    return contextlib.redirect_stdout(io.StringIO())
# ---------------------------------------------------------------------------
# Warm-up: forces singleton creation before timing
# (uses _silence to absorb output containing non-cp1252 characters)
# ---------------------------------------------------------------------------
print("[WARMUP] Initializing BN and Surrogate singletons...", flush=True)
_wteam = random.sample(CANDIDATOS_IDS, TEAM_SIZE)
_wp    = PROJETOS["P4"]
with _silence():
    _bn_eval(_wteam, _wp, log=False)
    _sur_eval(_wteam, _wp, log=False)
print("[WARMUP] OK", flush=True)
def _gen_teams(seed: int, n: int) -> list[list[int]]:
    rng = random.Random(seed)
    return [rng.sample(CANDIDATOS_IDS, TEAM_SIZE) for _ in range(n)]
# ---------------------------------------------------------------------------
# Without-GA conditions (C1, C3) -- N_TEAMS_SEM_AG direct evaluations
# ---------------------------------------------------------------------------
def run_c1_sur_noag(projeto: dict, seed: int) -> float:
    """C1: evaluates N_TEAMS_SEM_AG teams with the surrogate; returns time in seconds."""
    teams = _gen_teams(seed, N_TEAMS_SEM_AG)
    t0 = time.perf_counter()
    with _silence():
        for t in teams:
            _sur_eval(t, projeto, log=False)
    return time.perf_counter() - t0
def run_c3_bn_noag(projeto: dict, seed: int) -> float:
    """C3: evaluates N_TEAMS_SEM_AG teams with the BN; returns time in seconds."""
    teams = _gen_teams(seed, N_TEAMS_SEM_AG)
    t0 = time.perf_counter()
    with _silence():
        for t in teams:
            _bn_eval(t, projeto, log=False)
    return time.perf_counter() - t0
# ---------------------------------------------------------------------------
# With-GA conditions (C2, C4)
# COMPLETE pipeline: pop_size x (GA_GENS+1) actual evaluations,
# without FITNESS_CACHE or early stopping.
# ---------------------------------------------------------------------------
def run_c2_sur_ag(projeto: dict, seed: int) -> float:
    """C2: GA with evaluator=surrogate, without caching or early stopping."""
    # Injects the surrogate as the engine evaluator
    _engine.avaliar_equipe = _sur_eval
    with _silence():
        resultado = _run_ga_full(
            projeto_externo=projeto,
            team_size=TEAM_SIZE,
            pop_size=GA_POP_SIZE,
            geracoes=GA_GENS,
            seed=seed,
            stable_gens=9999,        # disables early stopping
        )
    return resultado["duration_sec"]
def run_c4_bn_ag(projeto: dict, seed: int) -> float:
    """C4: GA with evaluator=BN, without caching or early stopping."""
    # Restores the BN evaluator in the engine
    _engine.avaliar_equipe = _bn_eval
    with _silence():
        resultado = _run_ga_full(
            projeto_externo=projeto,
            team_size=TEAM_SIZE,
            pop_size=GA_POP_SIZE,
            geracoes=GA_GENS,
            seed=seed,
            stable_gens=9999,        # disables early stopping
        )
    return resultado["duration_sec"]
# ---------------------------------------------------------------------------
# Condition map
# ---------------------------------------------------------------------------
CONDITIONS = {
    "C1_Sur_noGA": run_c1_sur_noag,
    "C2_Sur_withGA": run_c2_sur_ag,
    "C3_BN_noGA":  run_c3_bn_noag,
    "C4_BN_withGA":  run_c4_bn_ag,
}
# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------
def main():
    rows: list[dict] = []
    total = len(CONDITIONS) * len(PROJETOS) * N_ROUNDS
    done  = 0
    print(f"\n[BENCH] Starting: {len(CONDITIONS)} conditions x "
          f"{len(PROJETOS)} projects x {N_ROUNDS} rounds = {total} measurements")
    print(f"[BENCH] N_TEAMS_SEM_AG={N_TEAMS_SEM_AG}  "
          f"GA_POP_SIZE={GA_POP_SIZE}  GA_GENS={GA_GENS}  "
          f"(actual GA evaluations per round = {GA_POP_SIZE*(GA_GENS+1)})\n")
    for proj_id, proj_def in PROJETOS.items():
        for cond_name, cond_fn in CONDITIONS.items():
            for rodada in range(1, N_ROUNDS + 1):
                seed = SEED_BASE + rodada * 100 + list(PROJETOS).index(proj_id)
                try:
                    elapsed = cond_fn(proj_def, seed)
                    status  = "OK"
                except Exception as exc:
                    elapsed = float("nan")
                    status  = f"ERROR: {exc}"
                rows.append({
                    "condition": cond_name,
                    "project":   proj_id,
                    "round":     rodada,
                    "time_s":    f"{elapsed:.6f}",
                })
                done += 1
                print(
                    f"  [{done:3d}/{total}] {cond_name} | {proj_id} | "
                    f"round {rodada} -> {elapsed:.3f}s  {status}",
                    flush=True,
                )
    # Saves CSV
    with open(OUTPUT_CSV, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["condition", "project", "round", "time_s"])
        writer.writeheader()
        writer.writerows(rows)
    print(f"\n[OK] Results saved to: {OUTPUT_CSV}")
    # Summary by condition
    from collections import defaultdict
    import statistics
    by_cond: dict[str, list[float]] = defaultdict(list)
    for r in rows:
        try:
            by_cond[r["condition"]].append(float(r["time_s"]))
        except ValueError:
            pass
    print("\n=== SUMMARY (mean ± std by condition, all rounds and projects) ===")
    for cond in CONDITIONS:
        vals = by_cond.get(cond, [])
        if not vals:
            print(f"  {cond}: no data")
            continue
        m   = statistics.mean(vals)
        std = statistics.stdev(vals) if len(vals) > 1 else 0.0
        print(f"  {cond}: {m:.3f}s ± {std:.3f}s  (n={len(vals)})")
    print(f"\n[NOTE] C2 and C4 measure the COMPLETE GA pipeline: "
          f"{GA_POP_SIZE*(GA_GENS+1)} actual evaluations (without caching or early stopping).")
    print(f"       C1 and C3 measure {N_TEAMS_SEM_AG} direct evaluations (same volume).")
if __name__ == "__main__":
    main()
