# RTG-001 Real Evidence Status

## Real Evidence Location

Real workflow evidence has been detected.

```text
repo: GCAT-BCAT-Engine/workflows
workflow_run_id: 27597978374
workflow_name: StegVerse External Full Process v2 - Erdos Class
workflow_conclusion: success
artifact_id: 7658749562
artifact_name: external-full-results
artifact_size_in_bytes: 3813
artifact_expired: false
```

## Returned Files

```text
ext2_phase1.json
ext2_sources.json
ext2_phase3.json
ext2_report.json
```

## Actual Cost Receipt

```text
reported_run_id: EXT-002-FIXED
total_cost_usd: 0.0219265
total_tokens: 3193
sources_verified: true
```

## Boundary Finding

This is real workflow evidence, but it is not a clean direct RTG-001 ingestion receipt yet.

Reason:

```text
artifact reported run id: EXT-002-FIXED
RTG case id: RTG-001
claim_boundary field in ext2_report.json: absent
```

## Current Claim Boundary

Publisher may now say:

```text
artifact_returned: true
actual_solver_cost_receipt_detected: true
```

Publisher must still not say:

```text
artifact_ingested_as_rtg_001
rtg_state_updated_from_real_artifact
final_correctness_claimed
autonomous_theorem_proving_claimed
```

## Next Step

Use the RTG-Tests normalization / crosswalk adapter before any RTG-001 state update from the real artifact.
