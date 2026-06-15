# Site Mirror Dispatch Protocol

## Purpose

This protocol defines how Publisher should notify `StegVerse-Labs/Site` that current paper or case-study display data may need to be refreshed.

Publisher remains the source of truth. Site remains the public display surface.

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

## Failure Handling

If dispatch fails, Publisher should not mark the Site display as current.

If Site mirror fails, Site should keep the last successful public display and expose failure through workflow logs rather than silently publishing partial mirror output.

## Done State

Publisher-to-Site dispatch is complete when:

```text
Publisher validates source records
Publisher can trigger Site mirror workflow
Site policy checker runs before mirroring
Site records source repository and source ref in workflow summary
Site commit references Publisher as source
```
