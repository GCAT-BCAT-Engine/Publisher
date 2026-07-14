# GCAT Capacity Paper Mirror Handoff

## Status

This file is the current handoff and task source of truth for the GCAT capacity-based stability paper workstream in `GCAT-BCAT-Engine/Publisher`.

This workstream is repository-local and must not alter Publisher activation authority, Site state, wiki propagation state, release status, or the priority declared in `PUBLISHER_MIRROR_HANDOFF.md`.

## Purpose

Develop a publication-grade paper that formalizes governance failure as a capacity mismatch between institutional stabilization and autonomous execution pressure.

Working title:

> GCAT: A Capacity-Based Stability Condition for Governance in Autonomous Systems

## Durable Decisions

1. Effective governance capacity is modeled as

   `G_eff = K g^alpha c^beta t^gamma`.

2. The governance load ratio is

   `Omega = a / G_eff`.

3. `Omega <= 1` identifies the candidate governable region; `Omega > 1` identifies an overload regime. The threshold alone is not a proof that drift must occur without additional system dynamics and assumptions.

4. The same boundary is interpreted through:
   - control barrier functions and forward invariance;
   - viability theory and recoverability;
   - a Cobb-Douglas-type institutional production frontier.

5. The federal IT case is an observational structural illustration only. It is not evidence of malicious activity, causation, or a calibrated numerical value of `Omega`.

6. The paper must distinguish:
   - admissibility from stability;
   - an admissible state from a viable/recoverable state;
   - strong constraints from effective governance capacity;
   - simulated results from empirical measurements.

## Artifacts

- `papers/GCAT-BCAT/P14_GCAT_Capacity_Stability_v1.md`
- `models/gcat_capacity_model.json`
- future reproducible simulation implementation and generated figures
- future LaTeX/PDF publication artifacts derived from the reviewed source

## Remaining Work

1. Add explicit state dynamics and bounded intervention assumptions.
2. Replace threshold-only theorem language with a valid conditional forward-invariance proposition.
3. Add numerical scenarios with positivity-preserving dynamics.
4. Add parameter sweeps, sensitivity analysis, and reproducibility metadata.
5. Expand related work using primary sources.
6. Validate the observational case-study wording and remove unsupported scale claims.
7. Produce reviewed LaTeX and PDF outputs.
8. Record validation receipts and update the paper index.

## Validation Requirements

The workstream is not publication-ready until:

- equations and propositions receive mathematical review;
- all simulations reproduce from committed source and parameters;
- generated figures identify synthetic data explicitly;
- citations are complete and primary-source grounded;
- case-study statements are either sourced, qualified as first-person observation, or removed;
- repository checks pass without modifying cross-repository authority.

## Ownership

Current build ownership: `agent/gcat-capacity-paper` draft branch.

Publisher mirror, Site activation, wiki propagation, release, and deployment ownership remain governed by `PUBLISHER_MIRROR_HANDOFF.md` and are outside this workstream.

## Permitted Continuation Scope

A successor may edit the paper source, model specification, local simulations, tests, figures, bibliography, and validation records. A successor may not claim external deployment, calibrated empirical prediction, theorem completion, or downstream propagation without corresponding durable evidence.
