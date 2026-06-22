# Publisher Mirror Handoff

## Status

This file is the current handoff and task source of truth for `GCAT-BCAT-Engine/Publisher`.

## Current Priority

Publish or update StegTalk non-production local candidate status from the Site mirror and StegTalk source artifacts.

## Source Artifacts

Primary source: `StegVerse-Labs/Site`

- `SITE_MIRROR_HANDOFF.md`
- `data/stegtalk-local-candidate.json`
- `data/stegtalk-local-candidate-receipt.json`

Original source: `StegVerse-Labs/StegTalk`

- `STEGTALK_MIRROR_HANDOFF.md`
- `STEGTALK_CANDIDATE_STATUS.json`
- `STEGTALK_LOCAL_CANDIDATE.json`
- `STEGTALK_RELEASE_HANDOFF.json`

## Required Publisher Install

Destination: `GCAT-BCAT-Engine/Publisher`

- Publisher-visible StegTalk local candidate record
- Publisher receipt preserving non-production boundary and downstream wiki targets

## Downstream Propagation Still Required

Destination: `admissibility-wiki`

- add/update StegTalk admissibility boundary notes

Destination: `stegguardian-wiki`

- add/update StegTalk guardian/account boundary notes

## Build Rule

Before continuing any Publisher mirror task, check this file first and treat it as the current handoff and task source of truth.

## Boundary

StegTalk remains a non-production local prototype candidate. Do not publish it as production ready.
