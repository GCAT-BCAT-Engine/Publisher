# ICAT: Integrity Constraint Admissibility Transform

**Formal Specification v0.1.0-draft**  
**Org:** ECAT-ICAT-Formal  
**Date:** 2026-05-03  
**Status:** Initial formal draft for integration with the StegVerse Cost Tensor

---

## 0. Purpose and Scope

The Integrity Constraint Admissibility Transform (ICAT) formalizes the proof-bound constraints that determine whether a proposed data transition is verifiable, conserved, reconstructible, and non-corrupting at commit time.

ICAT does not replace GCAT, BCAT, or ECAT.

It contributes the integrity-side component of the total cost and admissibility framework:

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
- \(I^{\mu\nu}\) is the integrity constraint component.

ICAT answers a narrower question:

\[
\textbf{Can this transition be proven, witnessed, conserved, and bounded against unintended change?}
\]

A transition that is admissible under GCAT, BCAT, and ECAT may still be inadmissible under ICAT if the system cannot prove the transition, verify the required witnesses, preserve invariants, or confirm that protected state remains unchanged.

All ICAT checks are evaluated at commit time.

If required proof is unavailable, stale, unverifiable, or insufficient at the moment of commit, the transition must FAIL_CLOSED.

---

## 1. Foundational Axiom

A transition may become effect-capable only if its required integrity conditions are independently verifiable at the moment of commit.

Integrity is not inferred from intent, policy, reputation, or historical success.

It must be proven against the current transition, current state, current witnesses, current invariants, and current inverse constraints.

ICAT formalizes four measurable primitives:

\[
P(\Delta D,t),\quad A(\Delta D,t),\quad K(\Delta D,t),\quad X(\Delta D,t)
\]

where:

- \(P(\Delta D,t)\) is proof sufficiency.
- \(A(\Delta D,t)\) is witness or attestation sufficiency.
- \(K(\Delta D,t)\) is conservation-law preservation.
- \(X(\Delta D,t)\) is inverse constraint preservation.

The ICAT admissibility question is:

\[
ICAT\_PASS(\Delta D,t)
\iff
P\_PASS
\land
A\_PASS
\land
K\_PASS
\land
X\_PASS
\]

---

## 2. Integrity State Vector

For a proposed transition \(\Delta D\), define the ICAT state vector:

\[
x_I(\Delta D,t)
=
\left[
P(\Delta D,t),
A(\Delta D,t),
K(\Delta D,t),
X(\Delta D,t)
\right]
\]

where:

- \(P\) measures whether the transition proof exists and verifies.
- \(A\) measures whether required independent witnesses confirm the transition.
- \(K\) measures whether conserved quantities remain invariant.
- \(X\) measures whether protected non-changing state remains unchanged.

The ICAT gate evaluates:

\[
\mathcal I(\Delta D,t)
=
\left(
P,\,
A,\,
K,\,
X,\,
Receipt
\right)
\]

where `Receipt` is the commit-time evidence artifact recording the result of the integrity check.

---

## 3. Proof Function \(P\)

### 3.1 Definition

\[
P(\Delta D,t)\in[0,1]
\]

Interpretation:

- \(P=1\): proof exists, is current, complete, and verifies.
- \(P=0\): no usable proof exists.
- \(0<P<1\): proof exists but is partial, degraded, stale, or probabilistic.
- \(P<P_{min}\): proof is insufficient for commit.

### 3.2 Proof Object

A proof object is defined as:

\[
\pi(\Delta D,S_t,S_{t+1},Policy_t)
\]

where:

- \(S_t\) is the pre-transition state.
- \(S_{t+1}\) is the proposed post-transition state.
- \(Policy_t\) is the policy or admissibility basis current at commit.
- \(\Delta D=S_{t+1}-S_t\) is the proposed transition.

The proof object must bind:

\[
hash(S_t),\quad hash(S_{t+1}),\quad hash(\Delta D),\quad hash(Policy_t),\quad t_{commit}
\]

### 3.3 Proof Verification

Define:

\[
VerifyProof(\pi,\Delta D,S_t,S_{t+1},Policy_t)\in\{0,1\}
\]

