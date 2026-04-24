# Commit-Time Triage as a Governance Primitive for Embodied Systems

**Authors:** GCAT-BCAT-Engine Contributors  
**Date:** April 2026  
**Status:** Draft for submission  
**Target venues:** IEEE Transactions on Robotics (T-RO), ACM Computing Surveys, or arXiv preprint with journal submission

---

## Abstract

We present Commit-Time Triage, a minimal admissibility-based governance primitive for evaluating whether human, robotic, or AI-enabled embodied systems remain in recoverable states at decision points. The framework separates three concerns: sufficiency (can we claim anything?), admissibility (can we safely continue?), and scalar reserve (how close to failure?). We prove that this separation enables fail-closed safety guarantees while remaining domain-agnostic across medical, robotic, and AI contexts. We provide an open-source implementation, formalize the safety invariants, and demonstrate that the same architecture governs all three domains without modification to core logic. This work establishes commit-time triage as a foundational primitive for safety-critical embodied system governance.

---

## 1. Introduction

### 1.1 Motivation

Embodied systems — systems that interact with the physical world through sensors and actuators — face a common governance challenge: how to decide, at the moment a critical action is committed, whether the system remains in a recoverable state. This challenge spans:

- **Human medical monitoring:** Is the patient stable enough for discharge, transfer, or procedure?
- **Mobile robotics:** Is the robot safe to continue operation, or must it stop?
- **Embodied AI:** Does the AI system retain sufficient coherence and authority to act?

Current approaches treat these domains separately, with domain-specific safety checks that share no common structure. This fragmentation prevents cross-domain learning, makes formal verification expensive, and obscures the underlying governance primitive.

### 1.2 Contribution

We introduce **Commit-Time Triage**, a domain-agnostic governance primitive with three properties:

1. **Sufficiency gate:** No diagnosis without sufficient data. Required signals must be present, meet quality thresholds, and have minimum observation duration.
2. **Admissibility gate:** Fail-closed. Any hard safety trigger (no pulse, loss of control, low observability, incoherent signals) forces inadmissibility regardless of other factors.
3. **Scalar reserve:** A continuous metric U ∈ [0,1] estimating distance to failure, computed from energy integrity, mechanical output, oxygen/resource delivery, respiration/exchange, coherence, trend, and observability.

The framework is:
- **Platform agnostic:** Works on any Git host (GitHub, GitLab, Gitea, SourceHut, local).
- **Formally verifiable:** Safety invariants are independently testable.
- **Extensible:** New domains add only configuration, not core logic.
- **Auditable:** Every evaluation is hashed and logged via commit-time binding.

### 1.3 Related Work

**Medical triage systems** (START, SALT) prioritize patients but do not separate sufficiency from admissibility. **Robot safety standards** (ISO 10218, ISO/TS 15066) specify stopping conditions but lack a unified scalar reserve metric. **AI safety frameworks** (Constitutional AI, RLHF) focus on training-time alignment, not commit-time governance. Our work fills the gap between these approaches by providing a single primitive that governs all three.

---

## 2. Formal Model

### 2.1 Definitions

Let S be the set of possible sensor inputs, where each input s ∈ S is either:
- **Present:** s = (value, quality, duration_sec)
- **Missing:** s = ⊥

Let R be a sufficiency registry specifying:
- Required signals R_req ⊂ S
- Optional signals R_opt ⊂ S
- Quality thresholds q_min: R_req → [0,1]
- Duration thresholds d_min: R_req → ℝ⁺

**Definition 1 (Sufficiency).** A set of inputs I ⊂ S is *sufficient* under R iff:
∀r ∈ R_req: r ∈ I ∧ quality(r) ≥ q_min(r) ∧ duration(r) ≥ d_min(r)

No optional signal may substitute for a required signal.

### 2.2 Admissibility Gate

Let H be the set of hard triggers:
H = {NO_PULSE, NO_BREATHING, CRITICAL_PERFUSION_FAILURE, LOSS_OF_CONTROL, LOSS_OF_AUTHORITY, LOW_OBSERVABILITY, INCOHERENT_SIGNALS, SUFFICIENCY_FAIL}

**Definition 2 (Admissibility).** A system is *admissible* at commit time t iff:
∀h ∈ H: trigger_h(I_t) = false

Where trigger_h is a boolean predicate over inputs. If any trigger fires, admissible = false. This is a fail-closed gate.

### 2.3 Scalar Reserve

Let F = {E, M, O, R, C, T, Q} be the scalar factors:
- E = energy integrity
- M = mechanical output
- O = oxygen/resource delivery
- R = respiration/exchange
- C = coherence
- T = trend
- Q = observability

