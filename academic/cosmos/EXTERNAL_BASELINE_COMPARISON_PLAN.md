# GCAT/BCAT External Baseline Comparison Plan

Assumptions for this plan:

- This plan applies to physics-facing GCAT/BCAT claims in `academic/cosmos`.
- The plan is a research boundary, not a claim of completed empirical validation.
- Repository paths are shown without a leading slash.
- Any path that normally begins with a leading dot is shown without that leading dot and noted when used.

## Purpose

GCAT/BCAT cosmos materials currently provide a formal and executable hypothesis framework for comparing transition admissibility, scalar regimes, entropy debt, and information-theoretic structure with quantum/cosmological concepts.

Before any physics-facing claim is described as validated, it must be compared against external baselines with defined observables, units, error metrics, failure conditions, and reproducible inputs.

This plan defines that path.

## Done criteria

External-baseline comparison is considered ready when the repo contains:

1. A named external baseline for each physics-facing hypothesis.
2. A defined observable for each comparison.
3. Units and normalization rules.
4. A reproducible dataset or documented public source.
5. A comparison script or notebook.
6. Pass/fail or fit-quality metrics.
7. Failure criteria and interpretation boundaries.
8. A result file that distinguishes model fit, weak correlation, no result, and contradiction.
9. A note preserving that GCAT/BCAT is not validated physical theory unless the evidence supports that move.

## Current posture

```text
Governance formalism: present
Physics analogy: present
Physics hypothesis: present
Model-level reproducibility: present
Internal stress testing: present
External baseline comparison: planned
Validated physical result: not established
```

## Claim classes requiring external comparison

### 1. Scalar-regime claims

GCAT/BCAT currently labels scalar regimes as:

- quantum-contracted,
- quantum-mixed,
- near-quantum,
- classical-critical,
- near-astrophysical,
- astrophysical-mixed,
- astrophysical-expanded.

External comparison requirement:

- Define what observable distinguishes a quantum-contracted, classical-critical, or astrophysical-expanded regime.
- Define whether these labels are analogical, statistical, physical, or scale-normalized.
- Compare scalar distributions against a selected baseline rather than relying on label semantics.

Candidate external baselines:

- scale separation between Planck-scale, laboratory/classical scale, and cosmological scale,
- dimensionless scale ratios,
- entropy or information measures from accepted physical datasets,
- existing cosmological parameter distributions where appropriate.

Minimum result standard:

```text
The scalar labels remain analogical unless a measurable external observable is mapped, normalized, tested, and reported.
```

### 2. Entropy-debt claims

GCAT/BCAT currently uses entropy debt to describe information loss or unresolved transition cost across a gap.

External comparison requirement:

- Define whether entropy debt is Shannon entropy, thermodynamic entropy, algorithmic/information entropy, or a model-local proxy.
- Define units and conversion limits.
- Compare any entropy-to-energy claim against accepted entropy/energy relations only within stated assumptions.

Candidate external baselines:

- Shannon entropy for discrete distributions,
- Landauer-style information/energy bounds,
- thermodynamic entropy only where units and physical temperature are defined,
- information-theoretic model diagnostics.

Minimum result standard:

```text
Entropy debt may be treated as model-local information debt unless conversion to physical entropy is explicitly justified and validated.
```

### 3. Mass-energy imprint claims

GCAT/BCAT currently proposes mappings such as imprint energy and imprint mass.

External comparison requirement:

- Define whether the claim is symbolic, analogical, information-theoretic, or physical.
- Define constants, units, scale factors, and assumptions.
- Compare against accepted energy/mass relations only after dimensional consistency is shown.

Candidate external baselines:

- dimensional analysis,
- information-energy conversion bounds,
- accepted mass-energy equivalence only under valid physical assumptions,
- scale-normalized toy-model comparison.

Minimum result standard:

```text
Mass-energy imprint claims remain hypothesis-level until dimensional consistency and baseline comparison are complete.
```

### 4. Dark-matter / dark-energy mapping claims

GCAT/BCAT currently hypothesizes mappings such as:

