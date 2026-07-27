# Marketplace–Coinbase Publication Handoff

## Goal
Consume only verified Marketplace–Coinbase paper settlement evidence after Marketplace has independently accepted and acknowledged the settlement packet and issued the chained Publisher transport receipt.

## Current State
The packet-plus-acknowledgement gate, durable publication ledger, repository-owned import runner, transport-chain verifier, publication receipt generator, tests, and workflow are installed.

## Required Inputs
1. A settlement export packet with version `marketplace-coinbase-settlement-export-v1`.
2. A Marketplace acknowledgement with version `marketplace-coinbase-settlement-ack-v1`.
3. A Marketplace-to-Publisher transport receipt with version `marketplace-coinbase-transport-v1`.
4. Exact packet-digest and intent-ID binding across all artifacts.
5. Marketplace result `ACCEPTED` or `DUPLICATE` with `marketplace_indexed=true`.
6. Transport source Marketplace, destination Publisher, sequence 2, and previous digest bound to the sequence-1 transport recorded in the acknowledgement.
7. Explicit false authority flags throughout.

## Automated Import
`scripts/import_marketplace_coinbase_settlements.py` consumes artifact triplets from `incoming/marketplace-coinbase/`. `.github/workflows/import-marketplace-coinbase-settlements.yml` runs on relevant pushes or manual dispatch, executes the failure-case test suite, imports verified triplets, and commits only changed bounded projections and receipts.

## Results
- `ACCEPTED`: packet, acknowledgement, and transport chain verify; a bounded projection and publication receipt are stored.
- `DUPLICATE`: identical accepted evidence was already stored.
- `REJECTED`: missing acknowledgement or transport, invalid digest, mismatched binding, broken sequence chain, conflict, unsupported decision, or false authority claim.

## Projection Boundary
Every stored projection and publication receipt preserves:

```text
paper_evidence_verified = true only after all gates pass
publication_authorized = false
release_authorized = false
live_authority_granted = false
```

The projection records verified evidence. It does not authorize publication, release, custody, deployment, payment, entitlement, Coinbase execution, or live financial activity.

## Installed Files
- `marketplace_coinbase_publication.py`
- `scripts/import_marketplace_coinbase_settlements.py`
- `.github/workflows/import-marketplace-coinbase-settlements.yml`
- `tests/test_marketplace_coinbase_publication.py`
- `tests/test_marketplace_coinbase_import_runner.py`
- `docs/MARKETPLACE_COINBASE_SETTLEMENT_PUBLICATION.md`
- issue `GCAT-BCAT-Engine/Publisher#16`

## Remaining Work
1. Observe accepted, duplicate, missing-acknowledgement, transport-mismatch, digest-mismatch, conflict, and false-live-claim evidence in repository workflows.
2. Preserve the exact cross-repository packet, acknowledgement, transport, projection, and publication-receipt chain.
3. Publish only after the separate publication-authority process grants authority; transport and verification remain non-authoritative.

## Progress Snapshot
Publisher settlement import - 98% complete
Publisher publication gate - 98% complete
Remaining - observed workflow and cross-repository evidence only

## Archive Readiness
This file and the installed executable gate preserve all continuation context required for this workstream.