Then:

\[
P\_PASS
\iff
VerifyProof(\pi,\Delta D,S_t,S_{t+1},Policy_t)=1
\]

For scalar scoring:

\[
P(\Delta D,t)=
q_{proof}
\cdot
q_{fresh}
\cdot
q_{scope}
\cdot
q_{binding}
\]

where each \(q_i\in[0,1]\):

- \(q_{proof}\): proof cryptographically verifies.
- \(q_{fresh}\): proof was generated for the current commit window.
- \(q_{scope}\): proof covers the complete transition scope.
- \(q_{binding}\): proof binds pre-state, post-state, policy, actor, and timestamp.

### 3.4 Proof Freshness

A proof is fresh only if:

\[
t_{commit}-t_{proof}\le \tau_{proof}
\]

where \(\tau_{proof}\) is the maximum allowed proof age.

If:

\[
t_{commit}-t_{proof}>\tau_{proof}
\]

then:

\[
P\_PASS=false
\]

### 3.5 Proof Gate

\[
P(\Delta D,t)<P_{min}(\Delta D)\Rightarrow DENY
\]

If the proof is required but unavailable:

\[
\pi=\emptyset\Rightarrow FAIL\_CLOSED
\]

If the proof cannot be parsed, bound, or verified:

\[
VerifyProof\ unavailable\Rightarrow FAIL\_CLOSED
\]

---

## 4. Witness and Attestation Function \(A\)

### 4.1 Definition

\[
A(\Delta D,t)\in[0,1]
\]

Witness sufficiency measures whether the required independent attestations exist, are valid, and satisfy quorum.

### 4.2 Witness Set

Let:

\[
\mathcal W(\Delta D)=\{w_1,w_2,\ldots,w_n\}
\]

be the witness set for transition \(\Delta D\).

Each witness produces an attestation:

\[
a_i = Attest(w_i,\Delta D,S_t,S_{t+1},t)
\]

### 4.3 Witness Validity

Each attestation has validity:

\[
v_i\in\{0,1\}
\]

where:

\[
v_i=1
\iff
VerifyAttestation(a_i,w_i,\Delta D,S_t,S_{t+1},t)=1
\]

### 4.4 Witness Weight

Each witness has reliability weight:

\[
\rho_i\in[0,1]
\]

where \(\rho_i\) may be derived from witness reputation, independence, cryptographic identity, prior accuracy, or validator class.

The weighted attestation score is:

\[
A(\Delta D,t)
=
\frac{
\sum_{i=1}^n \rho_i v_i
}{
\sum_{i=1}^n \rho_i
}
\]

provided:

\[
\sum_{i=1}^n \rho_i>0
\]

If:

\[
\sum_i \rho_i=0
\]

then:

\[
A=0
\]

### 4.5 Independence Constraint

Witnesses must satisfy independence:

\[
Independent(\mathcal W)\in\{0,1\}
\]

If witness independence cannot be established:

\[
Independent(\mathcal W)=unknown\Rightarrow FAIL\_CLOSED
\]

If witnesses are known to be non-independent and independence is required:

\[
Independent(\mathcal W)=0\Rightarrow DENY
\]

### 4.6 Quorum Gate

A transition passes the witness gate only if:

\[
A(\Delta D,t)\ge A_{min}(\Delta D)
\]

and:

\[
|\{i:v_i=1\}|\ge N_{min}(\Delta D)
\]

Thus:

\[
A\_PASS
\iff
A\ge A_{min}
\land
N_{valid}\ge N_{min}
\land
Independent(\mathcal W)=1
\]

### 4.7 Witness Availability

If witness attestations are required but unavailable at commit:

\[
\mathcal W=\emptyset\Rightarrow FAIL\_CLOSED
\]

If attestation verification cannot be performed:

\[
VerifyAttestation\ unavailable\Rightarrow FAIL\_CLOSED
\]

---

## 5. Conservation Function \(K\)

### 5.1 Definition

\[
K(\Delta D,t)\in\{0,1\}
\]

Conservation verifies that required invariants remain preserved across the transition.

