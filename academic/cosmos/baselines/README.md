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
- store machine-readable comparison result records.

## Current files

```text
academic/cosmos/baselines/claim_registry.json
academic/cosmos/baselines/results/COSMOS-SCALAR-REGIME-001.json
academic/cosmos/baselines/results/COSMOS-ENTROPY-DEBT-001.json
academic/cosmos/baselines/results/COSMOS-MASS-ENERGY-IMPRINT-001.json
academic/cosmos/baselines/results/COSMOS-DARK-COMPONENTS-001.json
academic/cosmos/baselines/results/COSMOS-BLACK-HOLE-CIRCLE-001.json
```

The registry catalogs physics-facing GCAT/BCAT claims that require external comparison before any validated-physics language is used.

The result records currently exist as placeholders marked:

```text
not_testable_yet
```

They are machine-readable boundary records, not empirical validation results.

## Current claim posture

```text
Physics analogy: present
Physics hypothesis: present
External baseline scaffold: present
Placeholder result records: present
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

## Result records

Current result records are placeholders. Each one states:

- the claim ID,
- the claim layer,
- the source artifact,
- the candidate external baseline,
- the fact that observable, normalization, input data, method, and metric are not defined yet,
- result status: `not_testable_yet`,
- limitations,
- explicit does-not-claim boundaries.

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

## Verifier

Use:

```bash
python academic/cosmos/verify_baseline_records.py
```

The verifier checks the claim registry and all JSON records under:

```text
academic/cosmos/baselines/results/
```

## Next work

1. Add a public reproduction note explaining how to run the workflow and interpret artifacts.
2. Add edge-case tests for invalid states and boundary-condition states.
3. Add actual baseline comparison scripts only after observables, units, and data sources are defined.
