# StegVerse Cost Tensor Specification

**Integrating GCAT / BCAT / ECAT / ICAT for Financial Conversion**  
**Version:** 0.2.0-draft  
**Date:** 2026-05-03  
**Status:** Integrated formal draft after ECAT v0.2.0 and ICAT v0.1.0

---

## 0. Purpose and Scope

This specification defines the cost of changing one unit of data, or a data transition \(\Delta D\), in terms of financial capital.

The Cost Tensor formalism integrates four admissibility layers:

\[
C^{\mu\nu}(\Delta D)
=
G^{\mu\nu}
+
B^{\mu\nu}
+
E^{\mu\nu}
+
I^{\mu\nu}
\]

where:

- \(G^{\mu\nu}\): GCAT geometric admissibility component.
- \(B^{\mu\nu}\): BCAT bounded consequence component.
- \(E^{\mu\nu}\): ECAT entity constraint component.
- \(I^{\mu\nu}\): ICAT integrity constraint component.

The purpose of the Cost Tensor is not merely to price computation.

It determines whether a proposed transition is economically, geometrically, consequentially, entity-wise, and integrity-wise admissible at commit time.

A transition is ALLOW only if all required admissibility gates pass and the scalarized total cost is within the current transition budget.

---

## 1. Core Conversion Problem

### 1.1 Goal

Define the cost of changing data:

\[
\Delta D:S_t\rightarrow S_{t+1}
\]

in terms of financial capital:

\[
\mathcal C(\Delta D)\in\mathbb R_{\ge0}
\]

### 1.2 Constraint

All cost components must resolve to a common scalar denominator before comparison to a financial budget.

Therefore, the raw tensor:

\[
C^{\mu\nu}(\Delta D)
\]

must be scalarized before budget comparison.

### 1.3 Invariant

No transition is ALLOW unless:

\[
\mathcal C(\Delta D)\le Budget(\Delta D,t)
\]

and all required admissibility gates pass at commit time.

### 1.4 Commit-Time Rule

All values used in the admissibility decision must be current at the commit boundary:

\[
t=t_{commit}
\]

Authority, budget, proof, witness state, policy, entity state, and consequence bounds must be evaluated against the state that exists when the transition becomes effect-capable.

No prior approval is sufficient by itself.

---

## 2. Transition Object

A proposed transition is represented as:

\[
\Theta(\Delta D)
=
(e,D,S_t,S_{t+1},Policy_t,Budget_t,t_{commit})
\]

where:

- \(e\) is the acting entity.
- \(D\) is the data object or data region being changed.
- \(S_t\) is the pre-transition state.
- \(S_{t+1}\) is the proposed post-transition state.
- \(Policy_t\) is the current policy/admissibility basis.
- \(Budget_t\) is the current allocated budget for the transition.
- \(t_{commit}\) is the commit-time boundary.

The transition delta is:

\[
\Delta D=S_{t+1}-S_t
\]

A transition may not be evaluated without a resolvable transition object.

If the transition object is incomplete at commit time:

\[
\Theta(\Delta D)=unknown\Rightarrow FAIL\_CLOSED
\]

---

## 3. Tensor Form

The Cost Tensor is:

\[
C^{\mu\nu}(\Delta D)
=
G^{\mu\nu}(\Delta D)
+
B^{\mu\nu}(\Delta D)
+
E^{\mu\nu}(e,\Delta D,t)
+
I^{\mu\nu}(\Delta D,t)
\]

Each tensor component may encode local geometry, coupling, curvature, constraint pressure, or risk interaction inside its own domain.

However, admission is not performed by comparing a tensor directly to a scalar budget.

Admission uses scalarized cost:

\[
\mathcal C(\Delta D)
=
\Phi
\left(
C^{\mu\nu}(\Delta D),
\Delta S
\right)
\]

The default scalarized form is:

\[
\mathcal C(\Delta D)
=
\$G(\Delta D)
+
\$B(\Delta D)
+
\$E(e,\Delta D,t)
+
\$I(\Delta D,t)
\]

---

## 4. GCAT Component

### 4.1 Purpose

GCAT measures the geometric and physical cost of moving from the pre-transition state to the proposed post-transition state.