ICAT defines a conservation law set:

\[
\mathcal K(D)=\{k_1,k_2,\ldots,k_m\}
\]

where each \(k_j\) is an invariant predicate.

### 5.2 Conservation Predicate

Each conservation law is evaluated as:

\[
k_j(S_t,S_{t+1},\Delta D)\in\{0,1\}
\]

A transition preserves conservation iff:

\[
K(\Delta D,t)=
\prod_{j=1}^m
k_j(S_t,S_{t+1},\Delta D)
\]

Thus:

\[
K=1
\iff
\forall j,\ k_j=1
\]

### 5.3 Examples of Conservation Laws

Conservation laws may include:

- ownership weight conservation;
- stake non-negativity;
- receipt chain continuity;
- hash-chain preservation;
- data category immutability;
- budget non-negativity;
- state transition reversibility bounds;
- identity binding continuity;
- legal hold preservation;
- archival continuity.

### 5.4 Conservation Gate

\[
K(\Delta D,t)=0\Rightarrow DENY
\]

If any required conservation law cannot be evaluated:

\[
k_j=unknown\Rightarrow FAIL\_CLOSED
\]

If the set of required conservation laws cannot be resolved:

\[
\mathcal K(D)=unknown\Rightarrow FAIL\_CLOSED
\]

---

## 6. Inverse Constraint Function \(X\)

### 6.1 Definition

\[
X(\Delta D,t)\in\{0,1\}
\]

Inverse constraints verify that state which must not change remains unchanged.

Where conservation asks:

\[
\textbf{What must remain invariant in aggregate?}
\]

inverse constraints ask:

\[
\textbf{What specific state must not be touched?}
\]

### 6.2 Protected State Set

Define the protected non-change set:

\[
\mathcal X(D)=\{x_1,x_2,\ldots,x_r\}
\]

Each \(x_l\) is a predicate over protected state.

### 6.3 Inverse Predicate

Each inverse constraint is evaluated as:

\[
x_l(S_t,S_{t+1},\Delta D)\in\{0,1\}
\]

where:

\[
x_l=1
\]

means the protected state remained unchanged.

The inverse constraint function is:

\[
X(\Delta D,t)
=
\prod_{l=1}^r
x_l(S_t,S_{t+1},\Delta D)
\]

Thus:

\[
X=1
\iff
\forall l,\ x_l=1
\]

### 6.4 Examples of Inverse Constraints

Inverse constraints may include:

- protected records not modified;
- sealed evidence not altered;
- identity anchors not rotated;
- consent receipts not overwritten;
- original timestamps not rewritten;
- legal-hold fields not mutated;
- hash-chain ancestors not changed;
- external attestation anchors not invalidated.

### 6.5 Inverse Constraint Gate

\[
X(\Delta D,t)=0\Rightarrow DENY
\]

If any required inverse constraint cannot be checked:

\[
x_l=unknown\Rightarrow FAIL\_CLOSED
\]

If the protected non-change set cannot be resolved:

\[
\mathcal X(D)=unknown\Rightarrow FAIL\_CLOSED
\]

---

## 7. ICAT Scalar Cost

### 7.1 Component Costs

The ICAT scalar cost is:

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
\sum_{i=1}^n
C_{attest}(w_i,\Delta D,t)
\]

\[
C_K
=
\lambda_K
\sum_{j=1}^m
C_{check}(k_j,\Delta D,t)
\]

\[
C_X
=
\lambda_X
\sum_{l=1}^r
C_{inverse}(x_l,\Delta D,t)
\]

### 7.2 Coefficients

- \(\lambda_P\) scales proof generation and verification cost.
- \(\lambda_A\) scales witness attestation cost.
- \(\lambda_K\) scales conservation checking cost.
- \(\lambda_X\) scales inverse constraint checking cost.

### 7.3 Proof Cost

Proof cost may be decomposed as:

\[
C_{proof}
=
C_{generate}
+
C_{verify}
+
C_{bind}
+
C_{store}
\]

where:

