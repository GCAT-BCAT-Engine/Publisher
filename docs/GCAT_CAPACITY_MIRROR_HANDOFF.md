# GCAT Capacity Paper Mirror Handoff

## Status

This file is the current handoff and task source of truth for the GCAT capacity-based stability paper workstream in `GCAT-BCAT-Engine/Publisher`.

This workstream is repository-local and must not alter Publisher activation authority, Site state, wiki propagation state, release status, or the priority declared in `PUBLISHER_MIRROR_HANDOFF.md`.

## Purpose

Develop a publication-grade paper that formalizes governance failure as a capacity mismatch between institutional stabilization and autonomous execution pressure.

Working title:

> GCAT: A Capacity-Based Stability Condition for Governance in Autonomous Systems

## Durable Decisions

1. Effective governance capacity is modeled as `G_eff = K g^alpha c^beta t^gamma`.
2. The governance load ratio is `Omega = a / G_eff`.
3. `Omega <= 1` identifies the candidate governable region; `Omega > 1` identifies an overload regime. The threshold alone is not proof that drift must occur.
4. The same boundary is interpreted through control barrier functions, viability theory, and a Cobb-Douglas-type institutional production frontier.
5. The federal IT case is an observational structural illustration only. It is not evidence of malicious activity, causation, or a calibrated numerical `Omega`.
6. The paper must distinguish admissibility from stability, admissible state from viable state, strong constraints from effective governance capacity, and synthetic output from empirical measurement.

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
- `governance/receipts/gcat-capacity-sensitivity-validation-v1.json`
- `tools/gcat_capacity_timeseries.py`
- `tools/check_gcat_capacity_timeseries.py`
- `governance/receipts/gcat-capacity-timeseries-validation-v1.json`
- `docs/gcat-capacity-reproducibility.md`
- future generated CSV, JSON, manifests, and SVG outputs
- future LaTeX/PDF publication artifacts derived from the reviewed source

## Completed in Current Workstream

1. Added explicit proportional state dynamics in log-state coordinates.
2. Added bounded and delayed intervention assumptions.
3. Added a conditional forward-invariance proposition with a bounded claim.
4. Added four declared numerical scenarios: balanced adaptation, delayed intervention, constraint-heavy fragility, and bounded recovery failure.
5. Added fixed-step RK4 simulation code with no third-party dependencies.
6. Added CSV, summary JSON, SHA-256 digest, and manifest generation.
7. Added a simulation validator for positivity, margin identity, scenario behavior, delay enforcement, generated outputs, and provenance markers.
8. Added governance-pressure and elasticity sweeps.
9. Added Cobb-Douglas, weighted-geometric, weighted-additive, bottleneck-minimum, and CES comparisons.
10. Added a dependency-free SVG regime map with an explicit `Omega = 1` boundary.
11. Added a sensitivity validator covering grid dimensions, identities, classifications, model coverage, labels, file generation, and digests.
12. Added one dependency-free two-panel SVG generator per scenario.
13. Added a time-series figure validator covering scenario completeness, SVG structure, visible claim boundaries, legends, frontier labels, digests, and selected boundary behavior.
14. Integrated numerical methods, scenario design results, sensitivity methodology, alternative functional forms, figure generation, and validation limits into the paper source.
15. Expanded the reproducibility guide to include all three generation and validation workflows.

## Remaining Work

1. Execute all three committed validators in an authorized repository runtime and preserve exact outputs as validation evidence.
2. Generate and review committed synthetic CSV, JSON, manifests, regime-map SVG, and four time-series SVG files.
3. Expand related work using primary sources.
4. Validate or further qualify the observational case-study wording.
5. Produce reviewed LaTeX and PDF outputs.
6. Update the GCAT-BCAT paper index.
7. Obtain independent mathematical review of the proposition, dynamics, and production-function assumptions.
8. Determine whether a repository-local workflow should execute these validators without crossing existing Publisher authority boundaries.

## Validation Requirements

The workstream is not publication-ready until:

- equations and propositions receive mathematical review;
- all simulations reproduce from committed source and parameters;
- generated figures identify synthetic data explicitly;
- citations are complete and primary-source grounded;
- case-study statements are sourced, qualified as first-person observation, or removed;
- repository checks pass without modifying cross-repository authority.

## Ownership

Current build ownership: `agent/gcat-capacity-paper` draft branch and Publisher Issue #6.

Publisher mirror, Site activation, wiki propagation, release, and deployment ownership remain governed by `PUBLISHER_MIRROR_HANDOFF.md` and are outside this workstream.

## Permitted Continuation Scope

A successor may edit paper sources, model specifications, repository-local simulations, tests, figures, bibliography, and validation records. A successor may not claim external deployment, calibrated empirical prediction, theorem completion, or downstream propagation without corresponding durable evidence.
