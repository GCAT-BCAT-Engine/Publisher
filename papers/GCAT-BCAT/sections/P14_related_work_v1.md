## Related Work

### Control barrier functions and forward invariance

Control barrier function research formalizes safety as forward invariance of a designated set under controlled dynamics. Ames, Xu, Grizzle, and Tabuada develop control-barrier constraints that can be combined with control-Lyapunov objectives in real-time quadratic programs [@ames2017cbfqp]. Later survey work summarizes the use of CBFs to verify and enforce safety properties across safety-critical control applications [@ames2019cbfsurvey]. Robust extensions show that disturbance handling requires additional assumptions and may preserve a relaxed invariant set rather than the original set [@xu2018robustcbf].

GCAT uses this literature narrowly. The margin `h = -log Omega` defines a candidate admissible set, and the conditional proposition adopts a standard differential-inequality structure. GCAT does not claim a new general barrier theorem, nor does the present paper establish that an admissible institutional control policy exists. That existence question depends on measurable dynamics, available authority, intervention latency, bounded actuation, disturbance models, and state estimation.

### Viability, admissibility, and recoverability

Viability theory distinguishes a constraint set from the viability kernel: the initial states from which at least one admissible evolution can remain within the constraint set [@aubin1991viability; @aubin2011viability]. This distinction is central to the GCAT separation between a state that presently satisfies `Omega <= 1` and a state that remains recoverable under bounded governance intervention.

The current numerical scenarios illustrate this distinction but do not compute a viability kernel. In particular, the bounded-recovery scenario is designed to begin inside the candidate admissible set and cross the frontier under declared control limits. It is therefore an illustration of possible non-viability under one model, not a proof of the full kernel boundary.

### Production functions and institutional capacity

The multiplicative capacity form is analogous to the Cobb-Douglas production function introduced in production economics [@cobb1928production]. In GCAT, the produced quantity is modeled governable execution capacity rather than market output. The exponents are therefore proposed institutional elasticities, not estimated economic factor shares.

Because the multiplicative form imposes a particular complementarity and substitution structure, the sensitivity study also evaluates additive, weighted-geometric, bottleneck-minimum, and constant-elasticity-of-substitution alternatives. The CES comparator follows the production-function family developed to represent variable substitution patterns [@arrow1961ces]. Agreement across functional forms supports robustness of a qualitative classification; disagreement identifies dependence on an unvalidated modeling choice.

### Bounded decision capacity and organizational failure

Bounded-rationality research rejects the assumption that organizational decision makers possess unlimited information and computation [@simon1955behavioral]. Organizational-failure research further shows how mistakes, misconduct, and disaster can be produced through ordinary organizational processes rather than the absence of formal rules [@vaughan1999darkside]. Vaughan's Challenger analysis is especially relevant to gradual normalization of locally accepted practices, but it is not evidence for the paper's federal IT observation and must not be used to infer wrongdoing in that setting [@vaughan1996challenger].

Systems-theoretic safety work likewise frames accidents as control problems distributed across technical and organizational structures [@leveson2011safer]. GCAT is consistent with that systems orientation, but its proposed load ratio, production frontier, and latent variables remain distinct modeling claims requiring independent validation.

### Positioning of GCAT

The contribution is a synthesis and proposed institutional application, not a replacement for these fields. Barrier theory supplies a language for forward invariance; viability theory supplies a language for recoverability; production economics supplies testable functional forms; and organizational theory motivates bounded governance capacity. GCAT combines these elements into a falsifiable governance-load model while preserving explicit boundaries between established theory, synthetic illustration, observational mapping, and empirical validation.
