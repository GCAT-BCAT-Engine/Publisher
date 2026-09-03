# Publisher Mirror Handoff

## Source of truth

This file is the current handoff and task source of truth for `GCAT-BCAT-Engine/Publisher`.

## Current priority

```text
Goal: automatically ingest verified Ecosystem Chat activation evidence from StegVerse-Labs/Site and prepare bounded downstream publication status
Result: AUTOMATED_SITE_ACTIVATION_IMPORT_AND_DOWNSTREAM_CONSUMERS_INSTALLED_SOURCE_ACTIVATION_PENDING
Manual user action required: false
```

## Source chain

```text
StegVerse-org/LLM-adapter retained activation state
-> master-records/orchestration retained custody state
-> StegVerse-Labs/Site authenticated imports and activation-state validation
-> StegVerse-Labs/Site/data/ecosystem-chat-activation-state.json
-> StegVerse-Labs/Site/data/ecosystem-chat-activation-propagation.json
-> GCAT-BCAT-Engine/Publisher automated importer
-> GCAT-BCAT-Engine/Publisher/data/ecosystem-chat-activation-status.json
-> automated downstream wiki consumers
```

## Installed consumer

```text
scripts/import_ecosystem_chat_activation.py
.github/workflows/import-ecosystem-chat-activation.yml
```

The workflow runs hourly and on dispatch. It fetches the public Site state and propagation packet, validates both canonical hashes, validates the packet-to-state hash binding, requires Publisher to be an explicit destination, and commits only changed projection state.

## Acceptance requirements

Publisher records `VERIFIED_ACTIVATION_IMPORTED` only when:

```text
Site state record type is correct
Site state_sha256 matches canonical state content
Site state = ACTIVATION_COMPLETE
all Site activation gates = true
propagation packet schema is correct
packet_sha256 matches canonical packet content
packet source_state_sha256 matches Site state_sha256
packet state = READY_FOR_DOWNSTREAM_INGESTION
Publisher destination exists
Publisher ingestion_ready = true
manual_user_action_required = false
all propagation authority-boundary flags = false
```

Missing or incomplete Site state remains `PENDING_SITE_ACTIVATION`. Invalid hashes, bindings, destinations, or authority fields become `REJECTED_SITE_ACTIVATION` and fail closed.

## Output

```text
data/ecosystem-chat-activation-status.json
```

The output is projection-only and always preserves:

```text
publication_authorized = false
release_authorized = false
custody_recorded = false
execution_authorized = false
manual_user_action_required = false
```

## Installed downstream consumers

```text
StegVerse-Labs/admissibility-wiki
  scripts/import_publisher_ecosystem_chat_activation.py
  scripts/generate_external_framework_page_status.py integration
  ECOSYSTEM_CHAT_ACTIVATION_HANDOFF.md

StegVerse-002/stegguardian-wiki
  scripts/import_publisher_ecosystem_chat_activation.py
  scripts/check_guardian_local_state.py integration
  ECOSYSTEM_CHAT_ACTIVATION_HANDOFF.md
```

Both consumers fetch Publisher's checked-in status automatically through their existing repository-owned workflows. Neither requires manual artifact download, file movement, workflow dispatch, route inspection, or user confirmation.

The previous references to `StegVerse-Labs/stegguardian-wiki` and `StegVerse-Labs/Sit` were stale. The real Guardian destination is `StegVerse-002/stegguardian-wiki`; no `StegVerse-Labs/Sit` repository exists.

## Existing Standing-Proof Engine propagation

The earlier SPE v0.5.0 status remains recorded and is not superseded by this activation consumer. Its downstream wiki boundaries remain valid independently.

## Correctability projection — COMPLETE AND HOSTED-VALIDATED

Canonical source: `StegVerse-Labs/StegCore`, goal `CORRECTABILITY-LAYER-001`.

Installed target-native surfaces:

```text
data/correctability-projection.json
scripts/check_correctability_projection.py
.github/workflows/check-correctability-projection.yml
```

The projection preserves the validated source semantics that timely correction requires valid authority, reachability and enforceability; a request after the irreversible boundary is not timely correction; and post-irreversibility compensation is distinct from prevention. The target projection also preserves the bounded intervention vocabulary and keeps publication, release, custody, execution, Guardian and admissibility authority false.

Hosted target validation:

```text
workflow: Check Correctability Projection
run_id: 31290000111
job_id: 93185432929
head_sha: 0c6f5d3958151306c1bdf84d081fa5f2a252b8dd
status: completed
conclusion: success
validation_step: Validate bounded correctability projection
validation_step_result: success
source_workflow_run: 30774680694
source_artifact: 8841612361
source_artifact_digest: sha256:030f22b998a6f9c382db5463a4cc55f6d70132d5dd20d880778b5efda9844536
```

