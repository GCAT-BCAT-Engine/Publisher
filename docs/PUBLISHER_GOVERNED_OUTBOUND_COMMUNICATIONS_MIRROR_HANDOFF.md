# Publisher Governed Outbound Communications — Mirror Handoff

Updated: 2026-10-05

## Task pointer

- Goal Task ID: `PUBLISHER-GOVERNED-OUTBOUND-COMMUNICATIONS-001`
- Derived from incident evidence: `ELAN-HOLD-INDEPENDENT-SEMANTIC-ANALYSIS-PACKET-001`
- Canonical issue: `StegVerse-Labs/.github#2959`
- Intended owner: `GCAT-BCAT-Engine/Publisher`
- Status: `ACTIVE`

## Purpose

Extend Publisher's existing governed manifest/admission/receipt boundary to outbound media, beginning with email, without making Publisher a duplicate mailbox, relationship database, credential route, transport, or authority plane.

## Existing capabilities to reuse

Publisher already owns manifest-driven publication/admission boundaries, hash-bound artifact transfer/return packets, receipt writing, and explicit communication-completion boundaries. Those mechanisms are inputs to this Goal rather than reasons to create a parallel communications stack.

Authoritative communication/history data remains in its existing source system. Publisher retains references, hashes, predecessor relationships, context-resolution evidence, manifests and send/publication receipts required to reconstruct why an outbound communication was admitted.

## Required communication-event model

An inbound communication event must be representable by stable event identity, source-system locator, sender/recipient identities as exposed by the source, observed timestamp, immutable content digest, media type, predecessor/reply-chain references, relationship/workstream correlation when resolvable, and source evidence sufficient for later readback.

Publisher must not copy an entire mailbox merely to satisfy this contract.

## Purpose-derived context resolution

Before composition, an outbound intent declares its purpose. Purpose deterministically selects required context categories. Initial categories are:

- relationship/history;
- correspondence/thread history;
- active workstream/task state;
- prior commitments, constraints and promises;
- source artifacts specifically required by the outbound purpose.

Each required category must terminate in exactly one context disposition:

- `VERIFIED` — authoritative evidence was retrieved and bound;
- `NOT_APPLICABLE` — the category is not applicable to the declared purpose, with reason;
- `NO_PRIOR_HISTORY` — authoritative retrieval establishes that no prior history exists within the applicable source scope;
- `INSUFFICIENT_EVIDENCE` — required context cannot be established.

`INSUFFICIENT_EVIDENCE` is non-ALLOW for composition admission. Missing evidence must not be silently converted to `NO_PRIOR_HISTORY`.

## Composition and admission boundary

Composition is admitted only after every purpose-required category resolves to `VERIFIED`, `NOT_APPLICABLE`, or `NO_PRIOR_HISTORY`.

The outbound manifest must bind at minimum:

- declared purpose;
- recipient/channel;
- predecessor communication event(s), when any;
- required-context policy/version;
- each context disposition and evidence reference;
- composed body digest and attachment digests;
- requested transport action;
- authority/approval evidence required by the applicable policy.

The composition model may use retrieved context, but it must not invent relationship state when evidence is unresolved.

## Send and retained evidence

A successful external send is a separate observed transition from composition/admission. Retain transport-provider message/event identity when exposed, send timestamp, admitted outbound-manifest digest, exact body/attachment digests, predecessor linkage, and the existing Publisher publication/communication receipt references.

Draft creation, manifest validation, CI, or repository merge does not prove external send.

## Non-duplication invariants

This Goal must not create:

- a duplicate email store or mailbox;
- a new relationship database;
- a new mail transport;
- a new credential route;
- a new authority plane;
- an ÉLAN-specific communications implementation.

## Incident relationship

The ÉLAN incident demonstrates why context-blind composition is unsafe for an established collaboration. It is motivating evidence only. This Goal is ecosystem-wide and must remain reusable for unrelated outbound-media purposes.

## Machine-readable contract

The minimum v1 contract is `schemas/publisher-governed-outbound-communication.v1.schema.json`. It stores authoritative source locators and evidence references rather than source mailbox/history contents, requires explicit context dispositions, makes `INSUFFICIENT_EVIDENCE` incompatible with `ALLOW`, and keeps external send observation separate from composition admission.

## Implemented admission binding

`publisher/governed_outbound_communication.py` consumes a supplied v1 contract after authoritative context has been resolved outside Publisher. It validates the existing schema, returns an explicit ALLOW, DENY or FAIL_CLOSED composition-admission disposition, and writes that transition through the existing `PublicationReceiptWriter`. The retained receipt binds source event/locator/digest, predecessor IDs, purpose/policy, category dispositions and evidence references, manifest/body/attachment digests, requested transport and authority-evidence references.

This binding does not retrieve mailbox/history data, compose or send media, resolve credentials, or create authority. `send_executed` remains false; an authentic external send remains a separate required observation.

## Completion predicates

- authoritative inbound-event references and predecessor chains are machine-readable;
- purpose selects required context categories deterministically;
- all required categories terminate in the four explicit context dispositions;
- `INSUFFICIENT_EVIDENCE` prevents composition admission;
- admitted outbound manifests bind context evidence and exact composed bytes;
- external send is separately evidenced;
- retained receipts permit reconstruction of context -> composition -> admission -> send;
- existing storage, transport, credentials and authority mechanisms are reused;
- README and canonical Task Registry/handoff projections are current.


## 2026-10-05 prompt-limit closeout

The reusable contract/schema/purpose/context/composition-admission scope is complete through canonical Publisher merge `7caf5906dc417f318e0f5b0456e899e43d7a61b0`. This Goal is retired at 20/20 without claiming external send. The genuinely separable post-admission execution/evidence obligation continues under `PUBLISHER-GOVERNED-OUTBOUND-EXECUTION-EVIDENCE-001` / COSV `71000000100122`; see `docs/PUBLISHER_GOVERNED_OUTBOUND_EXECUTION_EVIDENCE_MIRROR_HANDOFF.md`.
