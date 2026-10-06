# Fixed-candidate aggregation sensitivity

## Question and design

How much does the final aggregation rule change rankings when the candidate
teams and their component scores are held fixed?

The corpus contains 960 historical GA run-result records across 16 project
contexts. For each project there are 30 records from before the technical
correction and 30 from after it, with seeds 1–30 in each generator group.
Both groups were rescored using corrected technical adequacy (AT) and compressed
collaboration adequacy (AC). Team sizes range from four to nine. No GA was rerun
for this sensitivity analysis. Do not merge this corpus with the separate
12-project RQ3/RQ4 experiments or infer its candidate-pool size from identifiers.

The 960 records contain 726 distinct project–team compositions. Repeated
compositions are retained. Each composition has an opaque identifier scoped
to its project; the identifiers preserve duplication information, not membership
or links to people across projects. Developer IDs and team memberships are not
distributed.

## Evaluation and selection rules

For fixed AT and AC:

- Simple mean: M = (AT + AC) / 2.
- MIXMINMAX family: F_w = (w min(AT, AC) + max(AT, AC)) / (w + 1).
- Minimum weights: 1, 3, 5, 7, 9; maximum weight: 1.
- F_1 equals the mean; F_5 is the retained V2 aggregation.
- F_5 = M − |AT − AC| / 3. Its lower mean score is the intended imbalance
  penalty, not evidence that the fixed teams became worse.

Spearman correlation is Pearson correlation of average ranks, using exact
floating-point equality for rank ties. Top-five selection uses descending score
and stable input-record order to break exact ties. Each list contains five
records, potentially including repeated compositions. Overlap is intersection
size divided by five, not Jaccard similarity or distinct-team overlap. Top-one
agreement compares the first selected record to the 5:1 selection within each
project. These conventions reproduce all supplied rank and selection records.

A separate diagnostic uses a 1e-12 absolute score tolerance and asks whether
the best-composition sets have at least one member in common. It returns the
same project counts as the record-selection statistic for these five weights.
It does not make the Top-5 result tie-invariant.

## Files and reproduction

All canonical files are in `data/v2/evaluator_sensitivity/`:

| File | Contents |
|---|---|
| inputs.csv | 960 de-identified records with component scores and recorded V2 AE |
| per_team.csv | Scores, average ranks, and Top-5 membership from the supplied analysis |
| global_summary.csv | Mean/MIXMINMAX distributions, pooled correlation, overlap, and score check |
| project_summary.csv | All 16 within-project correlations and Top-5 intersections |
| weight_sensitivity.csv | All five weight settings and Top-1 comparisons with 5:1 |

Run:

```bash
python scripts/analyze_evaluator_sensitivity.py
python scripts/verify_package.py
```

The analysis writes regenerated CSVs and a candidate/tie diagnostic under
`reproduced/evaluator_sensitivity/`. It checks every canonical row and numeric
summary, not only the headline values. It uses only the Python standard library.

The released script is an independent implementation of this documented
analysis, not the historical analysis script. The supplied spreadsheet stores
numeric observations as strings. During extraction, its three input score
columns were converted with pandas 3.0.1 `to_numeric` and serialized as
round-trip-precision floats. This numerical interpretation reproduces every
reported rank and summary. That extraction dependency is not required to run
the public analysis. Alternative decimal parsers can differ at the final
floating-point bit and alter exact ties; use the released input values and
documented conventions for canonical reproduction. Canonical result values
retain their supplied precision; verification allows 1e-11 absolute rounding
difference for ordinary numeric outputs, but compares ranks/selection fields
against the canonical records and separately checks the machine-precision
score-reproduction diagnostic.

## Results and interpretation

The mean-versus-5:1 pooled Spearman correlation is 0.983975818573, but the mean
within-project correlation is 0.874022, ranging from 0.720157 to 0.967552.
Mean Top-5 intersection is 3.3125 records (66.25%). Six projects retain all
five records; P7 retains one and P9 none. The selected Top-1 record is the
same in seven projects. Maximum absolute error against recorded V2 AE is
1.66533453694e-16.

| Minimum:maximum | Pooled rho versus 5:1 | Same selected Top-1 projects |
|---|---:|---:|
| 1:1 | 0.983976 | 7/16 |
| 3:1 | 0.998862 | 14/16 |
| 5:1 | 1.000000 | 16/16 |
| 7:1 | 0.999686 | 15/16 |
| 9:1 | 0.999257 | 14/16 |

Strong pooled agreement does not establish interchangeable project shortlists.
The tested bottleneck-emphasizing weights are locally stable relative to 5:1,
but the analysis does not identify a uniquely best weight, validate expert
preferences independently, or establish downstream team effectiveness.

The sample is generator-conditioned and includes repeated compositions, not
960 independent observations or a random sample of feasible teams. No
inferential significance or equivalence test is claimed. The study varies
only final aggregation: it does not test the saturation peak, no-history
default, history-specific floor, AC compression, or the effect of weights on
new search trajectories. Reproduction starts from component scores and does
not rerun feature extraction or historical GA executions.