Correctability propagation state for Publisher is therefore `COMPLETE_VALIDATED`. This does not imply publication authority or Site activation and does not alter the separate Ecosystem Chat activation dependency chain.

## Autonomous adjacent-construction ownership

Publisher now owns the no-manual-action bootstrap for the StegPay/StegOps two-generation construction goal.

Installed files:

```text
scripts/autonomous_adjacent_construction_bootstrap.py
.github/workflows/autonomous-adjacent-construction-bootstrap.yml
```

Repository-owned behavior:

1. fetch and validate the authoritative StegOps construction plan;
2. require this handoff marker before accepting Publisher as target one;
3. generate and self-validate the Publisher packet and Publisher-owned completion receipt;
4. preserve all publication, release, custody, deployment, payment, entitlement, and execution authority flags as false;
5. install only the bounded Site intake paths declared by the plan;
6. dispatch Site only after Publisher receipt validation;
7. require Site to persist its own receipt;
8. allow StegOps to pull both receipts and close only on `TWO-GENERATION AUTONOMY: COMPLETE`.

The workflow uses an already-governed Publisher credential path and requires no new user-created secret, manual file copy, workflow dispatch, or confirmation.

Current result:

```text
AUTONOMOUS_BOOTSTRAP_INSTALLED_SCHEDULED_EXECUTION_PENDING
manual_user_action_required = false
transport_is_authority = false
```

## Current blocker

```text
StegVerse-Labs/Site has not yet published ACTIVATION_COMPLETE with a hash-bound READY_FOR_DOWNSTREAM_INGESTION packet.
```

The Site scheduled workflow owns that transition after the adapter, deployment platform, and Master-Records custody service publish the required machine evidence.

For the separate two-generation construction goal, the next evidence is Publisher's target-owned adjacent-construction receipt followed by Site's independently persisted receipt.

## Next task

```text
1. Allow the hourly Publisher importer to observe Site activation automatically.
2. Allow the scheduled autonomous adjacent-construction bootstrap to persist Publisher's receipt and dispatch Site.
3. Preserve exact hash, binding, schema, destination, sequence, and authority-boundary rejection evidence.
4. Allow existing downstream wiki workflows to ingest Publisher status automatically.
5. Do not convert projection or transport into publication, release, custody, deployment, payment, entitlement, or execution authority.
6. Tag or release only after repository validation and all required downstream evidence are complete.
```

## Authority boundary

```text
Site activation state != Publisher authority.
Propagation packet != publication authority.
Publisher import != release authority.
Publisher projection != custody.
Adjacent-construction transport != target acceptance.
Publisher receipt != Site receipt.
Wiki projection != admissibility determination or Guardian enforcement authority.
Reconstruction PASS != execution authority.
No release tag is authorized by this handoff.
```

## Archive readiness

This handoff, the Site handoffs, Publisher importer, validated correctability projection, autonomous adjacent-construction bootstrap, downstream consumer handoffs, workflows, projection records, issues, and repository history preserve all continuation state. Earlier conversation context is not required and no manual user task remains. The active two-generation goal remains open until both target-owned receipts validate.


## Governance Observatory Publication Awareness — issue #29

```text
task_id: PUBLISHER-GOVOBS-PUBLICATION-AWARENESS-029
execution_class: PARALLEL_SAFE_NON_AUTHORIZING_AWARENESS
source: StegVerse-Labs/governance-observatory
source_publication_merge: 52d9a8f596ade145f5b08e44e98395d328476ecc
source_publication_state: PUBLISHED
state: IMPLEMENTED_VALIDATION_PENDING
manual_user_action_required: false
```

Installed bounded target-native surfaces:

```text
data/governance-observatory-publication-awareness.json
scripts/check_governance_observatory_publication_awareness.py
.github/workflows/check-governance-observatory-publication-awareness.yml
```

The projection records only verified publication awareness. It does not alter the machine-owned Site/HIL activation observer and does not create Publisher publication, release, custody, execution, Guardian, or admissibility authority.

```text
source publication != Publisher publication authority
projection != custody
observation != admissibility
AEGISAI source capture != runtime validation
```

Completion requires the dedicated target workflow to PASS, merge to main, main-branch PASS, release of this claim, and evidence return to StegVerse-Labs/governance-observatory issue #5.


### Governance Observatory publication awareness completion

