# Publisher Continuity Recall Mirror Handoff

**Repository:** `GCAT-BCAT-Engine/Publisher`  
**Source:** `StegVerse-Labs/continuity-vault-kit`  
**Source release:** `v0.1.8`  
**Status:** Active executable integration validation  
**Pull request:** `#10 Govern Continuity Vault recall exports into Publisher`  
**Branch:** `agent/continuity-recall-integration-v0-1`  
**Last updated:** 2026-07-17

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

## Remaining work

1. Observe `Continuity Recall Admission Validation` on the exact current PR head.
2. Correct any validator, fixture, test, or workflow mismatch.
3. Update PR #10 from draft only after the exact head is green and mergeable.
4. Merge only the validated head.
5. Record durable integration or release evidence after merge.
6. Review the next adjacent Publisher goal without converting unimplemented commercial behavior into a production claim.

## Acceptance condition

The Publisher integration is complete only when the contract and executable admission boundary are green on the exact head, merged, and reflected in durable integration evidence. Live ingestion, licensing, scoring, or payout remains a separate future capability unless independently implemented and proven.

## Archive rule

Do not declare this integration complete or archive its owning session while any accepted implementation, validation, merge, evidence, or required propagation obligation remains unresolved.

---

🔒 Layer: Publisher | Continuity Recall
