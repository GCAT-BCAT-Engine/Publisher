# GCAT Capacity Source Review

## Scope

This record maps each foundational source to the limited claim it may support in:

- `papers/GCAT-BCAT/P14_GCAT_Capacity_Stability_v1.md`
- future LaTeX and PDF derivatives

The source set does **not** validate GCAT empirically. It establishes adjacent theory, terminology, and prior methods against which GCAT must be distinguished.

Bibliography source:

- `papers/GCAT-BCAT/references/gcat_capacity_primary_sources.bib`

## Source-to-Claim Matrix

| Citation key | Domain | Permitted use | Prohibited inference | Verification posture |
|---|---|---|---|---|
| `ames2017cbfqp` | Control barrier functions | Support the relationship between barrier conditions and forward invariance in controlled systems; motivate combining safety constraints with control objectives. | Does not prove that GCAT variables form a valid physical control system or that an admissible GCAT policy exists. | Title, authors, journal, pages, arXiv record, and DOI recorded. |
| `ames2019cbfsurvey` | CBF survey | Support contemporary CBF terminology and the use of barrier functions to verify or enforce safety properties. | Does not establish institutional governance as a CBF application. | Title, authors, conference, pages, arXiv record, and DOI recorded. |
| `xu2018robustcbf` | Robust CBFs | Support the statement that disturbance robustness requires additional assumptions and may preserve only a relaxed invariant set. | Does not provide robustness guarantees for the current GCAT simulation. | Title, authors, journal metadata, arXiv record, and DOI recorded. |
| `aubin1991viability` | Viability theory | Support the distinction between a constraint set and the subset of initial states from which constrained evolution can be maintained. | Does not compute the GCAT viability kernel. | Foundational monograph metadata recorded; edition and ISBN require publication-toolchain confirmation before final submission. |
| `aubin2011viability` | Viability theory | Support viability-kernel and regulation-map language for constrained dynamics. | Does not establish recoverability for any declared GCAT scenario. | Publisher DOI and ISBN recorded; final bibliography check required. |
| `cobb1928production` | Production economics | Support the historical origin of the multiplicative production-function analogy. | Does not justify interpreting governance as empirically Cobb-Douglas or treating elasticities as measured. | Journal, volume, issue, and pages recorded from the original article metadata. |
| `arrow1961ces` | CES production function | Support use of CES as an alternative substitution structure in sensitivity analysis. | Does not select a correct institutional production function for GCAT. | Journal metadata and DOI recorded. |
| `simon1955behavioral` | Bounded rationality | Support the premise that organizational decision processes operate under bounded information and computation. | Does not imply a specific GCAT threshold or execution-pressure law. | Journal metadata and DOI recorded. |
| `vaughan1999darkside` | Organizational failure | Support discussion of mistake, misconduct, disaster, and organizational production of adverse outcomes. | Does not validate the federal IT observation or prove normalization of deviance in that environment. | Journal metadata and DOI recorded. |
| `vaughan1996challenger` | Organizational drift | Support the established Challenger case and normalization-of-deviance framing. | Must not be used to equate the GCAT observational case with Challenger or to infer wrongdoing. | Primary monograph metadata recorded; edition-specific details require final check. |
| `leveson2011safer` | System safety | Support a systems-theoretic view in which losses can arise from inadequate control across a sociotechnical system. | Does not validate GCAT equations, parameters, or simulations. | Publisher and ISBN metadata recorded; final edition check required. |

## Related-Work Structure

The future integrated paper section should make four bounded comparisons.

### 1. Barrier and invariance methods

GCAT adopts the language of a nonnegative margin and a forward-invariance condition. The contribution is not a new general barrier theorem. It is a proposed institutional state mapping whose validity depends on whether its variables, dynamics, controls, and disturbances can be operationalized.

### 2. Viability and recoverability

Viability theory supplies the distinction between being inside a constraint set and having at least one evolution that can remain there. GCAT uses that distinction to separate an admissible state (`Omega <= 1`) from a state recoverable under bounded governance action. The current work does not compute a viability kernel.

### 3. Institutional production functions

The Cobb-Douglas form supplies a compact multiplicative capacity frontier and elasticity interpretation. CES, additive, weighted-geometric, and bottleneck comparators are included because institutional inputs may have different substitution structures. No functional form is presently empirically preferred.

### 4. Organizational decision and failure

Bounded rationality, organizational-error research, and systems-theoretic safety motivate the claim that formal controls can coexist with insufficient operational control capacity. These literatures motivate the problem; they do not validate the GCAT threshold or the observational case mapping.

## Citation Rules

1. Cite primary articles, monographs, or official proceedings in the paper.
2. Do not cite search-result summaries, encyclopedias, or social posts as theoretical authority.
3. Do not describe GCAT as derived from Cobb-Douglas, CBF, viability, bounded rationality, or organizational-failure theory; describe it as a synthesis and proposed application.
4. Every theorem-level statement must identify its assumptions and distinguish an existing general result from a GCAT-specific modeling claim.
5. Every case-study statement must be sourced, explicitly identified as first-person observation, or removed.
6. Bibliographic metadata must be checked against publisher or DOI records before release.

## Remaining Source Work

- verify all BibTeX fields against publisher records in the final publication environment;
- add primary work on queueing or recovery saturation if those mechanisms remain in the final argument;
- add direct agent-safety literature only after selecting claims that are independently documented;
- add explicit citations to the integrated Markdown and future LaTeX source;
- preserve a bibliography-validation receipt with the exact commit and toolchain output.
