# Publisher Continuity Recall Mirror Handoff

**Repository:** `GCAT-BCAT-Engine/Publisher`  
**Source:** `StegVerse-Labs/continuity-vault-kit`  
**Source release:** `v0.1.8`  
**Status:** Active bounded integration review  
**Last updated:** 2026-07-17

## Purpose

This file is the repository-local continuation source of truth for the Publisher-facing integration of automated, provenance-preserving conversation recall.

## Source capability

`continuity-vault-kit` v0.1.8 publishes canonical append-only conversation events, hash-linked validation, rebuildable derived indexes, supersession-aware recall, explicit fidelity classes, supporting-event provenance, verification roots, deterministic fixtures, executable tests, and CI.

## Publisher boundary

Publisher may ingest only explicitly authorized, opt-in continuity exports. It must not:

- treat a derived recall index as canonical source;
- present semantic reconstruction, inference, integrity-only evidence, or unavailable payloads as exact content;
- ingest private vault data merely because it exists;
- infer consent from prior participation, credentials, technical access, or a release reference;
- use continuity events to broaden publishing, licensing, or revenue-sharing authority;
- remove provenance, retention-class, fidelity, or supersession metadata.

## Required integration work

1. Replace the speculative weekly endpoint language in `docs/VAULT_PUBLISHER_INTEGRATION.md` with a governed export contract.
2. Require explicit export authorization and a source receipt for each batch.
3. Preserve event identifiers, source release, verification root, retention class, fidelity, supersession state, and payload-availability status.
4. Reject batches that claim exact fidelity without an available exact payload.
5. Reject broken or unverifiable source chains.
6. Keep `03_Records/`, `_Policy/`, restricted content, credentials, and unrelated private material excluded.
7. Do not claim that revenue-sharing or live ingestion is implemented unless executable code, tests, receipts, and release evidence prove it.

## Acceptance condition

The Publisher integration is complete only when the contract is documented, validated by executable tests or a repository-native validator, merged from a green head, and reflected in durable release or integration evidence.

## Archive rule

Do not declare this integration complete or archive its owning session while any accepted implementation, validation, release, or required propagation obligation remains unresolved.

---

🔒 Layer: Publisher | Continuity Recall
