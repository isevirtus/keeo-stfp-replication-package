# Staffing-LLM provenance

The staffing-LLM condition was executed on August 27, 2026 in three separate
temporary chats through the ChatGPT web interface. The interface displayed the
model label `GPT-5.6 Sol` and `High` reasoning mode. This label is interface
metadata, not an immutable API model identifier.

Each execution used the same zero-shot prompt and graph-aligned pseudonymized
inputs: developer profiles, collaboration evidence, neutral project
requirements, and required team sizes. The task requested feasible teams that
prioritized mandatory technologies, then optional technologies and prior
collaboration. GA and MILP outputs and the evaluator scoring formula were
withheld.

The predefined selection rule retained the first complete, structurally valid
response in full before evaluator scoring or practitioner judgment. Response 1
was retained, response 2 contained invalid JSON and was discarded in full, and
response 3 was valid but unused. The same 16 teams from response 1 were used in
the practitioner revalidation and the separate industrial computational
comparison; the LLM was not rerun for the human condition.

An earlier condition was excluded because the supplied history could expose or
reconstruct membership in target-project historical teams. For the replacement
condition, 91 direct links to the 16 target projects were removed from 78
profiles. The collaboration graph remained available, so this control mitigates
specified direct leakage rather than removing all retrospective information.

## Repetition boundary

The prompt and three raw responses were reported as preserved locally but are
not included in this release. Temporary-chat session identifiers and hidden
interface configuration are unavailable. Consequently, the package documents
the retained condition but cannot support exact LLM repetition or measurement
of across-session uncertainty.
