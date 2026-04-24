# Provisional Patent Framework: Commit-Time Triage Engine

## Filing Strategy

**Type:** US Provisional Patent Application (PPA)  
**Filing deadline:** Within 12 months of first public disclosure  
**Convert to non-provisional:** Within 12 months of PPA filing  
**Priority date:** Date of PPA filing  

## Inventorship

- GCAT-BCAT-Engine Contributors (to be determined based on contribution)
- Recommended: list all contributors to the Triage repo with >10% code contribution

## Field of Invention

Computer-implemented safety governance for embodied systems, specifically a commit-time triage primitive that separates sufficiency evaluation, admissibility gating, and scalar reserve computation across human medical, robotic, and AI domains.

## Background Art

### Prior Art Search Results

1. **Medical triage systems** (START, SALT): Prioritize patients but do not separate sufficiency from admissibility. No scalar reserve metric. No commit-time binding.
2. **Robot safety standards** (ISO 10218, ISO/TS 15066): Specify stopping conditions but lack unified scalar reserve. Domain-specific, not agnostic.
3. **AI safety frameworks** (Constitutional AI, RLHF): Training-time alignment, not commit-time governance. No embodied system focus.
4. **Real-time operating systems** (RTOS): Task scheduling and priority inversion, but no medical/robotic/AI domain unification.
5. **Fault detection and isolation (FDI):** Sensor fault detection, but no governance primitive linking to action admissibility.

### Novelty Assessment

| Feature | Prior Art | Our Invention |
|---------|-----------|---------------|
| Sufficiency-admissibility separation | No | Yes |
| Scalar reserve metric U | No | Yes |
| Domain-agnostic core + config | No | Yes |
| Commit-time cryptographic binding | No | Yes |
| Bidirectional canonical governance | No | Yes |
| Coherence monitoring as admissibility trigger | No | Yes |

## Claims (Provisional)

### Independent Claim 1

A computer-implemented method for commit-time triage of embodied systems, comprising:

1. receiving, at a decision commit point, a plurality of sensor inputs characterizing state of an embodied system;
2. evaluating sufficiency of the sensor inputs by comparing against a registry of required signals, each required signal having a minimum quality threshold and minimum observation duration;
3. evaluating admissibility through a fail-closed gate that tests a plurality of hard safety triggers, wherein if any hard safety trigger is activated, the system is deemed inadmissible regardless of other factors;
4. computing a scalar reserve metric from a plurality of degradation factors including energy integrity, mechanical output, resource delivery, respiration/exchange, coherence, trend, and observability;
5. assigning a triage level from a predefined set based on the admissibility evaluation and the scalar reserve metric;
6. binding the evaluation to an immutable commit record comprising a cryptographic hash of a canonical representation of the evaluation.

### Independent Claim 2

The method of Claim 1, wherein the same core evaluation pipeline operates across human medical, mobile robotic, and embodied AI domains without modification to the core logic, with domain-specific behavior determined solely by configuration parameters comprising signal requirements, scalar weights, trend windows, and coherence rules.

### Independent Claim 3

The method of Claim 1, further comprising:

7. emitting governance events to a canonical database external to the embodied system;
8. receiving canonical updates from the canonical database;
9. applying received canonical updates to modify local configuration of the registry, scalar weights, or hard safety triggers.

### Dependent Claims

**Claim 4:** The method of Claim 1, wherein the scalar reserve metric is adjusted by an observability factor, and wherein low observability both reduces the scalar reserve metric and may trigger the inadmissibility evaluation.

**Claim 5:** The method of Claim 1, further comprising evaluating coherence between sensor signals through predefined coherence rules, and triggering inadmissibility when the sensor signals violate the coherence rules.

**Claim 6:** The method of Claim 1, wherein the hard safety triggers include: no pulse, no breathing, critical perfusion failure, loss of control, loss of authority, low observability, incoherent signals, and sufficiency failure.

**Claim 7:** The method of Claim 1, wherein the triage levels comprise: GREEN (normal operation), YELLOW (degraded), ORANGE (restricted), RED (hard stop), and BLACK (nonrecoverable).

**Claim 8:** The method of Claim 1, wherein the cryptographic hash is SHA-256 computed over a canonical JSON representation of the evaluation sorted by keys.

**Claim 9:** The method of Claim 3, wherein the canonical database is platform-agnostic and supports ingestion via git commit, webhook POST, file drop, or polling.

**Claim 10:** A non-transitory computer-readable medium storing instructions that, when executed by a processor, cause the processor to perform the method of Claim 1.

## Drawings Required

1. **Figure 1:** Pipeline flowchart (sufficiency → coherence → admissibility → scalar → level → commit)
2. **Figure 2:** Domain config comparison (human medical vs robotics vs embodied AI)
3. **Figure 3:** Commit record structure and hash computation
4. **Figure 4:** Bidirectional StegDB architecture (emit + receive)
5. **Figure 5:** Triage level decision tree

## Specification Outline

### Title
Commit-Time Triage Engine: A Domain-Agnostic Governance Primitive for Embodied Systems

### Cross-References to Related Applications
None (provisional filing).

### Statement Regarding Federally Sponsored Research
None.

### Abstract
[Same as paper abstract, condensed to 150 words]

### Detailed Description

#### Section 1: Field of Invention
Computer-implemented safety governance for embodied systems.

#### Section 2: Background
Prior art limitations and the need for domain-agnostic governance.

#### Section 3: Summary of Invention
The three-layer separation (sufficiency, admissibility, scalar) and commit-time binding.

#### Section 4: Brief Description of Drawings
Figures 1-5 as listed above.

#### Section 5: Detailed Description
- 5.1 Sufficiency registry and validation
- 5.2 Admissibility gate (fail-closed)
- 5.3 Scalar computation (formula, floors, weights)
- 5.4 Triage level assignment
- 5.5 Commit-time binding (hash, immutability)
- 5.6 Domain configurations (medical, robotic, AI)
- 5.7 StegDB integration (bidirectional)
- 5.8 Platform agnosticism
- 5.9 Safety invariants and proofs

#### Section 6: Claims
Claims 1-10 as listed above.

#### Section 7: Abstract
150-word abstract.

## Filing Checklist

- [ ] Prepare drawings (Figures 1-5)
- [ ] Write full specification (Sections 1-7)
- [ ] Format claims for USPTO
- [ ] Prepare inventor declarations
- [ ] Conduct prior art search (professional search recommended)
- [ ] File USPTO provisional application ($300 small entity fee)
- [ ] Mark repo as "patent pending" in README
- [ ] Set 12-month calendar reminder for non-provisional conversion

## Notes

- The open-source release (Apache 2.0) does not prevent patent filing. The patent covers the specific method/claims, not the implementation.
- The safety notice in the license is separate from patent status.
- Consider PCT filing for international protection within 12 months of non-provisional.
- Recommended patent attorney: one with experience in software patents + medical devices + robotics.

## Status

Framework complete. Ready for attorney review and prior art search.
