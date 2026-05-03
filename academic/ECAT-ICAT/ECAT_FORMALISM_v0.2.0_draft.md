# ECAT: Entity Constraint Admissibility Transform

**Formal Specification v0.2.0-draft**  
**Org:** ECAT-ICAT-Formal  
**Date:** 2026-05-03  
**Status:** Revised formal draft for integration with the StegVerse Cost Tensor

---

## 0. Purpose and Scope

The Entity Constraint Admissibility Transform (ECAT) formalizes the entity-bound constraints that determine whether a proposed data transition may be executed by a given actor.

ECAT does not replace GCAT, BCAT, or ICAT.

It contributes the entity-side component of the total cost and admissibility framework:

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

- \(G^{\mu\nu}\) is the geometric admissibility component.
- \(B^{\mu\nu}\) is the bounded consequence component.
- \(E^{\mu\nu}\) is the entity constraint component.
- \(I^{\mu\nu}\) is the integrity and proof component.

ECAT answers a narrower question:

\[
\textbf{Is this entity allowed to bear, impose, and pay for this transition?}
\]

A transition that is geometrically admissible under GCAT and consequence-bounded under BCAT may still be inadmissible under ECAT if the acting entity lacks reputation, stake, historical consistency, or authority over co-owned data.

---

## 1. Foundational Axiom

An entity \(e\) is any observer, actor, agent, account, process, or institution capable of bearing consequence within lived continuity.

For cost and admissibility computation, an entity is represented by four measurable primitives:

\[
R(e,t),\quad S(e,t),\quad H(e,\Delta D),\quad W(e,D)
\]

where:

- \(R(e,t)\) is the entity reputation at time \(t\).
- \(S(e,t)\) is the entity's risk-bearing stake at time \(t\).
- \(H(e,\Delta D)\) is the historical consistency deviation of transition \(\Delta D\).
- \(W(e,D)\) is the ownership or authority weight of entity \(e\) over data object \(D\).

All ECAT decisions are evaluated at commit time.

No entity receives standing authority merely because it was previously authorized.

Authority must be re-derived at the moment the proposed transition becomes effect-capable.

---

## 2. Entity State Vector

For a proposed transition \(\Delta D\), define the ECAT entity state vector:

\[
x_E(e,\Delta D,t)
=
\left[
R(e,t),
S_{risk}(e,t),
H(e,\Delta D),
W(e,D)
\right]
\]

where \(S_{risk}\) is the portion of stake currently locked and available to absorb penalty or consequence from the proposed transition.

The ECAT gate evaluates:

\[
\mathcal E(e,\Delta D,t)
=
\left(
R,\,
S_{risk},\,
H,\,
W,\,
Consent
\right)
\]

A transition is ECAT-admissible only if each hard gate passes and the scalar ECAT cost remains within the transition's allocated budget.

---

## 3. Reputation Function

### 3.1 Definition

\[
R(e,t)\in[0,1]
\]

Interpretation:

- \(R=1\): maximum reputation.
- \(R=0\): null reputation.
- \(R<R_{min}\): insufficient entity reliability for commit.
- \(R=0\): all non-recovery transitions FAIL_CLOSED.

### 3.2 Event Rates

Let:

\[
V_e(t)=\frac{N_{allow}+N_{consensus\_confirm}}{\Delta t}
\]

be the validation rate.

Let:

\[
L_e(t)=
\frac{
N_{slash}
+
N_{fork}
+
N_{double\_vote}
+
N_{data\_misuse}
+
N_{systemic\_harm}
}{\Delta t}
\]

be the violation rate.

Let:

\[
D_e(t)=\frac{N_{deny}}{\Delta t}
\]

be the denied-request rate.

DENY is not automatically treated as misconduct. A denied request may be a valid governance event. Actual violations are counted separately through \(L_e(t)\).

### 3.3 Bounded Reputation Dynamics

Reputation evolves according to:

\[
\frac{dR}{dt}
=
\alpha(1-R)V_e(t)
-
\beta R L_e(t)
-
\delta R D_e(t)
-
\gamma R(1-A_e(t))
\]

where:

- \(\alpha>0\) is the validation reward coefficient.
- \(\beta>0\) is the violation penalty coefficient.
- \(\delta\ge 0\) is the denied-request pressure coefficient.
- \(\gamma>0\) is the entropy decay coefficient.
- \(A_e(t)\in[0,1]\) is the activity fraction over the evaluation window.

