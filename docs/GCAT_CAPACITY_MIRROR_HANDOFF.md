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
- `tools/gcat_capacity_simulation.py`
- `tools/check_gcat_capacity_simulation.py`
- `data/gcat_capacity_scenarios.json`
- `governance/receipts/gcat-capacity-simulation-validation-v1.json`
- `data/gcat_capacity_sensitivity.json`
- `tools/gcat_capacity_sensitivity.py`
- `tools/check_gcat_capacity_sensitivity.py`
- `docs/gcat-capacity-reproducibility.md`
- future generated CSV, JSON, manifest, and SVG outputs
- future LaTeX/PDF publication artifacts derived from the reviewed source

## Completed in Current Workstream

1. Added explicit proportional state dynamics in log-state coordinates.
2. Added bounded, delayed intervention assumptions.
3. Replaced threshold-only theorem language with a conditional forward-invariance proposition in the paper source.
4. Added four declared numerical scenarios:
   - balanced adaptation;
   - delayed intervention;
   - constraint-heavy fragility;
   - bounded recovery failure.
5. Added fixed-step RK4 simulation code with no third-party dependencies.
6. Added CSV, summary JSON, SHA-256 digest, and manifest generation.
7. Added a repository-local validator for positivity, margin identity, scenario behavior, delay enforcement, generated outputs, and synthetic/calibration markers.
8. Added a governance-pressure regime sweep and elasticity sweep.
9. Added alternative production-function comparisons:
   - Cobb-Douglas;
   - normalized weighted geometric;
   - weighted additive;
   - bottleneck minimum;
   - CES.
10. Added a dependency-free SVG regime-map generator with an explicit `Omega = 1` boundary and synthetic-data warning.
11. Added a sensitivity validator covering grid dimensions, identities, classification, model coverage, publication labels, file generation, and digests.
12. Added a reproducibility guide covering commands, outputs, assumptions, and receipt requirements.

## Remaining Work

1. Execute both committed validators in an authorized repository runtime and preserve their exact outputs as validation evidence.
2. Generate and review the committed synthetic CSV, JSON, manifests, and SVG figure.
3. Add a time-series publication figure derived from committed scenario outputs.
4. Expand related work using primary sources.
5. Validate the observational case-study wording and remove or qualify unsupported statements.
6. Integrate the sensitivity methodology and results into the paper source.
7. Produce reviewed LaTeX and PDF outputs.
8. Update the GCAT-BCAT paper index.
9. Obtain independent mathematical review of the proposition, dynamics, and production-function assumptions.

## Validation Requirements

The workstream is not publication-ready until:

- equations and propositions receive mathematical review;
- all simulations reproduce from committed source and parameters;
- generated figures identify synthetic data explicitly;
- citations are complete and primary-source grounded;
- case-study statements are either sourced, qualified as first-person observation, or removed;
- repository checks pass without modifying cross-repository authority.

## Ownership

Current build ownership: `agent/gcat-capacity-paper` draft branch and Publisher Issue #6.

Publisher mirror, Site activation, wiki propagation, release, and deployment ownership remain governed by `PUBLISHER_MIRROR_HANDOFF.md` and are outside this workstream.

## Permitted Continuation Scope

A successor may edit the paper source, model specification, local simulations, tests, figures, bibliography, and validation records. A successor may not claim external deployment, calibrated empirical prediction, theorem completion, or downstream propagation without corresponding durable evidence.
