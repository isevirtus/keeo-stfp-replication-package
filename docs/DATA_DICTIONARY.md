# Data dictionary

## Shared identifiers and scores

| Field | Meaning |
|---|---|
| `projeto` / `project_id` | De-identified project label, P1-P12. |
| `team_size_testado` / `team_size_k` | Required number of selected profiles. |
| `AT` / `ilp_AT` / `ga_best_AT` | Technical adequacy. |
| `AC` / `ilp_AC` / `ga_best_AC` | Collaboration adequacy. |
| `AE` / `ilp_AE` / `ga_best_AE` | Overall adequacy optimized by the GA and MILP. |
| `seed` / `ga_best_seed` | Integer random seed. Final repeated-run studies use seeds 1-30. |
| `tempo_s` / `*_time_s` | Wall-clock elapsed time in seconds. |
| `status` / `ilp_status` | GA execution status or solver status. Only exact `Optimal` certifies the combined MILP result. |
| `mip_gap_pct` | Final MILP relative MIP gap in percent. It is not the GA optimality gap. |

## GA configuration fields

| Field | Meaning |
|---|---|
| `population_size` | Number of individuals per generation. |
| `generations` | Maximum number of complete generations after initialization. |
| `elitism_count` | Number of elite individuals retained. |
| `mutation_rate` | Configured mutation probability. |
| `crossover_rate` | Configured crossover probability. |
| `stable_gens` | Early-stopping patience in generations without improvement. |
| `crossover_operator` | Crossover operator identifier. |
| `best_generation` | Generation in which the run-best solution was first observed. |
| `gens_executed` | Number of executed generations. |
| `stop_reason` | Recorded stopping condition. |

## Comparison fields

| Field | Meaning |
|---|---|
| `raw_AE_difference_ILP_minus_GA` | `AE_ILP - AE_GA`; the sign is preserved. |
| `signed_difference_pct` | `100 * (AE_ILP - AE_GA) / AE_ILP`. |
| `absolute_difference_pct` | Absolute value of `signed_difference_pct`. |
| `reported_comparison` | `TIE`, `ILP_REPORTED_HIGHER`, or `GA_REPORTED_HIGHER`. |
| `ilp_optimal_certified` | True only when the complete MILP result has status exactly `Optimal`. |

`GA_REPORTED_HIGHER` must not be interpreted as exceeding the optimum when the MILP result is uncertified.

## Surrogate runtime fields

| Field | Meaning |
|---|---|
| `condition` | One of the four evaluator/search combinations described in the README. |
| `project` | De-identified project label P1-P5. |
| `round` | Consecutive timing round, 1-5. |
| `time_s` | Wall-clock time for exactly 210 evaluator calls. |
| `ms_per_evaluation` | Condition mean divided by 210, expressed in milliseconds. |

## Fidelity fields

| Field | Meaning |
|---|---|
| `brier_score` | Mean squared error between the surrogate and BN probability distributions. |
| `mae_expected_score` | Mean absolute difference between expected adequacy scores. |
| `n` | Number of evaluated scenarios or sampled teams. |
| `missing_teacher_rows` | Teacher evaluations unavailable in the end-to-end set. |

## De-identification

Selected-team IDs and project descriptions were removed before publication. `best_team_synthetic_membership.csv` retains only whether a recorded B1 run-best team contained a synthetic profile and the corresponding count.

