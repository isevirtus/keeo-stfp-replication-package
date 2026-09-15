#!/usr/bin/env python3
"""Validate and render separate V2 baseline and scalability summaries."""
from __future__ import annotations
import argparse
import csv
from decimal import Decimal
from pathlib import Path
from analyze_v2_scalability import analyze

ROOT = Path(__file__).resolve().parents[1]
COUNT_FIELDS = (
    'configurations', 'milp_certified', 'milp_feasible_uncertified',
    'ga_matches_returned_milp', 'milp_returned_higher', 'ga_returned_higher',
    'ga_feasible_runs', 'ga_runs',
)

def read_csv(path):
    with path.open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))

def load_and_validate():
    data = read_csv(ROOT / 'data/v2/optimization_summary.csv')
    assert [r['stratum'] for r in data] == ['k4', 'b0_scalability', 'b1_scalability']
    _, summaries, _ = analyze()
    seen = set()
    for row in data:
        assert row['knowledge_version'] == 'V2' and int(row['unique_projects']) == 12
        sizes = {int(k) for k in row['team_sizes'].split(';')}
        keys = {(int(row['candidate_pool_size']), k) for k in sizes}
        assert not (seen & keys)
        seen.update(keys)
        assert int(row['configurations']) == 12 * len(sizes)
        assert int(row['ga_runs']) == 30 * int(row['configurations'])
        assert int(row['ga_feasible_runs']) == int(row['ga_runs'])
        assert int(row['milp_certified']) + int(row['milp_feasible_uncertified']) == int(row['configurations'])
        assert sum(int(row[f]) for f in ('ga_matches_returned_milp','milp_returned_higher','ga_returned_higher')) == int(row['configurations'])
        if row['stratum'] == 'k4':
            assert row['evidence_level'] == 'reported_aggregate'
            assert tuple(int(row[f]) for f in COUNT_FIELDS) == (12,12,0,9,3,0,360,360)
        else:
            assert row['evidence_level'] == 'instance_summary_recomputed'
            expected = summaries[row['stratum'][:2]]
            assert all(int(row[f]) == expected[f] for f in COUNT_FIELDS)
            assert abs(Decimal(row['mean_absolute_AE_difference']) - expected['mean_absolute_AE_difference']) < Decimal('1e-12')
    # Arithmetic totals only: rows differ in evidence granularity and design.
    return data, {f: sum(int(r[f]) for r in data) for f in COUNT_FIELDS}

def render(data):
    headers = ['Pool / team sizes', 'Instances', 'Certified', 'GA ties', 'MILP higher', 'GA higher', 'Valid GA runs', 'Mean abs. AE difference']
    labels = ['510 / k=4 (RQ3 baseline)', '510 / k=5–10,12 (RQ4)', '1000 / k=4 (RQ4)']
    body = []
    for label,r in zip(labels,data):
        body.append([label,r['configurations'],r['milp_certified'],r['ga_matches_returned_milp'],r['milp_returned_higher'],r['ga_returned_higher'],r['ga_feasible_runs']+'/'+r['ga_runs'],f"{float(r['mean_absolute_AE_difference']):.5f}"])
    note = ('The k=4 B0 baseline is a reported aggregate. Both scalability rows are recomputed from '
            'released instance summaries. The same 12 project contexts recur; the rows are not '
            'independent project samples. GA quality is best-of-30. B1 has no certificates. '
            'No pooled quality or runtime mean is inferred across strata.')
    md = '# V2 optimization summary\n\n'+note+'\n\n'
    md += '| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'
    md += ''.join('| '+' | '.join(row)+' |\n' for row in body)
    tex = '% '+note+'\n\\begin{table}[htbp]\n\\centering\n\\scriptsize\n'
    tex += '\\caption{Separate V2 baseline and scalability summaries. Scores use best-of-30 GA results; B1 comparisons are with uncertified incumbents.}\n'
    tex += '\\label{tab:v2-package-summary}\n\\begin{tabular}{lrrrrrrr}\n\\hline\n'
    tex += 'Pool / sizes & N & Cert. & Ties & MILP higher & GA higher & Valid & Mean diff. \\\\\n\\hline\n'
    for row in body:
        tex += ' & '.join(s.replace('–','--') for s in row)+' \\\\\n'
    tex += '\\hline\n\\end{tabular}\n\\end{table}\n'
    return md,tex

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,default=ROOT/'reproduced/v2')
    args=parser.parse_args()
    data,_=load_and_validate()
    md,tex=render(data)
    args.output_dir.mkdir(parents=True,exist_ok=True)
    for name,content in [('optimization_table.md',md),('optimization_table.tex',tex)]:
        (args.output_dir/name).write_text(content,encoding='utf-8',newline='\n')
    print('Verified separate V2 baseline and scalability rows: 12, 84, and 12 configurations.')
    print('This reproduces released analyses, not the original optimization runs.')

if __name__=='__main__':
    main()