Recommended parameter constraint:

\[
0\le \delta \ll \beta
\]

This preserves the distinction between inadmissible requests and punishable misconduct.

### 3.4 Bounded Discrete Update

For implementation, reputation is updated as:

\[
R_{t+\Delta t}
=
\Pi_{[0,1]}
\left(
R_t+\Delta t\cdot \dot R_t
\right)
\]

where:

\[
\Pi_{[0,1]}(x)=\min(1,\max(0,x))
\]

This guarantees:

\[
R(e,t)\in[0,1]
\]

for all implemented updates.

### 3.5 Reputation Gate

\[
R(e,t)<R_{min}(\Delta D)\Rightarrow DENY
\]

\[
R(e,t)=0\Rightarrow FAIL\_CLOSED
\]

unless the proposed transition is explicitly classified as a recovery, appeal, or restoration transition.

---

## 4. Stake Function

### 4.1 Definition

\[
S(e,t)\ge 0
\]

Stake is economic capital bonded by entity \(e\).

For ECAT admissibility, the operative quantity is not total stake but risk-bearing locked stake:

\[
S_{risk}(e,t)
\]

This is the portion of stake currently locked, unencumbered, and slashable for the proposed transition.

### 4.2 Stake Lock

A stake lock operation is defined as:

\[
Lock(e,amount,T)\rightarrow S_{risk}(e,t_0^+)=S_{risk}(e,t_0^-)+amount
\]

where \(T\) is the lock duration.

### 4.3 Linear Release

For a lock of size \(S_0\) created at \(t_0\) with duration \(T\):

\[
S_{locked}(e,t)
=
S_0\cdot
\max
\left(
0,
1-\frac{t-t_0}{T}
\right)
\]

for:

\[
t_0\le t\le t_0+T
\]

The released portion is:

\[
S_{released}(e,t)=S_0-S_{locked}(e,t)
\]

Only stake that remains locked and slashable counts toward \(S_{risk}\).

### 4.4 Slash Transition

A violation \(v\) updates risk-bearing stake as:

\[
S_{risk}(e,t^+)
=
\max
\left(
0,
S_{risk}(e,t^-)-P(v)
\right)
\]

For percentage-based penalties:

\[
P(v)=\rho_v S_{risk}(e,t^-)
\]

where:

\[
\rho_v\in[0,1]
\]

### 4.5 Default Slash Schedule

| Violation Type | Penalty Coefficient \(\rho_v\) |
|---|---:|
| Invalid state transition | 0.01 |
| Fork creation | 0.10 |
| Double consensus vote | 0.25 |
| Data misuse | 0.50 |
| Systemic harm | 1.00 |

### 4.6 Stake Sufficiency

A transition is ECAT-admissible only if:

\[
S_{risk}(e,t)\ge S_{min}(\Delta D)
\]

where:

\[
S_{min}(\Delta D)
=
Base\_Stake
\times
Risk\_Factor(\Delta D)
\times
Category\_Multiplier(category)
\]

### 4.7 Category Multipliers

| Category | Multiplier |
|---|---:|
| Metadata only | 1.0 |
| Notes \((01\_Notes)\) | 2.0 |
| Media \((04\_Media)\) | 3.0 |
| Entities \((_Entities)\) | 4.0 |
| Records \((03\_Records)\) | \(\infty\) |

If:

\[
Category\_Multiplier(category)=\infty
\]

then:

\[
\Delta D\Rightarrow FAIL\_CLOSED
\]

unless the transition is explicitly classified as a protected recovery, correction, or legally required preservation action.

---

## 5. Historical Consistency Function

### 5.1 Definition

\[
H(e,\Delta D)\in[0,\infty)
\]

Historical consistency measures how much the proposed transition deviates from the entity's established transition pattern.

Lower values indicate ordinary behavior.

Higher values indicate anomalous behavior.

### 5.2 Pattern Model

Each entity has a learned transition distribution:

\[
P_e(D)
\]

derived from prior admitted transitions, denied requests, appeal outcomes, and verified recovery actions.

The proposed transition induces a comparison distribution:

\[
Q_{\Delta D}
\]

### 5.3 Smoothed Divergence