```text
task_id: PUBLISHER-GOVOBS-PUBLICATION-AWARENESS-029
target_pr: 30
merge_commit: 674aff42b32aee30818314e9b6bd92e8869ad914
dedicated_post_merge_run: 33024103131
dedicated_post_merge_conclusion: SUCCESS
publisher_readiness_run: 33024103118 SUCCESS
publisher_check_run: 33024103126 SUCCESS
architecture_guard_run: 33024103136 SUCCESS
claim_state: RELEASED_COMPLETE
state: COMPLETE_VALIDATED_MERGED
authority_effect: false
```

The unrelated `RTG-001 Artifact Watch` and `stegdb-sync` failures observed on the same merge head are not owned by this bounded awareness lane and are not converted to success by this completion. The dedicated awareness validator and relevant Publisher readiness/architecture checks passed.

No release tag is authorized by this awareness completion.


## Governance Observatory v0.1.0 release awareness — issue #31

```text
task_id: PUBLISHER-GOVOBS-V0.1.0-RELEASE-AWARENESS-031
execution_class: PARALLEL_SAFE_NON_AUTHORIZING_RELEASE_AWARENESS
source_release: v0.1.0
source_release_id: 377486341
source_release_state_head: 31afc11745507e4764c2c9f44be1e5143e920ef1
state: IMPLEMENTED_VALIDATION_PENDING
manual_user_action_required: false
```

The existing Governance Observatory awareness projection now records the actual versioned release in addition to publication state.

```text
release awareness != Publisher release authority
tag != execution authority
projection != custody
release != admissibility
AEGISAI remains source-only
```

This task does not alter the machine-owned Site/HIL observer or the GCAT capacity workstream.


### Governance Observatory v0.1.0 release awareness completion

```text
task_id: PUBLISHER-GOVOBS-V0.1.0-RELEASE-AWARENESS-031
target_pr: 32
merge_commit: 1d586db7b6b9b4ad5153fae70713d8d42e6311b2
dedicated_post_merge_run: 33025742073 SUCCESS
publisher_readiness_run: 33025741977 SUCCESS
publisher_check_run: 33025742031 SUCCESS
architecture_guard_run: 33025742037 SUCCESS
claim_state: RELEASED_COMPLETE
state: COMPLETE_VALIDATED_MERGED
authority_effect: false
```

Unrelated repository failures, including stegdb-sync and any RTG-001 watcher failures, remain separate and are not converted to success by this bounded release-awareness completion.


## Generated StegPay current Site receipt ingestion — 2026-08-27

The bounded generated StegPay ingestion lane now targets Site's current validated import receipt at `data/generated-stegpay-propagations/latest/import_receipt.json`, canonical JSON SHA-256 `687d06eb93693d0bd78f00cdefd465d23d92b54c0bbfa7bc0a04b1364f9a452f`. That receipt binds StegOps propagation SHA-256 `e59e71bf31879f0bf29a8356f8027304a94a4dee59d3c0be35c3ecc505e7cec9` and consumer-receipt SHA-256 `b8084ecc9821eb7738e4dccffd239185a072e0bc630e71c72906098a830cf515`.

This is test-only evidence ingestion. Publisher publication, release, payment, deployment, custody, execution, Guardian, and admissibility authority remain false. The completed Site historical task remains closed.

Detailed source of truth: `docs/GENERATED_STEGPAY_SITE_INGESTION_MIRROR_HANDOFF.md`.


## Generated StegPay downstream propagation closure — 2026-08-27

The current Site receipt ingestion and both bounded wiki projections are complete for the `2026-08-27T11:58:18Z` generation.

```text
Publisher merge: cf224d1ee78e16c259db3c6349c02c2444469509
Publisher canonical JSON SHA-256: bbae4456bb09de7eaa3b9782c000fdef106ad035c1f2dee64f62e4102df302a1
Site receipt canonical JSON SHA-256: 687d06eb93693d0bd78f00cdefd465d23d92b54c0bbfa7bc0a04b1364f9a452f
StegOps propagation SHA-256: e59e71bf31879f0bf29a8356f8027304a94a4dee59d3c0be35c3ecc505e7cec9
consumer receipt SHA-256: b8084ecc9821eb7738e4dccffd239185a072e0bc630e71c72906098a830cf515

Admissibility merge: 1cf24e3faddbe62bfea3db700145b39c3756d459
Admissibility main run: 33094673503 SUCCESS
StegGuardian merge: d7a4bdd0e92a4c2fa13ddf81ecf9af68974081cb
StegGuardian main Pages run: 33094989577 SUCCESS
```

