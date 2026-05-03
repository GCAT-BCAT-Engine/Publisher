# Cost Tensor Test Specification

**Formal Test Specification v0.1.0-draft**  
**Org:** ECAT-ICAT-Formal  
**Date:** 2026-05-03  
**Status:** Deterministic test layer for Cost Tensor v0.2.0

---

## 0. Purpose and Scope

This document defines deterministic tests for the StegVerse Cost Tensor formalism.

The Cost Tensor admissibility theorem states:

\[
ALLOW(\Delta D)
\iff
GCAT\_PASS
\land
BCAT\_PASS
\land
ECAT\_PASS
\land
ICAT\_PASS
\land
\mathcal C(\Delta D)\le Budget(\Delta D,t)
\]

The purpose of this test specification is to verify that every admissibility path produces the expected outcome:

\[
Outcome\in\{ALLOW,DENY,FAIL\_CLOSED\}
\]

The tests are designed to prove:

1. each gate fails correctly;
2. unknown basis always fails closed;
3. budget overflow denies;
4. all gates passing with budget sufficiency allows;
5. DENY and FAIL_CLOSED remain distinct;
6. receipts are emitted for all completed evaluations;
7. replay produces the same result.

---

## 1. Test Completion Criteria

This test layer is complete when:

1. every Cost Tensor gate has at least one passing test;
2. every Cost Tensor gate has at least one failing test;
3. every required unknown/unavailable basis has at least one FAIL_CLOSED test;
4. every cost component is included in at least one scalar-cost test;
5. every outcome type is covered:
   - ALLOW;
   - DENY;
   - FAIL_CLOSED;
6. every emitted receipt can be replayed deterministically;
7. replayed outcome equals original outcome;
8. all tests run under deterministic seed execution.

---

## 2. Deterministic Assumptions

All tests use fixed seed execution unless otherwise specified.

```text
seed = 42
```

All numeric values are assumed to be exact for test purposes unless the test explicitly defines tolerance.

Default floating-point tolerance:

\[
\epsilon = 10^{-9}
\]

A scalar value \(a\) equals expected value \(b\) if:

\[
|a-b|\le\epsilon
\]

---

## 3. Outcome Semantics

### 3.1 ALLOW

ALLOW means:

\[
GCAT\_PASS=true
\]

\[
BCAT\_PASS=true
\]

\[
ECAT\_PASS=true
\]

\[
ICAT\_PASS=true
\]

\[
\mathcal C(\Delta D)\le Budget(\Delta D,t)
\]

and receipt emission succeeds.

### 3.2 DENY

DENY means the system had sufficient basis to evaluate the transition and found it inadmissible.

Examples:

- invalid state geometry;
- consequence exceeds bound;
- reputation below threshold;
- stake below minimum;
- historical anomaly above threshold;
- proof verifies false;
- witness quorum fails;
- conservation law fails;
- inverse constraint fails;
- scalar cost exceeds budget.

### 3.3 FAIL_CLOSED

FAIL_CLOSED means the system lacked sufficient basis to safely evaluate, bind, or record the transition.

Examples:

- transition object incomplete;
- policy unavailable;
- budget unavailable;
- gate evaluation unavailable;
- entity state unavailable;
- required consent unavailable;
- proof unavailable;
- witness set unavailable;
- conservation law unresolved;
- inverse constraint unresolved;
- receipt emission failure.

---

## 4. Base Test Vector Schema

Each test vector must be encoded as JSON.

```json
{
  "test_id": "CT-000",
  "name": "descriptive test name",
  "seed": 42,
  "transition": {
    "entity_id": "entity.alpha",
    "data_id": "data.demo",
    "category": "metadata",
    "pre_state_hash": "hash_pre",
    "post_state_hash": "hash_post",
    "delta_hash": "hash_delta",
    "policy_hash": "hash_policy",
    "commit_time": "2026-05-03T00:00:00Z",
    "complete": true
  },
  "budget": {
    "available": true,
    "amount": 100.0
  },
  "gcat": {
    "available": true,
    "pass": true,
    "cost": 10.0
  },
  "bcat": {
    "available": true,
    "pass": true,
    "cost": 10.0
  },
  "ecat": {
    "available": true,
    "pass": true,
    "cost": 10.0,
    "reputation": 0.9,
    "r_min": 0.5,
    "stake_risk": 100.0,
    "stake_min": 10.0,
    "h": 0.1,
    "h_max": 1.0,
    "consent": true,
    "co_owner_rejected": false
  },
  "icat": {
    "available": true,
    "pass": true,
    "cost": 10.0,
    "proof_available": true,
    "proof_valid": true,
    "witness_available": true,
    "witness_score": 1.0,
    "witness_min": 0.67,
    "n_valid": 3,
    "n_min": 2,
    "independent": true,
    "conservation_available": true,
    "conservation_pass": true,
    "inverse_available": true,
    "inverse_pass": true
  },
  "receipt": {
    "emit_ok": true
  },
  "expected": {
    "outcome": "ALLOW",
    "reason": "cost_tensor_admissible",
    "total_cost": 40.0
  }
}
```