**Definition 3 (Scalar).** The scalar reserve U is:
U = ∏_{f ∈ F} clamp(f, floor, 1.0)^{w_f} × Q

Where w_f are domain-specific weights and floor is a per-factor minimum (default 0.05). The observability factor Q is double-weighted: low observability both reduces the scalar and may trigger inadmissibility.

**Definition 4 (Observability-adjusted scalar).** U* = U × Q. If Q < threshold, U* may trigger LOW_OBSERVABILITY.

### 2.4 Triage Levels

| Level | Condition | Action |
|-------|-----------|--------|
| GREEN | admissible ∧ U ≥ 0.8 | Normal operation |
| YELLOW | admissible ∧ U ≥ 0.5 | Degraded — monitor closely |
| ORANGE | admissible ∧ U < 0.5 | Restricted — reduced authority |
| RED | ¬admissible ∧ U > 0.05 | Hard stop — requires reset |
| BLACK | ¬admissible ∧ U ≤ 0.05 | Nonrecoverable — halt, notify oversight |

### 2.5 Commit-Time Binding

Every evaluation produces a CommitRecord:
- timestamp: ISO 8601 UTC
- domain: which domain config was used
- admissible, scalar, level: the decision
- sufficiency_flags, reason_codes: why
- commit_hash: SHA-256 of canonical JSON payload (first 16 chars)

This creates an immutable audit trail suitable for regulatory compliance and forensic replay.

---

## 3. Architecture

### 3.1 Pipeline

```
sensor input → sufficiency registry → sufficiency check →
coherence monitor → admissibility gate → scalar computation →
level assignment → commit binding
```

Each layer is independently testable. The core (sufficiency, admissibility, scalar, coherence, commit_binding) is domain-agnostic. Domain configs (human_medical, robotics, embodied_ai) specify only:
- Required/optional signals
- Quality and duration thresholds
- Scalar weights and floor
- Trend windows
- Coherence rules

### 3.2 Platform Agnosticism

The implementation uses only Python standard library modules (dataclasses, json, hashlib, subprocess, urllib). No GitHub-specific APIs, no cloud dependencies. The StegDB adapter supports four backends:
- git_commit: Write to local file, commit via git
- webhook: POST to HTTP endpoint
- file_drop: Write to shared filesystem
- polling: Read from remote source

This ensures the framework operates on GitHub, GitLab, Gitea, SourceHut, or entirely offline.

### 3.3 Safety Invariants

The following invariants are enforced by the test suite:

1. **Sufficiency invariant:** If required data is missing, diagnosis is not permitted.
2. **Admissibility invariant:** If any hard trigger fires, admissible = false.
3. **Scalar monotonicity:** If any factor degrades (decreases), U does not increase.
4. **Observability dominance:** If Q → 0, U* → 0 regardless of other factors.
5. **Coherence enforcement:** If coherence rules are violated, admissibility = false.
6. **Commit immutability:** Once a CommitRecord is created, its hash cannot change.
7. **Domain equivalence:** The same core pipeline runs for all domains; only config differs.

---

## 4. Implementation

### 4.1 Open Source Repository

https://github.com/GCAT-BCAT-Engine/Triage

- Language: Python 3.10+
- Dependencies: jsonschema (optional, for schema validation)
- Test framework: pytest
- Lint: ruff
- Format: black
- CI: GitHub Actions (matrix: 3.10, 3.11, 3.12)
- License: Apache 2.0 with safety notice

### 4.2 Domain Configurations

**Human medical:** Prioritizes oxygen_delivery (w=1.2), respiration (w=1.2), with 5-minute trend windows. Required: heart_rate, blood_pressure, oxygen_saturation.

**Robotics:** Prioritizes energy_integrity (w=1.2), mechanical_output (w=1.2), with 30-second trend windows. Required: energy_integrity, mechanical_output, control.

**Embodied AI:** Prioritizes coherence (w=1.3), observability (w=1.2), with 1-minute trend windows. Required: coherence, observability, authority.

### 4.3 StegDB Integration

Triage emits governance events to StegDB via a platform-agnostic adapter. Events include triage.evaluation (every evaluation), triage.canonical_update_request (when config drift is detected), and repo.architecture_guard (structural validation). StegDB can push canonical updates back to Triage, enabling bidirectional governance.

---

## 5. Discussion

### 5.1 Limitations

