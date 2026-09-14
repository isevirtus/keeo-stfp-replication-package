# Data dictionary

## Shared identifiers and scores

| Field | Meaning |
|---|---|
| `projeto` / `project_id` | De-identified project label, P1-P12. |
| `team_size_testado` / `team_size_k` | Required number of selected profiles. |
| `AT` / `ilp_AT` / `ga_best_AT` | Technical adequacy. |
| `AC` / `ilp_AC` / `ga_best_AC` | Collaboration adequacy. |
| `AE` / `ilp_AE` / `ga_best_AE` | Overall adequacy optimized by the GA and MILP. |
| `seed` / `ga_best_seed` | Integer random seed. Released V1 RQ3 run records use seeds 1-30; exact V2 seeds are not released. |
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

## Decision-level fidelity fields

| Field | Meaning |
|---|---|
| `candidate_id` | Project-local de-identified identifier for one sampled candidate team. It does not encode team membership. |
| `teacher_score` / `surrogate_score` | Expected AE produced by the V1 reference BN and V1 analytical surrogate, rounded to six decimals in the public file. |
| `spearman_rho` | Spearman rank correlation between BN and surrogate scores within one project. |
| `pairwise_order_agreement` | Proportion of non-tied candidate pairs ordered in the same direction by both evaluators. |
| `top10_overlap_rate` / `top20_overlap_rate` | Intersection divided by 10 or 20 for the evaluator-specific highest-ranked candidate sets. |
| `shared_top_candidate` | Whether the BN and surrogate maximal-score sets share at least one candidate. |
| `teacher_regret_surrogate_top` | BN-best score minus the BN score assigned to the surrogate-selected candidate. |

## Semantic traceability fields

| Field | Meaning |
|---|---|
| `semantic_definition` | Whether the controlled elicitation record defines the construct's decision meaning. |
| `five_state_anchors` | Whether VL, L, M, H, and VH are all explicitly anchored. |
| `knowledge_specification_path` | Relation or explicit experimental-only disposition in the knowledge specification; replaces the misleading legacy field name `authoritative_model_path`. |
| `evaluator_path` | Direct operational relation, or `not_operational` for an excluded construct. |
| `trace_status` | `direct` for the six operational constructs; `explicit_non_operational` for OSF and SLF. |
| `residual_boundary` | Construct or operationalization boundary retained by the audit. |

## V2 aggregate fields

Files in `data/v2/` contain reported aggregates and parameters, not individual
observations. Blank numeric fields mean unavailable, never zero.

| Field | Meaning |
|---|---|
| `knowledge_version` | Policy version, distinct from the evaluator's software revision. |
| `evidence_level` | `reported_aggregate`: transcribed study-level values; not re-estimated from public raw runs. |
| `stratum` | `k4` or `k5_to_10`; disjoint configurations over the same 12 projects. |
| `candidate_pool_size` | 510 organization-derived developer profiles. |
| `unique_projects` | 12 in each stratum and 12 in their union, not 24. |
| `k_min` / `k_max` | Inclusive required team-size range. |
| `configurations` | Number of project/team-size combinations, not independent projects. |
| `ga_runs_per_configuration` / `ga_runs_per_project` | 30 repeated runs used to select the best GA score. |
| `ga_runs` / `ga_feasible_runs` | Total and hard-Must-feasible GA runs in the stratum. |
| `milp_certified` / `milp_feasible_uncertified` | Complete optimality certificates versus feasible values without a certificate. |
| `ga_matches_returned_milp` | Reported best-of-30 matches to the returned MILP value; not all necessarily certified optimum hits. |
| `milp_returned_higher` / `ga_returned_higher` | Reported comparison counts; no run-level reclassification is possible here. |
| `mean_absolute_AE_difference` | Mean absolute score difference in raw AE units, not percent. |
| `mean_relative_gap_pct` / `max_relative_gap_pct` | Relative gap in percent to certified optima for `k4` only. |
| `max_relative_gap_project` | De-identified project with the maximum reported `k4` relative gap. |
| `milp_mean_time_per_project_s` | Mean single MILP solution time for the size-four project instances. |
| `ga_mean_time_per_run_s` | Mean time of one GA run, not best-of-30 batch time. |
| `original_elicitation_scenarios` / `preference_relations` | Six original scenarios implying 14 reported preference relations; individual cases not released. |
| `satisfied_preference_relations` | Reported relation coverage, 13 for V1 and 14 for V2. |
| `reported_fit_error` | Reported numerical fitting error; metric definition not supplied, so no metric name is inferred. |
| `parameter` / `value` / `status` | Parameter name, reported value when available, and its precision/availability status. |

The two optimization stratum counts can be summed. Rounded mean differences
must not be pooled to fabricate a full-series mean. See
[`REPRODUCIBILITY.md`](REPRODUCIBILITY.md) for interpretation and remaining artifacts.

## De-identification

Selected-team IDs and project descriptions were removed before publication.