---

## 5. Required Test Groups

The required groups are:

1. baseline ALLOW tests;
2. transition object tests;
3. policy and budget availability tests;
4. GCAT tests;
5. BCAT tests;
6. ECAT tests;
7. ICAT tests;
8. scalar cost and budget tests;
9. receipt tests;
10. replay tests;
11. conservation tests;
12. outcome distinction tests.

---

## 6. Baseline ALLOW Tests

### CT-001: Full Admissible Transition

**Purpose:** Prove that a transition is allowed when all gates pass and total cost is within budget.

Input:

\[
GCAT=true,\ BCAT=true,\ ECAT=true,\ ICAT=true
\]

\[
\mathcal C=40,\quad Budget=100
\]

Expected:

```text
ALLOW
reason = cost_tensor_admissible
total_cost = 40.0
```

### CT-002: Boundary Budget Allow

**Purpose:** Prove that equality with budget is admissible.

Input:

\[
\mathcal C=100,\quad Budget=100
\]

Expected:

```text
ALLOW
reason = cost_tensor_admissible
```

---

## 7. Transition Object Tests

### CT-010: Incomplete Transition Object

Input:

```text
transition.complete = false
```

Expected:

```text
FAIL_CLOSED
reason = transition_object_incomplete
```

### CT-011: Missing Pre-State Hash

Input:

```text
pre_state_hash = null
```

Expected:

```text
FAIL_CLOSED
reason = transition_object_incomplete
```

### CT-012: Missing Post-State Hash

Input:

```text
post_state_hash = null
```

Expected:

```text
FAIL_CLOSED
reason = transition_object_incomplete
```

### CT-013: Missing Delta Hash

Input:

```text
delta_hash = null
```

Expected:

```text
FAIL_CLOSED
reason = transition_object_incomplete
```

---

## 8. Policy and Budget Availability Tests

### CT-020: Policy Unavailable

Input:

```text
policy_hash = null
```

Expected:

```text
FAIL_CLOSED
reason = policy_unavailable
```

### CT-021: Budget Unavailable

Input:

```text
budget.available = false
```

Expected:

```text
FAIL_CLOSED
reason = budget_unavailable
```

### CT-022: Negative Budget

Input:

```text
budget.amount = -1.0
```

Expected:

```text
FAIL_CLOSED
reason = budget_invalid
```

---

## 9. GCAT Tests

### CT-030: GCAT Boundary Failure

Input:

```text
gcat.available = true
gcat.pass = false
```

Expected:

```text
DENY
reason = gcat_boundary_failure
```

### CT-031: GCAT Evaluation Unknown

Input:

```text
gcat.available = false
```

Expected:

```text
FAIL_CLOSED
reason = gcat_unknown
```

### CT-032: GCAT Negative Cost

Input:

```text
gcat.cost = -1.0
```

Expected:

```text
FAIL_CLOSED
reason = gcat_cost_invalid
```

---

## 10. BCAT Tests

### CT-040: BCAT Consequence Failure

Input:

```text
bcat.available = true
bcat.pass = false
```

Expected:

```text
DENY
reason = bcat_consequence_failure
```

### CT-041: BCAT Bound Unknown

Input:

```text
bcat.available = false
```

Expected:

```text
FAIL_CLOSED
reason = bcat_unknown
```

### CT-042: BCAT Negative Cost

Input:

```text
bcat.cost = -1.0
```

Expected:

```text
FAIL_CLOSED
reason = bcat_cost_invalid
```

---

## 11. ECAT Tests

### CT-050: ECAT Entity State Unknown

Input:

```text
ecat.available = false
```

Expected:

```text
FAIL_CLOSED
reason = ecat_unknown
```

### CT-051: Reputation Below Minimum

Input:

```text
reputation = 0.4
r_min = 0.5
```

Expected:

```text
DENY
reason = ecat_reputation_failure
```

### CT-052: Reputation Zero

Input:

```text
reputation = 0.0
```

Expected:

```text
FAIL_CLOSED
reason = ecat_reputation_null
```

### CT-053: Reputation Out of Bounds Above One

Input:

```text
reputation = 1.1
```

Expected:

```text
FAIL_CLOSED
reason = ecat_reputation_invalid
```

### CT-054: Reputation Out of Bounds Below Zero

Input:

```text
reputation = -0.1
```

Expected:

```text
FAIL_CLOSED
reason = ecat_reputation_invalid
```

### CT-055: Stake Below Minimum

Input:

```text
stake_risk = 5.0
stake_min = 10.0
```

Expected:

```text
DENY
reason = ecat_stake_failure
```

### CT-056: Stake Negative

Input:

```text
stake_risk = -1.0
```

Expected:

```text
FAIL_CLOSED
reason = ecat_stake_invalid
```

### CT-057: Historical Anomaly Above Threshold

Input:

```text
h = 2.0
h_max = 1.0
```

Expected:

```text
DENY
reason = ecat_historical_anomaly
```

### CT-058: Historical Anomaly Infinite

Input:

```text
h = Infinity
```

Expected:

```text
FAIL_CLOSED
reason = ecat_historical_impossible
```

### CT-059: Consent Unavailable

Input:

```text
consent = null
```

Expected:

```text
FAIL_CLOSED
reason = consent_unavailable
```

### CT-060: Required Co-Owner Rejects

Input:

```text
co_owner_rejected = true
```

Expected:

```text
FAIL_CLOSED
reason = co_owner_rejected
```

### CT-061: ECAT Negative Cost

Input:

```text
ecat.cost = -1.0
```

Expected:

```text
FAIL_CLOSED
reason = ecat_cost_invalid
```

---

## 12. ICAT Tests

### CT-070: ICAT State Unknown

Input:

```text
icat.available = false
```

Expected:

```text
FAIL_CLOSED
reason = icat_unknown
```

### CT-071: Proof Unavailable

Input:

```text
proof_available = false
```

Expected:

```text
FAIL_CLOSED
reason = proof_unavailable
```

### CT-072: Proof Invalid

Input:

```text
proof_available = true
proof_valid = false
```

Expected:

```text
DENY
reason = proof_invalid
```

### CT-073: Witness Set Unavailable

Input:

```text
witness_available = false
```

Expected:

```text
FAIL_CLOSED
reason = witness_unavailable
```

### CT-074: Witness Independence Unknown

Input:

```text
independent = null
```

Expected:

```text
FAIL_CLOSED
reason = witness_independence_unknown
```

### CT-075: Witness Non-Independent

Input:

```text
independent = false
```

Expected:

```text
DENY
reason = witness_non_independent
```

### CT-076: Witness Score Below Minimum

Input:

```text
witness_score = 0.5
witness_min = 0.67
```

Expected:

```text
DENY
reason = witness_quorum_failure
```

### CT-077: Valid Witness Count Below Minimum

Input:

```text
n_valid = 1
n_min = 2
```

Expected:

```text
DENY
reason = witness_quorum_failure
```

### CT-078: Conservation Set Unavailable

Input:

```text
conservation_available = false
```

Expected:

```text
FAIL_CLOSED
reason = conservation_unavailable
```

### CT-079: Conservation Failure

Input:

```text
conservation_available = true
conservation_pass = false
```

Expected:

```text
DENY
reason = conservation_failure
```

### CT-080: Inverse Constraint Set Unavailable

Input:

```text
inverse_available = false
```

Expected:

```text
FAIL_CLOSED
reason = inverse_unavailable
```

### CT-081: Inverse Constraint Failure

Input:

```text
inverse_available = true
inverse_pass = false
```

Expected:

```text
DENY
reason = inverse_failure
```

### CT-082: ICAT Negative Cost

Input:

```text
icat.cost = -1.0
```

Expected:

```text
FAIL_CLOSED
reason = icat_cost_invalid
```

---

## 13. Scalar Cost and Budget Tests

### CT-090: Budget Overflow

Input:

\[
\$G=30,\quad \$B=30,\quad \$E=30,\quad \$I=30
\]

\[
\mathcal C=120,\quad Budget=100
\]

Expected:

```text
DENY
reason = budget_exceeded
total_cost = 120.0
```

### CT-091: Cost Exactly Equals Budget

Input:

\[
\$G=25,\quad \$B=25,\quad \$E=25,\quad \$I=25
\]

\[
\mathcal C=100,\quad Budget=100
\]

Expected:

```text
ALLOW
reason = cost_tensor_admissible
total_cost = 100.0
```