GCAT asks:

\[
\textbf{Can this state transition exist within the admissible state geometry?}
\]

### 4.2 Tensor Form

\[
G^{\mu\nu}
=
g^{\mu\nu}
(\Delta S_\mu\Delta S_\nu)
\]

where \(g^{\mu\nu}\) is the GCAT metric tensor over the state manifold.

### 4.3 Operational Cost

The scalar GCAT cost is:

\[
\$G
=
(E_{energy}P_{energy})
+
(F_{compute}P_{compute})
+
(B_{storage}P_{storage})
+
(B_{bandwidth}P_{bandwidth})
\]

where:

- \(E_{energy}\): physical energy cost.
- \(P_{energy}\): unit energy price.
- \(F_{compute}\): compute work required to validate transition.
- \(P_{compute}\): unit compute price.
- \(B_{storage}\): bytes required to persist state and receipts.
- \(P_{storage}\): unit storage price.
- \(B_{bandwidth}\): bytes required to transmit state, receipts, or proofs.
- \(P_{bandwidth}\): unit bandwidth price.

### 4.4 GCAT Gate

\[
GCAT\_PASS(\Delta D,t)
\]

requires that the transition remain inside the admissible GCAT region at commit time.

If GCAT cannot evaluate the transition geometry:

\[
GCAT\_Eval=unknown\Rightarrow FAIL\_CLOSED
\]

If the proposed transition violates the GCAT admissibility boundary:

\[
GCAT\_PASS=false\Rightarrow DENY
\]

---

## 5. BCAT Component

### 5.1 Purpose

BCAT measures downstream consequence, bounded cascade risk, reconstruction cost, fork exposure, and governance friction.

BCAT asks:

\[
\textbf{Can the consequence of this transition remain bounded and recoverable?}
\]

### 5.2 Tensor Form

\[
B^{\mu\nu}
=
b^{\mu\nu}
(Impact_\mu Impact_\nu)
\]

where \(b^{\mu\nu}\) encodes consequence geometry.

### 5.3 Operational Cost

The scalar BCAT cost is:

\[
\$B
=
(N_{cascade}C_{update})
+
(P_{fork}C_{recovery})
+
(T_{confirm}C_{validator\_opportunity})
+
C_{reconstruction}
\]

where:

- \(N_{cascade}\): number of dependent states affected.
- \(C_{update}\): cost to update one dependent state.
- \(P_{fork}\): probability of consensus or state split.
- \(C_{recovery}\): cost of recovery if fork/split occurs.
- \(T_{confirm}\): confirmation time.
- \(C_{validator\_opportunity}\): validator opportunity cost.
- \(C_{reconstruction}\): cost to reconstruct state if transition fails.

### 5.4 BCAT Gate

\[
BCAT\_PASS(\Delta D,t)
\]

requires that the transition remain within bounded consequence and recoverability limits.

If consequence cannot be bounded:

\[
BCAT\_Bound=unknown\Rightarrow FAIL\_CLOSED
\]

If downstream consequence exceeds admissible bounds:

\[
BCAT\_PASS=false\Rightarrow DENY
\]

---

## 6. ECAT Component

### 6.1 Purpose

ECAT measures whether the acting entity is admissible to perform the proposed transition.

ECAT asks:

\[
\textbf{Is this entity allowed to bear, impose, and pay for this transition?}
\]

### 6.2 Entity Primitives

ECAT defines four entity primitives:

\[
R(e,t),\quad S_{risk}(e,t),\quad H(e,\Delta D),\quad W(e,D)
\]

where:

- \(R(e,t)\in[0,1]\): reputation.
- \(S_{risk}(e,t)\ge0\): locked slashable risk-bearing stake.
- \(H(e,\Delta D)\in[0,\infty)\): historical consistency deviation.
- \(W(e,D)\in[0,1]\): authority or co-ownership weight over data \(D\).

### 6.3 Scalar ECAT Cost

The scalar ECAT cost is:

\[
\$E(e,\Delta D,t)
=
C_R+C_S+C_H+C_W
\]

where:

\[
C_R
=
\lambda_R C_{base}(1-R(e,t))
\]

