# RTG-001 Lifecycle Cost Ledger Summary

## Scope

This summary tracks RTG-001 from initial planning through final review candidate preparation.

## Actual Costs From Previous Stage

```text
repo_build_and_documentation_commits: 0.00 USD paid API cost recorded
local_fixture_tests: 0.00 USD paid API cost recorded
github_actions_cost_recorded_in_artifacts: pending
anthropic_api_cost_recorded_in_artifacts: pending
```

The previous stage consisted of repository updates, documentation, fixture-compatible tests, and staged automation. No returned solver receipt has been ingested yet.

## Reference Costs Already Recorded

```text
external_full_process_reference_usd: 0.02086
external_incremental_reference_usd: 0.035
native_full_process_reference_usd: 0.06505
validation_connectivity_reference_usd: 0.015
prior_framework_total_validation_spend_usd: 0.25
```

These values are reference costs, not current RTG-001 final receipts.

## Estimated Upcoming Stage Costs

```text
review_packet_generation_local: 0.00 USD paid API cost expected
review_packet_ci_smoke_expected: 0.00 USD paid API cost expected
artifact_watcher_polling_expected_api_cost: 0.00 USD paid API cost expected
expected_solver_artifact_receipt_range_usd: 0.02086 - 0.035
optional_solver_replay_or_iteration_range_usd: 0.02086 - 0.06505
human_or_formal_review_cost_usd: not estimated here
```

## Cost Rule

The final actual solver cost must be read from the returned `ext2_report.json` file once `external-full-results` exists.

Until then, Publisher must say:

```text
pre_execution_estimate_only
actual_cost_receipt_pending
within_budget_reference_gate
```
