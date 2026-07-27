# Marketplace–Coinbase Publication Handoff

## Goal
Consume only verified Marketplace–Coinbase paper settlement evidence after Marketplace has independently accepted and acknowledged the settlement packet, issued the chained Publisher transport receipt, and Publisher has reconstructed the complete evidence chain without requiring crypto-bot's final release decision first.

## Current State
The packet-plus-acknowledgement gate, durable publication ledger, repository-owned import runner, transport-chain verifier, publication receipt generator, cross-repository artifact collector, ecosystem reconstruction verifier, tests, private-evidence custody controls, and workflows are installed.

## Two-Stage Release Protocol
The previous dependency was circular and is superseded.

### Stage 1 — Repository Readiness
Crypto-bot CI may emit:

- `PAPER_RELEASE_BLOCKED_PENDING_CROSS_REPOSITORY_EVIDENCE`; and
- a digest-valid repository-readiness receipt proving its own tests and paper runtime passed.

Publisher accepts this as repository readiness only. It does not require `PAPER_RELEASE_READY` at this stage.

### Stage 2 — Ecosystem Verification
Publisher combines:

1. the crypto-bot repository-readiness artifact;
2. the Marketplace settlement packet;
3. sequence-1 crypto-bot-to-Marketplace transport;
4. the Marketplace acknowledgement;
5. sequence-2 Marketplace-to-Publisher transport;
6. Publisher's own stored projection; and
7. Publisher's publication receipt.

Publisher independently verifies every digest, identity, sequence, binding, result, and authority boundary. A `VERIFIED` status then becomes the public ecosystem-verification input for crypto-bot's finalizer. Crypto-bot alone emits the final paper-release receipt after confirming the Publisher status references the exact crypto commit and repository-readiness receipt.

## Required Inputs
1. A settlement export packet with version `marketplace-coinbase-settlement-export-v1`.
2. A Marketplace acknowledgement with version `marketplace-coinbase-settlement-ack-v1`.
3. A Marketplace-to-Publisher transport receipt with version `marketplace-coinbase-transport-v1`.
4. Exact packet-digest and intent-ID binding across all artifacts.
5. Marketplace result `ACCEPTED` or `DUPLICATE` with `marketplace_indexed=true`.
6. Transport source Marketplace, destination Publisher, sequence 2, and previous digest bound to sequence 1.
7. A digest-valid crypto-bot repository-readiness receipt with `ci_tests=PASS`, `paper_runtime=IMPLEMENTED`, and `live_authority=NOT_GRANTED`.
8. Publisher projection and publication receipt bound to the same intent, packet, acknowledgement, and sequence-2 transport.
9. Explicit false authority flags throughout.

## Automated Import
`scripts/import_marketplace_coinbase_settlements.py` consumes artifact triplets from `incoming/marketplace-coinbase/`. `.github/workflows/import-marketplace-coinbase-settlements.yml` runs on relevant pushes or manual dispatch, executes the failure-case test suite, imports verified triplets, and commits only changed bounded projections and receipts.

## Cross-Repository Evidence Collection
`scripts/collect_marketplace_coinbase_release_evidence.py` collects the latest non-expired named artifacts from private crypto-bot and Marketplace repositories through the established repository-scoped artifact-token pattern. `.github/workflows/collect-marketplace-coinbase-release-evidence.yml` runs hourly, on dispatch, and on collector changes.

The collector records one explicit state:

- `PENDING_CREDENTIAL`: the governed private-repository read credential is unavailable;
- `PENDING_SOURCE`: an upstream artifact cannot yet be collected;
- `REJECTED`: artifacts exist but fail digest, identity, sequence, authority-boundary, or decision checks;
- `VERIFIED`: Publisher reconstructed and verified the complete paper evidence chain.

The `VERIFIED` status includes exact evidence bindings and the crypto-bot artifact's commit SHA, artifact ID, workflow run ID, readiness receipt digest, and manifest digest. An absent credential never becomes a false failure or false success. Manual dispatch remains validation-only and cannot persist release state.

## Private Evidence Custody Boundary
Private crypto-bot and Marketplace artifacts are temporary verification inputs only. The Publisher workflow:

1. downloads them into the ephemeral Actions workspace;
2. verifies their digests and exact chain bindings;
3. deletes the extracted private artifacts before persistence or upload;
4. commits and uploads only `data/marketplace-coinbase-release-evidence-status.json`.

The bounded status may retain source repository, artifact ID, workflow run ID, source commit, timestamps, manifest digest, readiness receipt digest, evidence bindings, and findings. It must never publish or commit the private artifact contents. A rejected result is preserved before the workflow fails so negative evidence is not lost.

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
- issues `GCAT-BCAT-Engine/Publisher#16` and `#19`

## Remaining Work
1. Allow the hourly collector to observe the named private-repository artifacts through the governed evidence token.
2. Preserve a `VERIFIED` evidence status with exact artifact IDs, workflow run IDs, source commit, readiness receipt digest, manifest digest, and evidence bindings.
3. Allow crypto-bot's public-status finalizer to consume that exact Publisher status and emit the final paper-release receipt.
4. Observe accepted, duplicate, missing-acknowledgement, transport-mismatch, digest-mismatch, conflict, and false-live-claim evidence in repository workflows.
5. Publish only after the separate publication-authority process grants authority; transport and verification remain non-authoritative.

## Progress Snapshot
Publisher settlement import - 100% implemented
Publisher publication gate - 100% implemented
Cross-repository evidence reconstruction - 100% implemented
Private evidence custody boundary - 100% implemented
Two-stage release deadlock removal - 100% implemented
Remaining - observed artifact collection, Publisher `VERIFIED`, and crypto-bot final receipt only

## Archive Readiness
This file and the installed executable gates preserve all continuation context required for this workstream.
