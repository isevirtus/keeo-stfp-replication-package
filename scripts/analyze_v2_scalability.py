#!/usr/bin/env python3
"""Recompute V2 comparisons from de-identified MILP and GA instance summaries.

This reproduces analysis, not optimization runs. No external dependencies.
"""
from __future__ import annotations

import argparse
import csv
from collections import Counter
from decimal import Decimal
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parents[1]
TOLERANCE = Decimal('0.00001')
D = Decimal


def read(path):
    with Path(path).open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def mean(values):
    values = list(values)
    return sum(values, D(0)) / len(values)


def classify(milp, ga):
    delta = milp - ga
    return 'TIE' if abs(delta) <= TOLERANCE else ('MILP_HIGHER' if delta > 0 else 'GA_HIGHER')


def load_pool(pool):
    folder = ROOT / 'data/v2' / ('scalability_' + pool)
    ilp, ga = read(folder / 'ilp_results.csv'), read(folder / 'ga_summary.csv')
    key = lambda r: (r['project'], int(r['team_size_tested']))
    imap, gmap = {key(r): r for r in ilp}, {key(r): r for r in ga}
    sizes = (5, 6, 7, 8, 9, 10, 12) if pool == 'b0' else (4,)
    expected = {(f'P{p}', k) for p in range(1, 13) for k in sizes}
    assert len(ilp) == len(ga) == len(expected)
    assert set(imap) == set(gmap) == expected
    out = []
    for project, k in sorted(expected, key=lambda x: (x[1], int(x[0][1:]))):
        i, g = imap[project, k], gmap[project, k]
        a, b = D(i['AE']), D(g['best_AE'])
        assert D(0) <= a <= 1 and D(0) <= b <= 1
        assert int(g['n_runs']) == int(g['n_valid_runs']) == 30
        assert i['all_must_ok'].lower() == 'true'
        assert abs(D(g['time_total_s']) / 30 - D(g['time_mean_s'])) <= D('0.000001')
        delta = a - b
        out.append(dict(
            pool=pool.upper(), candidate_pool_size=510 if pool == 'b0' else 1000,
            project=project, team_size_k=k, knowledge_version='V2',
            milp_status=i['status'], milp_certified=int(i['status'] == 'Optimal'),
            milp_AE=a, ga_best_AE=b, signed_AE_difference=delta,
            absolute_AE_difference=abs(delta),
            signed_relative_difference_pct=100 * delta / a,
            comparison=classify(a, b), ga_runs=30, ga_valid_runs=int(g['n_valid_runs']),
            ga_AE_mean=D(g['AE_mean']), ga_AE_median=D(g['AE_median']),
            ga_AE_std=D(g['AE_std']), milp_time_s=D(i['time_s']),
            ga_mean_time_s=D(g['time_mean_s']), ga_total_time_s=D(g['time_total_s']),
            runtime_review_required=int(pool == 'b0' and project == 'P10' and k == 8),
        ))
    return out


def summarize(records, label):
    outcomes = Counter(r['comparison'] for r in records)
    return dict(
        stratum=label, configurations=len(records),
        milp_certified=sum(r['milp_certified'] for r in records),
        milp_feasible_uncertified=sum(1-r['milp_certified'] for r in records),
        ga_matches_returned_milp=outcomes['TIE'], milp_returned_higher=outcomes['MILP_HIGHER'],
        ga_returned_higher=outcomes['GA_HIGHER'],
        ga_runs=sum(r['ga_runs'] for r in records),
        ga_feasible_runs=sum(r['ga_valid_runs'] for r in records),
        mean_absolute_AE_difference=mean(r['absolute_AE_difference'] for r in records),
        max_absolute_AE_difference=max(r['absolute_AE_difference'] for r in records),
        mean_signed_relative_difference_pct=mean(r['signed_relative_difference_pct'] for r in records),
        milp_time_mean_s=mean(r['milp_time_s'] for r in records),
        milp_time_median_s=median(r['milp_time_s'] for r in records),
        ga_time_mean_per_run_s=mean(r['ga_mean_time_s'] for r in records),
        ga_time_mean_30_runs_s=mean(r['ga_total_time_s'] for r in records),
        ga_mean_AE_across_instances=mean(r['ga_AE_mean'] for r in records),
        ga_within_instance_std_median=median(r['ga_AE_std'] for r in records),
        ga_within_instance_std_min=min(r['ga_AE_std'] for r in records),
        ga_within_instance_std_max=max(r['ga_AE_std'] for r in records),
    )