\[
C_S
=
\lambda_S
\max
\left(
0,
S_{min}(\Delta D)-S_{risk}(e,t)
\right)
\]

\[
C_H
=
\lambda_H C_{base}H(e,\Delta D)
\]

\[
C_W
=
\lambda_W
\sum_{o\in Owners(D)}
W(o,D)C_{request}(o)
\]

### 6.4 ECAT Tensor-Compatible Form

Define:

\[
\epsilon(e,\Delta D,t)
=
\begin{bmatrix}
1-R(e,t)\\
\frac{\max(0,S_{min}(\Delta D)-S_{risk}(e,t))}{S_{min}(\Delta D)}\\
\bar H(e,\Delta D)\\
\bar C_W(e,\Delta D)
\end{bmatrix}
\]

Then a quadratic ECAT scalar may be represented as:

\[
\$E
=
C_{base}\epsilon^\top M_E\epsilon
\]

where:

\[
M_E\succeq0
\]

The linear scalar form is the default minimum implementation.

### 6.5 ECAT Gate

\[
ECAT\_PASS(e,\Delta D,t)
\]

requires:

\[
R(e,t)\ge R_{min}(\Delta D)
\]

\[
S_{risk}(e,t)\ge S_{min}(\Delta D)
\]

\[
H(e,\Delta D)\le H_{max}(\Delta D)
\]

\[
Consent(D,\Delta D)=true
\]

and protected-category rules must pass.

If required entity state is unavailable:

\[
ECAT\_State=unknown\Rightarrow FAIL\_CLOSED
\]

If required co-owner consent is unavailable:

\[
Consent=unknown\Rightarrow FAIL\_CLOSED
\]

If a required co-owner rejects:

\[
Consent=false\Rightarrow FAIL\_CLOSED
\]

---

## 7. ICAT Component

### 7.1 Purpose

ICAT measures whether the transition is provable, witnessed, conserved, reconstructible, and bounded against unintended change.

ICAT asks:

\[
\textbf{Can this transition be proven, witnessed, conserved, and protected against unauthorized non-change violations?}
\]

### 7.2 Integrity Primitives

ICAT defines four integrity primitives:

\[
P(\Delta D,t),\quad A(\Delta D,t),\quad K(\Delta D,t),\quad X(\Delta D,t)
\]

where:

- \(P(\Delta D,t)\in[0,1]\): proof sufficiency.
- \(A(\Delta D,t)\in[0,1]\): witness or attestation sufficiency.
- \(K(\Delta D,t)\in\{0,1\}\): conservation-law preservation.
- \(X(\Delta D,t)\in\{0,1\}\): inverse constraint preservation.

### 7.3 Scalar ICAT Cost

The scalar ICAT cost is:

\[
\$I(\Delta D,t)
=
C_P+C_A+C_K+C_X
\]

where:

\[
C_P
=
\lambda_P C_{proof}(\Delta D,t)
\]

\[
C_A
=
\lambda_A
\sum_{i=1}^{n}
C_{attest}(w_i,\Delta D,t)
\]

\[
C_K
=
\lambda_K
\sum_{j=1}^{m}
C_{check}(k_j,\Delta D,t)
\]

\[
C_X
=
\lambda_X
\sum_{l=1}^{r}
C_{inverse}(x_l,\Delta D,t)
\]

### 7.4 ICAT Tensor-Compatible Form

Define:

\[
\eta(\Delta D,t)
=
\begin{bmatrix}
1-P(\Delta D,t)\\
1-A(\Delta D,t)\\
1-K(\Delta D,t)\\
1-X(\Delta D,t)
\end{bmatrix}
\]

Then:

\[
\$I
=
C_{base}\eta^\top M_I\eta
+
C_{ops}
\]

where:

\[
M_I\succeq0
\]

and \(C_{ops}\) is the direct operational cost of proof, witness, conservation, and inverse checks.

The scalar component form is the default minimum implementation.

### 7.5 ICAT Gate

\[
ICAT\_PASS(\Delta D,t)
\]

requires:

\[
P(\Delta D,t)\ge P_{min}(\Delta D)
\]

\[
A(\Delta D,t)\ge A_{min}(\Delta D)
\]