### CT-092: Zero Cost Transition

Input:

\[
\$G=0,\quad \$B=0,\quad \$E=0,\quad \$I=0
\]

\[
\mathcal C=0,\quad Budget=0
\]

Expected:

```text
ALLOW
reason = cost_tensor_admissible
total_cost = 0.0
```

### CT-093: Negative Total Cost Defense

Input:

```text
gcat.cost = -10
bcat.cost = 0
ecat.cost = 0
icat.cost = 0
```

Expected:

```text
FAIL_CLOSED
reason = gcat_cost_invalid
```

---

## 14. Receipt Tests

### CT-100: Receipt Emission Failure

Input:

```text
receipt.emit_ok = false
```

Expected:

```text
FAIL_CLOSED
reason = receipt_emission_failed
```

### CT-101: Receipt Contains Required Fields

Input:

```text
all gates pass
receipt.emit_ok = true
```

Expected receipt fields:

```text
transition_id
entity_id
data_id
pre_state_hash
post_state_hash
delta_hash
policy_hash
budget_id
commit_time
gcat
bcat
ecat
icat
total_cost
budget
outcome
reason
prev_receipt_hash
receipt_hash
signer
```

Expected:

```text
ALLOW
receipt_valid = true
```

### CT-102: Receipt Hash Binds Outcome

Input:

```text
receipt emitted, then outcome mutated
```

Expected:

```text
replay_verification = false
reason = receipt_hash_mismatch
```

---

## 15. Replay Tests

### CT-110: Replay ALLOW Receipt

Input:

```text
receipt.outcome = ALLOW
original context available
```

Expected:

```text
replay_outcome = ALLOW
replay_matches_original = true
```

### CT-111: Replay DENY Receipt

Input:

```text
receipt.outcome = DENY
original context available
```

Expected:

```text
replay_outcome = DENY
replay_matches_original = true
```

### CT-112: Replay FAIL_CLOSED Receipt

Input:

```text
receipt.outcome = FAIL_CLOSED
original context available
```

Expected:

```text
replay_outcome = FAIL_CLOSED
replay_matches_original = true
```

### CT-113: Replay Context Missing

Input:

```text
receipt available
original context unavailable
```

Expected:

```text
FAIL_CLOSED
reason = replay_context_unavailable
```

---

## 16. Conservation Tests

### CT-120: Ownership Weight Conservation

Input:

```text
weights = [0.25, 0.25, 0.50]
```

Expected:

\[
\sum W=1.0
\]

```text
PASS
```

### CT-121: Ownership Weight Sum Invalid

Input:

```text
weights = [0.25, 0.25, 0.25]
```

Expected:

```text
FAIL_CLOSED
reason = ownership_weight_conservation_failure
```

### CT-122: Reputation Bound Conservation

Input:

```text
reputation = 0.75
```

Expected:

```text
PASS
```

### CT-123: Proof Score Bound Conservation

Input:

```text
proof_score = 1.2
```

Expected:

```text
FAIL_CLOSED
reason = proof_score_invalid
```

### CT-124: Witness Score Bound Conservation

Input:

```text
witness_score = -0.1
```

Expected:

```text
FAIL_CLOSED
reason = witness_score_invalid
```

---

## 17. Outcome Distinction Tests

### CT-130: Invalid Proof Is DENY

Input:

```text
proof_available = true
proof_valid = false
```

Expected:

```text
DENY
not FAIL_CLOSED
```

### CT-131: Missing Proof Is FAIL_CLOSED

Input:

```text
proof_available = false
```

Expected:

```text
FAIL_CLOSED
not DENY
```

### CT-132: Low Reputation Is DENY

Input:

```text
reputation = 0.4
r_min = 0.5
```

Expected:

```text
DENY
not FAIL_CLOSED
```

### CT-133: Unknown Reputation Is FAIL_CLOSED

Input:

```text
reputation = null
```

Expected:

```text
FAIL_CLOSED
not DENY
```

### CT-134: Budget Overflow Is DENY

Input:

```text
total_cost = 120
budget = 100
```

Expected:

```text
DENY
not FAIL_CLOSED
```

### CT-135: Missing Budget Is FAIL_CLOSED

Input:

```text
budget.available = false
```

Expected:

```text
FAIL_CLOSED
not DENY
```

---

## 18. Minimal Test Vector Set

The minimum required executable test vector set is:

