# Data dictionary

## Shared identifiers and scores

| Field | Meaning |
|---|---|
| `projeto` / `project_id` | De-identified project label, P1-P12. |
| `team_size_testado` / `team_size_k` | Required number of selected profiles. |
| `AT` / `ilp_AT` / `ga_best_AT` | Technical adequacy. |
| `AC` / `ilp_AC` / `ga_best_AC` | Collaboration adequacy. |
| `AE` / `ilp_AE` / `ga_best_AE` | Overall adequacy optimized by the GA and MILP. |
| `seed` / `ga_best_seed` | Integer random seed. Released V1 RQ3 run records use seeds 1-30; V2 scalability summaries preserve best_seed only; full per-run seed records are not released. |
| `tempo_s` / `*_time_s` | Wall-clock elapsed time in seconds. |
| `status` / `ilp_status` | GA execution status or solver status. Only exact `Optimal` certifies the combined MILP result. |
| `mip_gap_pct` | Reported solver diagnostic in percent. It is not the GA optimality gap; V2 branch diagnostics are not global AE gaps (see below). |

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

## V2 baseline, refinement, and aggregate fields

Blank numeric fields mean unavailable, never zero. The top-level
`optimization_summary.csv` separates three non-overlapping strata; it does
not pool their means.

| Field | Meaning |
|---|---|
| `knowledge_version` | Policy version, distinct from a software revision. |
| `evidence_level` | `reported_aggregate` for the original B0 k=4 baseline; `instance_summary_recomputed` for the two scalability series. |
| `stratum` | `k4` (B0 baseline), `b0_scalability`, or `b1_scalability`. |
| `candidate_pool_size` | 510 (B0) or 1000 (B1). |
| `unique_projects` | 12 recurring contexts, not independent projects per configuration. |
| `team_sizes` | Explicit semicolon-delimited set; B0 scalability excludes 11. |
| `k_min` / `k_max` | Minimum/maximum, not a claim that every intervening size was tested. |
| `configurations` | Project/team-size combinations within one pool. |
| `ga_runs_per_configuration` | 30 repeated runs used for best-of-30 quality. |
| `ga_runs` / `ga_feasible_runs` | Recorded total and hard-Must-feasible runs. |
| `milp_certified` / `milp_feasible_uncertified` | Optimal combined statuses versus feasible values without a certificate. |
| `ga_matches_returned_milp` | Best-of-30 score matches; not necessarily certified optimum hits. |
| `milp_returned_higher` / `ga_returned_higher` | Counts from the signed AE comparison. |
| `mean_absolute_AE_difference` | Mean absolute difference in AE units, not percent. |
| `mean_relative_gap_pct` / `max_relative_gap_pct` | Gaps to certified optima for the reported B0 k=4 baseline only. |
| `max_relative_gap_project` | De-identified baseline project with greatest reported relative gap. |
| `milp_mean_time_per_project_s` / `ga_mean_time_per_run_s` | Baseline timing aggregates; single-run GA time is not the best-of-30 cost. |
| `original_elicitation_scenarios` / `preference_relations` | Six original scenarios, 14 preference relations; individual cases not released. |
| `satisfied_preference_relations` | 13 for V1 and 14 for V2. |
| `reported_fit_error` | Recorded calibration error; no more specific metric name is inferred. |
| `parameter` / `value` / `status` | Reported coefficient and its precision/availability status. |

## V2 scalability input summaries

Each `data/v2/scalability_b0/` or `scalability_b1/` folder contains:

- `ilp_results.csv`: one returned MILP result per project/team-size.
- `ga_summary.csv`: one recorded 30-run GA summary per project/team-size.
- `comparison.csv`: joined, recomputed score comparison and diagnostics.
- `summary.csv`: overall pool/experiment aggregate.
- `team_size_summary.csv` (B0 only): the same measures for each tested k.

| Input field | Meaning |
|---|---|
| `project`, `team_size_tested` | Project P1–P12 and tested team size; together form the within-pool key. |
| `metodo` | Original method label (ILP); the paper uses MILP for the mathematical formulation. |
| `status` | Combined solver status with branch outcomes where applicable. |
| `AT`, `AC_original`, `AC_after_compression`, `AE` | MILP solution's technical, original collaboration, V2 collaboration, and final scores. |
| `time_s` | MILP invocation duration, including both branches. |
| `mip_gap_pct`, `best_bound` | Literal internal branch diagnostics, **not global AE gap/bound**. Do not compare best_bound directly to final AE. |
| `must_dom_ok`, `must_eco_ok`, `must_ling_ok`, `all_must_ok` | Recorded hard-requirement checks by technical dimension and jointly. |
| `ilp_suffered` | Source diagnostic flag; preserved, not used as a certification criterion. |
| `n_runs`, `n_valid_runs`, `valid_rate` | Recorded GA run and feasibility counts/rate. |
| `best_AE`, `best_AT`, `best_AC` | Best GA solution's scores; AC uses the V2 compressed scale. |
| `best_seed`, `best_time_s`, `stop_reason_best` | Recorded best run's seed, duration, and stopping reason. |
| `AE_mean`, `AE_median`, `AE_std` | Recorded within-configuration GA score summaries; SD is not recomputed from raw runs. |
| `AT_mean`, `AC_mean` | Recorded run-mean component scores. |
| `time_total_s`, `time_mean_s`, `time_median_s` | Sum, mean and median of 30 GA run durations; no time SD is supplied. |

## V2 derived comparison and summary fields

| Derived field | Meaning |
|---|---|
| `pool`, `candidate_pool_size`, `team_size_k`, `knowledge_version` | Explicit experiment/version keys. |
| `milp_status`, `milp_certified` | Original status and 1 only for exact Optimal. |
| `milp_AE`, `ga_best_AE` | Score pair at released precision. |
| `signed_AE_difference` | MILP minus GA; negative values are preserved. |
| `absolute_AE_difference` | Absolute score difference. |
| `signed_relative_difference_pct` | 100 times signed difference divided by returned MILP AE; not an optimality gap for uncertified results. |
| `comparison` | TIE if absolute difference <=1e-5; otherwise MILP_HIGHER or GA_HIGHER. |
| `ga_AE_mean`, `ga_AE_median`, `ga_AE_std` | Recorded within-configuration GA summaries. |
| `ga_runs`, `ga_valid_runs` | Configuration counts. |
| `milp_time_s`, `ga_mean_time_s`, `ga_total_time_s` | MILP invocation, mean GA run, and all 30 GA run durations in seconds. |
| `runtime_review_required` | 1 for B0 P10/k=8, the material nominal-budget exception; not an automatic exclusion. |
| `milp_time_mean_s`, `milp_time_median_s` | Across-configuration MILP duration summaries. |
| `ga_time_mean_per_run_s`, `ga_time_mean_30_runs_s` | Mean per-configuration GA run mean and 30-run total. |
| `ga_mean_AE_across_instances` | Mean of recorded within-configuration score means, not a measure of task effectiveness. |
| `ga_within_instance_std_median/min/max` | Summary of recorded GA score SDs, not a pooled SD. |
| `mean_signed_relative_difference_pct` | Signed relative differences averaged without truncation. |
| `max_absolute_AE_difference` | Largest observed absolute difference within the stratum. |

See [V2_SCALABILITY.md](V2_SCALABILITY.md) for precision, bounds and protocol
exceptions; [REPRODUCIBILITY.md](REPRODUCIBILITY.md) for the artifact boundary.

## De-identification

Selected-team IDs and project descriptions were removed before publication.
