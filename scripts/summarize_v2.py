#!/usr/bin/env python3
"""Render V2 reported aggregates; this is not a raw-run reanalysis."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COUNT_FIELDS = (
    "configurations", "milp_certified", "milp_feasible_uncertified",
    "ga_matches_returned_milp", "milp_returned_higher", "ga_returned_higher",
    "ga_feasible_runs", "ga_runs",
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def load_and_validate() -> tuple[list[dict[str, str]], dict[str, int]]:
    data = read_csv(ROOT / "data/v2/optimization_summary.csv")
    assert [row["stratum"] for row in data] == ["k4", "k5_to_10"]
    covered_sizes: set[int] = set()
    for row in data:
        assert row["knowledge_version"] == "V2"
        assert row["evidence_level"] == "reported_aggregate"
        assert int(row["candidate_pool_size"]) == 510
        assert int(row["unique_projects"]) == 12
        sizes = set(range(int(row["k_min"]), int(row["k_max"]) + 1))
        assert sizes and not covered_sizes.intersection(sizes)
        covered_sizes.update(sizes)
        counts = {key: int(row[key]) for key in COUNT_FIELDS}
        assert all(value >= 0 for value in counts.values())
        assert counts["configurations"] == 12 * len(sizes)
        assert int(row["ga_runs_per_configuration"]) == 30
        assert counts["ga_runs"] == 30 * counts["configurations"]
        assert counts["ga_feasible_runs"] == counts["ga_runs"]
        assert counts["milp_certified"] + counts["milp_feasible_uncertified"] == counts["configurations"]
        assert sum(counts[key] for key in (
            "ga_matches_returned_milp", "milp_returned_higher", "ga_returned_higher"
        )) == counts["configurations"]
    assert covered_sizes == set(range(4, 11))
    totals = {key: sum(int(row[key]) for row in data) for key in COUNT_FIELDS}
    assert totals == dict(zip(COUNT_FIELDS, (84, 82, 2, 64, 20, 0, 2520, 2520)))
    return data, totals


def render(data: list[dict[str, str]], totals: dict[str, int]) -> tuple[str, str]:
    table = []
    for row in data:
        label = "4" if row["stratum"] == "k4" else "5--10"
        table.append([
            label, row["configurations"], row["milp_certified"],
            row["milp_feasible_uncertified"], row["ga_matches_returned_milp"],
            row["milp_returned_higher"], f"{row['ga_feasible_runs']}/{row['ga_runs']}",
            row["mean_absolute_AE_difference"],
        ])
    table.append([
        "Total", str(totals["configurations"]), str(totals["milp_certified"]),
        str(totals["milp_feasible_uncertified"]), str(totals["ga_matches_returned_milp"]),
        str(totals["milp_returned_higher"]),
        f"{totals['ga_feasible_runs']}/{totals['ga_runs']}", "---",
    ])
    headers = ["Team size", "Configurations", "Certified", "Feasible uncertified",
               "GA matches", "MILP higher", "Valid GA runs", "Mean abs. AE difference"]
    note = ("Reported V2 aggregates on 510 candidates. The same 12 projects occur in both "
            "strata; k=4 is the RQ3 baseline reused in RQ4. Matches concern returned MILP "
            "values, not necessarily certified optima. No pooled mean is computed "
            "from rounded stratum means. GA quality uses the best of 30 runs.")
    markdown = "# V2 optimization summary\n\n" + note + "\n\n"
    markdown += "| " + " | ".join(headers) + " |\n"
    markdown += "| " + " | ".join(["---"] * len(headers)) + " |\n"
    for row in table:
        markdown += "| " + " | ".join(row) + " |\n"

    runtime = read_csv(ROOT / "data/v2/runtime_summary.csv")[0]
    ilp_time = float(runtime["milp_mean_time_per_project_s"])
    ga_time = float(runtime["ga_mean_time_per_run_s"])
    batch = ga_time * int(runtime["ga_runs_per_project"])
    markdown += (f"\nFor k=4, the reported means are {ilp_time:.1f} s per MILP project "
                 f"and {ga_time:.2f} s per GA run (ratio {ilp_time / ga_time:.2f}). "
                 f"Thirty sequential GA runs imply approximately {batch:.1f} s from "
                 "the rounded mean; this is not a measured batch runtime.\n")
    latex = "% Generated from reported aggregates, not individual runs.\n"
    latex += "\\begin{table}[htbp]\n\\centering\n\\small\n"
    latex += "\\caption{" + note.replace("k=4", "$k=4$") + "}\n"
    latex += "\\label{tab:v2-package-summary}\n"
    latex += "\\begin{tabular}{lrrrrrrr}\n\\hline\n"
    latex += "k & Instances & Certified & Uncertified & Matches & MILP higher & Valid runs & Mean diff. \\\\\n\\hline\n"
    for row in table:
        latex += " & ".join(row) + " \\\\\n"
    latex += "\\hline\n\\end{tabular}\n\\end{table}\n"
    return markdown, latex


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "reproduced/v2")
    args = parser.parse_args()
    data, totals = load_and_validate()
    markdown, latex = render(data, totals)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, content in (("optimization_table.md", markdown), ("optimization_table.tex", latex)):
        (args.output_dir / name).write_text(content, encoding="utf-8", newline="\n")
    print("Rendered reported V2 aggregates: 84 configurations, 82 certificates, 64 matches, 2520 valid GA runs.")
    print("This verifies aggregation arithmetic; it does not reproduce the original V2 experiment.")


if __name__ == "__main__":
    main()
