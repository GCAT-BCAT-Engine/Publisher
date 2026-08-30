# Publisher KnowledgeVault Document Pipeline Mirror Handoff

Status: IMPLEMENTED_LOCAL_VALIDATED
Repository: GCAT-BCAT-Engine/Publisher
Source: StegVerse-Labs/continuity-vault-kit
Updated: 2026-08-29

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
IMPLEMENTED: source complete on feature branch
VALIDATED: dependency-light unit, CLI, compile, and deterministic replay checks pass
MERGED: no
DEPLOYED: no
ACTIVATED: no private-KV request or artifact readback
OBSERVED: no public publication
RECONSTRUCTED: synthetic fixture replay is byte-identical; no retained private-KV replay evidence
RELEASED: no
COMPLETE: no
```

## Remaining gates

1. Pass hosted validation on the exact branch head.
2. Merge only the validated head.
3. Consume one owner-authorized private-KV bundle through admitted InTr.
4. Return manifest and rendering receipt to `_System/Exports/Receipts/`.
5. Read back and verify artifacts in `_System/Exports/Artifacts/`.
6. Reconstruct identical artifacts from the retained private bundle.
7. Grant publication authority only through a separate explicit transition.

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
