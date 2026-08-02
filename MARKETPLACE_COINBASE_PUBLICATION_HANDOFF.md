# Marketplace–Coinbase Publication Mirror Handoff

## Active goal and goal ID

- Goal ID: `MARKETPLACE-COINBASE-PAPER-ACCESSIBILITY-001`
- Goal: reconstruct the governed paper settlement chain, publish only a bounded verification status, propagate paper accessibility to Site, and permit crypto-bot finalization without granting live authority.
- Repository: `GCAT-BCAT-Engine/Publisher`
- Branch: `main`
- Owner issue: `GCAT-BCAT-Engine/Publisher#19`

## Authoritative files

- `data/marketplace-coinbase-connected-relay.json`
- `scripts/verify_marketplace_coinbase_connected_relay.py`
- `tests/test_marketplace_coinbase_connected_relay.py`
- `data/marketplace-coinbase-publications/intent-marketplace-release-73a0543ddb27.publication.json`
- `data/marketplace-coinbase-release-evidence-status.json`
- `.github/workflows/collect-marketplace-coinbase-release-evidence.yml`
- `scripts/collect_marketplace_coinbase_release_evidence.py`

## Current state

```text
PUBLISHER_CONNECTED_RELAY_RECONSTRUCTION_VERIFIED_AND_WORKFLOW_PERSISTED
```

Publisher has reconstructed the exact paper chain and persisted a bounded `VERIFIED` status. Raw private Marketplace evidence was inspected through the connected GitHub control plane and was not committed to Publisher. Publisher persists only source identities, file and receipt digests, evidence bindings, the bounded publication projection, and the bounded verification status.

## Completed work and evidence

### Upstream identities

- crypto-bot source commit: `73a0543ddb27a88fd4913e7dcfa2127132299baa`
- first-accessibility workflow run: `30681165495`
- first-accessibility artifact: `first-accessibility-mark-30681165495-1`
- artifact ID: `8812256538`
- artifact digest: `sha256:fa051f49f259c54f491dc1395568447393e6ea83dbd9c8535e3cbdfe03e2ada7`
- observed receipt digest: `sha256:5f6cc484c74f5795973cd2e6c52cc349e1cc464064841a29c3d28ed863e98758`
- Marketplace collection-status commit: `7bad3827613cfc3e882fb3b121567bfa689c581c`
- Marketplace relay receipt digest: `sha256:07aedebdf3bcb32407adec99d5d160ce5be315709d958beb75b0a73fabe5caf2`

### Exact chain bindings

- intent: `intent-marketplace-release-73a0543ddb27`
- packet: `sha256:ae990ce837cac3077a80c966b4e2d960f4158065dcec9c7fdc4da8b8f26ea89b`
- sequence 1: `sha256:f6f41875a5e066fc348cac68691c1d4fb77f3559282eb4ede26a398c87ee7e64`
- acknowledgement: `sha256:c76c0decad6b82f9356a58598ef5e217f92802dc657e9f5ed95cae9b8f77f0a3`
- sequence 2: `sha256:805000ab776b00863f5962514bcb8f843ccaa27ab9e0ac7821b92499b2e347f1`
- Publisher projection: `sha256:4ab30925412757058f3f752fad1d7e452e95dcddf3d2e272ecd9605cee97e8d9`
- publication receipt: `sha256:0dc495cf5f7de0b4610d5b4fc7732f3ddb888543fbe6c9a55ef07ad7f175d240`

### Repository mutations

- bounded projection: commit `25b9e66014ec02f4c7173a8bd93d9fe5eeaa347f`
- bounded connected relay: commit `c6a7f3591efe5d915de0ab65d8fc724d2ed8ed23`
- connected relay verifier: commit `43ad9acebf8d9e99aadd0b548ea2ef03ac1dd312`
- connected relay tests: commit `cfc412d9da6f0851f15e258c2cf2fc936c00968d`
- workflow activation: commit `21d9ad2333c4a5b76a319d2adef2625cb5801616`
- machine-persisted `VERIFIED` status: commit `913a89d0ec867c3c9b570ec8352be554790a45f0`

### Current bounded status

- status: `VERIFIED`
- paper release verified: `true`
- status digest: `sha256:36a2f6da4b5af18375fd798ef954ec703ea719beefbab2d5949954b79ca1e477`
- publication authority: `false`
- release authority: `false`
- execution authority: `false`
- live authority: `false`

## Automation

The workflow `.github/workflows/collect-marketplace-coinbase-release-evidence.yml` now:

1. runs deterministic collector and connected-relay tests;
2. verifies a digest-bound connected relay first;
3. uses the credentialed private-artifact collector only when the relay is absent;
4. removes temporary private evidence before persistence;
5. commits only the bounded status;
6. uploads the bounded status artifact;
7. fails after preserving rejected evidence.

The machine-owned status commit `913a89d0ec867c3c9b570ec8352be554790a45f0` proves the activated workflow persisted `VERIFIED`. The workflow run ID, job logs, and uploaded bounded-status artifact ID have not yet been directly recorded in this handoff.

## Cross-repository propagation

- Source: `GCAT-BCAT-Engine/Publisher/data/marketplace-coinbase-release-evidence-status.json`
- Consumer: `StegVerse-Labs/Site/scripts/import_marketplace_coinbase_accessibility.py`
- Site result: `PAPER_ACCESSIBLE`
- Site machine persistence commit: `99eeb59f757e4bdbaf020817b6ece5267349e93b`
- Crypto finalizer: `StegVerse-Labs/crypto-bot/scripts/build_final_paper_release_receipt.py`

## Incomplete work

1. Record Publisher workflow run, job, logs, and bounded-status artifact identity when observable.
   - Owner: `GCAT-BCAT-Engine/Publisher#19`
   - Workflow: `.github/workflows/collect-marketplace-coinbase-release-evidence.yml`
   - Release condition: inspectable successful run and retained status artifact.
2. Complete crypto-bot final receipt and exact tag.
   - Owner: `StegVerse-Labs/crypto-bot#6`
   - Workflow: `.github/workflows/finalize-paper-release.yml`
   - Required outputs: `FINAL_PAPER_RELEASE_RECEIPT.json`, `FINAL_PAPER_RELEASE_TAG_AUTHORIZATION.json`, and tag `marketplace-coinbase-paper-v1.0.0` at commit `73a0543ddb27a88fd4913e7dcfa2127132299baa`.

## Validation commands

```bash
pytest -q tests/test_marketplace_coinbase_release_evidence_collector.py tests/test_marketplace_coinbase_connected_relay.py
python scripts/verify_marketplace_coinbase_connected_relay.py
```

## Authority boundary

Publisher verification, connected transport, Site projection, final receipt generation, and repository tagging do not grant publication, release, execution, custody, withdrawal, funded-order, or live Coinbase authority.

## Archive conditions

This workstream is not archive-complete until the exact crypto-bot final receipt, `ALLOW_TAG`, exact tag target, issue closure evidence, and hosted validation identities are preserved. No unspecified external tasks exist.

## Progress

- developed files: 7/7 = 100%
- validation: deterministic relay validation PASS; hosted persistence observed; workflow run metadata pending
- integration: Publisher-to-Site complete
- goal activation: 85%