This is a governance primitive, not a complete safety system. It does not:
- Replace emergency responders or medical professionals
- Perform formal verification of hardware
- Handle adversarial sensor attacks (though incoherence detection helps)
- Guarantee correctness of sensor inputs (only their sufficiency and coherence)

### 5.2 Future Work

- **Temporal modeling:** Extend trend from scalar derivative to full time-series analysis
- **Probabilistic factors:** Replace crisp thresholds with Bayesian confidence intervals
- **Multi-agent triage:** Extend to fleets of robots or distributed AI systems
- **Regulatory alignment:** Map triage levels to FDA/CE/FAA safety categories
- **Hardware integration:** Bind scalar factors directly to sensor firmware

### 5.3 Ethical Considerations

The framework makes no diagnostic claims — it only governs whether action is admissible. This is intentional: we separate governance (should we act?) from diagnosis (what is wrong?). The safety notice in the license explicitly disclaims medical device status.

---

## 6. Conclusion

Commit-Time Triage is a minimal, domain-agnostic governance primitive that separates sufficiency, admissibility, and scalar reserve. It provides fail-closed safety guarantees, formalizes safety invariants, and creates immutable audit trails. The same architecture governs human medical, robotic, and AI systems — demonstrating that the underlying governance problem is universal, not domain-specific.

We release the implementation as open source to enable independent validation, extension, and adoption across safety-critical domains.

---

## References

1. START Triage System, US Department of Health and Human Services.
2. ISO 10218-1:2011, Robots and robotic devices — Safety requirements.
3. ISO/TS 15066:2016, Collaborative robots — Safety requirements.
4. Bai, Y., et al. "Constitutional AI: Harmlessness from AI Feedback." arXiv:2212.08073.
5. Christiano, P., et al. "Deep Reinforcement Learning from Human Preferences." NeurIPS 2017.
6. Leveson, N. "Engineering a Safer World." MIT Press, 2012.
7. GCAT-BCAT-Engine. "Commit-Time Triage Engine." GitHub repository, 2026.

---

## Appendix A: Safety Invariant Proofs

### A.1 Sufficiency Invariant

*Theorem:* If required data is missing, diagnosis is not permitted.

*Proof:* SufficiencyRegistry.check() returns sufficient = false if any required signal is missing, has quality < q_min, or duration < d_min. The evaluator checks sufficiency before admissibility. If sufficient = false, the admissibility gate receives sufficiency_ok = false and appends SUFFICIENCY_FAIL to triggers. Therefore admissible = false. ∎

### A.2 Admissibility Invariant

*Theorem:* If any hard trigger fires, admissible = false.

*Proof:* AdmissibilityGate.check() collects all triggered hard safety conditions into triggers list. It returns admissible = (len(triggers) == 0). Therefore if any trigger fires, admissible = false. ∎

### A.3 Scalar Monotonicity

*Theorem:* If any factor f ∈ F decreases (and no other factor increases), U does not increase.

*Proof:* U = ∏ clamp(f_i, floor, 1)^{w_i} × Q. Each term is non-negative and exponentiation with w_i > 0 is monotonic in [floor, 1]. If f_j decreases, clamp(f_j) decreases, so the product decreases. The observability double-weighting preserves this: Q is a factor in the product and multiplied again. ∎

---

## Appendix B: Patent-Relevant Claims

### Claim 1: The Governance Primitive

A computer-implemented method for commit-time triage of embodied systems, comprising:
(a) receiving sensor inputs at a decision commit point;
(b) evaluating sufficiency of the sensor inputs against a registry of required signals;
(c) evaluating admissibility through a fail-closed gate testing hard safety triggers;
(d) computing a scalar reserve metric from multiple degradation factors;
(e) assigning a triage level based on admissibility and scalar reserve;
(f) binding the evaluation to an immutable commit record with a cryptographic hash.

### Claim 2: Domain Agnosticism

The method of Claim 1, wherein the same core pipeline operates across human medical, robotic, and AI domains without modification, with domain-specific behavior determined solely by configuration parameters.

### Claim 3: Bidirectional Canonical Governance

The method of Claim 1, further comprising:
(g) emitting governance events to a canonical database;
(h) receiving canonical updates from the canonical database;
(i) applying received canonical updates to modify local configuration.

### Claim 4: Observability-Adjusted Scalar

The method of Claim 1, wherein the scalar reserve is adjusted by an observability factor, and low observability both reduces the scalar reserve and may trigger inadmissibility.

### Claim 5: Coherence Monitoring

The method of Claim 1, further comprising evaluating coherence between sensor signals, and triggering inadmissibility when signals violate predefined coherence rules.

---

*End of draft*
