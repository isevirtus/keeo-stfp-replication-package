#!/usr/bin/env python3
"""Verify the public data package against the article's canonical results."""

from __future__ import annotations

import csv
import math
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOLERANCE = 1e-5


def rows(relative_path: str) -> list[dict[str, str]]:
    with (ROOT / relative_path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def close(actual: float, expected: float, tolerance: float = 1e-6) -> None:
    if not math.isclose(actual, expected, rel_tol=0.0, abs_tol=tolerance):
        raise AssertionError(f"Expected {expected}, found {actual}")


def assert_seed_grid(data: list[dict[str, str]], project_field: str = "projeto") -> None:
    grouped: dict[str, set[int]] = defaultdict(set)
    for row in data:
        grouped[row[project_field]].add(int(row["seed"]))
    assert len(grouped) == 12
    assert all(seeds == set(range(1, 31)) for seeds in grouped.values())


def verify_surrogate() -> None:
    runtime = rows("data/surrogate/runtime_raw.csv")
    assert len(runtime) == 100
    assert Counter(row["condition"] for row in runtime) == {
        "C1_Sur_noGA": 25,
        "C2_Sur_withGA": 25,
        "C3_BN_noGA": 25,
        "C4_BN_withGA": 25,
    }
    overall = {row["condition"]: row for row in rows("data/surrogate/runtime_summary_overall.csv")}
    close(float(overall["C3_BN_noGA"]["mean_s"]) / float(overall["C1_Sur_noGA"]["mean_s"]), 19.69374458)
    close(float(overall["C4_BN_withGA"]["mean_s"]) / float(overall["C2_Sur_withGA"]["mean_s"]), 21.69028457)

    fidelity = {row["phase"]: row for row in rows("data/surrogate/fidelity_summary.csv")}
    assert int(fidelity["Training (calibration)"]["n"]) == 20930
    assert int(fidelity["Controlled holdout"]["n"]) == 5320
    assert int(fidelity["Real teams (end-to-end)"]["n"]) == 1200
    close(float(fidelity["Controlled holdout"]["brier_score"]), 0.015573546099842399, 1e-12)
    close(float(fidelity["Controlled holdout"]["mae_expected_score"]), 0.038542252795535394, 1e-12)
    close(float(fidelity["Real teams (end-to-end)"]["mae_expected_score"]), 0.04956032787614873, 1e-12)

    per_team = rows("data/surrogate/decision_fidelity_per_team.csv")
    by_project = rows("data/surrogate/decision_fidelity_by_project.csv")
    decision = rows("data/surrogate/decision_fidelity_summary.csv")[0]
    assert len(per_team) == 1200 and len(by_project) == 6
    assert all("team" not in row for row in per_team)
    close(float(decision["spearman_mean"]), 0.793942)
    close(float(decision["spearman_min"]), 0.447632)
    close(float(decision["pairwise_order_agreement_mean"]), 0.858523)
    assert int(decision["shared_top_candidate_count"]) == 3
    close(float(decision["top10_overlap_rate_mean"]), 0.8)
    close(float(decision["top20_overlap_rate_mean"]), 0.775)
    close(float(decision["teacher_regret_mean"]), 0.02369)
    close(float(decision["teacher_regret_max"]), 0.060474)


def verify_traceability() -> None:
    audit = rows("data/keeo_traceability/semantic_traceability_audit.csv")
    summary = {
        row["measure"]: (int(row["value"]), int(row["denominator"]))
        for row in rows("data/keeo_traceability/semantic_traceability_summary.csv")
    }
    assert len(audit) == 8
    assert Counter(row["trace_status"] for row in audit) == {
        "direct": 6,
        "documented_indirect": 2,
    }
    assert summary["constructs_with_definition"] == (8, 8)
    assert summary["state_specific_examples"] == (40, 40)
    assert summary["core_authoritative_model_relations_preserved_in_surrogate"] == (5, 5)


def verify_rq3() -> None:
    ilp = rows("data/rq3_exact_vs_ga/ilp.csv")
    ga = rows("data/rq3_exact_vs_ga/ga_runs.csv")
    comparison = rows("data/rq3_exact_vs_ga/comparison.csv")
    summary = rows("data/rq3_exact_vs_ga/summary.csv")[0]
    assert len(ilp) == 12 and len(ga) == 360 and len(comparison) == 12
    assert_seed_grid(ga)
    assert all(row["status"] == "Optimal" for row in ilp)
    outcomes = Counter(row["reported_comparison"] for row in comparison)
    assert outcomes == {"TIE": 8, "ILP_REPORTED_HIGHER": 4}
    close(float(summary["mean_absolute_difference_pct"]), 0.496081)
    close(float(summary["max_absolute_difference_pct"]), 2.26104)

    optimum_by_project = {row["projeto"]: float(row["AE"]) for row in ilp}
    optimum_hits = sum(
        abs(float(row["AE"]) - optimum_by_project[row["projeto"]]) <= TOLERANCE for row in ga
    )
    assert optimum_hits == 73


def verify_b0_scalability() -> None:
    project = rows("data/scalability_b0/project_level.csv")
    summary = rows("data/scalability_b0/team_size_summary.csv")
    assert len(project) == 84 and len(summary) == 7
    assert sum(row["ilp_status"] == "Optimal" for row in project) == 83
    outcomes = Counter(row["winner_quality"] for row in project)
    assert outcomes["TIE"] == 65
    absolute = [abs(float(row["gap_pct"])) for row in project]
    close(sum(absolute) / len(absolute), 0.3221, 5e-5)
    close(max(absolute), 3.961952)
    by_k = {int(float(row["team_size_k"])): row for row in summary}
    close(float(by_k[12]["ilp_time_mean_s"]) / float(by_k[5]["ilp_time_mean_s"]), 14.3168, 5e-4)


def verify_b1_scalability() -> None:
    ilp = rows("data/scalability_b1/ilp.csv")
    ga = rows("data/scalability_b1/ga_runs.csv")
    comparison = rows("data/scalability_b1/comparison.csv")
    summary = rows("data/scalability_b1/summary.csv")[0]
    membership = rows("data/scalability_b1/best_team_synthetic_membership.csv")
    assert len(ilp) == 12 and len(ga) == 360 and len(comparison) == 12 and len(membership) == 360
    assert_seed_grid(ga)
    outcomes = Counter(row["reported_comparison"] for row in comparison)
    assert outcomes == {
        "TIE": 7,
        "ILP_REPORTED_HIGHER": 2,
        "GA_REPORTED_HIGHER": 3,
    }
    close(float(summary["ga_total_time_s"]), 2140.810299)
    close(float(summary["ga_mean_time_per_run_s"]), 5.946695)
    close(float(summary["mean_absolute_difference_pct"]), 1.174941)
    close(float(summary["max_absolute_difference_pct"]), 4.332014)
    assert all(row["best_team_contains_synthetic_profile"].lower() == "false" for row in membership)


def verify_deidentification() -> None:
    forbidden_headers = {"project_name", "equipe", "ilp_team", "ga_best_team", "best_team", "timestamp"}
    for path in (ROOT / "data").rglob("*.csv"):
        with path.open(encoding="utf-8", newline="") as handle:
            header = next(csv.reader(handle))
        overlap = forbidden_headers.intersection(header)
        if overlap:
            raise AssertionError(f"Direct identifiers remain in {path}: {sorted(overlap)}")

    sensitive_patterns = [
        re.compile(r"WLSSecret", re.I),
        re.compile(r"WLSAccessID", re.I),
        re.compile(r"registered to", re.I),
        re.compile(r"[A-Z]:\\\\Users\\\\", re.I),
        re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}"),
    ]
    for path in ROOT.rglob("*"):
        if (
            not path.is_file()
            or path.resolve() == Path(__file__).resolve()
            or ".git" in path.parts
        ):
            continue
        content = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in sensitive_patterns:
            if pattern.search(content):
                raise AssertionError(f"Sensitive pattern {pattern.pattern!r} found in {path}")


def main() -> None:
    verify_surrogate()
    verify_traceability()
    verify_rq3()
    verify_b0_scalability()
    verify_b1_scalability()
    verify_deidentification()
    print("All replication-package checks passed.")


if __name__ == "__main__":
    main()