```text
test_vectors/
  CT-001_full_allow.json
  CT-002_budget_boundary_allow.json
  CT-010_transition_incomplete_fail_closed.json
  CT-020_policy_unavailable_fail_closed.json
  CT-021_budget_unavailable_fail_closed.json
  CT-030_gcat_boundary_deny.json
  CT-031_gcat_unknown_fail_closed.json
  CT-040_bcat_consequence_deny.json
  CT-041_bcat_unknown_fail_closed.json
  CT-051_ecat_reputation_deny.json
  CT-052_ecat_reputation_zero_fail_closed.json
  CT-055_ecat_stake_deny.json
  CT-057_ecat_anomaly_deny.json
  CT-059_ecat_consent_unknown_fail_closed.json
  CT-060_ecat_co_owner_rejected_fail_closed.json
  CT-071_icat_proof_unavailable_fail_closed.json
  CT-072_icat_proof_invalid_deny.json
  CT-073_icat_witness_unavailable_fail_closed.json
  CT-076_icat_witness_quorum_deny.json
  CT-078_icat_conservation_unavailable_fail_closed.json
  CT-079_icat_conservation_failure_deny.json
  CT-080_icat_inverse_unavailable_fail_closed.json
  CT-081_icat_inverse_failure_deny.json
  CT-090_budget_overflow_deny.json
  CT-100_receipt_emission_fail_closed.json
  CT-110_replay_allow.json
  CT-111_replay_deny.json
  CT-112_replay_fail_closed.json
```

This set is sufficient to validate the first executable reference implementation.

The full suite should include all tests defined in this document.

---

## 19. Required Test Report Format

The test runner must emit a machine-readable report:

```json
{
  "schema": "stegverse.cost_tensor.test_report.v1",
  "seed": 42,
  "suite": "COST_TENSOR_TEST_SPEC_v0.1.0",
  "started_at": "2026-05-03T00:00:00Z",
  "finished_at": "2026-05-03T00:00:01Z",
  "summary": {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "skipped": 0
  },
  "results": [
    {
      "test_id": "CT-001",
      "name": "Full Admissible Transition",
      "expected": "ALLOW",
      "actual": "ALLOW",
      "reason_expected": "cost_tensor_admissible",
      "reason_actual": "cost_tensor_admissible",
      "passed": true,
      "receipt_hash": "<hash>"
    }
  ]
}
```

The report must be written to:

```text
brain_reports/cost_tensor_test_report.json
```

and a line-delimited receipt index must be written to:

```text
brain_reports/cost_tensor_receipts.jsonl
```

---

## 20. GitHub Actions Requirements

A compliant workflow must:

1. run on `workflow_dispatch`;
2. run on pull requests touching Cost Tensor files;
3. install the minimal Python runtime;
4. run the deterministic test suite;
5. write reports under `brain_reports/`;
6. upload `brain_reports/` as an artifact;
7. fail the workflow if any required test fails.

Recommended workflow name:

```text
Cost Tensor Deterministic Tests
```

Recommended command:

```text
python cost_tensor_reference.py --vectors test_vectors --out brain_reports
```

---

## 21. Open Questions

1. Should unknown co-owner rejection remain FAIL_CLOSED, or should explicit rejection become DENY in future legal-policy modes?
2. Should null reputation always FAIL_CLOSED, or should recovery transitions use a separate appeal gate?
3. Should budget equality remain ALLOW for all categories, or should high-risk categories require strict inequality?
4. Should proof invalidity always DENY, or should malformed proof remain FAIL_CLOSED?
5. How should replay behave when external context is intentionally privacy-hidden?
6. Should witness non-independence be DENY or FAIL_CLOSED when collusion cannot be proven but cannot be excluded?
7. Should receipt emission failure halt the entire runtime or only the attempted transition?
8. Should reconstruction-quality tests be part of ICAT or part of a later Rigel recoverability extension?

---

## 22. Version Note

This test specification converts the Cost Tensor v0.2.0 formalism into deterministic executable expectations.

It defines:

1. base JSON test vector schema;
2. ALLOW, DENY, and FAIL_CLOSED semantics;
3. required tests for GCAT, BCAT, ECAT, ICAT, budget, receipts, replay, conservation, and outcome distinction;
4. minimum executable test vector set;
5. required machine-readable test report format;
6. GitHub Actions requirements.

The next artifact is:

```text
cost_tensor_reference.py
```

followed by:

```text
test_vectors/*.json
```

and a GitHub Actions workflow.

---

**Document:** COST_TENSOR_TEST_SPEC.md  
**Version:** 0.1.0-draft  
**Date:** 2026-05-03  
**Org:** ECAT-ICAT-Formal