\[
N_{valid}\ge N_{min}(\Delta D)
\]

\[
Independent(\mathcal W)=1
\]

\[
K(\Delta D,t)=1
\]

\[
X(\Delta D,t)=1
\]

and receipt emission must succeed.

If proof is required but unavailable:

\[
\pi=unknown\Rightarrow FAIL\_CLOSED
\]

If proof verifies false:

\[
P\_PASS=false\Rightarrow DENY
\]

If witnesses are required but unavailable:

\[
\mathcal W=unknown\Rightarrow FAIL\_CLOSED
\]

If conservation or inverse constraints cannot be resolved:

\[
K=unknown\lor X=unknown\Rightarrow FAIL\_CLOSED
\]

---

## 8. Total Scalar Cost

The total scalar transition cost is:

\[
\mathcal C(\Delta D)
=
\$G(\Delta D)
+
\$B(\Delta D)
+
\$E(e,\Delta D,t)
+
\$I(\Delta D,t)
\]

Expanded:

\[
\mathcal C(\Delta D)
=
\left[
(E_{energy}P_{energy})
+
(F_{compute}P_{compute})
+
(B_{storage}P_{storage})
+
(B_{bandwidth}P_{bandwidth})
\right]
\]

\[
+
\left[
(N_{cascade}C_{update})
+
(P_{fork}C_{recovery})
+
(T_{confirm}C_{validator\_opportunity})
+
C_{reconstruction}
\right]
\]

\[
+
\left[
\lambda_R C_{base}(1-R)
+
\lambda_S\max(0,S_{min}-S_{risk})
+
\lambda_H C_{base}H
+
\lambda_W\sum_{o\in Owners(D)}W(o,D)C_{request}(o)
\right]
\]

\[
+
\left[
\lambda_P C_{proof}
+
\lambda_A\sum_i C_{attest}(w_i)
+
\lambda_K\sum_j C_{check}(k_j)
+
\lambda_X\sum_l C_{inverse}(x_l)
\right]
\]

All terms must resolve to the same financial unit before comparison to budget.

---

## 9. Full Admissibility Theorem

### 9.1 Theorem: Commit-Time Cost Tensor Admissibility

For a proposed transition:

\[
\Delta D:S_t\rightarrow S_{t+1}
\]

submitted by entity \(e\) at commit time \(t\), the transition is ALLOW iff:

\[
ALLOW(\Delta D)
\iff
\left[
\begin{array}{c}
GCAT\_PASS(\Delta D,t)\\
BCAT\_PASS(\Delta D,t)\\
ECAT\_PASS(e,\Delta D,t)\\
ICAT\_PASS(\Delta D,t)\\
\mathcal C(\Delta D)\le Budget(\Delta D,t)
\end{array}
\right]
\]

Equivalently:

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
Budget\_PASS
\]

where:

\[
Budget\_PASS
\iff
\mathcal C(\Delta D)\le Budget(\Delta D,t)
\]

### 9.2 Corollary: No Budget-Only Admission

A transition may not be admitted solely because:

\[
\mathcal C(\Delta D)\le Budget(\Delta D,t)
\]

If any gate fails:

\[
GCAT\_PASS=false
\lor
BCAT\_PASS=false
\lor
ECAT\_PASS=false
\lor
ICAT\_PASS=false
\Rightarrow
ALLOW=false
\]

### 9.3 Corollary: No Gate-Only Admission

A transition may not be admitted solely because all gates pass.

If:

\[
\mathcal C(\Delta D)>Budget(\Delta D,t)
\]

then:

\[
ALLOW=false
\]

### 9.4 Corollary: Unknown Basis Fails Closed

If any required state, policy, proof, witness, consent, ownership, consequence bound, or budget is unknown at commit time:

\[
Basis=unknown\Rightarrow FAIL\_CLOSED
\]

---

## 10. DENY vs FAIL_CLOSED

The Cost Tensor distinguishes DENY from FAIL_CLOSED.

### 10.1 DENY

DENY means the system had sufficient basis to evaluate the proposed transition and found it inadmissible.

Examples:

