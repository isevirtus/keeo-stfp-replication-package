#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
bench_escalabilidade_ilp_ga.py
================================

ILP vs. GA scalability benchmark for STFP.

Experiment design:
  - Uses the same target projects.
  - Keeps the same must/should/could requirements.
  - Changes only the tested team size: k=5, then k=6, then k=7, etc.
  - For each (project, k), runs:
      1) ILP in AE_FULL_EXACT_BINS mode.
      2) Calibrated GA through Algorithms.GA.engine.py, using the same surrogate.
  - Measures quality (AT, AC, AE), status, gap, and runtime.

Correct interpretation:
  This benchmark does not claim that the real project had a team of size k.
  It tests how ILP and GA behave when the same technical instance is solved
  with larger teams.

Recommended use inside an experiment directory, for example:

  cd /d <STFP_ROOT>\Experimento_Escalabilidade_ILP_GA

  python bench_escalabilidade_ilp_ga.py ^
    --project-root <STFP_ROOT> ^
    --target-projects <STFP_ROOT>\Experimento_ILP_STFP_T\target_projects.json ^
    --ilp-module-dir <STFP_ROOT>\Experimento_ILP_STFP_T ^
    --projects P1,P2,P3,P4,P5,P6,P7,P8,P9,P10,P11,P12 ^
    --team-sizes 5,6,7 ^
    --seeds 5 ^
    --ilp-time-limit 1800 ^
    --restart

For a full experiment run:

  python bench_escalabilidade_ilp_ga.py ^
    --project-root <STFP_ROOT> ^
    --target-projects <STFP_ROOT>\Experimento_ILP_STFP_T\target_projects.json ^
    --ilp-module-dir <STFP_ROOT>\Experimento_ILP_STFP_T ^
    --projects P1,P2,P3,P4,P5,P6,P7,P8,P9,P10,P11,P12 ^
    --team-sizes 5,6,7,8,9 ^
    --seeds 30 ^
    --ilp-time-limit 7200 ^
    --restart