def analyze():
    pools = {p: load_pool(p) for p in ('b0', 'b1')}
    summaries = {p: summarize(rs, p.upper()) for p, rs in pools.items()}
    by_k = [summarize([r for r in pools['b0'] if r['team_size_k'] == k], str(k))
            for k in (5, 6, 7, 8, 9, 10, 12)]
    # Regression checks: preserve signed improvements, non-contiguous size set,
    # uncertified matches, actual runtime anomaly, and prior k=5..10 findings.
    assert classify(D('.5'), D('.50001')) == 'TIE'
    assert classify(D('.5'), D('.5000101')) == 'GA_HIGHER'
    assert classify(D('.5000101'), D('.5')) == 'MILP_HIGHER'
    fields = ('configurations', 'milp_certified', 'ga_matches_returned_milp',
              'milp_returned_higher', 'ga_returned_higher', 'ga_feasible_runs')
    assert tuple(summaries['b0'][f] for f in fields) == (84, 80, 65, 19, 0, 2520)
    assert tuple(summaries['b1'][f] for f in fields) == (12, 0, 9, 2, 1, 360)
    old = summarize([r for r in pools['b0'] if r['team_size_k'] <= 10], 'prior')
    assert tuple(old[f] for f in fields) == (72, 70, 55, 17, 0, 2160)
    assert round(old['mean_absolute_AE_difference'], 4) == D('.0014')
    p5 = next(r for r in pools['b1'] if r['project'] == 'P5')
    assert p5['signed_AE_difference'] == D('-.00352661')
    anomaly = [r for r in pools['b0'] if r['runtime_review_required']]
    assert len(anomaly) == 1 and anomaly[0]['milp_time_s'] == D('14390.14')
    assert sum(r['comparison'] == 'TIE' and not r['milp_certified'] for r in pools['b0']) == 2
    return pools, summaries, by_k


def write_csv(path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(records[0]), lineterminator='\n')
        w.writeheader()
        w.writerows(records)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'reproduced/v2_scalability')
    args = parser.parse_args()
    pools, summaries, by_k = analyze()
    for pool, records in pools.items():
        write_csv(args.output_dir / pool / 'comparison.csv', records)
        write_csv(args.output_dir / pool / 'summary.csv', [summaries[pool]])
    write_csv(args.output_dir / 'b0/team_size_summary.csv', by_k)
    lines = ['# V2 scalability analysis', '',
             'B0: 510 candidates, k=5,6,7,8,9,10,12. B1: 1,000 candidates, k=4.',
             'The separate 510-candidate k=4 RQ3 baseline is not included in these counts.', '',
             '| Pool | Instances | Certified | GA ties | MILP higher | GA higher | Mean abs. AE difference | MILP mean (s) | GA 30-run mean (s) |',
             '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for p, s in summaries.items():
        lines.append(f"| {p.upper()} | {s['configurations']} | {s['milp_certified']} | {s['ga_matches_returned_milp']} | {s['milp_returned_higher']} | {s['ga_returned_higher']} | {s['mean_absolute_AE_difference']:.8f} | {s['milp_time_mean_s']:.2f} | {s['ga_time_mean_30_runs_s']:.2f} |")
    lines += ['', 'Differences are signed MILP minus GA before classification; ties use 1e-5 AE units.',
              'B1 comparisons concern feasible incumbents, not certified optima.',
              'B0 includes the 14,390.14-second P10/k=8 runtime requiring protocol review.',
              'Reported branch-level solver gaps/bounds are not used to infer global AE optimality gaps.',
              'GA quality is best-of-30; GA timing above is the sum of those 30 run durations.',
              'This analysis does not regenerate individual optimization runs.']
    (args.output_dir / 'summary.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
