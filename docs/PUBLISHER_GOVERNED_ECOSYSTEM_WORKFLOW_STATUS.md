# Publisher Governed Ecosystem Workflow Status

## Purpose

This document records the current workflow status for Publisher governed ecosystem awareness validation.

## Current status

```text
PUBLISHER_GOVERNED_ECOSYSTEM_WORKFLOW_STATUS_PRESENT
DEDICATED_WORKFLOW_PRESENT
DEDICATED_WORKFLOW_RUN_PENDING
AGGREGATE_RUNNER_WIRING_PARTIAL
```

## Dedicated workflow

```text
github/workflows/validate-governed-ecosystem-awareness.yml
```

## Aggregate workflow

```text
github/workflows/validate-emergency-ai-cases.yml
```

## Dedicated workflow command set

```text
python tools/check_governed_ecosystem_site_mirror_awareness.py
python tools/check_stegguardian_propagation_status.py
python tools/check_publisher_governed_ecosystem_sync_status.py
python tools/check_publisher_governed_ecosystem_validation_status.py
python tools/check_publisher_governed_ecosystem_workflow_request.py
```

## Boundary

This status does not claim the dedicated workflow has passed. It records that the workflow and required checker surfaces are present and awaiting run evidence.

## Remaining evidence

```text
Successful validate-governed-ecosystem-awareness.yml run
Successful validate-emergency-ai-cases.yml run after aggregate wiring is complete
```