- ALLOW transitions as ordinary matter,
- DENY transitions with quantum-side scalar as dark-matter-like trace,
- DENY transitions with astrophysical-side scalar or entropy debt as dark-energy-like expansion.

External comparison requirement:

- Define observables that could be compared to accepted cosmological quantities.
- Define whether outputs are dimensionless fractions, relative weights, or physical density parameters.
- Compare model-derived fractions against accepted cosmological parameter baselines only after normalization is explicit.

Candidate external baselines:

- accepted matter, dark matter, and dark energy density fractions,
- cosmological parameter tables from recognized public datasets,
- dimensionless density parameter comparisons,
- uncertainty-bounded fit or mismatch reports.

Minimum result standard:

```text
The mapping may be described as a proposed analogy or hypothesis unless model outputs reproduce or meaningfully compare against external density-parameter baselines under stated assumptions.
```

### 5. Black-hole / circle-condition claims

GCAT/BCAT currently uses a circle-condition or equal-obscurity limit as a black-hole-like symmetry analogy.

External comparison requirement:

- Define whether the black-hole comparison is geometric, informational, thermodynamic, relativistic, or merely analogical.
- Avoid claiming replacement of event-horizon physics, general relativity, or black-hole thermodynamics unless a direct equation-level comparison exists.
- Compare only explicitly defined quantities.

Candidate external baselines:

- information loss/paradox literature as conceptual baseline,
- entropy-area relation only if units and surface assumptions are defined,
- symmetry/degeneracy metrics,
- toy-model collapse-to-center behavior.

Minimum result standard:

```text
The circle condition should remain a black-hole-like analogy unless directly compared against accepted black-hole observables or equations.
```

## Required comparison record format

Each future baseline comparison should produce a record with this shape:

```json
{
  "claim_id": "string",
  "claim_layer": "physics_hypothesis",
  "artifact": "academic/cosmos/<file>",
  "external_baseline": "string",
  "observable": "string",
  "units": "string or dimensionless",
  "normalization": "string",
  "input_data": "path or public source description",
  "method": "string",
  "metric": "string",
  "result": "fit | weak_correlation | no_result | contradiction | not_testable_yet",
  "limitations": ["string"],
  "does_not_claim": ["validated physical theory"]
}
```

## Proposed repo additions

### Baseline claim registry

```text
academic/cosmos/baselines/claim_registry.json
```

Purpose:

- List every physics-facing claim.
- Assign claim IDs.
- Assign current claim layer.
- Link each claim to source artifact and validation status.

### Baseline comparison notes

```text
academic/cosmos/baselines/README.md
```

Purpose:

- Explain accepted baseline sources.
- Explain what will and will not be compared.
- Preserve overclaim boundaries.

### Baseline result records

```text
academic/cosmos/baselines/results/<claim_id>.json
```

Purpose:

- Store structured comparison outputs.
- Keep results machine-readable.
- Allow later verifier/workflow support.

### Baseline verifier

```text
academic/cosmos/verify_baseline_records.py
```

Purpose:

- Check that every baseline record includes claim ID, baseline, observable, units, method, metric, result, and limitations.
- Ensure no record silently upgrades a hypothesis into validated physics.

## Minimum public-language policy

Until baseline comparison is complete, use:

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

## External comparison readiness checklist

Before a comparison is run, confirm:

- [ ] The claim has a stable claim ID.
- [ ] The source artifact is named.
- [ ] The claim layer is physics analogy or physics hypothesis, not validated result.
- [ ] The external baseline is named.
- [ ] The observable is defined.
- [ ] Units or dimensionless normalization are defined.
- [ ] The comparison metric is defined.
- [ ] Failure criteria are defined.
- [ ] Output format is machine-readable.
- [ ] Public-language limits are preserved.

## Current next step

Create the baseline registry:

```text
academic/cosmos/baselines/claim_registry.json
```

Then create:

```text
academic/cosmos/baselines/README.md
academic/cosmos/verify_baseline_records.py
```

This will move external-baseline comparison from planned to scaffolded.