- GCAT boundary violation.
- BCAT consequence exceeds allowed bound.
- ECAT reputation below threshold.
- ECAT stake below minimum.
- ICAT proof verifies false.
- Witness quorum fails.
- Conservation law fails.
- Inverse constraint fails.
- Total scalar cost exceeds budget.

### 10.2 FAIL_CLOSED

FAIL_CLOSED means the system lacked sufficient basis to safely evaluate, bind, or record the transition.

Examples:

- Transition object incomplete.
- Current policy unavailable.
- Entity state unavailable.
- Required proof unavailable.
- Proof parser unavailable.
- Witness set unavailable.
- Witness independence unknown.
- Conservation law set unresolved.
- Inverse constraint set unresolved.
- Required consent unavailable.
- Receipt emission fails.
- Budget unavailable.
- Commit-time state cannot be resolved.

### 10.3 Receipt Requirement

Both DENY and FAIL_CLOSED are first-class governance outcomes.

Every outcome must emit a receipt:

\[
Outcome\in\{ALLOW,DENY,FAIL\_CLOSED\}
\]

If the system cannot emit a receipt:

\[
ReceiptEmit=failed\Rightarrow FAIL\_CLOSED
\]

If the system cannot even record the FAIL_CLOSED event, the runtime must halt the transition and enter recovery diagnostics.

---

## 11. Cost Tensor Gate Logic

Minimum integrated gate logic:

```text
INPUT:
  entity e
  transition ΔD
  data object D
  pre-state S_t
  proposed post-state S_t+1
  policy Policy_t
  commit time t
  budget Budget(ΔD,t)

REQUIRE:
  transition object Θ(ΔD)
  current entity state
  current consequence bounds
  current proof state
  current witness state
  current conservation law set
  current inverse constraint set
  current budget

IF Θ(ΔD) is incomplete:
    FAIL_CLOSED

IF Policy_t unavailable:
    FAIL_CLOSED

IF Budget(ΔD,t) unavailable:
    FAIL_CLOSED

EVALUATE GCAT:
    IF GCAT evaluation unavailable:
        FAIL_CLOSED
    IF GCAT_PASS false:
        DENY

EVALUATE BCAT:
    IF BCAT bound unavailable:
        FAIL_CLOSED
    IF BCAT_PASS false:
        DENY

EVALUATE ECAT:
    IF entity state unavailable:
        FAIL_CLOSED
    IF required consent unavailable:
        FAIL_CLOSED
    IF required co-owner rejects:
        FAIL_CLOSED
    IF ECAT_PASS false:
        DENY

EVALUATE ICAT:
    IF required proof unavailable:
        FAIL_CLOSED
    IF required witness set unavailable:
        FAIL_CLOSED
    IF conservation or inverse set unresolved:
        FAIL_CLOSED
    IF ICAT_PASS false:
        DENY

COMPUTE:
    $G
    $B
    $E
    $I
    C_total = $G + $B + $E + $I

IF C_total > Budget(ΔD,t):
    DENY

EMIT receipt:
    IF receipt emission fails:
        FAIL_CLOSED

ELSE:
    ALLOW
```

---

## 12. Receipt Schema

Every Cost Tensor evaluation must emit a receipt.

Minimum receipt fields:

```json
{
  "schema": "stegverse.cost_tensor.receipt.v1",
  "transition_id": "<id>",
  "entity_id": "<entity>",
  "data_id": "<data-object>",
  "pre_state_hash": "<hash>",
  "post_state_hash": "<hash>",
  "delta_hash": "<hash>",
  "policy_hash": "<hash>",
  "budget_id": "<budget-id>",
  "commit_time": "<timestamp>",
  "gcat": {
    "pass": true,
    "cost": 0.0,
    "basis_hash": "<hash>"
  },
  "bcat": {
    "pass": true,
    "cost": 0.0,
    "basis_hash": "<hash>"
  },
  "ecat": {
    "pass": true,
    "cost": 0.0,
    "basis_hash": "<hash>"
  },
  "icat": {
    "pass": true,
    "cost": 0.0,
    "basis_hash": "<hash>"
  },
  "total_cost": 0.0,
  "budget": 0.0,
  "outcome": "ALLOW",
  "reason": "<reason>",
  "prev_receipt_hash": "<hash>",
  "receipt_hash": "<hash>",
  "signer": "<system-or-validator-id>"
}
```

