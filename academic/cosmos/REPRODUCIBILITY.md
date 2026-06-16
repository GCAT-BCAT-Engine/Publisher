# GCAT/BCAT Cosmos Reproducibility Note

Assumptions for this note:

- This note explains how to reproduce in-repo GCAT/BCAT cosmos model checks.
- This note does not claim empirical validation of quantum, cosmological, dark-matter, dark-energy, or black-hole physics.
- Repository paths are shown without a leading slash.
- Paths that normally begin with a leading dot are shown without the leading dot and explicitly noted.

## Purpose

The GCAT/BCAT cosmos slice now includes documentation, posture boundaries, executable model checks, stress tests, edge-case tests, baseline claim records, and a GitHub Actions workflow.

The purpose of this note is to make reproduction clear while preserving the distinction between:

```text
model-level reproducibility
external-baseline comparison
validated physical result
```

At this stage, the repo supports model-level reproducibility and baseline-record discipline. It does not yet establish validated physical theory.

## Quick start: local commands

Run from the repository root.

### 1. Run deterministic sweep

```bash
python academic/cosmos/governance_random_sweep.py --samples 100 --seed 42 --stats academic/cosmos/sweep_statistics.json
```

Expected generated file:

```text
sweep_randomized_results.json
```

Note: the sweep script writes `sweep_randomized_results.json` to the current working directory. If run from the repository root, the result lands at the repository root. The workflow runs the script from `academic/cosmos`, so workflow artifacts land inside `academic/cosmos`.

### 2. Verify sweep results

If the result file is under `academic/cosmos`:

```bash
python academic/cosmos/verify_sweep_results.py academic/cosmos/sweep_randomized_results.json
```

If the result file is at the repository root:

```bash
python academic/cosmos/verify_sweep_results.py sweep_randomized_results.json
```

This verifies model-level consistency only.

### 3. Run multi-seed stress suite

```bash
cd academic/cosmos
python stress_sweep.py --samples 100 --seeds 1,7,13,42,101 --output stress_sweep_results.json
```

Expected generated file:

```text
academic/cosmos/stress_sweep_results.json
```

The stress suite checks model-health thresholds across deterministic seeds.

### 4. Run edge-case tests

```bash
cd academic/cosmos
python edge_case_tests.py
```

These tests cover:

- invalid simplex states,
- zero-invariant boundary states,
- ALLOW / DENY / FAIL_CLOSED classification behavior,
- projection clamping and renormalization,
- scalar range behavior,
- reality-label boundary behavior,
- random simplex generator smoke checks.

They verify model-level behavior only.

### 5. Verify baseline registry and result records

From repository root:

```bash
python academic/cosmos/verify_baseline_records.py
```

This checks:

- claim registry structure,
- required claim fields,
- claim ID uniqueness,
- analogy/hypothesis-only claim layers,
- recognized validation statuses,
- placeholder result-record structure,
- explicit `does_not_claim` boundaries.

It does not validate physical or cosmological claims.

## GitHub Actions workflow

Workflow path:

```text
github/workflows/cosmos-sweep-verify.yml
```

Note: the actual repository path starts with a leading dot.

The workflow runs on:

- manual dispatch,
- pushes affecting the cosmos sweep/verifier/stress/edge-case/baseline files,
- pull requests affecting the cosmos sweep/verifier/stress/edge-case/baseline files.

Workflow steps:

1. Checkout repository.
2. Set up Python 3.11.
3. Run deterministic seed-42 sweep.
4. Verify generated sweep results.
5. Run multi-seed stress suite.
6. Run edge-case tests.
7. Verify baseline registry and result records.
8. Upload generated artifacts.

## Workflow artifacts

The workflow uploads:

```text
academic/cosmos/sweep_randomized_results.json
academic/cosmos/sweep_statistics.json
academic/cosmos/stress_sweep_results.json
```

These artifacts are evidence that the in-repo model checks ran. They are not empirical proof of physical claims.

## How to interpret results

### PASS from `verify_sweep_results.py`

Means:

- the sweep output is valid JSON,
- top-level metadata matches the expected sweep,
- counts and frequencies are internally consistent,
- scalar values stay within expected model range,
- simplex states are structurally valid,
- boundary-proximity values are internally consistent.

Does not mean:

- GCAT/BCAT is empirically validated physics,
- scalar regimes are physical quantum/cosmological fields,
- dark matter or dark energy has been proven,
- quantum mechanics or general relativity has been replaced.

### PASS from `stress_sweep.py`

Means:

- deterministic seeds ran through the current model,
- model-health thresholds were satisfied,
- generated states avoided `FAIL_CLOSED`,
- scalar and boundary ranges stayed inside expected model bounds.

Does not mean:

- the model matches external observations,
- the scalar labels are physical observables,
- cosmological claims are validated.

### PASS from `edge_case_tests.py`

Means:

- invalid states are rejected,
- boundary states are handled deterministically,
- classification behavior is stable for direct ALLOW / DENY / FAIL_CLOSED cases,
- projection behavior remains normalized,
- scalar and label behavior remains bounded.

Does not mean:

- boundary states correspond to physical states,
- scalar labels are empirical observables,
- external physics comparison has been completed.

### PASS from `verify_baseline_records.py`

Means:

- the baseline registry is structurally valid,
- placeholder baseline records are structurally valid,
- no record silently upgrades analogy/hypothesis language into validated physical theory.

Does not mean:

- an external comparison has been completed,
- any placeholder result is a physics result,
- any `not_testable_yet` claim has become validated.

## Current validation posture

```text
Cataloged: yes
Public posture boundary: yes
Executable model artifact: yes
Model-level result verifier: yes
Deterministic reproducibility workflow: yes
Internal stress-test suite: yes
Edge-case test suite: yes
Baseline claim registry: yes
Baseline result placeholders: yes
Baseline record verifier: yes
External physics baseline comparison: scaffolded, not completed
Validated physical result: not yet
```

## Public-language rule

Use:

```text
GCAT/BCAT provides a formal and executable hypothesis framework for comparing transition admissibility with selected quantum/cosmological concepts.
```

Do not use:

```text
GCAT/BCAT proves dark matter.
GCAT/BCAT proves dark energy.
GCAT/BCAT replaces quantum mechanics.
GCAT/BCAT replaces general relativity.
GCAT/BCAT has validated a cosmological theory.
```

## Next reproducibility work

1. Add a changelog entry for the cosmos validation slice.
2. Add actual baseline comparison scripts only after observables, units, normalization, and public data sources are defined.
