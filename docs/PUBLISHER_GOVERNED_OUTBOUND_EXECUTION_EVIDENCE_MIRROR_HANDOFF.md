# Publisher Governed Outbound Execution Evidence — Mirror Handoff

Updated: 2026-10-05

## Task pointer

- Goal Task ID: `PUBLISHER-GOVERNED-OUTBOUND-EXECUTION-EVIDENCE-001`
- Parent: `PUBLISHER-GOVERNED-OUTBOUND-COMMUNICATIONS-001`
- Canonical issue: `StegVerse-Labs/.github#2969`
- COSV: `71000000100122`
- Owner: `GCAT-BCAT-Engine/Publisher`
- Status: `ACTIVE / CHECKED_OUT`

## Completed predecessor boundary

Publisher merge `7caf5906dc417f318e0f5b0456e899e43d7a61b0` implements the reusable governed-outbound schema and composition-admission binding. It can return ALLOW, DENY or FAIL_CLOSED and retains a Publisher receipt while `send_executed=false`. Admission is not send evidence.

## Existing machinery to reuse

- `StegVerse-Labs/Comms-Gateway/adapters/base.py`: provider-neutral `CommunicationAdapter` delivery boundary; delivery requires an outbound allowed transition, routed decision, dispatch authority and matching dispatch receipt.
- `StegVerse-Labs/Comms-Gateway/gateway/delivery.py`: canonical delivery result requiring `provider_evidence.provider_event_id`, provider/status and binding to transition/routing/dispatch receipt hashes.
- `StegVerse-Labs/Comms-Gateway/gateway/lifecycle.py`: canonical full communication lifecycle binding transition, routing, dispatch receipt and delivery result.
- TV/TVC remains the credential-bearing provider-operation authority. Consumer repositories must not regain OAuth/token custody.
- `StegVerse-Labs/StegOps-Orchestrator/README_GMAIL.md` explicitly retires historical consumer-side Gmail OAuth/refresh-token execution; current admitted Gmail broker operations are SEARCH_MESSAGES, SEARCH_IDS, ARCHIVE_IDS and GET_LABEL_COUNTS.
- `StegVerse-Labs/Comms-Gateway/adapters/microsoft365.py` is read-only and raises `PermissionError` on delivery.

## First attempted successor transition

```text
GOVERNANCE_DISPOSITION::FAIL_CLOSED
predicate = AUTHORIZED_EMAIL_PROVIDER_SEND_OPERATION_ADMITTED_THROUGH_EXISTING_TV_TVC_AND_COMMS_GATEWAY_PATH
```

Cause: the canonical transport, dispatch-authority and delivery/lifecycle evidence contracts already exist, and TV/TVC already owns provider credentials, but no current credential-bearing email provider operation is admitted for outbound send. Historical StegOps Gmail draft-send code is not current authority and must not be revived as a consumer-side credential path.

## Required remediation path

Extend the existing TV/TVC provider-operation authority with one bounded email-send operation and expose it through the existing Comms-Gateway adapter delivery contract. Do not create a new transport, credential route, mailbox/history store, relationship store or authority plane. Do not restore direct consumer OAuth/refresh-token custody.

The provider operation must return authentic provider evidence sufficient for the existing Comms-Gateway delivery result. When exposed by the provider, retain message/event identity and provider timestamp. Feed that evidence into the existing delivery-result and lifecycle records.

Then bind the observed lifecycle back to the already-admitted Publisher artifact by retaining:

- admitted outbound-manifest digest;
- exact composed body digest;
- exact attachment digests;
- predecessor communication event linkage;
- Publisher admission receipt reference;
- Comms-Gateway dispatch receipt reference;
- Comms-Gateway delivery-result reference;
- Comms-Gateway lifecycle-record reference;
- provider event/message identity and provider send timestamp when exposed.

## Disposition rules

- ALLOW only after an admitted Publisher ALLOW traverses the existing authorized send path and authentic provider evidence is retained with all required digest/receipt linkage.
- DENY when existing authority explicitly rejects dispatch/send.
- FAIL_CLOSED at the first missing/malformed authority, routing, provider-operation, provider-evidence or binding predicate.
- Never infer send from Publisher admission, draft creation, CI, repository merge, dispatch intent or a provider call without retained authentic provider evidence.

## Non-duplication invariants

No new transport. No new credential route. No duplicate mailbox/history store. No duplicate relationship database. No new authority plane. No second user-operated device requirement.