The receipt must bind:

\[
hash(S_t),\quad hash(S_{t+1}),\quad hash(\Delta D),\quad hash(Policy_t),\quad t_{commit}
\]

---

## 13. Verification Requirements

### 13.1 Deterministic Testing

All Cost Tensor test suites must support deterministic seed execution.

Default seed:

```text
seed = 42
```

### 13.2 Required Integrated Tests

| Test | Input | Expected Result |
|---|---|---|
| Full admissible transition | All gates pass and cost within budget | ALLOW |
| GCAT boundary failure | Invalid state geometry | DENY |
| GCAT unknown | Cannot evaluate geometry | FAIL_CLOSED |
| BCAT consequence failure | Consequence exceeds bound | DENY |
| BCAT unknown | Consequence cannot be bounded | FAIL_CLOSED |
| ECAT reputation failure | \(R<R_{min}\) | DENY |
| ECAT stake failure | \(S_{risk}<S_{min}\) | DENY |
| ECAT anomaly failure | \(H>H_{max}\) | DENY |
| ECAT consent unavailable | Required consent missing | FAIL_CLOSED |
| ECAT co-owner rejection | Required owner rejects | FAIL_CLOSED |
| ICAT proof missing | Required proof unavailable | FAIL_CLOSED |
| ICAT proof invalid | Proof verifies false | DENY |
| ICAT witness unavailable | Witness set unavailable | FAIL_CLOSED |
| ICAT quorum failure | Insufficient valid witnesses | DENY |
| ICAT conservation failure | Required invariant violated | DENY |
| ICAT inverse failure | Protected state changed | DENY |
| Budget unavailable | No current budget | FAIL_CLOSED |
| Budget overflow | \(\mathcal C>Budget\) | DENY |
| Receipt emission failure | Cannot write receipt | FAIL_CLOSED |
| Scalarization check | Tensor exists, budget scalar | Compare scalar \(\mathcal C\), not tensor |
| Replay consistency | Recompute from receipt | Same outcome |
| Reconstruction degraded | Reconstruction score below threshold | DENY or FAIL_CLOSED by policy |

### 13.3 Conservation Checks

Every integrated evaluation must verify:

\[
\$G\ge0
\]

\[
\$B\ge0
\]

\[
\$E\ge0
\]

\[
\$I\ge0
\]

\[
\mathcal C(\Delta D)\ge0
\]

\[
R(e,t)\in[0,1]
\]

\[
S_{risk}(e,t)\ge0
\]

\[
\sum_{o\in Owners(D)}W(o,D)=1
\]

\[
P(\Delta D,t)\in[0,1]
\]

\[
A(\Delta D,t)\in[0,1]
\]

\[
K(\Delta D,t)\in\{0,1\}
\]

\[
X(\Delta D,t)\in\{0,1\}
\]

---

## 14. Implementation Requirements

A compliant Cost Tensor implementation must expose:

1. `build_transition_object(e, D, pre_state, post_state, policy, budget)`
2. `evaluate_gcat(transition_context)`
3. `compute_gcat_cost(transition_context)`
4. `evaluate_bcat(transition_context)`
5. `compute_bcat_cost(transition_context)`
6. `evaluate_ecat(entity, transition_context)`
7. `compute_ecat_cost(entity, transition_context)`
8. `evaluate_icat(transition_context)`
9. `compute_icat_cost(transition_context)`
10. `scalarize_cost_tensor(gcat, bcat, ecat, icat)`
11. `compare_budget(total_cost, budget)`
12. `emit_cost_tensor_receipt(evaluation_context)`
13. `verify_cost_tensor_receipt(receipt)`
14. `replay_cost_tensor_evaluation(receipt, context)`
15. `evaluate_commit_admissibility(transition_context)`

A compliant implementation must also produce machine-readable outcomes:

```text
ALLOW
DENY
FAIL_CLOSED
```

and must never collapse DENY and FAIL_CLOSED into the same outcome.

---

## 15. Minimal Reference Algorithm

