#!/usr/bin/env python3
"""Regenerate ILP-versus-GA comparison and summary tables from public CSV files.

This script uses only the Python standard library. It preserves the sign of
ILP-minus-GA differences and applies the same absolute raw-AE tie tolerance
used in the paper (1e-5 by default).
"""

from __future__ import annotations

import argparse
import csv
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


COMPARISON_FIELDS = [
    "project_id",
    "team_size_k",
    "ilp_status",
    "ilp_optimal_certified",
    "ilp_AE",
    "ilp_AT",
    "ilp_AC",
    "ilp_time_s",
    "ilp_mip_gap_pct",
    "ga_best_AE",
    "ga_best_AT",
    "ga_best_AC",
    "ga_best_seed",
    "ga_total_time_s",
    "ga_mean_time_per_run_s",
    "ga_n_runs",
    "raw_AE_difference_ILP_minus_GA",
    "signed_difference_pct",
    "absolute_difference_pct",
    "reported_comparison",
]

SUMMARY_FIELDS = [
    "dataset",
    "n_projects",
    "ilp_optimal_certified_count",
    "tie_count",
    "ilp_reported_higher_count",
    "ga_reported_higher_count",
    "mean_signed_difference_pct",
    "mean_absolute_difference_pct",
    "max_absolute_difference_pct",
    "ga_total_time_s",
    "ga_mean_time_per_project_s",
    "ga_mean_time_per_run_s",
]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_rows(path: Path, fields: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def project_order(project_id: str) -> int:
    return int(project_id[1:])


def classify(ilp_ae: float, ga_ae: float, tolerance: float) -> tuple[str, float, float]:
    raw_difference = ilp_ae - ga_ae
    signed_pct = 100.0 * raw_difference / ilp_ae
    if abs(raw_difference) <= tolerance:
        outcome = "TIE"
    elif raw_difference > 0:
        outcome = "ILP_REPORTED_HIGHER"
    else:
        outcome = "GA_REPORTED_HIGHER"
    return outcome, signed_pct, abs(signed_pct)


def regenerate(
    ilp_rows: list[dict[str, str]],
    ga_rows: list[dict[str, str]],
    dataset_label: str,
    tolerance: float,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    grouped: dict[tuple[str, int], list[dict[str, str]]] = defaultdict(list)
    for row in ga_rows:
        team_size = int(row.get("team_size_testado") or 4)
        if row.get("status") == "OK" and row.get("AE") not in (None, ""):
            grouped[(row["projeto"], team_size)].append(row)

    comparison: list[dict[str, Any]] = []
    for ilp in sorted(
        ilp_rows,
        key=lambda row: (project_order(row["projeto"]), int(row.get("team_size_testado") or 4)),
    ):
        project_id = ilp["projeto"]
        team_size = int(ilp.get("team_size_testado") or 4)
        runs = grouped[(project_id, team_size)]
        if not runs:
            raise ValueError(f"No valid GA runs for {project_id}, k={team_size}")
        best = max(runs, key=lambda row: float(row["AE"]))
        ilp_ae = float(ilp["AE"])
        ga_ae = float(best["AE"])
        outcome, signed_pct, absolute_pct = classify(ilp_ae, ga_ae, tolerance)
        times = [float(row["tempo_s"]) for row in runs]
        comparison.append(
            {
                "project_id": project_id,
                "team_size_k": team_size,
                "ilp_status": ilp.get("status", ""),
                "ilp_optimal_certified": str(ilp.get("status", "")).strip() == "Optimal",
                "ilp_AE": ilp_ae,
                "ilp_AT": ilp.get("AT", ""),
                "ilp_AC": ilp.get("AC", ""),
                "ilp_time_s": ilp.get("tempo_s", ""),
                "ilp_mip_gap_pct": ilp.get("mip_gap_pct", ""),
                "ga_best_AE": ga_ae,
                "ga_best_AT": best.get("AT", ""),
                "ga_best_AC": best.get("AC", ""),
                "ga_best_seed": best.get("seed", ""),
                "ga_total_time_s": round(sum(times), 6),
                "ga_mean_time_per_run_s": round(statistics.mean(times), 6),
                "ga_n_runs": len(runs),
                "raw_AE_difference_ILP_minus_GA": round(ilp_ae - ga_ae, 10),
                "signed_difference_pct": round(signed_pct, 6),
                "absolute_difference_pct": round(absolute_pct, 6),
                "reported_comparison": outcome,
            }
        )

    outcomes = Counter(row["reported_comparison"] for row in comparison)
    signed = [float(row["signed_difference_pct"]) for row in comparison]
    absolute = [float(row["absolute_difference_pct"]) for row in comparison]
    total_ga_time = sum(float(row["ga_total_time_s"]) for row in comparison)
    total_ga_runs = sum(int(row["ga_n_runs"]) for row in comparison)
    summary = {
        "dataset": dataset_label,
        "n_projects": len(comparison),
        "ilp_optimal_certified_count": sum(
            str(row["ilp_optimal_certified"]).lower() == "true" for row in comparison
        ),
        "tie_count": outcomes["TIE"],
        "ilp_reported_higher_count": outcomes["ILP_REPORTED_HIGHER"],
        "ga_reported_higher_count": outcomes["GA_REPORTED_HIGHER"],
        "mean_signed_difference_pct": round(statistics.mean(signed), 6),
        "mean_absolute_difference_pct": round(statistics.mean(absolute), 6),
        "max_absolute_difference_pct": round(max(absolute), 6),
        "ga_total_time_s": round(total_ga_time, 6),
        "ga_mean_time_per_project_s": round(total_ga_time / len(comparison), 6),
        "ga_mean_time_per_run_s": round(total_ga_time / total_ga_runs, 6),
    }
    return comparison, summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ilp", required=True, type=Path, help="Public ILP CSV")
    parser.add_argument("--ga-runs", required=True, type=Path, help="Public GA run-level CSV")
    parser.add_argument("--dataset-label", required=True)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--tie-tolerance", type=float, default=1e-5)
    args = parser.parse_args()

    comparison, summary = regenerate(
        read_rows(args.ilp),
        read_rows(args.ga_runs),
        args.dataset_label,
        args.tie_tolerance,
    )
    write_rows(args.output_dir / "comparison.csv", COMPARISON_FIELDS, comparison)
    write_rows(args.output_dir / "summary.csv", SUMMARY_FIELDS, [summary])
    print(f"Wrote {len(comparison)} comparisons to {args.output_dir}")


if __name__ == "__main__":
    main()
