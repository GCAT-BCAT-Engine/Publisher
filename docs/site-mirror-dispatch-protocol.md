# Site Mirror Dispatch Protocol

## Purpose

This protocol defines how Publisher should notify `StegVerse-Labs/Site` that current paper or case-study display data may need to be refreshed.

Publisher remains the source of truth. Site remains the public display surface.

## Publisher Dispatch Workflow

The Publisher workflow that performs validation and dispatch is:

```text
.github/workflows/dispatch-site-mirror.yml
```

The workflow name is:

```text
Dispatch Site Paper Mirror
```

It runs after eligible Publisher changes on `main` and may also be run manually.

## Target Site Workflow

The target Site workflow is:

```text
StegVerse-Labs/Site/.github/workflows/mirror-papers.yml
```

The workflow name is:

```text
Mirror Papers from Publisher
```

The workflow accepts these dispatch inputs:

```text
source_repository
source_ref
```

Default values should be:

```text
source_repository: GCAT-BCAT-Engine/Publisher
source_ref: main
```

## Dispatch Eligibility

Publisher may dispatch the Site mirror workflow after changes to:

```text
papers/**
papers_manifest.yml
papers.json
cases/**
governance/cases/**
governance/receipts/**
docs/site-paper-display-policy.md
docs/site-mirror-dispatch-protocol.md
```

Publisher should not dispatch Site if Publisher validation fails.

## Required Dispatch Sequence

Use this order:

```text
1. Publisher paper or case source record changes.
2. Publisher validation passes.
3. Publisher sends workflow_dispatch to Site mirror workflow.
4. Site mirror workflow runs Site policy checker.
5. Site checks out Publisher at the requested ref.
6. Site mirrors papers and regenerates indexes.
7. Site commits visible paper display changes if needed.
```

## Required Token Boundary

The dispatch credential must be limited to the minimum access required to trigger the Site workflow.

The Site mirror workflow separately needs read access to Publisher if Publisher is private or otherwise inaccessible to the default workflow token.

Suggested secret names:

```text
SITE_MIRROR_DISPATCH_TOKEN
STEGVERSE_REPO_SYNC_TOKEN
```

`SITE_MIRROR_DISPATCH_TOKEN` belongs in Publisher when Publisher dispatches Site.

`STEGVERSE_REPO_SYNC_TOKEN` belongs in Site when Site must read Publisher.

## Dry-Run Procedure

Use dry run before installing or relying on cross-repo dispatch credentials.

```text
1. Open GCAT-BCAT-Engine/Publisher Actions.
2. Select Dispatch Site Paper Mirror.
3. Run workflow on main.
4. Set dry_run to true.
5. Leave site_repository as StegVerse-Labs/Site unless testing a fork.
6. Leave source_ref as main unless testing a branch or SHA.
7. Confirm Publisher validation passes.
8. Confirm Site mirror dispatch configuration check passes.
9. Confirm the workflow prints that Site mirror dispatch was not attempted.
```

Dry run does not require `SITE_MIRROR_DISPATCH_TOKEN` and does not trigger the Site workflow.

## Manual Dispatch Procedure

To test live dispatch after dry run passes:

```text
1. Confirm SITE_MIRROR_DISPATCH_TOKEN is installed in Publisher.
2. Open GCAT-BCAT-Engine/Publisher Actions.
3. Select Dispatch Site Paper Mirror.
4. Run workflow on main.
5. Set dry_run to false.
6. Leave site_repository as StegVerse-Labs/Site unless testing a fork.
7. Leave source_ref as main unless testing a branch or SHA.
8. Confirm Publisher validation passes.
9. Confirm the Site workflow starts.
10. Confirm Site mirror completes and records the source repository and ref.
```

## Failure Handling

If dispatch fails, Publisher should not mark the Site display as current.

If Site mirror fails, Site should keep the last successful public display and expose failure through workflow logs rather than silently publishing partial mirror output.

## Done State

Publisher-to-Site dispatch is complete when:

```text
Publisher validates source records
Publisher dry run passes without requiring a dispatch token
Publisher can trigger Site mirror workflow
Site policy checker runs before mirroring
Site records source repository and source ref in workflow summary
Site commit references Publisher as source
```