```python
def evaluate_commit_admissibility(ctx):
    if not ctx.transition_object_complete:
        return fail_closed("transition_object_incomplete")

    if not ctx.policy_current:
        return fail_closed("policy_unavailable")

    if not ctx.budget_current:
        return fail_closed("budget_unavailable")

    gcat = evaluate_gcat(ctx)
    if gcat.status == "UNKNOWN":
        return fail_closed("gcat_unknown")
    if not gcat.pass_:
        return deny("gcat_boundary_failure")

    bcat = evaluate_bcat(ctx)
    if bcat.status == "UNKNOWN":
        return fail_closed("bcat_unknown")
    if not bcat.pass_:
        return deny("bcat_consequence_failure")

    ecat = evaluate_ecat(ctx)
    if ecat.status == "UNKNOWN":
        return fail_closed("ecat_unknown")
    if ecat.status == "CONSENT_REJECTED":
        return fail_closed("co_owner_rejected")
    if not ecat.pass_:
        return deny("ecat_failure")

    icat = evaluate_icat(ctx)
    if icat.status == "UNKNOWN":
        return fail_closed("icat_unknown")
    if not icat.pass_:
        return deny("icat_failure")

    total_cost = (
        gcat.cost
        + bcat.cost
        + ecat.cost
        + icat.cost
    )

    if total_cost > ctx.budget:
        return deny("budget_exceeded")

    receipt = emit_receipt(ctx, gcat, bcat, ecat, icat, total_cost)

    if not receipt.ok:
        return fail_closed("receipt_emission_failed")

    return allow("cost_tensor_admissible", receipt)
```

This algorithm is intentionally minimal.

It defines the required order of evaluation and the distinction between failure classes, not an optimized runtime implementation.

---

## 16. Status of Component Formalisms

| Component | Status | Required Formalism | Current State |
|---|---|---|---|
| GCAT | Complete baseline | GCAT framework | Available |
| BCAT | Complete baseline | BCAT framework | Available |
| ECAT | Draft formalized | ECAT v0.2.0 | Entity constraints defined |
| ICAT | Draft formalized | ICAT v0.1.0 | Integrity constraints defined |
| Cost Tensor | Integrated draft | This document | v0.2.0-draft |

---

## 17. Open Questions

1. **Unit calibration:** What canonical financial unit should all cost terms resolve into?
2. **Parameter governance:** Who sets \(\lambda_R,\lambda_S,\lambda_H,\lambda_W,\lambda_P,\lambda_A,\lambda_K,\lambda_X\)?
3. **Category policy:** Which data categories are always protected, and which admit recovery exceptions?
4. **Budget allocation:** Is budget allocated per transition, per entity, per data object, or per governance epoch?
5. **Tensor coupling:** When should the scalar linear sum be replaced with quadratic or higher-order coupling?
6. **Policy freshness:** What maximum lag is allowed between policy evaluation and commit?
7. **Witness markets:** How should witness cost and reliability be priced without creating perverse incentives?
8. **Privacy-preserving receipts:** Which receipt fields may be hidden while preserving replayability?
9. **Cross-org verification:** How should receipt chains span StegVerse-org, StegVerse-Labs, StegGhost, and external systems?
10. **Recoverability metric:** Where should the Rigel number enter the cost tensor: BCAT, ICAT reconstruction, or a separate secondary constraint?

---

## 18. Version Note

This revision integrates the newly formalized ECAT and ICAT layers into the StegVerse Cost Tensor.

It replaces the prior ECAT and ICAT placeholders with explicit scalar forms:

\[
\$E=C_R+C_S+C_H+C_W
\]

\[
\$I=C_P+C_A+C_K+C_X
\]

It also formalizes:

1. Tensor-to-scalar budget comparison.
2. Commit-time evaluation.
3. Full admissibility theorem.
4. DENY versus FAIL_CLOSED distinction.
5. Receipt schema.
6. Integrated verification requirements.
7. Minimal reference algorithm.

The next required artifact is a deterministic test specification:

```text
COST_TENSOR_TEST_SPEC_v0.1.0.md
```

followed by a minimal executable reference implementation.

---

**Document:** COST_TENSOR_SPEC.md  
**Version:** 0.2.0-draft  
**Date:** 2026-05-03  
**Org:** ECAT-ICAT-Formal
