# GCAT Capacity Case-Study Evidence Note

## Scope

This note governs the observational federal IT case in:

- `papers/GCAT-BCAT/P14_GCAT_Capacity_Stability_v1.md`

The case is not a calibrated dataset, causal investigation, allegation of wrongdoing, or proof that a GCAT overload condition occurred. It is a first-person operational recollection used to illustrate a falsifiable measurement mapping.

## Provenance Classification

| Statement | Provenance class | Publication treatment | Status |
|---|---|---|---|
| The author worked in IT operations during a Windows deployment and integration effort in a federal medical-center environment. | first-person professional recollection | Attribute to the author; do not imply institutional endorsement. | QUALIFIED |
| Approximately 10 to 15 workstations per week were observed to become unavailable. | first-person quantitative recollection | Use only with an approximation qualifier and no claim of a complete incident census. | QUALIFIED |
| Network time or date mismatch conditions were associated with the observed removals. | first-person diagnostic recollection | Describe as the operationally reported or observed condition, not an independently established root cause. | QUALIFIED |
| Local login was disabled on affected systems. | first-person policy and operational recollection | State as a condition encountered by the author; do not generalize to every system or period. | QUALIFIED |
| Recovery through an Active Directory holding mechanism was discouraged or unavailable in routine practice. | first-person process recollection | Preserve the uncertainty between discouraged and unavailable; do not claim a formal enterprise-wide prohibition without records. | QUALIFIED |
| Reimaging became the operational response. | first-person workflow recollection | State as the response used in the observed work context, not the only technically possible recovery path. | QUALIFIED |
| The recurring incidents consumed deployment and recovery capacity. | analytic inference from the recollected workflow | Present as an interpretation supported by repeated rebuild work, not a measured capacity estimate. | QUALIFIED |
| The incidents limited reconstruction of the preceding workstation state. | analytic inference | Present as a reconstructability limitation in the observed workflow; do not claim forensic impossibility. | QUALIFIED |
| Similar behavior later appeared at another facility after a supervisor transfer. | unsupported for this paper's bounded case | Exclude unless independent records are obtained and reviewed. | EXCLUDED |
| The incidents were connected to criminal, malicious, retaliatory, or coordinated activity. | unsupported allegation | Prohibited. | EXCLUDED |
| The observed environment had more than 10,000 devices. | unsupported scale claim in current record | Exclude unless sourced to a durable institutional record. | EXCLUDED |
| A numerical value of `Omega` can be reconstructed retrospectively. | unsupported quantitative claim | Prohibited because variables and elasticities were not measured. | EXCLUDED |

## Required Case Language

The paper must preserve all of these boundaries:

1. The case is based on the author's first-person recollection.
2. Approximate incident frequency is not a complete incident census.
3. The reported time/date mismatch is not presented as a proven root cause.
4. No malicious activity, wrongdoing, or causal mechanism is alleged.
5. No numerical `Omega`, elasticity, calibration, or viability-kernel result is claimed.
6. The GCAT mapping is qualitative and proposed for future measurement.

## Permitted GCAT Mapping

- `g`: observed investigation, escalation, remediation, and rebuild throughput;
- `c`: encountered authentication, domain-membership, and local-login restrictions;
- `t`: continuity and reconstructability of trusted workstation state in the observed recovery workflow;
- `a`: deployment volume, ordinary operations, and recurring recovery demand.

This mapping is a research hypothesis. It may motivate instrument design but does not establish that the Cobb-Douglas capacity function is correct for the observed environment.

## Evidence Needed for Stronger Claims

A stronger empirical case would require, at minimum:

- incident or ticket records with dates and disposition;
- workstation inventory and deployment-volume records;
- time-synchronization and domain-membership logs;
- documented recovery and escalation policy;
- rebuild duration and staffing records;
- state-reconstruction or forensic-retention evidence;
- a declared normalization and calibration method for `g`, `c`, `t`, and `a`.

## Ownership and Release Condition

Owner: Publisher Issue #6 evidence-review lane.

Release condition: the final manuscript language is checked against this note, and every case statement is either sourced, explicitly attributed as first-person recollection, retained as a bounded analytic inference, or removed.
