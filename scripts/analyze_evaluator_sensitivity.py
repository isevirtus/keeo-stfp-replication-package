#!/usr/bin/env python3
"""Reproduce fixed-candidate aggregation sensitivity with the standard library.

This is an independent implementation of the documented analysis, not the
original experiment script. It rescales no features and performs no GA search.
"""
from __future__ import annotations

import argparse
import csv
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path

from analyze_decision_fidelity import average_ranks, pearson

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/v2/evaluator_sensitivity'


def read(path):
    with path.open(encoding='utf-8', newline='') as stream:
        return list(csv.DictReader(stream))


def rho(left, right):
    return pearson(average_ranks(left), average_ranks(right))


def score(at, ac, weight):
    return (weight * min(at, ac) + max(at, ac)) / (weight + 1)


def top_indices(values, count):
    # Python's stable sort preserves input-record order for exactly equal scores.
    return sorted(range(len(values)), key=values.__getitem__, reverse=True)[:count]


def quantile(values, fraction):
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lo, hi = math.floor(position), math.ceil(position)
    return ordered[lo] + (ordered[hi] - ordered[lo]) * (position - lo)


def analyze():
    records = read(DATA / 'inputs.csv')
    assert len(records) == 960
    assert len({r['sample_id'] for r in records}) == 960
    assert len({r['candidate_id'] for r in records}) == 726
    assert Counter(r['generator'] for r in records) == {'GA_before':480,'GA_corrected':480}
    grouped = defaultdict(list)
    for r in records:
        at, ac = float(r['AT_final']), float(r['AC_final'])
        assert 0 <= at <= 1 and 0 <= ac <= 1
        assert r['candidate_id'].startswith(r['project'] + '-T')
        grouped[r['project']].append(r)
    assert set(grouped) == {f'P{i}' for i in range(1,17)}
    for project, group in grouped.items():
        assert len(group) == 60
        for generator in ['GA_before','GA_corrected']:
            assert sorted(int(r['seed']) for r in group if r['generator']==generator) == list(range(1,31))

    at = [float(r['AT_final']) for r in records]
    ac = [float(r['AC_final']) for r in records]
    means = [(a+c)/2 for a,c in zip(at,ac)]
    weighted = {w:[score(a,c,w) for a,c in zip(at,ac)] for w in [1,3,5,7,9]}
    by_sample = {r['sample_id']:i for i,r in enumerate(records)}
    per_team, per_project, diagnostics = [], [], []
    same_counts = Counter()
    shared_best_counts = Counter()
    for project, group in grouped.items():
        indices = [by_sample[r['sample_id']] for r in group]
        a = [means[i] for i in indices]
        b = [weighted[5][i] for i in indices]
        ra, rb = average_ranks(a), average_ranks(b)
        ta, tb = set(top_indices(a,5)), set(top_indices(b,5))
        overlap = len(ta & tb)
        per_project.append(dict(project=project,n=len(group),spearman=rho(a,b),
            top5_overlap_count=overlap,top5_overlap_rate=overlap/5))
        diagnostics.append(dict(project=project,unique_candidates=len({r['candidate_id'] for r in group}),
            mean_top_tie_records=sum(x==max(a) for x in a),
            mix_top_tie_records=sum(x==max(b) for x in b)))
        for j,r in enumerate(group):
            per_team.append(dict(sample_id=r['sample_id'],project=project,generator=r['generator'],
                seed=int(r['seed']),candidate_id=r['candidate_id'],
                AT_final=float(r['AT_final']),AC_final=float(r['AC_final']),
                AE_mean=a[j],AE_mixminmax_w5=b[j],diferenca_media_menos_mixminmax=a[j]-b[j],
                rank_mean_in_project=ra[j],rank_mixminmax_in_project=rb[j],
                top5_mean=j in ta,top5_mixminmax=j in tb))
        base_top = top_indices(b,1)[0]
        best_base = {group[j]['candidate_id'] for j,x in enumerate(b) if abs(x-max(b))<=1e-12}
        for w in weighted:
            scores = [weighted[w][i] for i in indices]
            same_counts[w] += top_indices(scores,1)[0] == base_top
            best_w = {group[j]['candidate_id'] for j,x in enumerate(scores) if abs(x-max(scores))<=1e-12}
            shared_best_counts[w] += bool(best_w & best_base)

    global_rows = []
    for name,values in [('Mean',means),('MIXMINMAX 5:1',weighted[5])]:
        stats = dict(n=len(values),mean=statistics.mean(values),std_sample=statistics.stdev(values),
            min=min(values),q1=quantile(values,.25),median=statistics.median(values),
            q3=quantile(values,.75),max=max(values))
        global_rows.extend(dict(scope='evaluator',evaluator=name,metric=k,value=v) for k,v in stats.items())
    comparisons = dict(spearman_global=rho(means,weighted[5]),
        top5_overlap_average_count=statistics.mean(r['top5_overlap_count'] for r in per_project),
        top5_overlap_average_rate=statistics.mean(r['top5_overlap_rate'] for r in per_project))
    global_rows.extend(dict(scope='comparison',evaluator='both',metric=k,value=v) for k,v in comparisons.items())
    global_rows.append(dict(scope='validation',evaluator='MIXMINMAX 5:1',
        metric='max_abs_error_vs_AE_compressed',
        value=max(abs(weighted[5][i]-float(r['AE_recorded_v2'])) for i,r in enumerate(records))))
    weight_rows = [dict(weight_min=w,weight_max=1,mean=statistics.mean(weighted[w]),
        std_sample=statistics.stdev(weighted[w]),spearman_vs_w5=rho(weighted[w],weighted[5]),
        top1_same_projects=same_counts[w],top1_same_rate=same_counts[w]/16) for w in weighted]
    # This additional tie-aware diagnostic is separate from the original selection statistic.
    assert dict(same_counts) == dict(shared_best_counts)
    result = {'per_team.csv':per_team,'project_summary.csv':per_project,
        'global_summary.csv':global_rows,'weight_sensitivity.csv':weight_rows,
        'candidate_diagnostics.csv':diagnostics}
    return result


