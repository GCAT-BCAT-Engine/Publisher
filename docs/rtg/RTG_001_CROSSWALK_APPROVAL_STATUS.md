# RTG-001 Crosswalk Approval Status

## Current Status

RTG-001 now has a crosswalk approval layer in `Data-Continuation/RTG-Tests`.

It handles the mismatch:

```text
returned artifact run_id: EXT-002-FIXED
RTG case_id: RTG-001
```

## Approved Posture

The crosswalk may approve a wrapped ingestion candidate only if it preserves:

```text
original run id
actual cost receipt
source verification
missing claim-boundary wrapper
mismatch visibility
```

## Allowed After Crosswalk Approval

```text
crosswalk_approved
wrapped_receipt_created
artifact_returned
actual_solver_cost_receipt_detected
```

## Still Blocked

```text
artifact_ingested_as_rtg_001
rtg_state_updated_from_real_artifact
final_correctness_claimed
autonomous_theorem_proving_claimed
```

## Next Step

Create the real RTG-001 ingestion layer that consumes:

```text
evidence/rtg_001/rtg_001_wrapped_real_artifact_receipt.json
```

and only then allows:

```text
artifact_ingested_as_rtg_001: true
```
