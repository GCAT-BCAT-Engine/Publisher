# Publisher Mirror Handoff

## Authority and scope

This file is the current task source of truth for `GCAT-BCAT-Engine/Publisher` on `main`.

Read in this order before mutation:

1. `docs/PUBLISHER_MIRROR_HANDOFF.md`
2. `docs/MIRROR_ECOSYSTEM_MANAGEMENT_HANDOFF.md`
3. `data/publisher-orchestration-state.json`
4. `docs/receipts/st017-evidence-integrity-2026-08-02.md`
5. `docs/PUBLISHER_PENDING_CLOSURE_STATUS.md`

Incoming requests are candidate work, not publication or execution authority.

## Active goal

```text
goal_id: PUBLISHER-ST017-SITE-PROPAGATION-001
goal: maintain a validated, repository-native ST-017 governed-awareness lane and consume the first valid Site propagation packet after Site readiness
repository: GCAT-BCAT-Engine/Publisher
branch: main
state: BLOCKED_BUT_OBSERVED
publication_posture: publication_awareness_only
manual_user_action_required: false
```

## Current execution inventory

### Complete and validated

- ST-017 isolated sandbox runner: `tools/run_sandbox_validation.py`
- ST-017 profile: `templates/sandbox-first/publisher.sandbox-profile.json`
- deterministic report validator and task-state writer: `tools/check_st017_sandbox_report.py`
- bounded activation validator: `tools/check_publisher_st017_activation.py`
- structural adoption validator: `tools/check_st017_sandbox_adoption.py`
- Site propagation acquisition: `tools/acquire_site_ecosystem_chat_propagation.py`
- Site propagation validator: `tools/check_site_ecosystem_chat_propagation.py`
- recurring workflow owner: `.github/workflows/validate-governed-ecosystem-awareness.yml`
- durable implementation receipt: `docs/receipts/st017-evidence-integrity-2026-08-02.md`

Evidence:

```text
pull_request: #24
merge_commit: b036613ab7b78ddeead745a10cc87afd63febc74
receipt_commit: e17987801e8dadc3bc52cf25ecab52680ac69ff9
validated_pr_head: aa459fe46e8a6d3b21bd565370aae0b042ae6063
workflow: Validate Governed Ecosystem Awareness
workflow_run_number: 219
workflow_run_id: 30738849526
sandbox_job: 91472470327 PASS
validate_job: 91472488246 PASS
artifact_id: 8830569156
artifact_digest: sha256:5cb502751522fd02b2635055c198714ef59387c76e86e8f2bff5b23e90459207
sandbox_state: COMPLETE
sandbox_commands: 4/4 PASS
```

The workflow also observed and preserved the current Site dependency boundary without granting authority.

### Implemented and active, dependency-blocked

Publisher's Site consumer currently records:

```text
state: PENDING_SITE_ACTIVATION
blocker: publisher_destination_not_declared_by_site
source: StegVerse-Labs/Site/data/ecosystem-chat-activation-propagation.json
release_condition: Site declares GCAT-BCAT-Engine/Publisher as a destination and reports READY_FOR_DOWNSTREAM_INGESTION
next_executable_task: recheck-site-propagation-destination-and-readiness
owner: GCAT-BCAT-Engine/Publisher/.github/workflows/validate-governed-ecosystem-awareness.yml
trigger: hourly schedule, workflow dispatch, relevant pull request, or relevant push
```

The observer must persist `PENDING_SITE_ACTIVATION` until the release condition is directly observed. Missing destination declaration or readiness is not success.

### Separate active ownership

- PR #5, branch `agent/gcat-capacity-paper`: GCAT capacity-based stability paper; parallel-safe and not owner of Site propagation.
- Publisher closure evidence remains pending under `docs/PUBLISHER_CLOSURE_EVIDENCE_PRODUCTION.md` and `docs/PUBLISHER_PENDING_CLOSURE_STATUS.md`.
- Upstream HIL succession remains owned by `StegVerse-org/LLM-adapter`, `master-records/orchestration`, then `StegVerse-Labs/Site`.

## Automation contract

Owner repository: `GCAT-BCAT-Engine/Publisher`

Workflow: `.github/workflows/validate-governed-ecosystem-awareness.yml`

Deterministic outputs:

- `reports/sandbox-first-validation.report.json`
- `reports/st017-task-state.json`
- `data/ecosystem-chat-site-propagation-status.json`
- uploaded artifact `publisher-st017-sandbox-report`

Required machine states:

```text
COMPLETE
BLOCKED
RETRY
REVIEW_REQUIRED
FAILED
```

Current task-state semantics:

- ST-017 sandbox validation: `COMPLETE`
- Site propagation activation: `BLOCKED`
- release condition: exact Site destination declaration plus `READY_FOR_DOWNSTREAM_INGESTION`
- duplicate prevention: deterministic report hash / execution key
- authority posture: publication, release, activation, execution, custody, and admissibility authority remain false

## Cross-repository succession

```text
StegVerse-Labs/Site valid propagation packet
-> GCAT-BCAT-Engine/Publisher acquisition and validation
-> durable Publisher awareness state
-> evaluate existing propagation contracts for StegVerse-Labs/admissibility-wiki
-> evaluate existing propagation contracts for StegVerse-002/stegguardian-wiki
```

Publisher does not duplicate Site, LLM-adapter, Master-Records, admissibility-wiki, or StegGuardian canonical authority.

## Validation commands

```text
python tools/run_sandbox_validation.py
python tools/check_st017_sandbox_report.py --report reports/sandbox-first-validation.report.json --state-output reports/st017-task-state.json
python tools/check_st017_sandbox_adoption.py --structural-only
python tools/acquire_site_ecosystem_chat_propagation.py
python tools/check_site_ecosystem_chat_propagation.py
python tools/check_governed_ecosystem_site_mirror_awareness.py
python tools/check_stegguardian_propagation_status.py
python tools/check_publisher_governed_ecosystem_sync_status.py
python tools/check_publisher_governed_ecosystem_validation_status.py
python tools/check_publisher_governed_ecosystem_workflow_request.py
python tools/check_publisher_st017_activation.py
```

## Exact remaining tasks

1. Inspect the workflow triggered by this handoff update on `main`, including jobs, logs, and artifact; persist a main-branch verification receipt under `docs/receipts/`.
2. Continue the installed hourly Site observer until the release condition is met.
3. When Site becomes ready, verify `data/ecosystem-chat-site-propagation-status.json` records `VERIFIED_INGESTION_READY` and has no blockers.
4. Then inspect and execute the existing downstream propagation contracts for `StegVerse-Labs/admissibility-wiki` and `StegVerse-002/stegguardian-wiki`; do not claim propagation before direct evidence.
5. Preserve Publisher closure as pending until fresh ordered Publisher, Site, and closure artifacts exist.

## Completion accounting

```text
task_completion: 11/13
required_developed_files: 8
developed_files: 8
scaffolding_or_stubs: 0
missing_required_files: 0
validation_completion: 7/8
goal_activation: 78%
```

The denominator covers the sandbox profile, runner, report validator, bounded activation validator, adoption validator, Site acquisition, Site validator, workflow integration, PR validation, artifact inspection, merge receipt, main-branch validation, and final Site-ready consumption.

## Archive conditions

Do not archive while any of the following remains:

- the main-branch post-handoff workflow is uninspected;
- Site does not declare Publisher;
- Site is not `READY_FOR_DOWNSTREAM_INGESTION`;
- Publisher has not persisted and validated the ready state;
- required downstream propagation remains unverified;
- closure evidence remains pending without its installed observer and release condition.