The old August 2 generated-Ste gPay hashes are no longer current active projection state; where retained, they are historical provenance only. No duplicate downstream task or workflow was created.

Authority remains false for production payment, publication, release, deployment, custody, execution, admissibility determination, and Guardian enforcement. Wiki Pages/public-route success is observation/transport evidence only. No production tag or release is authorized by this test-only propagation closure.

## Execution ownership and collision partition

Standard: `StegVerse-Labs/Continuity/docs/REPOSITORY_HANDOFF_STANDARD.md` / `stegverse.handoff-execution-ownership/v1`.

### MANUAL / SESSION-STARTABLE

```yaml
- task_id: PUBLISHER-HANDOFF-OWNERSHIP-ADOPTION-035
  execution_owner: repo-standards #37 integration lane + Publisher repository owner
  claim_state: CLAIMED_FOR_INTEGRATION
  worker_registry_ref: StegVerse-Labs/repo-standards#37 + GCAT-BCAT-Engine/Publisher#35
  manual_execution_allowed: true
  manual_allowed_role: integration
  collision_scope: ownership metadata/textual migration in PUBLISHER_MIRROR_HANDOFF.md only; excludes importers, scheduled workflows, Site activation, adjacent construction execution, publication/release/custody/deployment/payment/entitlement/execution authority, credentials, claims/fences/leases, and downstream wiki product logic
  release_condition: this textual migration is merged and issue #35 is closed or superseded
  next_executable_action: merge only the handoff ownership metadata after repository validation; do not enter machine-owned product/runtime scopes
```

### WORKER-OWNED / DO NOT COMPETE

```yaml
- task_id: PUBLISHER-ACTIVE-MACHINE-WORK-AGGREGATE
  execution_owner: existing Publisher scheduled/importer/bootstrap lanes plus their canonical upstream/downstream repository owners
  claim_state: MACHINE_OWNED
  worker_registry_ref: this handoff + docs/GENERATED_STEGPAY_SITE_INGESTION_MIRROR_HANDOFF.md + current task-specific issues/claims/receipts/workflows
  manual_execution_allowed: false
  manual_allowed_role: observation
  collision_scope: Ecosystem Chat Site activation ingestion, autonomous adjacent construction, generated StegPay ingestion/propagation, downstream wiki consumers, and all current repository-native scheduled execution paths
  release_condition: each canonical machine owner independently reaches its own machine-observable terminal condition or explicitly releases/supersedes the relevant collision scope
  next_executable_action: allow existing repository-native automation to continue and observe durable evidence without manually substituting completion
```

### ESCALATED / AUTHORITY-OWNED

```yaml
- task_id: PUBLISHER-AUTHORITY-BOUNDARY
  execution_owner: applicable Publisher/component authority -> ecosystem governance -> human authority when explicitly required
  claim_state: ESCALATED
  worker_registry_ref: this handoff + task-specific current authority records + StegVerse-Labs/Continuity/docs/REPOSITORY_HANDOFF_STANDARD.md
  manual_execution_allowed: false
  manual_allowed_role: reconciliation
  collision_scope: publication, release, custody, deployment, production payment, entitlement, execution, Guardian enforcement, admissibility determination, credential authority, or promotion of transport/projection/receipt evidence into authority
  release_condition: the applicable canonical authority explicitly grants or reassigns the exact bounded authority scope
  next_executable_action: fail closed and escalate rather than inferring authority from Site state, propagation packets, Publisher projection, receipts, workflow success, or wiki publication
```

### COMPLETED / SUPERSEDED

- Correctability projection is `COMPLETE_VALIDATED` as recorded above.
- Governance Observatory publication-awareness and v0.1.0 release-awareness lanes are complete, validated, merged, and non-authorizing.
- The 2026-08-27 generated StegPay Publisher-to-wiki bounded projection chain is complete; older August 2 hashes are historical only.
- Stale `StegVerse-Labs/stegguardian-wiki` and nonexistent `StegVerse-Labs/Sit` destinations are superseded by `StegVerse-002/stegguardian-wiki` and `StegVerse-Labs/Site`.
- Any inference that projection, transport, workflow success, publication awareness, or test evidence grants Publisher publication/release/custody/deployment/payment/entitlement/execution authority is superseded/prohibited.

## Governed KnowledgeVault document pipeline — 2026-08-29

Merged PR #39 adds a general,
renderer-neutral composition path over the merged continuity-recall admission
boundary.

