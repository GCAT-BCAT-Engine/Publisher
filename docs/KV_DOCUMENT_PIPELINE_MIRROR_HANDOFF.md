# Publisher KnowledgeVault Document Pipeline Mirror Handoff

Status: SOURCE_MERGED_VALIDATED / PRIVATE_KV_EXECUTION_PENDING
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
DEPLOYED: no
ACTIVATED: no private-KV request or artifact readback
OBSERVED: no public publication
RECONSTRUCTED: synthetic fixture replay is byte-identical; no retained private-KV replay evidence
RELEASED: no
COMPLETE: no
```

## Remaining gates

1. Consume one owner-authorized private-KV bundle through admitted InTr.
2. Return manifest and rendering receipt to `_System/Exports/Receipts/`.
3. Read back and verify artifacts in `_System/Exports/Artifacts/`.
4. Reconstruct identical artifacts from the retained private bundle.
5. Grant publication authority only through a separate explicit transition.

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
