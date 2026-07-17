# Vault → Publisher Integration Spec

## Status

This document defines a bounded integration contract. It does **not** claim that a live vault endpoint, weekly ingestion workflow, licensing market, contribution scoring system, or payout system is currently implemented.

Source capability reviewed: `StegVerse-Labs/continuity-vault-kit` `v0.1.8`.

Continuation source of truth: [`PUBLISHER_CONTINUITY_RECALL_MIRROR_HANDOFF.md`](./PUBLISHER_CONTINUITY_RECALL_MIRROR_HANDOFF.md).

## Purpose

Define how a user-authorized continuity export may be admitted into Publisher without confusing recalled or reconstructed knowledge with exact source evidence and without treating technical access as consent.

## Governed export flow

```text
continuity-vault-kit user
    ├── explicitly selects export scope
    ├── declares permitted purpose and destination
    ├── excludes restricted categories and files
    └── produces a signed or attributable export receipt

          ↓ governed export bundle

Publisher admission boundary
    ├── validates source release and schema
    ├── verifies event chain and verification root
    ├── checks authorization and scope
    ├── preserves fidelity and retention metadata
    ├── rejects prohibited or unverifiable content
    └── records an admission receipt

          ↓ only after separate authority

Optional dataset construction or licensing workflow
```

No recurring schedule is authoritative merely because it appears in documentation. A future scheduled workflow requires executable implementation, tests, explicit standing delegation, revocation behavior, and receipts.

## Required export fields

```json
{
  "schema_version": "0.2.0",
  "export_id": "uuid",
  "source": {
    "repository": "StegVerse-Labs/continuity-vault-kit",
    "release": "v0.1.8",
    "verification_root": "sha256",
    "event_ids": ["event-id"]
  },
  "authorization": {
    "authority_source": "direct_instruction_or_active_standing_delegation",
    "scope": ["selected_category_or_artifact"],
    "purpose": "declared-purpose",
    "destination": "GCAT-BCAT-Engine/Publisher",
    "receipt_id": "receipt-id",
    "revocable": true
  },
  "evidence": [
    {
      "subject_id": "subject-id",
      "retention_class": "integrity_only|reconstructable|full_fidelity",
      "fidelity": "exact|semantic_reconstruction|inference|integrity_only|unavailable",
      "superseded": false,
      "payload_available": true,
      "content_hash": "sha256",
      "artifact_refs": []
    }
  ]
}
```

## Admission rules

Publisher must reject an export when:

- authorization is absent, expired, revoked, destination-mismatched, or purpose-mismatched;
- the source chain or verification root cannot be confirmed;
- exact fidelity is claimed while the exact payload is unavailable;
- a derived index is presented as canonical source;
- supersession metadata is omitted or contradicted;
- restricted content, credentials, `_Policy/`, or `03_Records/` material is included;
- the export would broaden authority beyond the user-declared scope;
- required provenance or retention metadata has been stripped.

Publisher must preserve the source fidelity label. It may create a new derived interpretation only as a separately identified, attributable record linked to the source events.

## Explicit exclusions

The following remain excluded unless a later, separately governed contract and implementation proves otherwise:

- automatic ingestion of an entire vault;
- silent recurring exports;
- private medical, financial, legal, credential, or third-party records;
- treating hashes as recoverable content;
- treating semantic reconstruction as verbatim evidence;
- revenue calculation, contribution scoring, licensing, or payout claims without executable evidence.

## Governance events

| Event | Emitted by | Purpose |
|---|---|---|
| `vault.export_prepared` | continuity-vault-kit | Bind scope, purpose, destination, and evidence |
| `vault.export_revoked` | continuity-vault-kit | End previously delegated export authority |
| `publisher.export_admitted` | Publisher | Record successful validation and admission |
| `publisher.export_rejected` | Publisher | Record deterministic rejection and reason |
| `publisher.derived_record_created` | Publisher | Link a derived interpretation to source evidence |

## Safety and fidelity

- Individual data is not exposed by default.
- `03_Records/`, `_Policy/`, credentials, and restricted files remain excluded.
- Users retain authority over export scope and revocation.
- Missing content is reported as unavailable, not reconstructed without basis.
- Superseded decisions do not silently appear as current.
- Publisher admission does not certify truth, legal admissibility, ownership, commercial suitability, or licensing authority.

## Implementation state

This repository currently contains the integration specification and mirror handoff. A production claim requires a validator or ingestion implementation, fixtures, tests, CI, admission receipts, and release evidence.
