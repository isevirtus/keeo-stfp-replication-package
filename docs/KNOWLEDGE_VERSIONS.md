# Knowledge versions and refinement evidence

KESO makes the versioned knowledge specification authoritative. A Bayesian
network (BN), a lightweight evaluator, and an optimization model are realizations
of that specification; their software versions must be recorded separately.

## Two different changes

| Transition | What changes | Evidence in this package |
|---|---|---|
| V1 BN to V1 surrogate | Executable representation; the V1 policy remains the reference | RQ1 pointwise and decision fidelity; RQ2 evaluator-call runtime |
| V1 to V2 | Technical-priority semantics, useful Must redundancy levels, and AC scale | Change-impact record below, reported preference-order aggregates, and V2 GA/MILP baseline and configuration-level scalability summaries |

The V1 surrogate is optional. Keeping the V1 BN is a supported design choice.
V2 was implemented with a lightweight evaluator by choice, not because its
knowledge changes require abandoning a BN. A BN could encode V2, but no
executed V2 BN-versus-surrogate equivalence or runtime experiment is released
here. V1 approximation accuracy must not be attributed to V2.

## Optimizer choice is a separate decision

The selected knowledge version defines the objective and feasibility rules.
A GA, an exact MILP solver, or another compatible engine can optimize that
specification. Either GA or MILP can supply the recommendation directly;
running both is optional. A MILP formulation is not an evolutionary algorithm,
and a time-limited exact-solver invocation may return a feasible incumbent
without certifying optimality. Optimizer selection and configuration do not
change the policy version unless the represented objective or constraints change.

The GA/MILP experiments assess the implementations used in this study. They
do not evaluate every engine permitted by the KESO process. BN/surrogate
fidelity and optimizer solution quality are distinct questions.

## Change-impact record

| Change | Diagnostic observation | V2 rule | Affected artifacts | Validation evidence |
|---|---|---|---|---|
| AT priority composition and Must redundancy | In V1, increasing Should coverage reduced the Could contribution through a `(1 - cS)` interaction | Independent Must-gated Should and Could terms; distinguish Must redundancy at two and three members; retain four-member redundancy with zero weight | Coverage specification, feature calculation, evaluator, GA fitness, MILP formulation, recommendation explanations | Same six elicited scenarios: 13/14 orderings in V1, 14/14 in V2; nonnegative coefficients support coordinatewise monotonicity |
| AC operational scale | AC spanned a broader observed range than AT and could introduce implicit weighting in AE | `AC_V2 = 0.5 + 0.5 * (AC_V1 - 0.5)` | AC transformation, evaluator, MILP coefficients and bounds, reported score decomposition | Order-preserving global transformation, unchanged center, half the original distances; V2 optimization re-evaluation |

Concrete-team review provided diagnostic evidence. The AT coefficients were
recalibrated against the **same original six MoSCoW scenarios**, not fitted to
later pairwise team choices. The reported numerical fitting error increased
from 0.00170 to 0.00353 while preference-order coverage improved from 13/14 to
14/14. The released record does not define that error precisely enough to
rename it MSE, MAE, or another metric. The individual scenarios, 14 relations,
and calibration outputs are not included; `refinement_summary.csv` records
aggregate evidence, not executable regression cases.

## Technical-priority specification

For each technical dimension, let `cM`, `cS`, and `cC` be the fractions of
Must, Should, and Could requirements covered by at least one team member.
Let `r2M`, `r3M`, and `r4M` be the fractions of Must requirements covered by
at least two, three, and four members. They are cumulative thresholds, not
mutually exclusive counts. With two or more active priorities:

```text
V1 = clamp(b + w2M*r2M + wM*cM + wMS*cM*cS + wC*cM*cC*(1-cS), 0, 1)
V2 = clamp(b + wM*cM + w2M*r2M + w3M*r3M + w4M*r4M
             + wS*cM*cS + wC*cM*cC, 0, 1)
```

The reported V2 coefficients are `wM=0`, `w2M=0.4121`, `w3M=0.2582`,
`w4M=0`, and `wS=wC=0.2308`. Within this formula, increasing `cS` at fixed
other inputs cannot reduce the score: its pre-clamp slope is `wS*cM >= 0`.
Clamping preserves nondecreasing order. This is a property of the stated
formula, not an empirical test of the missing original implementation.

An additional multiplier `max(eta, cM)` applies when Must requirements exist.
The intercept `b`, the floor `eta`, full-precision parameters, single-priority
branch, and empty-requirement conventions must be obtained with the original
V2 implementation before claiming an end-to-end reproduction. Blank parameter
values in `data/v2/parameters.csv` mean unavailable, never zero.

## Collaboration scale and unchanged rules

The global AC transformation maps ordinal centroids
`(0.1, 0.3, 0.5, 0.7, 0.9)` to `(0.3, 0.4, 0.5, 0.6, 0.7)`.
It preserves order and the center, and halves every pairwise score distance.
The original no-history score 0.3 maps to 0.4. Alpha 0.5 was a global
sensitivity variant, not a value estimated from the first validation choices;
it does not imply identical AT and AC distributions.

The technical aggregation remains `AT = (3*DA + ED + 5*LP) / 9`.
The final aggregation remains `AE = (5*min(AT, AC) + max(AT, AC)) / 6`,
using the AC scale of the selected knowledge version. Full Must coverage
remains a hard feasibility condition. A high soft score cannot compensate
for an infeasible team.

The operational collaboration graph is derived from shared-project count
and the expert transformation of that count. OSF and SLF are not operational
graph inputs; see [`SEMANTIC_TRACEABILITY.md`](SEMANTIC_TRACEABILITY.md).
