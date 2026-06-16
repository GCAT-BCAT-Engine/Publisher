# GCAT/BCAT Cosmos Baselines

Assumptions for this folder:

- This folder tracks external-baseline scaffolding for physics-facing GCAT/BCAT hypotheses.
- Nothing in this folder establishes validated physical theory by itself.
- Repository paths are shown without a leading slash.

## Purpose

The baselines folder exists to prevent silent upgrades from analogy or hypothesis into empirical physics claims.

It provides a structured place to:

- assign stable claim IDs,
- identify source artifacts,
- name external baselines needed for comparison,
- define observables, units, normalization, and failure conditions,
- store future machine-readable comparison result records.

## Current files

```text
academic/cosmos/baselines/claim_registry.json
```

Initial registry of physics-facing GCAT/BCAT claims that require external comparison before any validated-physics language is used.

## Current claim posture

```text
Physics analogy: present
Physics hypothesis: present
External baseline scaffold: present
External comparison results: not yet
Validated physical result: not yet
```

## Claim registry

The registry currently includes claim IDs for:

- `COSMOS-SCALAR-REGIME-001`
- `COSMOS-ENTROPY-DEBT-001`
- `COSMOS-MASS-ENERGY-IMPRINT-001`
- `COSMOS-DARK-COMPONENTS-001`
- `COSMOS-BLACK-HOLE-CIRCLE-001`

Each claim record includes:

- claim ID,
- title,
- claim layer,
- validation status,
- source artifacts,
- summary,
- external baseline requirement,
- candidate external baselines,
- required observable,
- required units or normalization,
- failure condition,
- safe public language.

## Required result location

Future baseline comparison records should be stored under:

```text
academic/cosmos/baselines/results/
```

Recommended file naming:

```text
academic/cosmos/baselines/results/<claim_id>.json
```

## Required result status values

Future comparison results should use one of:

```text
fit
weak_correlation
no_result
contradiction
not_testable_yet
```

## Public-language rule

Until a claim has external comparison records and survives the required checks, use:

```text
GCAT/BCAT proposes a formal hypothesis mapping between transition admissibility and selected quantum/cosmological concepts.
```

Do not use:

```text
GCAT/BCAT proves dark matter.
GCAT/BCAT proves dark energy.
GCAT/BCAT replaces quantum mechanics.
GCAT/BCAT replaces general relativity.
GCAT/BCAT has validated a cosmological theory.
```

## Next work

1. Add `academic/cosmos/verify_baseline_records.py`.
2. Add placeholder result records under `academic/cosmos/baselines/results/` marked `not_testable_yet`.
3. Add a workflow step to validate baseline records.
4. Add actual baseline comparison scripts only after observables, units, and data sources are defined.
