# AaCT-E — Admissibility at Commit-Time Engine

## Abstract

AaCT-E is a runtime enforcement mechanism that determines whether an action should be allowed at the exact moment it becomes irreversible. Unlike existing systems that rely on pre-execution validation or post-execution monitoring, AaCT-E evaluates whether executing an action preserves the system’s ability to remain within a recoverable and governable state.

This Phase I work demonstrates the mechanism in a controlled simulation environment. The result is a deterministic system that produces ALLOW/DENY decisions at commit-time, based on projected system evolution and the continued availability of recovery actions.

---

## Operational Scope and Setup

This prototype is executed in a deterministic, local simulation environment using a simplified dynamic model. The system evaluates discrete action proposals over a fixed time horizon and produces a commit-time decision.

### Simulation characteristics
- State model: 2D position (x, y), heading, speed  
- Dynamics: constant velocity, instantaneous heading changes  
- Time model: fixed time step, short prediction horizon  
- Execution platform: local Python runtime (no external data feeds)  
- Inputs: manually constructed scenario files (JSON)  
- Outputs: deterministic execution traces and ALLOW/DENY decisions  

### Safety representation
- Safety is defined as minimum pairwise separation over the projected horizon  
- A threshold (e.g., 3 nautical miles) is used as a proxy for safe operation  
- This is a reduced safety model, not a full FAA separation implementation  

---

## Vehicle-Agnostic Design

This system is intentionally vehicle-type agnostic, meaning it does not assume or encode:

- specific aircraft classes (commercial, military, cargo, rotorcraft)  
- spacecraft dynamics (orbital mechanics, thrust modeling)  
- vehicle-specific performance limits (turn radius, climb rate, thrust curves)  
- procedural or regulatory constraints  

Instead, all entities are modeled as state-constrained agents evolving under simple dynamics.

### Why this matters

The purpose of this abstraction is to isolate and validate a single claim:

> A system can determine, at the moment of action, whether executing that action preserves the ability to recover.

This property is independent of vehicle type.  
It applies to any system where:
- state evolves over time  
- actions produce irreversible transitions  
- safety depends on maintaining recoverability  

---

## What This Demonstration Proves

- A commit-time decision mechanism can be implemented  
- The mechanism can evaluate future state trajectories, not just current state  
- The system can deny actions that lead to loss of recoverability  
- The decision process is deterministic and reproducible  

---

## What This Demonstration Does Not Claim

- It does not model real aircraft or spacecraft behavior  
- It does not implement certified separation standards  
- It does not include uncertainty, latency, or sensor error  
- It does not demonstrate operational readiness  

This is a mechanism validation, not an operational system.

---

## Demonstration Scenarios

### Scenario A — unsafe_merge
- Proposed action directs one agent toward a conflict trajectory  
- Projected separation falls below threshold  
- AaCT-E returns: DENY  
- Alternative actions exist that preserve recoverability  

### Scenario B — safe_hold
- Proposed action maintains safe geometry  
- Projected separation remains above threshold  
- AaCT-E returns: ALLOW  

---

## Core Definition

An action is admissible if executing it preserves the system’s ability to remain within a recoverable and governable state.

Formally:

- Let x be system state  
- Let U be the admissible (safe) set  

An action u is admissible if:

x(t + Δt) ∈ U  
and  
reachable_safe_states(x, u) ≠ ∅  

---

## Bottom Line

This prototype demonstrates a new control point:

> If an action would eliminate the ability to recover, it is not allowed to occur.
