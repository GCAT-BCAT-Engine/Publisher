# Marketplace–Coinbase Publication Handoff

## Goal
Consume only verified Marketplace–Coinbase paper settlement evidence after Marketplace has independently accepted and acknowledged the settlement packet, issued the chained Publisher transport receipt, and the complete private-repository evidence chain has been collected and verified.

## Current State
The packet-plus-acknowledgement gate, durable publication ledger, repository-owned import runner, transport-chain verifier, publication receipt generator, cross-repository artifact collector, tests, and workflows are installed.

## Required Inputs
1. A settlement export packet with version `marketplace-coinbase-settlement-export-v1`.
2. A Marketplace acknowledgement with version `marketplace-coinbase-settlement-ack-v1`.
3. A Marketplace-to-Publisher transport receipt with version `marketplace-coinbase-transport-v1`.
4. Exact packet-digest and intent-ID binding across all artifacts.
5. Marketplace result `ACCEPTED` or `DUPLICATE` with `marketplace_indexed=true`.
6. Transport source Marketplace, destination Publisher, sequence 2, and previous digest bound to the sequence-1 transport recorded in the acknowledgement.
7. A crypto-bot release-readiness receipt bound to a passing cross-repository evidence manifest.
8. Explicit false authority flags throughout.

## Automated Import
`scripts/import_marketplace_coinbase_settlements.py` consumes artifact triplets from `incoming/marketplace-coinbase/`. `.github/workflows/import-marketplace-coinbase-settlements.yml` runs on relevant pushes or manual dispatch, executes the failure-case test suite, imports verified triplets, and commits only changed bounded projections and receipts.

## Cross-Repository Evidence Collection
`scripts/collect_marketplace_coinbase_release_evidence.py` collects the latest non-expired named artifacts from private crypto-bot and Marketplace repositories through the established repository-scoped artifact-token pattern. `.github/workflows/collect-marketplace-coinbase-release-evidence.yml` runs hourly, on dispatch, and on collector changes.

The collector records one explicit state:

- `PENDING_CREDENTIAL`: the governed private-repository read credential is unavailable;
- `PENDING_SOURCE`: an upstream artifact cannot yet be collected;
- `REJECTED`: artifacts exist but fail digest, binding, or decision checks;
- `VERIFIED`: the hash-bound paper release and cross-repository manifest verify.

An absent credential never becomes a false failure or false success. Manual dispatch remains validation-only and cannot persist release state.

## Results
- `ACCEPTED`: packet, acknowledgement, and transport chain verify; a bounded projection and publication receipt are stored.
- `DUPLICATE`: identical accepted evidence was already stored.
- `REJECTED`: missing acknowledgement or transport, invalid digest, mismatched binding, broken sequence chain, conflict, unsupported decision, or false authority claim.

## Projection Boundary
Every stored projection, publication receipt, and evidence status preserves:

```text
publication_authorized = false
release_authorized = false
execution_authorized = false
live_authority_granted = false
```

`paper_evidence_verified` becomes true only after all evidence gates pass. Verification does not authorize publication, release, custody, deployment, payment, entitlement, Coinbase execution, or live financial activity.

## Installed Files
- `marketplace_coinbase_publication.py`
- `scripts/import_marketplace_coinbase_settlements.py`
- `scripts/collect_marketplace_coinbase_release_evidence.py`
- `.github/workflows/import-marketplace-coinbase-settlements.yml`
- `.github/workflows/collect-marketplace-coinbase-release-evidence.yml`
- `tests/test_marketplace_coinbase_publication.py`
- `tests/test_marketplace_coinbase_import_runner.py`
- `tests/test_marketplace_coinbase_release_evidence_collector.py`
- `docs/MARKETPLACE_COINBASE_SETTLEMENT_PUBLICATION.md`
- issue `GCAT-BCAT-Engine/Publisher#16`

## Remaining Work
1. Allow the hourly collector to observe the named private-repository artifacts through the governed evidence token.
2. Preserve a `VERIFIED` evidence status with exact artifact IDs, workflow run IDs, receipt digest, and manifest digest.
3. Observe accepted, duplicate, missing-acknowledgement, transport-mismatch, digest-mismatch, conflict, and false-live-claim evidence in repository workflows.
4. Publish only after the separate publication-authority process grants authority; transport and verification remain non-authoritative.

## Progress Snapshot
Publisher settlement import - 100% implemented
Publisher publication gate - 100% implemented
Cross-repository evidence collection - 100% implemented
Remaining - observed artifact collection and verified workflow evidence only

## Archive Readiness
This file and the installed executable gates preserve all continuation context required for this workstream.