To avoid false infinite values caused by zero-probability bins, ECAT uses smoothed distributions:

\[
P_e^\epsilon=(1-\epsilon)P_e+\epsilon U
\]

\[
Q_{\Delta D}^\epsilon=(1-\epsilon)Q_{\Delta D}+\epsilon U
\]

where:

- \(U\) is a uniform prior over valid transition classes.
- \(\epsilon\in(0,1)\) is a smoothing parameter.

The default historical deviation is:

\[
H(e,\Delta D)
=
D_{KL}
\left(
P_e^\epsilon
\|
Q_{\Delta D}^\epsilon
\right)
\]

### 5.4 Bounded Alternative

For systems requiring bounded anomaly scoring, ECAT may use Jensen-Shannon divergence:

\[
H_{JS}(e,\Delta D)=D_{JS}(P_e,Q_{\Delta D})
\]

with normalized range:

\[
H_{JS}\in[0,1]
\]

The implementation must declare whether it uses \(D_{KL}\) or \(D_{JS}\).

### 5.5 Historical Consistency Gate

\[
H(e,\Delta D)>H_{max}(\Delta D)\Rightarrow DENY
\]

\[
H(e,\Delta D)=\infty\Rightarrow FAIL\_CLOSED
\]

The \(H=\infty\) condition is reserved for impossible or structurally forbidden behavior, not merely unusual behavior.

---

## 6. Co-Ownership and Authority Weight

### 6.1 Definition

For data object \(D\) with owner set:

\[
Owners(D)=\{e_1,e_2,\ldots,e_n\}
\]

each owner has an authority weight:

\[
W(e_i,D)\in[0,1]
\]

subject to conservation:

\[
\sum_{e_i\in Owners(D)} W(e_i,D)=1
\]

### 6.2 Default Weighting Methods

| Method | Formula | Use Case |
|---|---|---|
| Equal | \(W(e_i,D)=1/N\) | Default presence-based sharing |
| Contribution | \(W(e_i,D)=C_i/\sum_j C_j\) | Contribution-proportional data |
| Time | \(W(e_i,D)=T_i/\sum_j T_j\) | Time-proportional participation |
| Explicit Policy | \(W(e_i,D)=Policy(e_i,D)\) | Negotiated or legal agreement |

### 6.3 Normalized Presence-Based Sharing

For shared memories or shared events, define the unnormalized weight:

\[
\tilde W(e,D)
=
Presence\_Fraction(e,event)
\cdot
Contribution\_Quality(e,D)
\]

Then normalize:

\[
W(e,D)
=
\frac{\tilde W(e,D)}
{\sum_{i\in Owners(D)}\tilde W(e_i,D)}
\]

This guarantees:

\[
\sum_e W(e,D)=1
\]

### 6.4 Consent Function

Let:

\[
Consent(o,\Delta D)\in\{0,1\}
\]

where \(o\) is a co-owner.

A transition requiring co-owner consent is admissible only if:

\[
\forall o\in Owners(D)
\quad
Required(o,\Delta D)=1
\Rightarrow
Consent(o,\Delta D)=1
\]

If any required co-owner rejects:

\[
\exists o:
Required(o,\Delta D)=1
\land
Consent(o,\Delta D)=0
\Rightarrow FAIL\_CLOSED
\]

### 6.5 Coordination Cost

Coordination cost is:

\[
C_W(e,\Delta D)
=
\lambda_W
\sum_{o\in Owners(D)}
W(o,D)C_{request}(o)
\]

where:

- \(C_{request}(o)\) is the cost of requesting and recording consent.
- \(\lambda_W\) is the coordination scaling factor.

A rejection is not treated as an arbitrarily high cost. It is treated as a hard admissibility failure.

---

## 7. ECAT Scalar Cost

### 7.1 Component Costs

The ECAT scalar cost is:

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

### 7.2 Coefficients

- \(\lambda_R\) converts reputation deficit into financial cost.
- \(\lambda_S\) converts stake shortfall into financial cost.
- \(\lambda_H\) converts historical deviation into financial cost.
- \(\lambda_W\) scales coordination burden.

### 7.3 Linear and Quadratic Anomaly Modes

The default anomaly cost is linear:

\[
C_H=\lambda_H C_{base}H
\]

For high-risk categories, a quadratic anomaly premium may be used:

