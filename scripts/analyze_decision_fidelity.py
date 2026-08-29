#!/usr/bin/env python3
"""Analyze ranking- and decision-level fidelity between the BN and surrogate.

The input is the private end-to-end per-team evaluation file. The public
per-team output replaces team membership with a project-local candidate ID.
Only the Python standard library is required.
"""

from __future__ import annotations

import argparse
import csv
import math
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any


PER_TEAM_FIELDS = [
    "project_id",
    "candidate_id",
    "teacher_score",
    "surrogate_score",
    "absolute_error",
]

PROJECT_FIELDS = [
    "project_id",
    "n_candidates",
    "spearman_rho",
    "pairwise_order_agreement",
    "comparable_pairs",
    "shared_top_candidate",
    "teacher_top_tie_count",
    "surrogate_top_tie_count",
    "teacher_rank_of_surrogate_top",
    "surrogate_rank_of_teacher_top",
    "top10_intersection",
    "top10_overlap_rate",
    "top10_jaccard",
    "top20_intersection",
    "top20_overlap_rate",
    "top20_jaccard",
    "teacher_best_score",
    "teacher_score_at_surrogate_top",
    "teacher_regret_surrogate_top",
    "teacher_regret_surrogate_top_pct",
]

SUMMARY_FIELDS = [
    "n_projects",
    "n_candidates",
    "spearman_mean",
    "spearman_min",
    "pairwise_order_agreement_mean",
    "shared_top_candidate_count",
    "top10_overlap_rate_mean",
    "top20_overlap_rate_mean",
    "teacher_regret_mean",
    "teacher_regret_max",
    "teacher_regret_pct_mean",
    "teacher_regret_pct_max",
]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_rows(path: Path, fields: list[str], data: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(data)


def average_ranks(values: list[float], descending: bool = True) -> list[float]:
    order = sorted(range(len(values)), key=values.__getitem__, reverse=descending)
    ranks = [0.0] * len(values)
    start = 0
    while start < len(order):
        end = start + 1
        while end < len(order) and values[order[end]] == values[order[start]]:
            end += 1
        average = ((start + 1) + end) / 2.0
        for index in order[start:end]:
            ranks[index] = average
        start = end
    return ranks


def pearson(left: list[float], right: list[float]) -> float:
    mean_left = statistics.mean(left)
    mean_right = statistics.mean(right)
    numerator = sum((x - mean_left) * (y - mean_right) for x, y in zip(left, right))
    denominator = math.sqrt(
        sum((x - mean_left) ** 2 for x in left)
        * sum((y - mean_right) ** 2 for y in right)
    )
    return numerator / denominator if denominator else 1.0


def pairwise_order_agreement(
    teacher: list[float], surrogate: list[float], tolerance: float = 1e-12
) -> tuple[float, int]:
    concordant = 0
    comparable = 0
    for i in range(len(teacher)):
        for j in range(i + 1, len(teacher)):
            teacher_diff = teacher[i] - teacher[j]
            surrogate_diff = surrogate[i] - surrogate[j]
            if abs(teacher_diff) <= tolerance or abs(surrogate_diff) <= tolerance:
                continue
            comparable += 1
            concordant += (teacher_diff > 0) == (surrogate_diff > 0)
    return concordant / comparable if comparable else 1.0, comparable


def top_set(values: list[float], size: int) -> set[int]:
    return set(sorted(range(len(values)), key=values.__getitem__, reverse=True)[:size])


def top_overlap(teacher: list[float], surrogate: list[float], size: int) -> tuple[int, float, float]:
    teacher_top = top_set(teacher, size)
    surrogate_top = top_set(surrogate, size)
    intersection = len(teacher_top & surrogate_top)
    union = len(teacher_top | surrogate_top)
    return intersection, intersection / size, intersection / union


def analyze(input_path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in read_rows(input_path):
        grouped[row["project_id"]].append(row)

    public_rows: list[dict[str, Any]] = []
    project_rows: list[dict[str, Any]] = []
    for project_id in sorted(grouped, key=lambda value: int(value[1:])):
        source = grouped[project_id]
        teacher = [float(row["AE_teacher_mean"]) for row in source]
        surrogate = [float(row["AE_sur_mean"]) for row in source]
        teacher_ranks = average_ranks(teacher)
        surrogate_ranks = average_ranks(surrogate)
        spearman = pearson(teacher_ranks, surrogate_ranks)
        pair_agreement, comparable_pairs = pairwise_order_agreement(teacher, surrogate)

        teacher_best = max(range(len(source)), key=teacher.__getitem__)
        surrogate_best = max(range(len(source)), key=surrogate.__getitem__)
        teacher_top = {index for index, score in enumerate(teacher) if score == teacher[teacher_best]}
        surrogate_top = {
            index for index, score in enumerate(surrogate) if score == surrogate[surrogate_best]
        }
        regret = teacher[teacher_best] - teacher[surrogate_best]
        regret_pct = 100.0 * regret / teacher[teacher_best]
        top10 = top_overlap(teacher, surrogate, 10)
        top20 = top_overlap(teacher, surrogate, 20)

        project_rows.append(
            {
                "project_id": project_id,
                "n_candidates": len(source),
                "spearman_rho": round(spearman, 6),
                "pairwise_order_agreement": round(pair_agreement, 6),
                "comparable_pairs": comparable_pairs,
                "shared_top_candidate": bool(teacher_top & surrogate_top),
                "teacher_top_tie_count": len(teacher_top),
                "surrogate_top_tie_count": len(surrogate_top),
                "teacher_rank_of_surrogate_top": round(teacher_ranks[surrogate_best], 3),
                "surrogate_rank_of_teacher_top": round(surrogate_ranks[teacher_best], 3),
                "top10_intersection": top10[0],
                "top10_overlap_rate": round(top10[1], 6),
                "top10_jaccard": round(top10[2], 6),
                "top20_intersection": top20[0],
                "top20_overlap_rate": round(top20[1], 6),
                "top20_jaccard": round(top20[2], 6),
                "teacher_best_score": round(teacher[teacher_best], 6),
                "teacher_score_at_surrogate_top": round(teacher[surrogate_best], 6),
                "teacher_regret_surrogate_top": round(regret, 6),
                "teacher_regret_surrogate_top_pct": round(regret_pct, 6),
            }
        )

        for index, (teacher_score, surrogate_score) in enumerate(zip(teacher, surrogate), start=1):
            public_rows.append(
                {
                    "project_id": project_id,
                    "candidate_id": f"{project_id}_T{index:03d}",
                    "teacher_score": f"{teacher_score:.6f}",
                    "surrogate_score": f"{surrogate_score:.6f}",
                    "absolute_error": f"{abs(teacher_score - surrogate_score):.6f}",
                }
            )

    summary = {
        "n_projects": len(project_rows),
        "n_candidates": len(public_rows),
        "spearman_mean": round(statistics.mean(float(row["spearman_rho"]) for row in project_rows), 6),
        "spearman_min": round(min(float(row["spearman_rho"]) for row in project_rows), 6),
        "pairwise_order_agreement_mean": round(
            statistics.mean(float(row["pairwise_order_agreement"]) for row in project_rows), 6
        ),
        "shared_top_candidate_count": sum(
            str(row["shared_top_candidate"]).lower() == "true" for row in project_rows
        ),
        "top10_overlap_rate_mean": round(
            statistics.mean(float(row["top10_overlap_rate"]) for row in project_rows), 6
        ),
        "top20_overlap_rate_mean": round(
            statistics.mean(float(row["top20_overlap_rate"]) for row in project_rows), 6
        ),
        "teacher_regret_mean": round(
            statistics.mean(float(row["teacher_regret_surrogate_top"]) for row in project_rows), 6
        ),
        "teacher_regret_max": round(
            max(float(row["teacher_regret_surrogate_top"]) for row in project_rows), 6
        ),
        "teacher_regret_pct_mean": round(
            statistics.mean(float(row["teacher_regret_surrogate_top_pct"]) for row in project_rows), 6
        ),
        "teacher_regret_pct_max": round(
            max(float(row["teacher_regret_surrogate_top_pct"]) for row in project_rows), 6
        ),
    }
    return public_rows, project_rows, summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()

    public_rows, project_rows, summary = analyze(args.input)
    write_rows(args.output_dir / "decision_fidelity_per_team.csv", PER_TEAM_FIELDS, public_rows)
    write_rows(args.output_dir / "decision_fidelity_by_project.csv", PROJECT_FIELDS, project_rows)
    write_rows(args.output_dir / "decision_fidelity_summary.csv", SUMMARY_FIELDS, [summary])
    print(f"Analyzed {len(public_rows)} candidate teams across {len(project_rows)} projects.")


if __name__ == "__main__":
    main()
