# KEEO semantic traceability audit

This document records the post-construction audit of the semantic-to-executable
artifact chain used in the STFP instantiation. It is a documentary audit of the
controlled elicitation records and executable specifications; it is not an
independent user study of whether new analysts apply the definitions
consistently.

## Audit units and criteria

The audit covered eight elicited constructs: DA, ED, LP, AT, AC, AE, OSF, and
SLF. For every construct, the audit checked:

1. an explicit decision-oriented definition;
2. the complete five-state ordinal domain (VL, L, M, H, and VH);
3. state-specific characteristics;
4. at least one state-specific example;
5. a documented disposition in the knowledge specification;
6. a direct route to the run-time evaluator, or an explicit non-operational disposition;
7. a route to the optimization objective when operational; and
8. the evidence exposed in the recommendation record when operational.

The source elicitation specifications contain one characteristics block and one
worked example for each of the five states of every construct. The technology
taxonomy was audited separately for classification rules, boundary cases, and
recorded refinements.

## Results

All eight constructs have a definition, five ordinal anchors, five
characteristics blocks, and five worked examples. This gives 40 state-specific
characteristics blocks and 40 state-specific examples. All eight constructs
have a documented disposition, but only six have operational end-to-end traces:
DA, ED, LP, AT, AC, and AE. OSF and SLF were considered in a parameterized
experimental compatibility branch using synthetic inputs. They are absent
from the organizational records and are not consumed by the operational
collaboration graph, team evaluator, or optimizer. They must not be counted as
indirect operational inputs.

The five direct relations in the V1 BN reference implementation are preserved in
the V1 analytical surrogate: DA->AT, ED->AT, LP->AT, AT->AE, and AC->AE. The audit
also identified explicit construct narrowing. In particular, the semantic AT
and AC rubrics contain properties that are broader than the available
technical-profile and collaboration-history indicators. The operational graph
uses shared-project count N and the expert-defined transformation f(N), not
structured OSF or SLF observations. These exclusions are recorded rather than
presented as full construct coverage.

The authoritative artifact in KEEO is the versioned knowledge specification,
not the BN. The BN realizes V1; its surrogate is an optional alternative
implementation. V2 changes the technical-priority rules and AC scale, and is
implemented directly by a lightweight evaluator. See
[`KNOWLEDGE_VERSIONS.md`](KNOWLEDGE_VERSIONS.md) for the change-impact record.

The technology taxonomy contains three role-based classification rules, three
worked boundary cases, and one recorded category refinement. The refinement
split a broad Desktop category into Desktop-Standalone and Desktop-Client after
the elicitation exercises exposed an architectural distinction relevant to
technological proximity.

The machine-readable audit and aggregate counts are in
`data/keeo_traceability/semantic_traceability_audit.csv` and
`data/keeo_traceability/semantic_traceability_summary.csv`.

## Interpretation boundary

The audit establishes documentary completeness and explicit traceability for
this instantiation. It does not establish inter-rater semantic stability,
multi-expert agreement, adoption, or downstream project effectiveness.
