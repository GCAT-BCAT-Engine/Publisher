# ERL KV Provider Proof Publisher Projection Mirror Handoff

Updated: 2026-09-09

Goal Task ID: SS-ERL-KV-PROPAGATION-VERIFICATION-001

## Purpose

Bind Publisher's governed KnowledgeVault document-rendering pipeline to the completed ERL native-writer, provider-operation, exact provider-byte readback, retained receipt, and Master Records reconstruction evidence when an owner-authorized ERL export is rendered.

## Installed surfaces

- `data/erl-kv-provider-proof-projection.json`
- `tools/check_erl_kv_provider_proof_projection.py`
- `.github/workflows/validate-erl-kv-provider-proof-projection.yml`
- `README.md`

## Pinned evidence

- ERL integration: `722a11cf2ada6205a31e3678d489254fb736e8f7`
- ERL provider evidence: `8569d8b811b787cd49ee3f38c352c46fb86c3bca`
- Master Records custody: `3e1bc4f2f98bde1932261c2ce96ca42fa9952a19`
- Provider-operation receipt SHA-256: `bb74904fcd8169829c78bdc1c0d64905b33243c2c22852565c13e614abcd1fa8`

## Evidence boundary

Upstream storage and custody proof does not publish a paper, authorize an export, activate Publisher, or prove Site propagation. The existing renderer must still receive an owner-authorized, hash-bound KV export.

## Merge evidence

- Publisher PR #60 merged at `93a4743ceb5974689c1872c0e88dbb86de980f7e`.
- All four hosted workflows passed: focused ERL KV projection validation, Publisher Check, Publisher Readiness, and Architecture Guard.

## Current state

UPDATE_REQUIRED_IMPLEMENTED / VALIDATED / MERGED