- \(C_{generate}\) is proof generation cost.
- \(C_{verify}\) is proof verification cost.
- \(C_{bind}\) is state/policy/actor/timestamp binding cost.
- \(C_{store}\) is receipt persistence cost.

### 7.4 Witness Cost

Witness cost may be decomposed as:

\[
C_{attest}(w_i)
=
C_{observe}(w_i)
+
C_{sign}(w_i)
+
C_{transmit}(w_i)
+
C_{incentive}(w_i)
\]

### 7.5 Conservation Check Cost

\[
C_{check}(k_j)
=
C_{load}(k_j)
+
C_{evaluate}(k_j)
+
C_{record}(k_j)
\]

### 7.6 Inverse Check Cost

\[
C_{inverse}(x_l)
=
C_{load}(x_l)
+
C_{compare}(x_l)
+
C_{record}(x_l)
\]

---

## 8. ICAT Tensor Form

### 8.1 Normalized ICAT Deviation Vector

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

where \(K,X\in\{0,1\}\).

### 8.2 Quadratic Tensor Cost

The ICAT tensor-induced scalar cost may be represented as:

\[
\$I
=
C_{base}
\cdot
\eta^\top M_I\eta
+
C_{ops}
\]

where:

\[
M_I\succeq0
\]

is a positive semidefinite ICAT weighting matrix, and \(C_{ops}\) is the direct operational cost of proof, attestation, conservation, and inverse checks.

The scalar component form in Section 7 is the default minimum implementation.

The tensor form is reserved for higher-order coupling between integrity risk dimensions.

---

## 9. ICAT Hard Gates

For proposed transition \(\Delta D\), ICAT evaluates the following hard gates.

### 9.1 Proof Gate

\[
P(\Delta D,t)\ge P_{min}(\Delta D)
\]

### 9.2 Witness Gate

\[
A(\Delta D,t)\ge A_{min}(\Delta D)
\]

\[
N_{valid}\ge N_{min}(\Delta D)
\]

\[
Independent(\mathcal W)=1
\]

### 9.3 Conservation Gate

\[
K(\Delta D,t)=1
\]

### 9.4 Inverse Constraint Gate

\[
X(\Delta D,t)=1
\]

### 9.5 Receipt Gate

A commit-time receipt must be emitted for every ICAT outcome:

\[
Receipt_{ICAT}
\in
\{ALLOW,DENY,FAIL\_CLOSED\}
\]

If receipt emission fails:

\[
\Delta D\Rightarrow FAIL\_CLOSED
\]

---

## 10. Integration with GCAT/BCAT/ECAT

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
\$I(\Delta D,t)
\]

### 10.2 Full Admissibility Condition

\[
ALLOW(\Delta D)
\iff
\left[
\begin{array}{c}
GCAT\_PASS(\Delta D,t)\\
BCAT\_PASS(\Delta D,t)\\
ECAT\_PASS(e,\Delta D,t)\\
ICAT\_PASS(\Delta D,t)\\
\mathcal C(\Delta D)\le Budget(\Delta D)
\end{array}
\right]
\]

where:

\[
ICAT\_PASS(\Delta D,t)
\iff
P\_PASS
\land
A\_PASS
\land
K\_PASS
\land
X\_PASS
\land
Receipt\_PASS
\]

### 10.3 Scalarization Requirement

A rank-2 tensor may not be directly compared to a scalar budget.

Admissibility must use:

\[
\mathcal C(\Delta D)
\]

not the raw tensor:

\[
C^{\mu\nu}(\Delta D)
\]

---

## 11. Gate Logic

Minimum ICAT gate logic:

