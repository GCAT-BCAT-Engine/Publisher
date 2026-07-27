# Marketplace–Coinbase Publication Handoff

## Goal
Consume only verified Marketplace–Coinbase paper settlement evidence after Marketplace has independently accepted and acknowledged the settlement packet.

## Current State
`marketplace_coinbase_publication.py` and its test suite are installed. Publisher now has an executable packet-plus-acknowledgement gate and durable idempotent publication ledger.

## Required Inputs
1. A settlement export packet with version `marketplace-coinbase-settlement-export-v1`.
2. A Marketplace acknowledgement with version `marketplace-coinbase-settlement-ack-v1`.
3. Exact packet-digest and intent-ID binding between both artifacts.
4. Marketplace result `ACCEPTED` or `DUPLICATE` with `marketplace_indexed=true`.
5. Explicit `live_authority_granted=false` in both artifacts.

## Results
- `ACCEPTED`: packet and acknowledgement verify and a bounded projection is stored.
- `DUPLICATE`: the identical packet and acknowledgement were already stored.
- `REJECTED`: missing acknowledgement, invalid digest, mismatched binding, conflicting state, unsupported decision, or false live-authority claim.

## Projection Boundary
Every stored projection preserves:

```text
paper_evidence_verified = true
publication_authorized = false
release_authorized = false
live_authority_granted = false
```

The projection records verified evidence. It does not itself authorize publication, release, custody, deployment, payment, entitlement, Coinbase execution, or live financial activity.

## Installed Files
- `marketplace_coinbase_publication.py`
- `tests/test_marketplace_coinbase_publication.py`
- `docs/MARKETPLACE_COINBASE_SETTLEMENT_PUBLICATION.md`
- issue `GCAT-BCAT-Engine/Publisher#16`

## Remaining Work
1. Add an automated repository-owned importer for Marketplace packet and acknowledgement artifacts.
2. Verify the Marketplace-to-Publisher transport receipt and sequence binding.
3. Persist downstream publication transport and projection receipts.
4. Observe accepted, duplicate, missing-acknowledgement, digest-mismatch, conflict, and false-live-claim evidence in CI.
5. Publish only after the separate publication-authority process grants authority; transport and verification remain non-authoritative.

## Archive Readiness
This file and the installed executable gate preserve all continuation context required for this workstream.
