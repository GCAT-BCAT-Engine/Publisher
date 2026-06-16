# iPhone Dry-Run Runbook — Publisher to Site Mirror

## Purpose

This runbook gives an iPhone-safe procedure for testing the Publisher-to-Site mirror path without installing tokens and without triggering the Site mirror workflow.

Use this before live dispatch.

## Target Workflow

In the GitHub mobile app or Safari, open:

```text
GCAT-BCAT-Engine/Publisher
```

Then open:

```text
Actions → Dispatch Site Paper Mirror
```

The repository path for the workflow is:

```text
.github/workflows/dispatch-site-mirror.yml
```

## Dry-Run Inputs

Use these values:

```text
branch: main
site_repository: StegVerse-Labs/Site
source_ref: main
dry_run: true
```

## Expected Passing Steps

The dry run should complete this shared activation check:

```text
Run Publisher activation validation
```

That activation step runs:

```text
Check emergency AI templates
Validate emergency AI case objects
Check Site mirror dispatch configuration
Check Publisher to Site release gate
```

The dry run should then complete:

```text
Resolve dispatch inputs
Stop after validation for dry run
```

It should not run these live-dispatch steps:

```text
Require dispatch token
Dispatch Site mirror workflow
```

## Expected Success Message

Look for this message in the workflow logs:

```text
Dry run requested. Publisher validation and dispatch configuration checks passed.
Site mirror dispatch was not attempted.
```

The activation runner should also print:

```text
valid: Publisher activation checks
```

## Failure Handling

If the dry run fails, do not install or use the live dispatch token yet.

Fix the first failing check and rerun dry run.

## After Dry Run Passes

After dry run passes:

```text
1. Update docs/verification-tracker.md from pending_dry_run to dry_run_passed.
2. Confirm SITE_MIRROR_DISPATCH_TOKEN is installed in Publisher.
3. Confirm Site can read Publisher during mirror checkout.
4. Run Dispatch Site Paper Mirror again with dry_run: false.
```

## Release Gate Reminder

Do not mark Site paper display current until `docs/release-gate-checklist.md` passes.