```text
input: stegverse.kv.publisher-document-export/v1
document model: stegverse.publisher.document/v1
formats: Markdown, HTML, PDF, DOCX, JSON
artifact state: GENERATED_VALIDATED_NOT_PUBLISHED
local unit validation: 16/16 PASS
synthetic deterministic replay: byte-identical PASS
authority_effect: NONE
state: SOURCE_MERGED_VALIDATED
merge_commit: be3f27cec7782507fb77e8cadafcc8c10f9e1835
```

Developed source includes the pipeline, two schemas, CLI, admitted fixture,
tests, validation workflow, and scoped handoff. These are functional components,
not placeholder scaffolding. Supporting repairs make continuity hashes accept
explicit `sha256:` roots, make receipt identity actually timestamp-independent,
and restore `press_summary.py` compilation.

No private-KV request, InTr delivery, returned receipt, public artifact,
publication decision, deployment, release, or runtime activation is claimed.
The scoped continuation source of truth is
`docs/KV_DOCUMENT_PIPELINE_MIRROR_HANDOFF.md`.


## StegClaw v1.0.0 release awareness — issue #46

```text
source release: Data-Continuation/StegClaw v1.0.0
release id: 381434394
release target: 6b89a4bfb3d4c2fcc61e6cccaa4f292fb4d58cdb
state: COMPLETE_VALIDATED_MERGED
execution class: PARALLEL_SAFE_NON_AUTHORIZING_RELEASE_AWARENESS
handoff: docs/STEGCLAW_RELEASE_AWARENESS_MIRROR_HANDOFF.md
data: data/stegclaw-release-awareness.json
validator: scripts/check_stegclaw_release_awareness.py
authority effect: NONE
```

This lane is independent of the Site HIL activation dependency and does not satisfy or alter that blocker.


### StegClaw release-awareness completion evidence

```text
issue: #46 CLOSED_COMPLETED
pull request: #48
validated head: 21b7fbf81915d1aad761ffac79f3c72b9ce07acb
dedicated validation: 33659262063 SUCCESS
Publisher Check: 33659262016 SUCCESS
Publisher Readiness: 33659261777 SUCCESS
Architecture Guard: 33659261813 SUCCESS
merge: bf7f77c445980292807364b8402c98afbd47689e
authority effect: NONE
```

## SV002 v0.3 T0 snapshot projection — 2026-09-02

Canonical projection: `data/sv002-t0-snapshot-projection.json`.

The projection is derived from `StegVerse-002/.github` release-manifest reconciliation merge `cf1b0d5ff44a26d42bf9953d8d2ba4b2bd1926ba`.

All ten recorded tag refs resolve to their pinned commits and all ten releases exist. The declared experiment snapshot class remains `EXPERIMENT_SNAPSHOT_PRERELEASE`, while GitHub currently reports `prerelease=false` for all ten releases. The projection therefore records `RELEASES_PRESENT_METADATA_MISMATCH` rather than claiming prerelease metadata conformance.

This projection is awareness/evidence identity only. It does not claim principal execution, SYSTEM_AI_ACTIVE, custody, reconstruction PASS, runtime activation, deployment, product release, admissibility, Guardian enforcement, or destination publication/release authority.

## SV002 T0 standard-release class reconciliation — 2026-09-02

Canonical source decision: `StegVerse-002/.github@5ec896ecf754d85493c38b2d5cb9772a0575e8bf`.

The experiment snapshot release class is now `EXPERIMENT_SNAPSHOT_RELEASE`. GitHub `prerelease=false` is conformant for this class, so the projection state is `RELEASES_PRESENT_METADATA_CONFORMANT`.

This classification change does not promote the snapshot into a product release and does not alter the frozen v0.3 experiment condition, exact tags, pinned commits, principal/runtime state, custody, reconstruction, activation, deployment, admissibility, Guardian enforcement, or destination authority.


## Ecosystem purpose contribution — 2026-09-02

Canonical organization invariant: `StegVerse-Labs/.github/docs/ECOSYSTEM_PURPOSE_INVARIANT.md`.
Machine declaration: `.stegverse/ecosystem-purpose-contribution.json`.

This repository contributes to the StegVerse ecosystem sum through: **evidence, interoperability, observability**.

This binding grants no new authority, does not change repository-local execution/credential/admission/routing/custody/publication/consequence boundaries, and does not establish a new runtime or maturity state. Existing handoff evidence remains authoritative for what this repository has actually implemented, validated, released, deployed, activated, observed, or reconstructed.

The repository should continue advancing the shared objective: preserve agency and explicit authority while making consequential transitions bounded and reconstructable, without requiring a specific intelligence provider or collapsing governance into a universal correctness authority.
