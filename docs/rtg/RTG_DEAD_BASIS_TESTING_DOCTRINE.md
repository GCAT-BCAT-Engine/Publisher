# RTG Dead Basis Testing Doctrine

## Purpose

This document records the RTG testing rule discovered during the RTG-001 solver-handoff buildout.

A **dead basis** is a test foundation that still exists, may still execute, and may still pass, but no longer produces meaningful transition power.

```text
dead_basis
= a basis set of tests, fixtures, tasks, candidate vectors, or assumptions
  that no longer distinguishes, routes, validates, rejects, emits, receives,
  learns from, or updates a real transition.
```

## Current RTG Risk

The central risk is:

```text
Data-Continuation/RTG-Tests keeps testing itself
while GCAT-BCAT-Engine/workflows is never invoked.
```

That creates a false-transition risk:

```text
local RTG test passed
→ therefore the system says the math-solver pipeline was tested
→ but the math-solver never ran
```

This must be blocked.

## Correct Live Basis

A live basis for RTG-001 must preserve the full transition boundary:

```text
Data-Continuation/RTG-Tests
→ governed RTG request / instruction / problem spec
→ GCAT-BCAT-Engine/workflows
→ math_solver/validation
→ Anthropic reasoning phase
→ GitHub Ubuntu deterministic validation phase
→ returned artifacts
→ RTG ingestion
→ RTG state update
```

## Claim Boundary

Before workflow dispatch, the only admissible claim is:

```text
handoff_contract_ready
```

After the workflows package is installed, the admissible claim becomes:

```text
handoff_installed_in_execution_repo
```

Only after GitHub Actions runs and returns artifacts may the system claim:

```text
artifact_returned
```

Only after RTG parses the returned artifacts may the system claim:

```text
artifact_ingested
```

Only after RTG writes the receipt chain and next-state record may the system claim:

```text
rtg_state_updated
```

## Dead Basis Diagnostic

A basis is dead if it passes while proving only:

```text
pytest_passed: yes
json_file_exists: yes
task_declared: yes
```

A basis is live if it identifies or constrains at least one real transition property:

```text
solver dispatch
workflow input validation
required secret expectation
returned artifact set
cost receipt
claim-boundary preservation
RTG ingestion
next-state selection
```

## Publisher Rule

Publisher must not present RTG-001 as solver-executed until the returned workflow artifacts exist and are ingested.

Safe wording before dispatch:

```text
RTG-001 has a live handoff contract and an install package for the workflows execution repo.
```

Unsafe wording before dispatch:

```text
RTG-001 executed the math-solver.
RTG-001 called Anthropic.
RTG-001 completed Ubuntu validation.
RTG-001 returned solver artifacts.
```
