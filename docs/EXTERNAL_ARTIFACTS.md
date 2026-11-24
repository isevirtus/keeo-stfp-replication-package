# Commit-pinned external artifacts

Some evidence referenced by the manuscript remains in companion repositories.
The links below identify immutable repository commits, and the SHA-256 values
allow a downloaded file to be checked against the artifact inspected while
preparing package version 1.3.1.

| Artifact | Purpose | Commit-pinned URL | SHA-256 |
|---|---|---|---|
| Direct-LLM baseline workbook | Stored-value computational evidence for the retained LLM teams | [05_RQ4_Algorithmic_Baselines.xlsx](https://github.com/isevirtus/stfp-thesis-replication-package/blob/b517b544c845d37dc5a3f2aa82f33623328e1220/06_baselines_algoritmicos/05_RQ4_Algorithmic_Baselines.xlsx) | `f517bc0c83f5f8f3a30cb60430907d9d426d62bf1440d5f8b9e8622b17f6c5f7` |
| STFP MILP formulation | Detailed formulation and linearization record | [STFP_MILP_Formulation.pdf](https://github.com/Felipeomc/expert-guided-stfp-seip-2027-supplementary-material/blob/0f35a500da440d6c66f4d1cd1a849f59e296a8e6/STFP_MILP_Formulation.pdf) | `3bf4f02a5d989c8c931a3c42e50f690f4f618b0591160af6ed1e00f6be3806c1` |
| Historical-profile availability manifest | Project-level profile-availability and denominator record | [09_Historical_Profile_Availability.csv](https://github.com/Felipeomc/expert-guided-stfp-seip-2027-supplementary-material/blob/0f35a500da440d6c66f4d1cd1a849f59e296a8e6/09_Historical_Profile_Availability.csv) | `42054873ece034eb261e43df8c85a7af6772f1f93014b44621e088214dbb91e1` |

Commit-pinned URLs prevent later branch edits from silently changing the cited
files, but long-term availability still depends on GitHub. A tagged archival
release or repository DOI remains preferable for final publication.

The linked workbook stores its summary and underlying records as values. It
should be treated as an evidence workbook, not as a formula-driven independent
recalculation of the reported baseline.
