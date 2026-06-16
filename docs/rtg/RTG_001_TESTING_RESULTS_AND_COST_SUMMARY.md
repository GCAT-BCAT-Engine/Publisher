# RTG-001 Testing Results and Cost Summary

## Current Test Coverage

RTG-001 now spans three repos:

```text
Data-Continuation/RTG-Tests
GCAT-BCAT-Engine/workflows
GCAT-BCAT-Engine/Publisher
```

## Test Stages Staged So Far

```text
handoff_contract_ready
handoff_installed_in_execution_repo
auto_dispatch_workflow_installed
auto_run_marker_committed
artifact_watch_installed
returned_artifact_ingestion_ready
rtg_state_update_path_ready
next_instruction_selection_ready
```

## RTG-Tests Declared Tasks

```text
rtg_to_gcat_bcat_workflows_connectivity_tests
rtg_001_returned_artifact_ingestion_tests
rtg_001_state_update_from_ingestion_tests
rtg_001_next_instruction_selection_tests
```

## Current Evidence Boundary

Still pending real returned workflow artifacts:

```text
artifact_returned
artifact_ingested_from_real_artifact
rtg_state_updated_from_real_artifact
```

Still blocked:

```text
autonomous_theorem_proving_claimed
final_correctness_claimed
```

## Cost Summary

Reference costs staged in RTG-001:

```text
external_full_process_reference_usd: 0.02086
external_incremental_reference_usd: 0.035
budget_ceiling_usd: 50.00
```

These are reference estimates until the real report artifact returns.

The actual cost receipt must be read from:

```text
ext2_report.json
```

## Current Cost Posture

```text
pre_execution_estimate_only
actual_cost_receipt_pending
within_budget_reference_gate
```
