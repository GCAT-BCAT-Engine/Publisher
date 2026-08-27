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
