# GCAT/BCAT Physics Formalism Index

Assumptions for this index:

- This index covers the currently identified GCAT/BCAT formalism materials in `academic/cosmos` that compare, derive, simulate, or posture-map GCAT/BCAT concepts against quantum, classical, astrophysical, cosmological, black-hole, entropy, information, dark-matter, or dark-energy concepts.
- This index does not claim peer-reviewed physical validity. It classifies repository artifacts by documentation role, evidentiary posture, and next validation step.
- The leading repository path is shown without a leading slash.

## Done criteria

This documentation slice is considered done when:

1. Every physics-relevant GCAT/BCAT artifact has a stable catalog entry.
2. Each artifact is classified as one of: primary formalism documentation, executable validation/sweep artifact, generated evidence/result artifact, or posture/speculative note.
3. Each artifact states whether it contains formal derivation, model analogy, executable calculation, empirical claim, or validation requirement.
4. The repo contains a clear boundary statement separating governance formalism, physics analogy, physics hypothesis, and validated physical result.
5. The sweep/test artifacts can be reproduced with a documented command and compared against expected output.

## Primary artifact

### `academic/cosmos/GCAT_BCAT_Formalism_Documentation.txt`

**Classification:** Primary formalism documentation.

**Status:** Strong match for quantum/cosmological comparisons and derivations.

**Contains:**

- BCAT simplex definition: `g + c + a + t = 1.0`.
- GCAT/BCAT invariant: `I(x) = gc + ca + at + tg`.
- Admissibility classification over projected state `x'`.
- Reality selector scalar `s`.
- Quantum-contracted, classical-critical, and astrophysical-expanded scalar regimes.
- Time-as-gap formulation.
- Entropy debt and imprint mass-energy mapping.
- Cosmological mapping of ALLOW/DENY/unresolved-gap transitions.
- Information-theoretic mass scaling between Planck and Hubble scales.
- Entity-weighted cosmological integral.
- Black-hole/circle-condition limit.
- Experimental signatures and falsification tests.

**Best use:**

Use this document as the canonical starting point for anyone asking which GCAT/BCAT documents compare or derive quantum and cosmological physics.

**Posture:**

Formalism draft / hypothesis layer. It contains equations and proposed mappings, but should not yet be described as validated physical theory without independent validation artifacts.

## Supporting executable artifact

### `academic/cosmos/governance_random_sweep.py`

**Classification:** Executable sweep / validation-support artifact.

**Status:** Strong supporting match.

**Contains:**

- BCAT simplex validity check.
- Invariant computation.
- Lambda capacity computation.
- Reality selector scalar computation.
- Scalar labels including:
  - `quantum-contracted`
  - `quantum-mixed`
  - `near-quantum`
  - `classical-critical`
  - `near-astrophysical`
  - `astrophysical-mixed`
  - `astrophysical-expanded`
- Randomized transition projection.
- ALLOW/DENY/FAIL_CLOSED classification.
- Outcome frequency, entropy, scalar, and boundary-proximity statistics.
- Cumulative statistics output.

**Best use:**

Use this file to reproduce the scalar-regime sweep behavior and inspect whether the formalism produces the expected admissibility and scalar distributions under randomized simplex sampling.

**Posture:**

Executable model artifact. It operationalizes the formalism but does not independently validate the physics mapping.

**Expected command:**

```bash
python academic/cosmos/governance_random_sweep.py --samples 100 --seed 42
```

**Expected generated files:**

```text
sweep_randomized_results.json
sweep_statistics.json
```

## Generated/result artifact

### `academic/cosmos/sweep_randomized_results.json`

**Classification:** Generated sweep result / evidence artifact.

**Status:** Supporting match if present and current.

**Contains:**

- Sampled transition records.
- Outcome distribution.
- Scalar distribution.
- Boundary-proximity statistics.
- Cumulative sweep statistics snapshot.

**Best use:**

Use this as a concrete evidence sample for the executable sweep, not as proof of physical correctness.

**Posture:**

Run-output evidence. It supports reproducibility of the sweep implementation only.

## Adjacent infrastructure artifact

### `GCAT-BCAT-Engine/workflows/README.md`

**Classification:** Validation infrastructure documentation.

**Status:** Adjacent but not itself a physics derivation document.

**Contains:**

- Workflow-level formal verification and mathematical solver context.
- Proof/sandbox infrastructure context.
- Potential execution environment for formalism tests.

**Best use:**

Use this to explain where validation workflows live, not as the canonical explanation of the quantum/cosmological mapping.

**Posture:**

Infrastructure documentation.

## Boundary statement

GCAT/BCAT physics-language artifacts should be read in four separated layers:

1. **Governance formalism:** The base GCAT/BCAT invariant, simplex state, transition classification, and admissibility mechanics.
2. **Physics analogy:** Terms such as quantum-contracted, classical-critical, astrophysical-expanded, entropy debt, and black-hole/circle condition may serve as explanatory mappings.
3. **Physics hypothesis:** Equations that propose mass-energy, dark matter, dark energy, Planck/Hubble scaling, or cosmological integrals are hypothesis-level claims unless separately validated.
4. **Validated physical result:** A claim should only move here after reproducible tests, external review, falsification criteria, and comparison against accepted physical observations.

No artifact in this index should be presented as completed validated physics unless later validation files explicitly establish that status.

## Current classification table

| Artifact | Quantum comparison | Cosmology comparison | Derivation content | Executable | Validation posture |
|---|---:|---:|---:|---:|---|
| `academic/cosmos/GCAT_BCAT_Formalism_Documentation.txt` | Yes | Yes | Yes | No | Formalism draft / hypothesis |
| `academic/cosmos/governance_random_sweep.py` | Yes | Partial | Partial implementation | Yes | Model/sweep support |
| `academic/cosmos/sweep_randomized_results.json` | Indirect | Indirect | No | No | Run-output evidence |
| `GCAT-BCAT-Engine/workflows/README.md` | No direct derivation | No direct derivation | No | Infrastructure context | Validation environment |

## Remaining work

1. Add a short `academic/cosmos/README.md` that links this index and the primary formalism document.
2. Add a reproducibility script or workflow for `governance_random_sweep.py`.
3. Add expected-output thresholds for ALLOW rate, entropy, scalar mean/range, and DENY boundary proximity.
4. Add a physics-posture note for public readers explaining the difference between formal analogy and validated empirical physics.
5. Add citations or comparison notes against standard physics concepts if this becomes an academic-facing paper.

## Recommended next repo addition

Create:

```text
academic/cosmos/PHYSICS_POSTURE.md
```

Purpose:

- Prevent overclaiming.
- Preserve the research value of the formalism.
- Make clear which claims are governance-formal, which are analogical, which are hypothesis-level, and which are validated.
