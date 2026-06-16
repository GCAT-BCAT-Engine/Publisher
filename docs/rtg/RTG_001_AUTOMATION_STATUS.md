# RTG-001 Automation Status

## Current Status

```text
auto-dispatch workflow installed
automation marker committed
awaiting GitHub Actions run/artifact evidence
```

## Updated Workflows Paths

```text
.github/workflows/rtg_001_auto_dispatch.yml
math_solver/validation/rtg_auto_run_request.json
```

## Target Existing Solver Workflow

```text
.github/workflows/validation_run.yml
```

Inputs intended for the existing solver workflow:

```text
run_id: RTG-001
budget_ceiling: 50.00
```

## Claim Boundary

Allowed now:

```text
RTG-001 automation has been staged.
```

Not yet allowed:

```text
artifact_returned
artifact_ingested
rtg_state_updated
final_correctness_claimed
autonomous_theorem_proving_claimed
```

## Next Evidence Required

The case must wait for the returned artifact set:

```text
external-full-results
  ext2_phase1.json
  ext2_sources.json
  ext2_phase3.json
  ext2_report.json
```