```text
INPUT:
  transition ΔD
  pre-state S_t
  proposed post-state S_t+1
  current policy Policy_t
  current time t
  witness set W
  conservation set K
  inverse constraint set X
  budget context Budget(ΔD)

COMPUTE:
  proof object π
  proof score P(ΔD,t)
  witness score A(ΔD,t)
  conservation result K(ΔD,t)
  inverse result X(ΔD,t)
  $I(ΔD,t)

GATES:
  IF proof required and π is unavailable:
      FAIL_CLOSED

  IF proof cannot be parsed or verified:
      FAIL_CLOSED

  IF P(ΔD,t) < P_min(ΔD):
      DENY

  IF witnesses required and witness set is unavailable:
      FAIL_CLOSED

  IF witness independence cannot be established:
      FAIL_CLOSED

  IF witness set is non-independent where independence is required:
      DENY

  IF A(ΔD,t) < A_min(ΔD):
      DENY

  IF N_valid < N_min(ΔD):
      DENY

  IF required conservation law set cannot be resolved:
      FAIL_CLOSED

  IF any conservation law cannot be evaluated:
      FAIL_CLOSED

  IF K(ΔD,t) = 0:
      DENY

  IF inverse constraint set cannot be resolved:
      FAIL_CLOSED

  IF any inverse constraint cannot be evaluated:
      FAIL_CLOSED

  IF X(ΔD,t) = 0:
      DENY

  IF ICAT receipt cannot be emitted:
      FAIL_CLOSED

  ELSE:
      ICAT_PASS
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
| Proof unavailable | Required proof missing | FAIL_CLOSED |
| Proof invalid | Proof verifies false | DENY |
| Proof stale | \(t_{commit}-t_{proof}>\tau_{proof}\) | DENY |
| Proof unparseable | Malformed proof object | FAIL_CLOSED |
| Proof scope incomplete | Proof excludes part of \(\Delta D\) | DENY |
| Proof binding mismatch | Proof bound to wrong state/policy | DENY |
| Witness set unavailable | Required witnesses absent | FAIL_CLOSED |
| Witness invalid | Attestation signature invalid | DENY if quorum fails |
| Witness non-independent | Colluding or duplicate witnesses | DENY |
| Independence unknown | Cannot establish independence | FAIL_CLOSED |
| Quorum failure | \(A<A_{min}\) or \(N_{valid}<N_{min}\) | DENY |
| Conservation pass | All \(k_j=1\) | \(K=1\) |
| Conservation failure | Any \(k_j=0\) | DENY |
| Conservation unknown | Any \(k_j=unknown\) | FAIL_CLOSED |
| Inverse pass | All \(x_l=1\) | \(X=1\) |
| Inverse failure | Any \(x_l=0\) | DENY |
| Inverse unknown | Any \(x_l=unknown\) | FAIL_CLOSED |
| Receipt failure | Cannot emit ICAT receipt | FAIL_CLOSED |
| Cost scalarization | Valid \(I^{\mu\nu}\), scalar budget | Compare \(\mathcal C\), not tensor |
| Full pass | All gates pass | ICAT_PASS |

### 12.3 Conservation Checks

Every ICAT evaluation must verify:

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

\[
\$I(\Delta D,t)\ge 0
\]

### 12.4 Receipt Requirements

Each ICAT receipt must include:

- transition identifier;
- pre-state hash;
- proposed post-state hash;
- transition hash;
- policy hash;
- proof hash;
- witness set hash;
- conservation set hash;
- inverse constraint set hash;
- proof result;
- witness result;
- conservation result;
- inverse result;
- scalar ICAT cost;
- final ICAT outcome;
- timestamp;
- signer or system identity.

---

## 13. Implementation Requirements

A compliant ICAT implementation must expose:

1. `build_proof_object(transition, pre_state, post_state, policy)`
2. `verify_proof(proof_object, transition, pre_state, post_state, policy)`
3. `compute_proof_score(proof_object, commit_time)`
4. `collect_attestations(transition, witness_policy)`
5. `verify_attestation(attestation, witness, transition)`
6. `compute_witness_score(attestations, witness_weights)`
7. `verify_witness_independence(witness_set)`
8. `resolve_conservation_laws(data_object, transition)`
9. `evaluate_conservation_law(law, pre_state, post_state, transition)`
10. `resolve_inverse_constraints(data_object, transition)`
11. `evaluate_inverse_constraint(constraint, pre_state, post_state, transition)`
12. `compute_icat_cost(transition, proof, attestations, laws, constraints)`
13. `emit_icat_receipt(outcome, evaluation_context)`
14. `evaluate_icat_gate(transition, pre_state, post_state, policy, budget_context)`

A compliant implementation must emit receipts for:

- proof creation;
- proof verification;
- proof failure;
- attestation request;
- attestation verification;
- witness quorum pass;
- witness quorum failure;
- conservation pass;
- conservation failure;
- inverse constraint pass;
- inverse constraint failure;
- ICAT ALLOW;
- ICAT DENY;
- ICAT FAIL_CLOSED.

---

## 14. ICAT and Receipt Chains

ICAT requires receipt-chain continuity.

For a transition to commit, the new receipt must link to the prior receipt chain:

\[
Receipt_{n}.prev\_hash = hash(Receipt_{n-1})
\]

and:

\[
Receipt_{n}.state\_pre = hash(S_t)
\]

\[
Receipt_{n}.state\_post = hash(S_{t+1})
\]

If the prior receipt chain cannot be resolved:

\[
ChainResolve=unknown\Rightarrow FAIL\_CLOSED
\]

If the prior receipt chain is invalid:

\[
ChainValid=0\Rightarrow DENY
\]

If the transition would create a receipt gap:

\[
ReceiptGap=1\Rightarrow FAIL\_CLOSED
\]

---

## 15. ICAT and Reconstruction

A transition is reconstruction-admissible only if the resulting receipt enables independent reconstruction of:

\[
S_t,\quad \Delta D,\quad S_{t+1},\quad Policy_t,\quad Outcome
\]

or, where full reconstruction is impossible, a declared degraded reconstruction score:

\[
Q_{recon}\in[0,1]
\]

must be emitted.

If reconstruction quality is required and:

\[
Q_{recon}<Q_{min}
\]

then:

\[
\Delta D\Rightarrow DENY
\]

If reconstruction quality cannot be estimated:

\[
Q_{recon}=unknown\Rightarrow FAIL\_CLOSED
\]

---

## 16. Open Questions

1. **Proof system selection:** Which transitions require hashes, signatures, Merkle proofs, zk-proofs, STARKs, SNARKs, or ordinary deterministic recomputation?
2. **Proof freshness:** How should \(\tau_{proof}\) vary by transition category?
3. **Witness incentives:** How should witness cost and reliability be priced?
4. **Witness independence:** What minimum evidence establishes non-collusion or independent observation?
5. **Conservation language:** What formal language defines \(k_j\) predicates?
6. **Inverse constraint language:** What formal language defines \(x_l\) predicates?
7. **Receipt compression:** How much proof material may be compressed without reducing reconstructability?
8. **Privacy-preserving proofs:** When should proof content be hidden while preserving verifiability?
9. **Failure appeal:** What process allows a failed proof or failed witness quorum to be retried?
10. **Cross-org receipts:** How should ICAT verify receipt continuity across StegVerse-org, StegVerse-Labs, StegGhost, and future namespaces?

---

## 17. Version Note

This initial ICAT draft defines the integrity-side formalism required by the StegVerse Cost Tensor.

It introduces:

1. Proof sufficiency \(P\).
2. Witness and attestation sufficiency \(A\).
3. Conservation-law preservation \(K\).
4. Inverse constraint preservation \(X\).
5. Scalar ICAT cost \(\$I=C_P+C_A+C_K+C_X\).
6. Tensor-compatible ICAT deviation vector \(\eta\).
7. Hard gates for proof, witness, conservation, inverse constraint, receipt, and reconstruction.
8. Receipt-chain requirements.
9. Reconstruction-quality requirements.

Together with ECAT v0.2.0, this draft closes the entity and integrity placeholder layers identified in the Cost Tensor Specification.

The next required artifact is:

```text
COST_TENSOR_SPEC_v0.2.0.md
```

which should integrate the finalized scalar forms:

\[
\$E=C_R+C_S+C_H+C_W
\]

\[
\$I=C_P+C_A+C_K+C_X
\]

into the full admissibility condition.

---

**Document:** ICAT_FORMALISM.md  
**Version:** 0.1.0-draft  
**Date:** 2026-05-03  
**Org:** ECAT-ICAT-Formal