def verify():
    computed = analyze()
    for filename, rows in computed.items():
        if filename == 'candidate_diagnostics.csv':
            continue
        expected = read(DATA / filename)
        assert len(rows) == len(expected), filename
        for actual, reference in zip(rows,expected):
            assert set(actual) == set(reference), filename
            for key,value in actual.items():
                if isinstance(value,bool):
                    assert str(value) == reference[key], (filename,key)
                elif isinstance(value,(int,float)):
                    tolerance = 1e-25 if key=='value' and actual.get('scope')=='validation' else 1e-11
                    assert math.isclose(value,float(reference[key]),rel_tol=0,abs_tol=tolerance), (filename,key,value,reference[key])
                else:
                    assert value == reference[key], (filename,key)
    # Regression cases guard weighting direction and stable exact-score ties.
    assert math.isclose(score(.2,.8,5),.3,abs_tol=1e-15)
    assert score(.4,.4,9)==.4
    assert top_indices([.7,.7,.6],1)==[0]
    assert average_ranks([.7,.7,.6])==[1.5,1.5,3.0]
    return computed


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,default=ROOT/'reproduced/evaluator_sensitivity')
    args=parser.parse_args()
    if __debug__ is False:
        raise SystemExit('Run without -O: verification assertions must be enabled.')
    outputs=verify()
    args.output_dir.mkdir(parents=True,exist_ok=True)
    for filename,rows in outputs.items():
        with (args.output_dir/filename).open('w',encoding='utf-8',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    print('Verified 960 fixed-candidate records, 16 projects, and five aggregation weights.')


if __name__=='__main__':
    main()
