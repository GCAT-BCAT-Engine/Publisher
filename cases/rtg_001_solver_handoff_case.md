# RTG-001 Solver Handoff Case

## Case ID

```text
RTG-001
```

## Case Type

```text
live-basis solver handoff
```

## Source Repo

```text
Data-Continuation/RTG-Tests
```

## Execution Repo

```text
GCAT-BCAT-Engine/workflows
```

## Case Summary

RTG-001 is the first explicit RTG live-basis handoff case. It exists to prevent a local test basis from being confused with external solver execution.

The case separates five states:

```text
contract_ready
handoff_installed_in_execution_repo
workflow_dispatch_attempted
artifact_returned
artifact_ingested
rtg_state_updated
```

## Current State

```text
handoff_installed_in_execution_repo
workflow_dispatch_pending
```

## Workflows Repo Install Evidence

The following paths have been staged into `GCAT-BCAT-Engine/workflows`:

```text
docs/RTG_001_WORKFLOWS_INSTALL_CONTRACT.md
math_solver/validation/problem_spec_rtg_001.yml
math_solver/validation/candidate_vectors/rtg/rtg_001.json
math_solver/validation/cost_estimates/rtg_001_cost_estimate.json
math_solver/validation/rtg_handoff_manifest.json
math_solver/validation/rtg_declared_tasks.json
math_solver/validation/tests/test_rtg_001_workflows_install_contract.py
```

## Required Next Action

Run the workflow dispatch in `GCAT-BCAT-Engine/workflows`:

```text
run_id: RTG-001
budget_ceiling: 50.00
```

## Returned Artifact Requirement

The case cannot advance to `artifact_returned` until this artifact set exists:

```text
external-full-results
  ext2_phase1.json
  ext2_sources.json
  ext2_phase3.json
  ext2_report.json
```

## RTG Ingestion Requirement

The case cannot advance to `artifact_ingested` until `Data-Continuation/RTG-Tests` ingests those files and verifies:

```text
cost receipt parsed
claim boundary preserved
sources verified
false proof claims blocked
next RTG state selected
```

## Claim Boundary

Allowed now:

```text
RTG-001 is staged for workflow execution.
```

Blocked now:

```text
RTG-001 executed the solver.
RTG-001 called Anthropic.
RTG-001 returned artifacts.
RTG-001 updated RTG state.
RTG-001 proved a theorem.
```
