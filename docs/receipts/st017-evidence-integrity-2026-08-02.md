# ST-017 Evidence-Integrity Activation Receipt

Date: 2026-08-02
Repository: `GCAT-BCAT-Engine/Publisher`
Branch: `main`
Goal: governed ecosystem awareness validation with deterministic, inspectable, fail-closed ST-017 evidence.

## Installed

- `tools/check_st017_sandbox_report.py`
- `tools/check_publisher_st017_activation.py`
- updated `tools/check_st017_sandbox_adoption.py`
- updated `templates/sandbox-first/publisher.sandbox-profile.json`
- updated `tools/acquire_site_ecosystem_chat_propagation.py`
- updated `tools/check_site_ecosystem_chat_propagation.py`
- updated `.github/workflows/validate-governed-ecosystem-awareness.yml`

## Merge evidence

- Pull request: `#24`
- PR head: `aa459fe46e8a6d3b21bd565370aae0b042ae6063`
- Squash merge: `b036613ab7b78ddeead745a10cc87afd63febc74`
- Workflow: `Validate Governed Ecosystem Awareness`
- Run: `30738849526` / run number `219`
- Conclusion: `success`
- Sandbox job: `91472470327`, success
- Validation job: `91472488246`, success
- Artifact: `publisher-st017-sandbox-report`, ID `8830569156`
- Artifact digest: `sha256:5cb502751522fd02b2635055c198714ef59387c76e86e8f2bff5b23e90459207`

## Artifact inspection

`sandbox-first-validation.report.json` recorded:

- `sandbox_status: PASS`
- all four required command results passed
- all authority non-claims remained false

`st017-task-state.json` recorded:

- `state: COMPLETE`
- `errors: []`
- `next_executable_task: validate-job`
- duplicate execution key and report SHA-256: `38891839ab3508992225cd7c5dcaadd1add91ce6421e2f974198cd2f6f7ff67e`

## Dependency observer state

The Site packet currently does not declare `GCAT-BCAT-Engine/Publisher` as a destination. This is now persisted as a valid fail-closed pending state rather than an unobservable workflow crash.

Exact blocker:

`publisher_destination_not_declared_by_site`

Machine-observable release condition:

`Site packet declares GCAT-BCAT-Engine/Publisher and state READY_FOR_DOWNSTREAM_INGESTION`

The hourly workflow continues to re-acquire and validate the Site packet. It grants no publication, release, activation, execution, custody, or admissibility authority.

## Remaining work

- Update `docs/PUBLISHER_MIRROR_HANDOFF.md` from its stale pre-execution ST-017 status to reference this receipt and run 219.
- Observe the post-merge push/scheduled workflow on `main` and preserve its artifact.
- Retain `PENDING_SITE_ACTIVATION` until the exact Site release condition is met.
- Preserve PR #5 ownership of the separate GCAT capacity-paper workstream.