"""

from __future__ import annotations

import argparse
import contextlib
import csv
import json
import os
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

# =============================================================================
# DEFAULT CONFIGURATION
# =============================================================================

MODO_ILP = "AE_FULL_EXACT_BINS"
MODO_GA = "AE_FULL_SURROGATE"
HARD_MUST_PENALTY = -1.0

GA_CALIBRADO_CCC: Dict[str, Any] = {
    "population_size": 150,
    "generations": 200,
    "elitism_count": 3,
    "mutation_rate": 0.005,
    "crossover_rate": 1.00,
    "stable_gens": 20,
    "crossover_operator": "ccc",
}

ILP_FIELDS = [
    "projeto", "project_name", "team_size_testado", "metodo", "modo", "status",
    "AT", "AC", "AE", "equipe", "tempo_s", "mip_gap_pct", "best_bound",
    "must_dom_ok", "must_eco_ok", "must_ling_ok", "all_must_ok",
    "ilp_sofreu", "timestamp",
]

GA_RUN_FIELDS = [
    "projeto", "project_name", "team_size_testado", "metodo", "modo", "seed", "status",
    "AT", "AC", "AE", "fitness_final", "AE_raw_surrogate", "equipe", "tempo_s",
    "must_dom_ok", "must_eco_ok", "must_ling_ok", "all_must_ok",
    "dom_score", "eco_score", "ling_score", "pc_score", "pc_label",
    "best_generation", "gens_executed", "stop_reason",
    "population_size", "generations", "elitism_count", "mutation_rate",
    "crossover_rate", "stable_gens", "crossover_operator", "timestamp",
]

GA_SUMMARY_FIELDS = [
    "projeto", "project_name", "team_size_testado", "metodo", "modo",
    "n_runs", "n_valid_runs", "valid_rate",
    "best_AE", "best_AT", "best_AC", "best_team", "best_seed", "best_tempo_s",
    "AE_mean", "AE_median", "AE_std", "AT_mean", "AC_mean",
    "tempo_total_s", "tempo_mean_s", "tempo_median_s",
    "gens_mean", "stop_reason_best", "timestamp",
]

COMPARISON_FIELDS = [
    "projeto", "project_name", "team_size_testado",
    "ilp_status", "ilp_AE", "ilp_AT", "ilp_AC", "ilp_team", "ilp_tempo_s", "ilp_mip_gap_pct", "ilp_sofreu",
    "ga_best_AE", "ga_best_AT", "ga_best_AC", "ga_best_team", "ga_best_seed",
    "ga_tempo_total_s", "ga_tempo_mean_s", "ga_n_runs",
    "dif_ILP_GA", "gap_pct", "speedup_best_of_n", "speedup_execucao_media",
    "winner_quality", "winner_time_total", "timestamp",
]

K_SUMMARY_FIELDS = [
    "team_size_testado", "n_projects",
    "ilp_optimal_count", "ilp_feasible_count", "ilp_hard_count", "ilp_time_total_s", "ilp_time_mean_s", "ilp_time_median_s", "ilp_time_max_s",
    "ga_time_total_s", "ga_time_mean_project_s", "ga_time_mean_run_s",
    "gap_mean_pct", "gap_max_pct", "ga_equal_ilp_count", "timestamp",
]


# =============================================================================
# ARGUMENTS
# =============================================================================

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="ILP vs. GA scalability benchmark with varying team size."
    )
    p.add_argument("--project-root", type=str, required=True,
                   help="STFP root directory containing Algorithms/, Pipeline/, and Data/.")
    p.add_argument("--ilp-module-dir", type=str, default="",
                   help="Directory containing stfp_ilp_gurobi_incumbent_corrigido.py. If empty, uses project-root/Experimento_ILP_STFP_T.")
    p.add_argument("--target-projects", type=str, default="target_projects.json",
                   help="Path to target_projects.json.")
    p.add_argument("--base-final", type=str, default="",
                   help="Path to base_final.json. If empty, uses project-root/Data/base_final.json.")
    p.add_argument("--graph", type=str, default="",
                   help="Path to Graph_DB_real.json. If empty, uses project-root/Data/Graph_DB_real.json.")
    p.add_argument("--projects", type=str, default="",
                   help="Comma-separated project IDs. If empty, uses all target projects.")
    p.add_argument("--team-sizes", type=str, default="5,6,7",
                   help="Comma-separated team sizes to test, e.g., 5,6,7,8,9.")
    p.add_argument("--seeds", type=int, default=5,
                   help="Number of GA seeds per project/k. Use 5 for a quick test and 30 for final results.")
    p.add_argument("--ilp-time-limit", type=int, default=1800,
                   help="ILP time limit per project/k in seconds. In FULL mode, it is split between the two cases.")
    p.add_argument("--skip-ilp", action="store_true", help="Skip ILP runs.")
    p.add_argument("--skip-ga", action="store_true", help="Skip GA runs.")
    p.add_argument("--stop-ilp-after-hard-k", action="store_true",
                   help="Stop running ILP for larger k values when all projects at one k are hard or non-optimal.")
    p.add_argument("--output-ilp", type=str, default="escala_ilp_runs.csv")
    p.add_argument("--output-ga-runs", type=str, default="escala_ga_runs.csv")
    p.add_argument("--output-ga-summary", type=str, default="escala_ga_resumo.csv")
    p.add_argument("--output-comparison", type=str, default="escala_comparacao_ilp_ga.csv")
    p.add_argument("--output-k-summary", type=str, default="escala_resumo_por_k.csv")
    p.add_argument("--restart", action="store_true", help="Delete previous output files before starting.")
    return p.parse_args()


# =============================================================================
# GENERAL HELPERS
# =============================================================================

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def parse_csv_list(s: str) -> List[str]:
    return [x.strip() for x in str(s).split(",") if x.strip()]


def parse_int_list(s: str) -> List[int]:
    out: List[int] = []
    for x in parse_csv_list(s):
        out.append(int(x))
    return out


def resolve_path(path_text: str, base: Optional[Path] = None) -> Path:
    p = Path(path_text)
    if p.is_absolute():
        return p.resolve()
    if base is not None:
        return (base / p).resolve()
    return (Path.cwd() / p).resolve()


@contextlib.contextmanager
def silent_stdout():
    old = sys.stdout
    try:
        with open(os.devnull, "w", encoding="utf-8") as devnull:
            sys.stdout = devnull
            yield
    finally:
        sys.stdout = old


def read_json(path: Path) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def carregar_target_projects(path: Path) -> Dict[str, Dict[str, Any]]:
    data = read_json(path)
    if isinstance(data, dict) and isinstance(data.get("projects"), list):
        return {str(p["id"]): p for p in data["projects"]}
    if isinstance(data, dict):
        out: Dict[str, Dict[str, Any]] = {}
        for pid, p in data.items():
            if isinstance(p, dict):
                p2 = dict(p)
                p2.setdefault("id", pid)
                out[str(pid)] = p2
        if out:
            return out
    raise ValueError(f"Unrecognized format in {path}")


def project_payload(project: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "dominio": project.get("dominio", {}),
        "ecossistema": project.get("ecossistema", {}),
        "linguagens": project.get("linguagens", {}),
    }


def clone_project_with_k(project: Dict[str, Any], k: int) -> Dict[str, Any]:
    p = dict(project)
    p["team_size_original"] = project.get("team_size", "")
    p["team_size"] = int(k)
    return p


def ensure_csv(path: Path, fields: List[str], restart: bool = False) -> None:
    if restart and path.exists():
        path.unlink()
    if not path.exists():
        with open(path, "w", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=fields).writeheader()


def append_csv(path: Path, fields: List[str], row: Dict[str, Any]) -> None:
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writerow({k: row.get(k, "") for k in fields})


def load_csv_rows(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    with open(path, "r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def to_float(x: Any) -> Optional[float]:
    try:
        if x in (None, ""):
            return None
        return float(x)
    except Exception:
        return None


def mean(vals: Iterable[float]) -> float:
    vals = list(vals)
    return statistics.mean(vals) if vals else 0.0


def median(vals: Iterable[float]) -> float:
    vals = list(vals)
    return statistics.median(vals) if vals else 0.0


def pstdev(vals: Iterable[float]) -> float:
    vals = list(vals)
    return statistics.pstdev(vals) if len(vals) > 1 else 0.0


def is_true(x: Any) -> bool:
    return str(x).strip().lower() in ("true", "1", "yes", "sim")


def team_to_str(team: Any) -> str:
    if isinstance(team, str):
        return team
    try:
        return json.dumps(team, ensure_ascii=False)
    except Exception:
        return str(team)


# =============================================================================
# ILP AND GA IMPORTS
# =============================================================================

def importar_ilp(project_root: Path, ilp_module_dir: Path):
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    if str(ilp_module_dir) not in sys.path:
        sys.path.insert(0, str(ilp_module_dir))

    import stfp_ilp_gurobi_incumbent_corrigido as ilp
    return ilp


def importar_engine(project_root: Path, base_path: Path, graph_path: Path):
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    original_argv = sys.argv[:]
    try:
        sys.argv = [sys.argv[0]]
        try:
            import Feature_Extraction.Dimension_Scoring.dimension_scoring as _ds
            _ds.DEBUG_DIM = False
        except Exception:
            pass

        import Algorithms.GA.engine as engine
        from Pipeline.evaluate_teams_sur import avaliar_equipe_surrogate

        engine.avaliar_equipe = avaliar_equipe_surrogate

        # Algorithms/GA/engine.py loads its candidate pool (DEVS/CANDIDATOS_IDS)
        # and derived structures once, at import time, from a fixed path
        # (Data/base_final.json), independent of this script's --base-final/
        # --graph arguments. Without reloading here, the GA silently keeps
        # searching the wrong pool whenever a different candidate base is
        # passed on the ILP side, which is invisible unless AE/team values
        # are compared across runs. Reload everything derived from the pool,
        # using the SAME base/graph the ILP side is using.
        mapa, adj, valid_ids = engine._load_grafo(str(graph_path))
        devs = [
            d for d in engine._carregar_devs(str(base_path))
            if (d.get("id") or d.get("user_id")) is not None
            and int(d.get("id") or d.get("user_id")) in valid_ids
        ]
        candidatos_ids = [int(d.get("id") or d.get("user_id")) for d in devs]

        engine.MAPA_PESOS_GRAFO = mapa
        engine.ADJ = adj
        engine.VALID_IDS = valid_ids
        engine.DEVS = devs
        engine.CANDIDATOS_IDS = candidatos_ids
        # DEV_TECH_FIT is a proxy table pre-computed from DEVS/MAPA_PESOS_GRAFO,
        # used by the CCC crossover's replacement operator; it is NOT
        # recomputed automatically just because DEVS/MAPA_PESOS_GRAFO changed.
        engine.DEV_TECH_FIT = engine.build_dev_tech_fit(devs, mapa)
        engine.FITNESS_CACHE.clear()

        print(f"[GA] Candidate pool reloaded from: {base_path} ({len(devs)} developers)")

        return engine
    finally:
        sys.argv = original_argv


# =============================================================================
# METRIC EXTRACTION
# =============================================================================

def coverage_count(eval_res: Dict[str, Any], dim: str, prio: str) -> Tuple[int, int]:
    cov = eval_res.get("coverage", {})
    if not isinstance(cov, dict):
        return 0, 0
    d = cov.get(dim, {})
    if not isinstance(d, dict):
        return 0, 0
    p = d.get(prio)
    if isinstance(p, dict):
        return int(p.get("covered", 0) or 0), int(p.get("total", 0) or 0)
    return 0, 0


def must_flags_from_eval(eval_res: Dict[str, Any]) -> Dict[str, bool]:
    flags = {"must_dom_ok": True, "must_eco_ok": True, "must_ling_ok": True}
    for dim, flag in [("dominio", "must_dom_ok"), ("ecossistema", "must_eco_ok"), ("linguagens", "must_ling_ok")]:
        covered, total = coverage_count(eval_res, dim, "M")
        if total > 0 and covered < total:
            flags[flag] = False
    flags["all_must_ok"] = all(flags.values())
    return flags


def score_dim(eval_res: Dict[str, Any], dim: str) -> Any:
    try:
        return eval_res.get("scores", {}).get(dim, {}).get("score", "")
    except Exception:
        return ""


def must_ok_cobertura_ilp(cobertura: Dict[str, bool], dim: str) -> bool:
    keys = [k for k in cobertura.keys() if k.startswith(dim + ".")]
    return all(bool(cobertura[k]) for k in keys) if keys else True


def ilp_sofreu(row: Dict[str, Any], time_limit: int) -> bool:
    status = str(row.get("status", ""))
    tempo = to_float(row.get("tempo_s")) or 0.0
    gap = to_float(row.get("mip_gap_pct"))
    if status != "Optimal":
        return True
    if gap is not None and gap > 0.0001:
        return True
    # FULL mode splits the budget between two cases, so use the total-limit proximity.
    if tempo >= 0.95 * float(time_limit):
        return True
    return False


# =============================================================================
# RUN ILP
# =============================================================================

def rodar_ilp_uma_instancia(
    ilp,
    projeto: Dict[str, Any],
    devs: List[Dict[str, Any]],
    ac_medios: Dict[int, float],
    grafo_ilp: Dict[Tuple[int, int], float],
    k: int,
    time_limit: int,
) -> Dict[str, Any]:
    t0 = time.perf_counter()
    try:
        resultado = ilp.resolver_ilp(
            projeto=projeto,
            devs=devs,
            ac_medios=ac_medios,
            grafo_ilp=grafo_ilp,
            modo=MODO_ILP,
            tamanho_equipe=int(k),
            tempo_limite=int(time_limit),
        )
        tempo_real = time.perf_counter() - t0
    except Exception as e:
        return {
            "projeto": projeto.get("id", ""),
            "project_name": projeto.get("name", ""),
            "team_size_testado": k,
            "metodo": "ILP",
            "modo": MODO_ILP,
            "status": f"Erro: {e}",
            "tempo_s": round(time.perf_counter() - t0, 2),
            "ilp_sofreu": True,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        }

    cobertura = resultado.get("cobertura_must", {}) or {}
    must_dom = must_ok_cobertura_ilp(cobertura, "dominio")
    must_eco = must_ok_cobertura_ilp(cobertura, "ecossistema")
    must_ling = must_ok_cobertura_ilp(cobertura, "linguagens")

    row = {
        "projeto": projeto.get("id", ""),
        "project_name": projeto.get("name", ""),
        "team_size_testado": k,
        "metodo": "ILP",
        "modo": MODO_ILP,
        "status": resultado.get("status", ""),
        "AT": resultado.get("AT", ""),
        "AC": resultado.get("AC", ""),
        "AE": resultado.get("AE", ""),
        "equipe": team_to_str(resultado.get("equipe", [])),
        "tempo_s": resultado.get("tempo_s", round(tempo_real, 2)),
        "mip_gap_pct": resultado.get("mip_gap_pct", ""),
        "best_bound": resultado.get("best_bound", ""),
        "must_dom_ok": must_dom,
        "must_eco_ok": must_eco,
        "must_ling_ok": must_ling,
        "all_must_ok": must_dom and must_eco and must_ling,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }
    row["ilp_sofreu"] = ilp_sofreu(row, time_limit)
    return row


# =============================================================================
# RUN GA
# =============================================================================

def avaliar_time_ga(engine, projeto: Dict[str, Any], team: List[int]) -> Dict[str, Any]:
    with silent_stdout():
        eval_res = engine.avaliar_equipe(team, project_payload(projeto), log=False)
    if not isinstance(eval_res, dict):
        return {}
    return eval_res


def rodar_ga_uma_vez(engine, projeto: Dict[str, Any], k: int, config: Dict[str, Any], seed: int) -> Dict[str, Any]:
    try:
        engine.ELITISMO = int(config["elitism_count"])
    except Exception:
        pass

    t0 = time.perf_counter()
    try:
        with silent_stdout():
            result = engine.run_ga_com_config(
                PROJETO_ALVO_EXTERNO=project_payload(projeto),
                team_size=int(k),
                pop_size=int(config["population_size"]),
                geracoes=int(config["generations"]),
                seed=int(seed),
                crossover_rate=float(config["crossover_rate"]),
                mutation_rate=float(config["mutation_rate"]),
                stable_gens=int(config["stable_gens"]),
                crossover_operator=str(config["crossover_operator"]),
                verbose=False,
                report=False,
                log_eval=False,
            )
        elapsed = time.perf_counter() - t0
    except Exception as e:
        return {
            "projeto": projeto.get("id", ""),
            "project_name": projeto.get("name", ""),
            "team_size_testado": k,
            "metodo": "GA_CALIBRADO_CCC",
            "modo": MODO_GA,
            "seed": seed,
            "status": f"Erro: {e}",
            "tempo_s": round(time.perf_counter() - t0, 6),
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            **config,
        }

    best_team = result.get("best_team", []) or result.get("equipe", []) or []
    best_team = [int(x) for x in best_team]
    eval_res = result.get("best_eval") if isinstance(result.get("best_eval"), dict) else None
    if not eval_res:
        eval_res = avaliar_time_ga(engine, projeto, best_team)

    flags = must_flags_from_eval(eval_res) if eval_res else {
        "must_dom_ok": False, "must_eco_ok": False, "must_ling_ok": False, "all_must_ok": False
    }

    ae_raw = to_float(eval_res.get("media_AE") if eval_res else None)
    if ae_raw is None:
        ae_raw = to_float(result.get("fitness_final"))
    if ae_raw is None:
        ae_raw = to_float(result.get("best_fitness"))
    if ae_raw is None:
        ae_raw = 0.0

    fitness_final = ae_raw if flags["all_must_ok"] and len(best_team) == int(k) else HARD_MUST_PENALTY

    row = {
        "projeto": projeto.get("id", ""),
        "project_name": projeto.get("name", ""),
        "team_size_testado": k,
        "metodo": "GA_CALIBRADO_CCC",
        "modo": MODO_GA,
        "seed": seed,
        "status": "OK" if fitness_final >= 0 else "NO_VALID_TEAM",
        "AT": eval_res.get("AT_cont", eval_res.get("AT", "")) if eval_res else "",
        "AC": eval_res.get("AC_cont", eval_res.get("AC", "")) if eval_res else "",
        "AE": ae_raw,
        "fitness_final": fitness_final,
        "AE_raw_surrogate": ae_raw,
        "equipe": team_to_str(best_team),
        "tempo_s": round(elapsed, 6),
        "must_dom_ok": flags["must_dom_ok"],
        "must_eco_ok": flags["must_eco_ok"],
        "must_ling_ok": flags["must_ling_ok"],
        "all_must_ok": flags["all_must_ok"],
        "dom_score": score_dim(eval_res, "dominio") if eval_res else "",
        "eco_score": score_dim(eval_res, "ecossistema") if eval_res else "",
        "ling_score": score_dim(eval_res, "linguagens") if eval_res else "",
        "pc_score": eval_res.get("pc_score", "") if eval_res else "",
        "pc_label": eval_res.get("pc_label", "") if eval_res else "",
        "best_generation": result.get("best_generation", result.get("geracao_melhor", "")),
        "gens_executed": result.get("gens_executed", result.get("geracoes_executadas", "")),
        "stop_reason": result.get("stop_reason", ""),
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }
    row.update(config)
    return row


# =============================================================================
# SUMMARIES
# =============================================================================

def gerar_resumo_ga(ga_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    grupos: Dict[Tuple[str, int], List[Dict[str, Any]]] = {}
    for r in ga_rows:
        try:
            key = (str(r.get("projeto", "")), int(r.get("team_size_testado", 0)))
            grupos.setdefault(key, []).append(r)
        except Exception:
            continue

    out: List[Dict[str, Any]] = []
    for (pid, k), rows in sorted(grupos.items(), key=lambda x: (x[0][1], x[0][0])):
        valid = [r for r in rows if str(r.get("status")) == "OK" and to_float(r.get("AE")) is not None]
        aes = [to_float(r.get("AE")) for r in valid if to_float(r.get("AE")) is not None]
        ats = [to_float(r.get("AT")) for r in valid if to_float(r.get("AT")) is not None]
        acs = [to_float(r.get("AC")) for r in valid if to_float(r.get("AC")) is not None]
        tempos = [to_float(r.get("tempo_s")) for r in rows if to_float(r.get("tempo_s")) is not None]

        best = None
        if valid:
            best = max(valid, key=lambda r: to_float(r.get("AE")) or -999.0)
        first = rows[0]

        out.append({
            "projeto": pid,
            "project_name": first.get("project_name", ""),
            "team_size_testado": k,
            "metodo": "GA_CALIBRADO_CCC",
            "modo": MODO_GA,
            "n_runs": len(rows),
            "n_valid_runs": len(valid),
            "valid_rate": round(len(valid) / len(rows), 6) if rows else 0.0,
            "best_AE": round(to_float(best.get("AE")) or 0.0, 8) if best else "",
            "best_AT": round(to_float(best.get("AT")) or 0.0, 8) if best else "",
            "best_AC": round(to_float(best.get("AC")) or 0.0, 8) if best else "",
            "best_team": best.get("equipe", "") if best else "",
            "best_seed": best.get("seed", "") if best else "",
            "best_tempo_s": best.get("tempo_s", "") if best else "",
            "AE_mean": round(mean([x for x in aes if x is not None]), 8) if aes else "",
            "AE_median": round(median([x for x in aes if x is not None]), 8) if aes else "",
            "AE_std": round(pstdev([x for x in aes if x is not None]), 8) if aes else "",
            "AT_mean": round(mean([x for x in ats if x is not None]), 8) if ats else "",
            "AC_mean": round(mean([x for x in acs if x is not None]), 8) if acs else "",
            "tempo_total_s": round(sum([x for x in tempos if x is not None]), 6) if tempos else "",
            "tempo_mean_s": round(mean([x for x in tempos if x is not None]), 6) if tempos else "",
            "tempo_median_s": round(median([x for x in tempos if x is not None]), 6) if tempos else "",
            "gens_mean": "",
            "stop_reason_best": best.get("stop_reason", "") if best else "",
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        })
    return out


def gerar_comparacao(ilp_rows: List[Dict[str, Any]], ga_summary_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    ilp_idx: Dict[Tuple[str, int], Dict[str, Any]] = {}
    for r in ilp_rows:
        try:
            ilp_idx[(str(r.get("projeto")), int(r.get("team_size_testado")))] = r
        except Exception:
            pass

    out: List[Dict[str, Any]] = []
    for g in ga_summary_rows:
        try:
            key = (str(g.get("projeto")), int(g.get("team_size_testado")))
        except Exception:
            continue
        i = ilp_idx.get(key, {})
        ilp_ae = to_float(i.get("AE"))
        ga_ae = to_float(g.get("best_AE"))
        ilp_time = to_float(i.get("tempo_s"))
        ga_total_time = to_float(g.get("tempo_total_s"))
        ga_mean_time = to_float(g.get("tempo_mean_s"))

        dif = ""
        gap = ""
        winner_quality = ""
        if ilp_ae is not None and ga_ae is not None and ilp_ae != 0:
            dif_val = ilp_ae - ga_ae
            # Sign preserved: a negative gap means the GA beat the ILP
            # incumbent. Previously clamped to 0.0 here, which silently
            # hid GA wins from gap_pct and from any aggregate built on it.
            gap_val = 100.0 * dif_val / ilp_ae
            dif = round(dif_val, 8)
            gap = round(gap_val, 6)
            if abs(dif_val) <= 1e-5:
                winner_quality = "EMPATE"
            elif dif_val > 0:
                winner_quality = "ILP"
            else:
                # May occur because of search, evaluator, or numerical ties; this is not evidence against ILP.
                winner_quality = "GA_MAIOR_VALOR_REPORTADO"

        speed_total = ""
        speed_mean = ""
        winner_time = ""
        if ilp_time is not None and ga_total_time is not None and ga_total_time > 0:
            speed_total = round(ilp_time / ga_total_time, 6)
            winner_time = "GA_30_SEEDS" if ga_total_time < ilp_time else "ILP"
        if ilp_time is not None and ga_mean_time is not None and ga_mean_time > 0:
            speed_mean = round(ilp_time / ga_mean_time, 6)

        out.append({
            "projeto": key[0],
            "project_name": g.get("project_name", i.get("project_name", "")),
            "team_size_testado": key[1],
            "ilp_status": i.get("status", ""),
            "ilp_AE": i.get("AE", ""),
            "ilp_AT": i.get("AT", ""),
            "ilp_AC": i.get("AC", ""),
            "ilp_team": i.get("equipe", ""),
            "ilp_tempo_s": i.get("tempo_s", ""),
            "ilp_mip_gap_pct": i.get("mip_gap_pct", ""),
            "ilp_sofreu": i.get("ilp_sofreu", ""),
            "ga_best_AE": g.get("best_AE", ""),
            "ga_best_AT": g.get("best_AT", ""),
            "ga_best_AC": g.get("best_AC", ""),
            "ga_best_team": g.get("best_team", ""),
            "ga_best_seed": g.get("best_seed", ""),
            "ga_tempo_total_s": g.get("tempo_total_s", ""),
            "ga_tempo_mean_s": g.get("tempo_mean_s", ""),
            "ga_n_runs": g.get("n_runs", ""),
            "dif_ILP_GA": dif,
            "gap_pct": gap,
            "speedup_best_of_n": speed_total,
            "speedup_execucao_media": speed_mean,
            "winner_quality": winner_quality,
            "winner_time_total": winner_time,
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        })
    return out


def gerar_resumo_por_k(ilp_rows: List[Dict[str, Any]], ga_summary_rows: List[Dict[str, Any]], comp_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    ks = sorted({int(r.get("team_size_testado")) for r in ilp_rows + ga_summary_rows if str(r.get("team_size_testado", "")).isdigit()})
    out: List[Dict[str, Any]] = []
    for k in ks:
        ilp_k = [r for r in ilp_rows if str(r.get("team_size_testado")) == str(k)]
        ga_k = [r for r in ga_summary_rows if str(r.get("team_size_testado")) == str(k)]
        comp_k = [r for r in comp_rows if str(r.get("team_size_testado")) == str(k)]
        ilp_times = [to_float(r.get("tempo_s")) for r in ilp_k if to_float(r.get("tempo_s")) is not None]
        ga_times_project = [to_float(r.get("tempo_total_s")) for r in ga_k if to_float(r.get("tempo_total_s")) is not None]
        ga_times_run = [to_float(r.get("tempo_mean_s")) for r in ga_k if to_float(r.get("tempo_mean_s")) is not None]
        gaps = [to_float(r.get("gap_pct")) for r in comp_k if to_float(r.get("gap_pct")) is not None]
        ilp_hard = [r for r in ilp_k if is_true(r.get("ilp_sofreu"))]

        out.append({
            "team_size_testado": k,
            "n_projects": max(len(ilp_k), len(ga_k)),
            "ilp_optimal_count": sum(1 for r in ilp_k if str(r.get("status")) == "Optimal"),
            "ilp_feasible_count": sum(1 for r in ilp_k if str(r.get("status", "")).startswith("Feasible")),
            "ilp_hard_count": len(ilp_hard),
            "ilp_time_total_s": round(sum([x for x in ilp_times if x is not None]), 6) if ilp_times else "",
            "ilp_time_mean_s": round(mean([x for x in ilp_times if x is not None]), 6) if ilp_times else "",
            "ilp_time_median_s": round(median([x for x in ilp_times if x is not None]), 6) if ilp_times else "",
            "ilp_time_max_s": round(max([x for x in ilp_times if x is not None]), 6) if ilp_times else "",
            "ga_time_total_s": round(sum([x for x in ga_times_project if x is not None]), 6) if ga_times_project else "",
            "ga_time_mean_project_s": round(mean([x for x in ga_times_project if x is not None]), 6) if ga_times_project else "",
            "ga_time_mean_run_s": round(mean([x for x in ga_times_run if x is not None]), 6) if ga_times_run else "",
            "gap_mean_pct": round(mean([x for x in gaps if x is not None]), 6) if gaps else "",
            "gap_max_pct": round(max([x for x in gaps if x is not None]), 6) if gaps else "",
            # Reuse the authoritative per-project classification (winner_quality,
            # computed in gerar_comparacao() from the signed AE difference)
            # instead of re-deriving a tie test here from gap_pct (a percentage,
            # previously also sign-clamped) with the same 1e-5 constant applied
            # at the wrong scale. Having two independent tie tests was the
            # second bug: it both hid GA wins and, separately, excluded some
            # genuine ties whose gap_pct exceeded 1e-5 in percentage terms.
            "ga_equal_ilp_count": sum(1 for r in comp_k if str(r.get("winner_quality")) == "EMPATE"),
            "timestamp": datetime.now().isoformat(timespec="seconds"),
        })
    return out


# =============================================================================
# MAIN
# =============================================================================

def main() -> None:
    args = parse_args()
    script_dir = Path(__file__).resolve().parent
    project_root = Path(args.project_root).resolve()

    if not (project_root / "Algorithms").exists() or not (project_root / "Pipeline").exists():
        raise RuntimeError(f"Invalid project root: {project_root}")

    ilp_module_dir = Path(args.ilp_module_dir).resolve() if args.ilp_module_dir.strip() else (project_root / "Experimento_ILP_STFP_T").resolve()
    target_path = resolve_path(args.target_projects, Path.cwd())
    base_path = Path(args.base_final).resolve() if args.base_final.strip() else (project_root / "Data" / "base_final.json").resolve()
    graph_path = Path(args.graph).resolve() if args.graph.strip() else (project_root / "Data" / "Graph_DB_real.json").resolve()

    output_ilp = resolve_path(args.output_ilp, Path.cwd())
    output_ga_runs = resolve_path(args.output_ga_runs, Path.cwd())
    output_ga_summary = resolve_path(args.output_ga_summary, Path.cwd())
    output_comparison = resolve_path(args.output_comparison, Path.cwd())
    output_k_summary = resolve_path(args.output_k_summary, Path.cwd())

    for p in [target_path, base_path, graph_path]:
        if not p.exists():
            raise FileNotFoundError(f"File not found: {p}")
    if not ilp_module_dir.exists() and not args.skip_ilp:
        raise FileNotFoundError(f"ILP module directory not found: {ilp_module_dir}")

    projetos = carregar_target_projects(target_path)
    project_ids = parse_csv_list(args.projects) if args.projects.strip() else sorted(projetos.keys(), key=lambda x: int(x[1:]) if x.startswith("P") and x[1:].isdigit() else x)
    team_sizes = parse_int_list(args.team_sizes)
    seeds = list(range(1, int(args.seeds) + 1))

    ensure_csv(output_ilp, ILP_FIELDS, restart=args.restart)
    ensure_csv(output_ga_runs, GA_RUN_FIELDS, restart=args.restart)
    ensure_csv(output_ga_summary, GA_SUMMARY_FIELDS, restart=args.restart)
    ensure_csv(output_comparison, COMPARISON_FIELDS, restart=args.restart)
    ensure_csv(output_k_summary, K_SUMMARY_FIELDS, restart=args.restart)

    # ---------------------------------------------------------------------
    # AUTOMATIC RESUME
    # ---------------------------------------------------------------------
    # Without --restart, the script reads existing CSV files and skips
    # completed combinations. This allows it to continue after a power
    # outage, computer shutdown, or manual interruption.
    completed_ilp = set()
    completed_ga = set()

    if not args.restart:
        for r in load_csv_rows(output_ilp):
            pid_r = str(r.get("projeto", "")).strip()
            k_r = str(r.get("team_size_testado", "")).strip()
            status_r = str(r.get("status", "")).strip()
            if pid_r and k_r.isdigit() and status_r:
                # Any recorded row is considered complete for resume purposes.
                # To rerun it, use --restart or manually delete the row/CSV.
                completed_ilp.add((pid_r, int(k_r)))

        for r in load_csv_rows(output_ga_runs):
            pid_r = str(r.get("projeto", "")).strip()
            k_r = str(r.get("team_size_testado", "")).strip()
            seed_r = str(r.get("seed", "")).strip()
            status_r = str(r.get("status", "")).strip()
            if pid_r and k_r.isdigit() and seed_r.isdigit() and status_r:
                completed_ga.add((pid_r, int(k_r), int(seed_r)))

        print(f"[RESUME] ILP combinations already completed in CSV: {len(completed_ilp)} project/k combination(s)")
        print(f"[RESUME] GA runs already completed in CSV: {len(completed_ga)} project/k/seed run(s)")

    print("\n" + "#" * 78)
    print("# ILP vs. GA SCALABILITY BENCHMARK")
    print(f"# Project root     : {project_root}")
    print(f"# ILP module dir   : {ilp_module_dir}")
    print(f"# Target projects  : {target_path}")
    print(f"# Developer base   : {base_path}")
    print(f"# Graph            : {graph_path}")
    print(f"# Projects         : {', '.join(project_ids)}")
    print(f"# Team sizes       : {team_sizes}")
    print(f"# GA seeds         : {seeds}")
    print(f"# ILP time limit   : {args.ilp_time_limit}s per project/k")
    print("#" * 78 + "\n")

    ilp = None
    devs = []
    ac_medios = {}
    grafo_ilp = {}
    if not args.skip_ilp:
        print("[LOAD] Importing ILP and loading developer base/graph...")
        ilp = importar_ilp(project_root, ilp_module_dir)
        devs = ilp.carregar_base(str(base_path), None)
        grafo = ilp.carregar_grafo(str(graph_path))
        ac_medios = ilp.calcular_ac_medios(devs, grafo)
        grafo_ilp = ilp.preparar_grafo_ilp(devs, grafo)
        print(f"[LOAD] ILP ready | developers={len(devs)} | ilp_edges={len(grafo_ilp)}\n")

    engine = None
    if not args.skip_ga:
        print("[LOAD] Importing engine.py and selecting the surrogate evaluator...")
        engine = importar_engine(project_root, base_path, graph_path)
        print("[LOAD] GA ready\n")

    ilp_desativado_para_maiores = False

    # -------------------------------------------------------------------------
    # Main loop
    # -------------------------------------------------------------------------
    for k in team_sizes:
        print("\n" + "=" * 78)
        print(f"TESTED TEAM SIZE k={k}")
        print("=" * 78)

        ilp_rows_k: List[Dict[str, Any]] = []
        ga_rows_k: List[Dict[str, Any]] = []

        for pid in project_ids:
            if pid not in projetos:
                print(f"[WARNING] {pid} is missing from target_projects. Skipping.")
                continue

            projeto = clone_project_with_k(projetos[pid], k)
            print(f"\n--- {pid} | {projeto.get('name', '')} | k={k} ---")

            # ILP
            key_ilp = (pid, int(k))
            if not args.skip_ilp and not ilp_desativado_para_maiores:
                if key_ilp in completed_ilp:
                    print(f"[ILP] {pid} k={k} already exists in {output_ilp.name}. Skipping.")
                else:
                    print(f"[ILP] Running {pid}, k={k}...")
                    row_ilp = rodar_ilp_uma_instancia(
                        ilp=ilp,
                        projeto=projeto,
                        devs=devs,
                        ac_medios=ac_medios,
                        grafo_ilp=grafo_ilp,
                        k=k,
                        time_limit=int(args.ilp_time_limit),
                    )
                    append_csv(output_ilp, ILP_FIELDS, row_ilp)
                    completed_ilp.add(key_ilp)
                    ilp_rows_k.append(row_ilp)
                    print(
                        f"[ILP] {pid} k={k} status={row_ilp.get('status')} "
                        f"AE={row_ilp.get('AE', '-')} time={row_ilp.get('tempo_s', '-')}s "
                        f"gap={row_ilp.get('mip_gap_pct', '-')}")
            elif args.skip_ilp:
                pass
            else:
                print(f"[ILP] Skipped for k={k}: ILP was already hard at a previous k.")

            # GA
            if not args.skip_ga:
                for seed in seeds:
                    key_ga = (pid, int(k), int(seed))
                    if key_ga in completed_ga:
                        print(f"[GA] {pid} k={k} seed={seed} already exists in {output_ga_runs.name}. Skipping.")
                        continue

                    print(f"[GA] {pid} k={k} seed={seed}...")
                    row_ga = rodar_ga_uma_vez(
                        engine=engine,
                        projeto=projeto,
                        k=k,
                        config=GA_CALIBRADO_CCC,
                        seed=seed,
                    )
                    append_csv(output_ga_runs, GA_RUN_FIELDS, row_ga)
                    completed_ga.add(key_ga)
                    ga_rows_k.append(row_ga)
                    print(
                        f"[GA] {pid} k={k} seed={seed} status={row_ga.get('status')} "
                        f"AE={row_ga.get('AE', '-')} time={row_ga.get('tempo_s', '-')}s")

        # Regenerate cumulative summaries after each k.
        all_ga_rows = load_csv_rows(output_ga_runs)
        all_ilp_rows = load_csv_rows(output_ilp)
        ga_summary = gerar_resumo_ga(all_ga_rows)
        ensure_csv(output_ga_summary, GA_SUMMARY_FIELDS, restart=True)
        for r in ga_summary:
            append_csv(output_ga_summary, GA_SUMMARY_FIELDS, r)

        comparison = gerar_comparacao(all_ilp_rows, ga_summary)
        ensure_csv(output_comparison, COMPARISON_FIELDS, restart=True)
        for r in comparison:
            append_csv(output_comparison, COMPARISON_FIELDS, r)

        k_summary = gerar_resumo_por_k(all_ilp_rows, ga_summary, comparison)
        ensure_csv(output_k_summary, K_SUMMARY_FIELDS, restart=True)
        for r in k_summary:
            append_csv(output_k_summary, K_SUMMARY_FIELDS, r)

        # Optional criterion to avoid spending time on larger k values.
        if args.stop_ilp_after_hard_k and ilp_rows_k:
            hard_count = sum(1 for r in ilp_rows_k if is_true(r.get("ilp_sofreu")))
            if hard_count == len(ilp_rows_k):
                ilp_desativado_para_maiores = True
                print(f"\n[STOP-ILP] All projects at k={k} were hard or non-optimal. ILP will be skipped for larger k values.")

    print("\n" + "=" * 78)
    print("BENCHMARK COMPLETED")
    print("=" * 78)
    print(f"CSV ILP        : {output_ilp}")
    print(f"CSV GA runs    : {output_ga_runs}")
    print(f"CSV GA summary : {output_ga_summary}")
    print(f"CSV comparison : {output_comparison}")
    print(f"CSV k summary  : {output_k_summary}")


if __name__ == "__main__":
    main()
