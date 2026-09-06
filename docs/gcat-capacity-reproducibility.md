# GCAT Capacity Reproducibility Workflow

## Scope

This document describes the repository-local synthetic simulation, sensitivity, and figure workflow for:

> GCAT: A Capacity-Based Stability Condition for Governance in Autonomous Systems

All generated results are synthetic and uncalibrated. A modeled state with `Omega > 1` is classified as overload; it is not automatic evidence of behavioral drift, malicious action, or real-world causation.

## Requirements

- Python 3.9 or later
- no third-party Python packages

The tools use only the Python standard library.

## Scenario Simulation

Run:

```bash
python tools/gcat_capacity_simulation.py
```

Default inputs:

- `data/gcat_capacity_scenarios.json`

Default outputs:

- `generated/gcat-capacity/*.csv`
- `generated/gcat-capacity/*.summary.json`
- `generated/gcat-capacity/manifest.json`

Validate:

```bash
python tools/check_gcat_capacity_simulation.py
```

The simulation integrates logarithmic state variables with fixed-step RK4. Reconstructing state with the exponential function preserves strictly positive values for finite states.

## Sensitivity Study

Run:

```bash
python tools/gcat_capacity_sensitivity.py
```

Default input:

- `data/gcat_capacity_sensitivity.json`

Default outputs:

- `generated/gcat-capacity-sensitivity/regime_grid.csv`
- `generated/gcat-capacity-sensitivity/elasticity_sweep.csv`
- `generated/gcat-capacity-sensitivity/production_function_comparison.csv`
- `generated/gcat-capacity-sensitivity/gcat_regime_map.svg`
- `generated/gcat-capacity-sensitivity/sensitivity_summary.json`
- `generated/gcat-capacity-sensitivity/manifest.json`

Validate:

```bash
python tools/check_gcat_capacity_sensitivity.py
```

## Scenario Time-Series Figures

Run:

```bash
python tools/gcat_capacity_timeseries.py
```

Default input:

- `data/gcat_capacity_scenarios.json`

Default outputs:

- `generated/gcat-capacity-timeseries/balanced_adaptation.svg`
- `generated/gcat-capacity-timeseries/delayed_intervention.svg`
- `generated/gcat-capacity-timeseries/constraint_heavy_fragility.svg`
- `generated/gcat-capacity-timeseries/bounded_recovery_failure.svg`
- `generated/gcat-capacity-timeseries/manifest.json`

Each scenario figure contains two panels:

1. execution pressure and effective governance capacity over time;
2. governance load ratio `Omega` with an explicit `Omega = 1` frontier.

Validate:

```bash
python tools/check_gcat_capacity_timeseries.py
```

The figure validator checks scenario coverage, manifest parity, SHA-256 digests, frontier and legend labels, synthetic and uncalibrated warnings, and selected scenario boundary behavior.

## Complete Local Validation Sequence

```bash
python tools/check_gcat_capacity_simulation.py
python tools/check_gcat_capacity_sensitivity.py
python tools/check_gcat_capacity_timeseries.py
```

A successful run of one validator does not imply success of the others. Preserve exact evidence for each command.

## Production Functions Compared

### Cobb-Douglas baseline

```text
G_eff = K g^alpha c^beta t^gamma
```

This is the paper's current baseline assumption.

### Weighted geometric mean

The elasticities are normalized to sum to one. This removes returns-to-scale effects while preserving multiplicative complementarity.

### Weighted additive model

This comparator permits direct substitution among governance, constraint, and continuity inputs. It tests whether the baseline's strong complementarity materially changes overload classification.

### Bottleneck minimum

This Leontief-style comparator sets capacity by the weakest normalized input. It represents a non-substitutable governance architecture.

### CES comparator

The constant-elasticity-of-substitution model provides an intermediate family between substitution and complementarity. The declared specification currently uses `rho = -0.5`.

## Publication Figures

`gcat_regime_map.svg` is a vector figure generated directly by the sensitivity tool. It includes:

- governable and overload regions;
- the `Omega = 1` frontier;
- axis labels;
- an explicit synthetic and uncalibrated provenance statement;
- a warning that overload is not automatic proof of drift.

The four scenario SVGs are generated directly from the committed simulation functions. Each figure records the peak load and first overload time in its visible footer and binds the output to a manifest digest.

The SVG files are suitable for direct browser viewing and conversion by a publication toolchain. Any converted PDF or raster output must preserve the provenance statement and claim boundary.

## Reproducibility and Provenance

Each generated manifest records SHA-256 digests for its declared outputs. Scenario summaries also record a canonical digest of the scenario definition.

A valid execution receipt must preserve:

1. repository commit SHA;
2. Python version and operating system;
3. exact command;
4. exit code;
5. stdout and stderr;
6. generated manifest digest;
7. whether the working tree was clean.

## Validation Boundary

The committed validators inspect mathematical identities, positivity, declared scenario behavior, file generation, alternative-model coverage, provenance markers, vector-figure structure, and digest presence. They do not provide:

- independent mathematical peer review;
- empirical calibration;
- causal validation;
- external deployment evidence;
- permission to alter Publisher activation or downstream mirror state.
