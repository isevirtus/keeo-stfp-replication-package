# Changelog

## 1.3.0 — 2026-10-06

- Add fixed-candidate aggregation sensitivity: 960 run-result records, 726
  distinct project–team compositions, 16 project contexts, and five weights.
- Release component scores, opaque project-specific candidate IDs, reported
  per-record outputs, and global/project/weight summaries without memberships.
- Add an independently implemented standard-library analysis and integrate
  row-level, ranking, summary, and tie-diagnostic checks into package verification.
- Document exact-tie conventions, extraction precision, repeated compositions,
  and the distinction between evaluator rescoring and new optimizer experiments.
- Preserve all previous experimental data and the evaluated V1/V2 formulas.

## 1.2.2 — 2026-10-06

- Document the single expert's experience, consultative/shared decision role,
  project-specific ramp-up practices, and further collaboration-policy elicitation.
- Separate support for qualitative rationales from unresolved numerical choices
  and unimplemented refinement proposals.
- Clarify the cautious Low default and distinguish raw, ordinal, and V2 scales.
- Record the reporting boundary around historical external data preparation.
- Preserve the V1/V2 equations, experimental records, and analysis scripts.
- Do not add unverified sensitivity records or imply a new knowledge version.

## 1.2.1 — 2026-09-16

- Rename the method to Knowledge Engineering for Search and Optimization (KESO).
- Update the paper title, package name, citation metadata, and current documentation.
- Clarify that exact and heuristic optimization are context-dependent alternatives;
  the GA and MILP are the evaluated implementations, not required components.
- Distinguish evaluator selection from optimizer selection.
- Preserve all experimental data, numerical results, and analysis code.
- Retain the repository URL and data/keeo_traceability/ paths for compatibility.
- Regenerate the integrity manifest for the intentional documentation changes.

## 1.2.0 — 2026-09-14

- Add V2 configuration-level MILP and GA summaries for 510 candidates at
  k=5,6,7,8,9,10,12 and 1,000 candidates at k=4.
- Recompute score differences, certification, tie counts, GA dispersion, and
  per-size runtimes; retain the separate reported 510-candidate k=4 baseline.
- Confirm the former k=5..10 aggregates from the new instance records; the
  updated B0 scalability series includes k=12, not the baseline k=4.
- Preserve negative differences, including GA's higher returned score on B1/P5.
- Compare best-of-30 quality with the sum of all 30 GA run durations.
- Flag the B0 P10/k=8 duration above the nominal budget and prevent branch
  solver diagnostics from being interpreted as global AE bounds.
- Add reproducible decimal-arithmetic analysis and regression checks.
- Document code, input, individual-run and environment boundaries. Do not
  distribute truncated scripts as complete runnable implementations.
- Keep historical V1 evidence unchanged; no historical V1 B1 experiment is added.


## 1.1.0 — 2026-09-14

- Align the package with the V1/V2 distinction in the KBS manuscript.
- Correct semantic traceability: six operational constructs; OSF and SLF have
  explicit non-operational dispositions, not indirect optimizer traces.
- Add the V1-to-V2 change-impact record, reported V2 coefficients, and
  aggregate preference-order validation results.
- Add primary V2 optimization aggregates for 510 candidates and team sizes
  four through ten, together with a standard-library table generator.
- Distinguish reported aggregates from raw observations, returned-value matches
  from optimality certificates, and single-run time from best-of-30 quality.
- Correct the end-to-end fidelity label to semisynthetic teams.
- Add V2 environment and missing-artifact documentation; preserve historical
  V1 numerical results without relabeling them as V2.
- Add checksum verification and preserve exact checkout bytes across platforms.

The package version identifies this repository revision. It does not indicate
that a permanent archive DOI or formal archival release has been created.
