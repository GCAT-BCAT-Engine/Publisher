# RTG-001 State Update Boundary

## Purpose

This Publisher note records the boundary between:

```text
artifact_ingested
```

and:

```text
rtg_state_update_recorded
```

## Source Repo Update

`Data-Continuation/RTG-Tests` now contains a state-update module and test that read:

```text
ingestion/rtg_001/rtg_001_ingestion_result.json
```

and write:

```text
status/rtg_001_state_update.json
receipts/rtg_001/rtg_001_state_update_receipt.json
```

## Claim Boundary

The state update records receipt continuity and next-state selection readiness.

It still does not claim:

```text
final correctness
autonomous theorem proof
human or formal review completion
```

## Current Publisher Interpretation

Publisher may say:

```text
RTG-001 now has a complete RTG-side ingestion-to-state-update path staged.
```

Publisher must not say:

```text
RTG-001 has completed real artifact ingestion
```

until the fixture artifacts are replaced by returned `external-full-results` files from `GCAT-BCAT-Engine/workflows`.