\[
C_H^{quad}
=
\lambda_H C_{base}H^2
\]

The implementation must explicitly declare whether anomaly escalation is linear or quadratic.

No implementation may multiply by \(H\) twice unless quadratic anomaly escalation is explicitly enabled.

---

## 8. ECAT Tensor Form

### 8.1 Normalized ECAT Deviation Vector

Define the normalized deviation vector:

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

where:

\[
\bar H
\]

is the normalized historical deviation, and:

\[
\bar C_W
\]

is the normalized coordination cost.

### 8.2 Quadratic Tensor Cost

The ECAT tensor-induced scalar cost may be represented as:

\[
\$E
=
C_{base}
\cdot
\epsilon^\top M_E\epsilon
\]

where:

\[
M_E\succeq0
\]

is a positive semidefinite ECAT weighting matrix.

The linear scalar form in Section 7 is the default minimum implementation.

The quadratic form is reserved for higher-order coupling between entity risk dimensions.

---

## 9. ECAT Hard Gates

For proposed transition \(\Delta D\), entity \(e\), and data object \(D\), ECAT evaluates the following hard gates:

### 9.1 Reputation Gate

\[
R(e,t)\ge R_{min}(\Delta D)
\]

### 9.2 Stake Gate

\[
S_{risk}(e,t)\ge S_{min}(\Delta D)
\]

### 9.3 Historical Consistency Gate

\[
H(e,\Delta D)\le H_{max}(\Delta D)
\]

### 9.4 Co-Owner Consent Gate

\[
Consent(D,\Delta D)=true
\]

### 9.5 Protected Category Gate

If:

\[
Category(D)=Records
\]

then:

\[
\Delta D\Rightarrow FAIL\_CLOSED
\]

unless the action is explicitly classified as one of:

- recovery;
- legal preservation;
- error correction;
- restoration from verified receipt state;
- authorized archival continuity action.

---

## 10. Integration with GCAT/BCAT/ICAT

### 10.1 Total Scalar Cost

The scalarized cost of transition \(\Delta D\) is:

\[
\mathcal C(\Delta D)
=
\$G(\Delta D)
+
\$B(\Delta D)
+
\$E(e,\Delta D,t)
+
\$I(\Delta D)
\]

### 10.2 Scalarization Requirement

A rank-2 tensor may not be directly compared to a scalar budget.

Therefore, admissibility must use the scalarized cost:

\[
\mathcal C(\Delta D)
\]

not the raw tensor:

\[
C^{\mu\nu}(\Delta D)
\]

### 10.3 Full Admissibility Condition

\[
ALLOW(\Delta D)
\iff
\left[
\begin{array}{c}
R(e,t)\ge R_{min}(\Delta D)\\
S_{risk}(e,t)\ge S_{min}(\Delta D)\\
H(e,\Delta D)\le H_{max}(\Delta D)\\
Consent(D,\Delta D)=true\\
ProtectedCategory(D,\Delta D)=false\\
\mathcal C(\Delta D)\le Budget(\Delta D)
\end{array}
\right]
\]

If any required state, authority, consent, or proof is unavailable at commit time:

\[
\Delta D\Rightarrow FAIL\_CLOSED
\]

---

## 11. Gate Logic

Minimum ECAT gate logic:

```text
INPUT:
  entity e
  transition ΔD
  data object D
  current time t
  current budget Budget(ΔD)

COMPUTE:
  R(e,t)
  S_risk(e,t)
  H(e,ΔD)
  W(o,D) for all o ∈ Owners(D)
  Consent(D,ΔD)
  $E(e,ΔD,t)

GATES:
  IF R(e,t) = 0:
      FAIL_CLOSED

  IF R(e,t) < R_min(ΔD):
      DENY

  IF S_risk(e,t) < S_min(ΔD):
      DENY

  IF H(e,ΔD) = ∞:
      FAIL_CLOSED

  IF H(e,ΔD) > H_max(ΔD):
      DENY

  IF protected category and not recovery/correction/preservation:
      FAIL_CLOSED

  IF required co-owner rejects:
      FAIL_CLOSED

  IF required consent is unavailable:
      FAIL_CLOSED

  IF $G + $B + $E + $I > Budget(ΔD):
      DENY

  ELSE:
      ALLOW
```

---

## 12. Verification Requirements

