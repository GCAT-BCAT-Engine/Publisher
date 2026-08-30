# Publisher Continuity Recall Mirror Handoff

**Repository:** `GCAT-BCAT-Engine/Publisher`  
**Source:** `StegVerse-Labs/continuity-vault-kit`  
**Source release:** `v0.1.8`  
**Status:** MERGED_VALIDATED; document-rendering successor locally validated
**Pull request:** `#10 Govern Continuity Vault recall exports into Publisher` (merged)
**Merge commit:** `d7183ebf89373b7602af7f1e68386423bab57040`
**Successor branch:** `feature/kv-document-pipeline`
**Last updated:** 2026-08-29

## Purpose

This file is the repository-local continuation source of truth for the Publisher-facing integration of automated, provenance-preserving conversation recall.

## Source capability

`continuity-vault-kit` v0.1.8 publishes canonical append-only conversation events, hash-linked validation, rebuildable derived indexes, supersession-aware recall, explicit fidelity classes, supporting-event provenance, verification roots, deterministic fixtures, executable tests, and CI.

## Publisher boundary

Publisher may admit only explicitly authorized, opt-in continuity exports. It must not:

- treat a derived recall index as canonical source;
- present semantic reconstruction, inference, integrity-only evidence, or unavailable payloads as exact content;
- ingest private vault data merely because it exists;
- infer consent from prior participation, credentials, technical access, or a release reference;
- use continuity events to broaden publishing, licensing, or revenue-sharing authority;
- remove provenance, retention-class, fidelity, or supersession metadata.

## Implemented integration artifacts

- `docs/VAULT_PUBLISHER_INTEGRATION.md` — governed export and admission contract;
- `publisher/continuity_recall_admission.py` — dependency-light validator and receipt generator;
- `fixtures/continuity-recall/admitted.json` — valid bounded export;
- `fixtures/continuity-recall/rejected-exact-without-payload.json` — deterministic fidelity rejection;
- `tests/test_continuity_recall_admission.py` — authority, destination, path, fidelity, and canonical-source tests;
- `.github/workflows/continuity-recall-admission.yml` — compile, unit-test, admitted-receipt, and rejection validation.

## Admission invariants

1. Source repository, release, event identifiers, and verification root are required.
2. Authorization must be active, unrevoked, scoped, purpose-bound, destination-bound, and receipt-backed.
3. Exact fidelity requires an available exact payload.
4. Integrity-only and unavailable evidence cannot claim an available payload.
5. Derived indexes cannot be admitted as canonical source.
6. Supersession state and content hashes are required.
7. `03_Records/`, `_Policy/`, restricted data, and credentials are rejected.
8. Admission produces an attributable ADMITTED or REJECTED receipt with deterministic reasons and a receipt hash.
9. Admission does not create licensing, publishing, revenue-sharing, or payout authority.
10. No live recurring ingestion is claimed by this bounded implementation.

## Completed admission boundary

PR #10 merged on 2026-07-17 at
`d7183ebf89373b7602af7f1e68386423bab57040`. The admission contract, validator,
fixtures, tests, and validation workflow are therefore repository source rather
than pending-PR scaffolding.

## Successor work

The locally validated `feature/kv-document-pipeline` branch composes an admitted,
hash-bound KV bundle into Markdown, HTML, PDF, DOCX, and JSON artifacts. Its
continuation source of truth is `docs/KV_DOCUMENT_PIPELINE_MIRROR_HANDOFF.md`.
It remains unmerged and does not claim private-KV ingestion, publication,
deployment, release, or activation.

## Acceptance condition

The bounded recall-admission integration is merged and validated. Live ingestion,
document publication, licensing, scoring, or payout remains separate unless
independently implemented and proven.

## Archive rule

Do not declare this integration complete or archive its owning session while any accepted implementation, validation, merge, evidence, or required propagation obligation remains unresolved.

---

🔒 Layer: Publisher | Continuity Recall
