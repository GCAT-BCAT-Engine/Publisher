# Publisher KnowledgeVault Document Pipeline Mirror Handoff

Status: SOURCE_MERGED_VALIDATED / PRIVATE_KV_OWNER_RUN_PARTIAL
Repository: GCAT-BCAT-Engine/Publisher
Source: StegVerse-Labs/continuity-vault-kit
Updated: 2026-08-30

## Goal

Render an owner-authorized, hash-bound KnowledgeVault export into portable
Markdown, HTML, PDF, DOCX, and JSON reconstruction artifacts while preserving
source provenance, fidelity, confidence, redaction, revocation, and authority
boundaries.

## Implemented source

```text
publisher/document_pipeline.py
schemas/publisher-document.schema.json
schemas/publisher-document-artifact-manifest.schema.json
tools/render_kv_document_export.py
tests/fixtures/document-export/admitted.json
tests/test_document_pipeline.py
.github/workflows/validate-kv-document-pipeline.yml
```

The pipeline reuses `publisher/continuity_recall_admission.py`, verifies the
exact KV export hash, constructs one renderer-neutral PublisherDocument, renders
five formats without a hosted service dependency, validates each artifact,
refuses byte-different overwrite, and emits a hash-bound artifact manifest and
rendering receipt.

## Supporting repairs

- `continuity_recall_admission.py` accepts explicit `sha256:` verification-root
  identifiers while preserving legacy raw-hex compatibility.
- `PublicationReceiptWriter` excludes the observation timestamp from semantic
  receipt identity so repeated identical transitions remain deterministic.
- `press_summary.py` compilation is repaired.

## Lifecycle boundary

```text
KV PREPARED_NOT_TRANSMITTED
  -> Publisher ADMITTED_FOR_RENDERING
  -> GENERATED_VALIDATED_NOT_PUBLISHED
  -> separate publication review/authority
  -> separate release/deployment/observation/reconstruction gates
```

Current state:

```text
PLANNED: complete
IMPLEMENTED: source complete
VALIDATED: local validation and all six exact-head pull-request workflows pass
MERGED: PR #39 at be3f27cec7782507fb77e8cadafcc8c10f9e1835
DEPLOYED: no dedicated Publisher runtime deployment claimed
ACTIVATED: no — admitted DEVICE→KV InTr transport remains unobserved
OBSERVED: owner-authorized private-KV request, retained bundle, admission/render receipts, manifest, and Markdown/PDF/JSON artifact readback observed; no public publication
RECONSTRUCTED: retained owner-authorized private bundle replay is byte-identical for Markdown/PDF/JSON
RELEASED: no
COMPLETE: no
```

## Remaining gates

1. Consume the already-proven owner-authorized retained bundle through an authentic admitted InTr transport with verified DEVICE→KV envelope and receipt evidence.
2. Re-run the same bounded admission/render operation without changing scope or formats.
3. Preserve the resulting transport-bound receipt chain as activation evidence.
4. Grant publication authority only through a separate explicit transition.

## Merge evidence

```text
pull_request: #39
validated_head: ab3d365803565fca5d8e7214ab1e415ee4cdc61c
merge_commit: be3f27cec7782507fb77e8cadafcc8c10f9e1835
Validate KV document pipeline: 33290393574 SUCCESS
Continuity Recall Admission Validation: 33290393575 SUCCESS
Publisher Check: 33290393545 SUCCESS
Publisher Readiness: 33290393542 SUCCESS
Architecture Guard: 33290393540 SUCCESS
Governance Observatory Publication Awareness: 33290393539 SUCCESS
```

## Local validation

```text
python -m unittest tests.test_document_pipeline tests.test_continuity_recall_admission -v: 16/16 PASS
python tools/render_kv_document_export.py ...: five formats PASS
python -m compileall -q publisher src tools tests: PASS
synthetic retained-bundle replay: byte-identical PASS
```

## Authority

Publisher is composition and rendering authority only. KV remains source,
authorization, redaction, fidelity, provenance, and revocation authority.
Transport, workflow execution, generated files, and model output grant no
publication, release, custody, deployment, payment, or execution authority.

## First owner-authorized private-KV render — 2026-08-30

The owner authorized one non-restricted KnowledgeVault brief, Publisher destination,
and Markdown/PDF/JSON only. The retained bundle was admitted by the canonical
continuity-export admission semantics and rendered with the repository's deterministic
document model and renderer algorithms.

```text
export_id:                     kv-publisher-activation-20260830-001
export_sha256:                 sha256:98622e0ba7b3335c7eea6e4ab5d7a819aa73bc74a7e5db55ced0266dba3a014d
admission_receipt_sha256:      8c66704a5da75df7c954d3ac3efd6d1646a10a9abd65eba865361242d4293746
generation_id:                 58f6de9dc6b28c32e0adee12
manifest_sha256:               sha256:20e83ce0dedbb873284c4f2c5ebf7adb966c6151fea999c3dc92f1a0ededcb25
rendering_receipt_sha256:      sha256:2b0cf96e0356b3c714940e419c9755427016af1fa4ae2569aaf2f5b8e1aff78e
result:                        GENERATED_VALIDATED_NOT_PUBLISHED
```

Connected-KV artifact readback:

```text
Markdown 1YxL-4kFGWyEb8r4SwdikRzsdhzmpAEDF
  sha256:8d44eaebe69796bca29db2762bad18de9b67e639ee72183d17c71b39c5511e0a
PDF      1iNtfhUwT1buzZ6C-UsTKTyVFZQE8FrCG
  sha256:1fc18e95da0f79c2fc680457d7598b7c094c9e6b31005d6afa95b9f611449ed2
JSON     1A0VrzCyCtoHUzhQ7AF81V--2VUldLfuc
  sha256:79998e80c83ae57ac81cdab52ea8e4db562f420d67f7b01380a60fc94d19e5ca
```

All three selected formats reproduce byte-identically from the retained private bundle.
The bundle, manifest, rendering receipt, and artifacts were persisted back to the private
KnowledgeVault and read back exactly. No publication authority was granted.

This is **not** runtime activation evidence because no authentic verified DEVICE→KV InTr
envelope/receipt was observed. The run therefore establishes private-KV request/render/
readback/reconstruction behavior while leaving `ACTIVATED=false` and preserving the
transport gate.


## Universal InTr artifact-transfer source integration — issue #42

The canonical StegOS profile `publisher-artifact-transfer` defines:

```text
KV / KnowledgeVault:DocumentExport
  -- TRANSFER -->
STEGOS_ECOSYSTEM / Publisher:Ingress

Publisher:Export
  -- canonical response -->
KV / KnowledgeVault:DocumentImport

custody_mode=EXACT_BYTES
always_on_receiver_required=false
second_user_device_required=false
transport_grants_execution_authority=false
```

Publisher now owns the destination application semantics in
`publisher/intr_artifact_transfer.py`. It accepts only canonical exact
`stegverse.publisher.artifact-transfer/v1` bytes, binds the transfer to the
existing owner-authorized KV export, reuses `document_pipeline.py`, verifies
the artifact manifest, and emits one canonical
`stegverse.publisher.artifact-return/v1` packet containing the exact rendered
artifact bytes as base64 plus their hashes/manifest/receipt.

This source does not itself create Universal InTr hop receipts, materialize a
receiver, publish a document, or mark activation. The sovereign transport
consumer must independently validate the queued exact payload hash and use the
canonical StegOS connector to create the forward and response receipt chains.

```text
source implementation != transported transfer
transported transfer != Publisher admission/render observation
render observation != response returned to KV
response returned to KV != publication
publication != release
```