### 12.1 Deterministic Testing

All test suites must support deterministic seed execution.

Default seed:

```text
seed = 42
```

### 12.2 Required Tests

| Test | Input | Expected Result |
|---|---|---|
| Reputation upper bound | High validation rate | \(R\le 1\) |
| Reputation lower bound | High violation rate | \(R\ge 0\) |
| DENY separation | Denied request without misconduct | \(D_e\) increases, \(L_e\) unchanged |
| Slash accuracy | Violation event | \(S_{risk}\) reduced by \(P(v)\) |
| Stake sufficiency | \(S_{risk}<S_{min}\) | DENY |
| Protected records | Ordinary mutation of records | FAIL_CLOSED |
| Recovery exception | Verified records recovery | Evaluated under recovery policy |
| KL smoothing | Zero-probability category | Finite \(H\) if smoothing enabled |
| Impossible behavior | Structurally forbidden transition | \(H=\infty\), FAIL_CLOSED |
| Co-owner normalization | Presence/contribution weights | \(\sum W=1\) |
| Co-owner rejection | Required owner rejects | FAIL_CLOSED |
| Consent unavailable | Required consent cannot be verified | FAIL_CLOSED |
| Cost scalarization | Tensor and scalar budget | Compare \(\mathcal C(\Delta D)\), not \(C^{\mu\nu}\) |
| Budget overflow | \(\mathcal C>Budget\) | DENY |
| Budget admissible | All gates pass and \(\mathcal C\le Budget\) | ALLOW |

### 12.3 Conservation Checks

Every co-ownership update must verify:

\[
\sum_{e\in Owners(D)}W(e,D)=1
\]

Every stake update must verify:

\[
S_{risk}(e,t)\ge 0
\]

Every reputation update must verify:

\[
R(e,t)\in[0,1]
\]

---

## 13. Implementation Requirements

A compliant ECAT implementation must expose:

1. `compute_reputation(e, t)`
2. `update_reputation(e, events, Δt)`
3. `compute_risk_stake(e, t)`
4. `compute_stake_min(ΔD)`
5. `apply_slash(e, violation_type)`
6. `compute_historical_deviation(e, ΔD)`
7. `compute_ownership_weights(D)`
8. `verify_consent(D, ΔD)`
9. `compute_ecat_cost(e, ΔD, t)`
10. `evaluate_ecat_gate(e, D, ΔD, t, budget_context)`

A compliant implementation must also emit receipts for:

- ALLOW;
- DENY;
- FAIL_CLOSED;
- stake lock;
- stake release;
- slash;
- ownership weight update;
- consent request;
- consent approval;
- consent rejection;
- historical anomaly detection.

---

## 14. Open Questions

1. **Reputation bootstrapping:** How does a new entity establish nonzero reputation without granting unsafe initial authority?
2. **Appeal mechanics:** What transitions allow an entity with \(R=0\) to seek restoration?
3. **Stake rehypothecation:** Can locked stake be used as collateral elsewhere, or must it remain fully isolated?
4. **Pattern adaptation:** How quickly may \(P_e\) update after verified behavioral change?
5. **Dispute resolution:** What formal mechanism resolves contested \(W(e,D)\)?
6. **Cross-org identity:** Is an entity identical across StegVerse-org, StegVerse-Labs, StegGhost, and other namespaces?
7. **Consent latency:** How long may consent remain valid before commit-time revalidation is required?
8. **Protected records:** Which recovery and correction actions are allowed for otherwise immutable records?

---

## 15. Version Note

This revision closes the first mathematical gaps in the ECAT draft:

1. Reputation dynamics are now bounded.
2. DENY is separated from actual violation.
3. Stake lock, release, and slash updates are state-explicit.
4. Historical consistency supports smoothing and bounded divergence.
5. Co-ownership weights are normalized.
6. Anomaly premium no longer double-counts \(H\) unless quadratic mode is explicitly enabled.
7. Tensor cost is scalarized before comparison to budget.
8. Hard admissibility gates are separated from financial surcharge logic.

ICAT remains the remaining unformalized component required before the full Cost Tensor can reach v1.0.

---

**Document:** ECAT_FORMALISM.md  
**Version:** 0.2.0-draft  
**Date:** 2026-05-03  
**Org:** ECAT-ICAT-Formal
