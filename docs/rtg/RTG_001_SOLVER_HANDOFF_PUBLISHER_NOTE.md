# RTG-001 Solver Handoff Publisher Note

## Repository Boundary

RTG-001 spans two repositories:

```text
Data-Continuation/RTG-Tests
GCAT-BCAT-Engine/workflows
```

`Data-Continuation/RTG-Tests` is the request, proof-harness, and ingestion side.

`GCAT-BCAT-Engine/workflows` is the execution side. It owns the GitHub Actions workflow, the `math_solver/validation` layer, Anthropic API use, Ubuntu runner validation, and artifact upload.

## Current Publisher Status

The Publisher repo records this as a governed handoff case, not a completed solver execution.

Current status:

```text
handoff_contract_ready
handoff_install_package_created
workflow_execution_pending
returned_artifact_ingestion_pending
```

## Installed Workflows Paths

The workflows install package targets:

```text
math_solver/validation/problem_spec_rtg_001.yml
math_solver/validation/candidate_vectors/rtg/rtg_001.json
math_solver/validation/cost_estimates/rtg_001_cost_estimate.json
math_solver/validation/rtg_handoff_manifest.json
math_solver/validation/rtg_declared_tasks.json
math_solver/validation/tests/test_rtg_001_workflows_install_contract.py
```

## Required Workflow Run

The next execution step is a manual GitHub Actions dispatch in:

```text
GCAT-BCAT-Engine/workflows
.github/workflows/validation_run.yml
```

Inputs:

```text
run_id: RTG-001
budget_ceiling: 50.00
```

Required secret:

```text
ANTHROPIC_API_KEY
```

Runner:

```text
ubuntu-latest
```

## Expected Returned Artifact Set

The expected artifact upload is:

```text
external-full-results
```

Expected files:

```text
ext2_phase1.json
ext2_sources.json
ext2_phase3.json
ext2_report.json
```

## Publication Boundary

Before artifact return, Publisher may say:

```text
RTG-001 has been staged for GCAT-BCAT workflow execution.
```

After artifact return but before RTG ingestion, Publisher may say:

```text
RTG-001 returned workflow artifacts and is awaiting RTG ingestion.
```

After ingestion, Publisher may say:

```text
RTG-001 completed an artifact-ingested solver handoff cycle.
```

Publisher must not say:

```text
RTG-001 proved a theorem.
RTG-001 achieved final correctness.
RTG-001 completed autonomous theorem proving.
```

unless a separate human or formal verification record exists.
