# Publisher Security Mirror Handoff

Status: ACTIVE — TV/TVC DISPATCH / CLOSURE / PRIVATE-EVIDENCE AUTHORITY MIGRATION

Established: 2026-08-19
Canonical repository: `GCAT-BCAT-Engine/Publisher`
Parent handoff: `docs/PUBLISHER_MIRROR_HANDOFF.md`
Ecosystem-management handoff: `docs/MIRROR_ECOSYSTEM_MANAGEMENT_HANDOFF.md`
Canonical security task: issue `#28`

## Scope and precedence

This handoff is authoritative for Publisher credential, cross-repository dispatch, private-evidence acquisition, and closure/activation mutation boundaries.

Where older self-managed-closure documentation assumes a repository secret or `github.token` can authorize these operations, this security handoff supersedes that credential assumption while preserving the underlying evidence predicates and task history.

It does not supersede the separate ST-017 governed-awareness observer goal.

## Governing boundary

- Credential authority is TV/TVC only.
- Repository secrets, generic GitHub tokens, legacy artifact tokens, dispatch tokens, and private-evidence tokens are not substitutes for admitted TV/TVC authority.
- GitHub Actions may validate and transport evidence but may not become cross-repository dispatch, closure, activation, publication, or control-plane authority.
- Fresh ordered artifacts and validated Site readiness are evidence predicates, not mutation authority.
- Missing authority fails closed before private acquisition, dispatch, closure, or mutation.

## Containment completed 2026-08-19

The following workflows are now manual, read-only, fail-closed placeholders:

- `.github/workflows/publisher-sync.yml`
  - prior non-TV/TVC cross-repository artifact token.
- `.github/workflows/dispatch-site-mirror.yml`
  - prior repository-secret cross-repository Site workflow dispatch.
- `.github/workflows/close-site-mirror-activation.yml`
  - prior repository-secret / `github.token` fallback and direct commit/push of closure/activation state.
- `.github/workflows/collect-marketplace-coinbase-release-evidence.yml`
  - prior private evidence token and direct evidence-status mutation.

Containment removes current executable credential/mutation authority. It does not erase or certify historical executions.

## Preserved Publisher work

The active ST-017 governed-awareness lane remains separate:

- goal: `PUBLISHER-ST017-SITE-PROPAGATION-001`;
- owner: `.github/workflows/validate-governed-ecosystem-awareness.yml`;
- current dependency posture: `BLOCKED_BUT_OBSERVED` / `PENDING_SITE_ACTIVATION`;
- publication, release, activation, execution, custody, and admissibility authority remain false.

Existing evidence predicates remain valid requirements:

- Site must declare Publisher as a destination;
- Site must report `READY_FOR_DOWNSTREAM_INGESTION`;
- Publisher must validate the resulting packet;
- closure requires fresh ordered Publisher and Site evidence.

These predicates do not themselves authorize dispatch or mutation.

## Replacement architecture

### Private source / artifact acquisition

Use an activated TV/TVC exact-source materialization capability. Publisher receives only secret-free materialized evidence plus source identity/digest/receipt; no credential value is exported to Publisher.

### Site dispatch

Requires a separate admitted capability binding:

- caller repository/workload;
- exact Publisher source ref and source SHA;
- exact target repository/workflow/ref;
- bounded dispatch operation;
- actor/application provenance;
- expiry;
- result receipt.

### Closure / activation mutation

Requires a separate mutation capability binding:

- exact fresh ordered evidence identities and digests;
- closure decision;
- exact Publisher paths/refs to mutate;
- actor/application provenance;
- idempotency key;
- mutation/result receipt.

Fresh evidence is required but does not self-authorize this mutation.

## Historical audit requirements

For consequential prior dispatch/closure/private-evidence executions, reconstruct where retained evidence permits:

1. initiating actor/application;
2. credential/application identity or token provenance;
3. workflow source commit;
4. Publisher source and Site target refs;
5. private evidence/artifact identities;
6. mutated paths/refs and resulting commits;
7. repository visibility at event time;
8. whether activation/closure claims had complete evidence at the irreversible transition.

Organization audit-log evidence remains required to close historical actor/token/visibility gaps.

## Completion gate

This lane is not complete until:

- required private-source acquisition is TV/TVC-materialized or permanently retired;
- required Site dispatch is reintroduced only through target-scoped TV/TVC authority or permanently retired;
- required closure/activation mutation is separately admitted and attributable;
- the ST-017 observer continues truthfully without acquiring authority by implication;
- all active third-party dependencies are immutably bound;
- historical provenance gaps are reconciled as far as retained audit evidence permits.

Do not restore repository-secret or `github.token` mutation/dispatch fallbacks as a repair shortcut.
