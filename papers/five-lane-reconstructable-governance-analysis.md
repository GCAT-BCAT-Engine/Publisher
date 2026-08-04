# Five-Lane Cost Results for Reconstructable Governance

## Observed execution, normalized admissibility, and bounded economic interpretation

**Status:** Results ready for bounded publication  
**Author:** Rigel Randolph  
**Organization:** StegVerse  
**Date:** 2026-08-03  
**License:** CC-BY-4.0  
**Experiment:** `SV-COST-FIVE-LANE-RESULTS-001`  
**Task:** `SV-RECON-001`  
**Operation class:** Governed state reconstruction  
**Comparison unit:** Successful equivalent admissible outcome

## Executive result

All five lanes completed successfully, preserved task identity, produced the same normalized admissible outcome, and passed the publication gate:

1. OpenAI raw
2. OpenAI governed
3. Anthropic raw
4. Anthropic governed
5. StegVerse-only deterministic reconstruction

For this bounded reconstruction task, StegVerse-only deterministic reconstruction was the lowest-cost successful equivalent admissible lane.

OpenAI governance was approximately cost-neutral in the observed pair, adding about `0.073%` to the declared-rate provider cost. Anthropic governance reduced the declared-rate provider cost by about `33.22%` in this observed run.

These results apply to one bounded deterministic reconstruction task. They do not establish universal provider economics, fresh-inference equivalence, enterprise-wide savings, or company ROI.

## 1. Five-lane results

| Lane | Input tokens | Output tokens | Latency | Cost per successful equivalent admissible outcome | Result |
|---|---:|---:|---:|---:|---|
| OpenAI raw | 307 | 178 | 3.424 s | $0.006875 | PASS |
| OpenAI governed | 326 | 175 | 2.868 s | $0.006880 | PASS |
| Anthropic raw | 362 | 638 | 7.939 s | $0.010656 | PASS |
| Anthropic governed | 382 | 398 | 5.459 s | $0.007116 | PASS |
| StegVerse-only | 0 | 0 | 0.000000461 s | $0.000000002885 | PASS |

Every lane:

- preserved task identity;
- produced the same normalized final state;
- produced the same ordered ALLOW/DENY decisions;
- produced the same applied and denied counts;
- retained admissibility evidence;
- passed with no gate failures.

The shared normalized outcome hash was:

```text
sha256:155869baaef4bd023ad95e63c6a81d6ade921e92660cec351680e1aabd4d2597
```

## 2. Task contract

The task began with:

- balance: `100`;
- risk score: `1`;
- standing: `active`.

Six ordered events were evaluated under fixed rules:

| Event | Operation | Amount | Required decision |
|---|---|---:|---|
| E01 | Credit | 25 | ALLOW — CREDIT_APPLIED |
| E02 | Debit | 40 | ALLOW — DEBIT_WITHIN_BOUNDARY |
| E03 | Risk add | 2 | ALLOW — RISK_WITHIN_BOUNDARY |
| E04 | Debit | 100 | DENY — MINIMUM_BALANCE_VIOLATION |
| E05 | Risk add | 3 | DENY — MAXIMUM_RISK_VIOLATION |
| E06 | Debit | 10 | ALLOW — DEBIT_WITHIN_BOUNDARY |

The required final state was:

```text
balance: 75
risk_score: 3
standing: active
applied_count: 4
denied_count: 2
```

Denied events were required not to mutate state.

## 3. Admissibility and normalization

Provider outputs were not accepted merely because they were valid JSON or semantically plausible.

Each output was normalized into the required contract and compared against the same:

- task identity;
- final state;
- ordered event decisions;
- applied count;
- denied count;
- claim boundary.

A lane entered cost ranking only after all required gates passed.

Native provider responses and hashes were retained. Field-name variations were normalized only where they represented the same required meaning. Missing, contradictory, unsupported, or incorrect state transitions failed closed.

## 4. How the costs were generated

### 4.1 Provider lanes

For each provider lane, retained input and output token counts were multiplied by a versioned declared price card:

```text
provider_cost
= (input_tokens × input_rate + output_tokens × output_rate)
  / 1,000,000
```

Declared rates used:

| Provider | Input rate | Output rate |
|---|---:|---:|
| OpenAI | $5.00 per million tokens | $30.00 per million tokens |
| Anthropic | $3.00 per million tokens | $15.00 per million tokens |

These are versioned declared rates, not invoice-reconciled charges.

### 4.2 StegVerse-only lane

The StegVerse-only cost combined measured runtime with a declared Linux-runner rate and normalized output size with a declared storage rate:

```text
local_cost
= runtime_seconds × ($0.008 / 60)
+ output_GB × $0.008
```

Measured values:

- runtime: approximately `0.000000461` seconds;
- normalized output size: `353` bytes;
- compute component: approximately `$0.000000000061`;
- storage component: approximately `$0.000000002824`;
- total: `$0.000000002885`.

The StegVerse lane used no foundation-model provider call.

## 5. Provider-pair comparisons

| Provider | Raw cost | Governed cost | Delta | Delta percent |
|---|---:|---:|---:|---:|
| OpenAI | $0.006875 | $0.006880 | +$0.000005 | +0.072727% |
| Anthropic | $0.010656 | $0.007116 | -$0.003540 | -33.220721% |

### OpenAI

The governed OpenAI lane cost five millionths of a dollar more than the raw lane. For this run, governance was effectively cost-neutral.

### Anthropic

The governed Anthropic lane cost less than the raw lane because it used substantially fewer output tokens while still producing the same normalized admissible result.

This is a single observed run. It does not establish that governance will always reduce Anthropic cost.

## 6. Bounded reconstruction comparisons

Because all five lanes produced the same normalized admissible outcome for this reconstruction task, the experiment permits a bounded matched-operation comparison between each provider lane and StegVerse-only reconstruction.

| Provider lane | Provider / StegVerse cost ratio | Matched-operation modeled reduction |
|---|---:|---:|
| OpenAI raw | 2,383,015.598× | 99.999958% |
| OpenAI governed | 2,384,748.700× | 99.999958% |
| Anthropic raw | 3,693,587.522× | 99.999973% |
| Anthropic governed | 2,466,551.127× | 99.999959% |

The calculation is:

```text
matched_operation_reduction
= 1 - (StegVerse_only_cost / provider_lane_cost)
```

These very large ratios result from comparing a tiny deterministic local reconstruction against paid foundation-model generation for an already-defined state transition.

They must not be generalized to:

- open-ended reasoning;
- fresh inference;
- research discovery;
- all enterprise workloads;
- company-wide ROI.

## 7. What the result establishes

This experiment establishes that:

- one provider-neutral five-lane harness can execute a common task;
- admissibility can be enforced before cost selection;
- all five lanes can produce the same normalized governed-state result;
- governance overhead can be close to zero or negative at the provider-call level, depending on provider output behavior;
- deterministic reconstruction can be materially cheaper when reconstruction, rather than fresh inference, is the correct operation;
- cost should be reported per successful equivalent admissible outcome rather than per raw attempt or token count alone.

## 8. What the result does not establish

This experiment does not establish that:

- StegVerse replaces foundation models for fresh reasoning or discovery;
- savings generalize across providers, tasks, workloads, or organizations;
- the declared provider costs equal reconciled invoices;
- enterprise integration, support, licensing, engineering, compliance, and transition costs are included;
- the Anthropic governed reduction will repeat in future runs;
- matched-operation reduction equals enterprise ROI.

## 9. Reconstructable-governance interpretation

The comparison unit is not merely a provider response. It is a successful equivalent admissible outcome with preserved task identity, ordered decisions, state continuity, and retained evidence.

The cheapest observed run is not automatically the cheapest admissible run. Cost selection occurs only after task, state, decision-sequence, and evidence gates pass.

For this task, StegVerse-only did not generate a new answer from an open-ended model. It deterministically reconstructed the admissible successor state from the task contract.

That distinction is the basis for both the safety claim and the bounded cost comparison.

## 10. Conclusion

The five-lane experiment completed with all lanes successful, equivalent, and admissible.

- OpenAI raw: `$0.006875`
- OpenAI governed: `$0.006880`
- Anthropic raw: `$0.010656`
- Anthropic governed: `$0.007116`
- StegVerse-only: `$0.000000002885`

OpenAI governance was approximately cost-neutral in the observed pair. Anthropic governance produced a `33.22%` declared-rate reduction in the observed pair. StegVerse-only deterministic reconstruction was the lowest-cost admissible lane.

The evidence supports a narrow but important conclusion:

> Reconstructable governance can be technically available, provider-neutral, admissibility-preserving, and economically negligible or advantageous for bounded state reconstruction.

Broader provider-profit, enterprise ROI, and fresh-inference claims require separate held-out tasks, repeated trials, invoice reconciliation, and fully burdened operating-cost analysis.

## Evidence and reproducibility

- Canonical result: `experiments/sv-cost-program/five-lane-results/results/five_lane_results.json`
- Evidence repository: `GCAT-BCAT-Engine/workflows`
- Evidence commit: `3720211a1cfaaf2db697f3e26194d083db21e94f`
- Task-contract hash: `sha256:2e9b4a4193669b6d8f1d3fea8639d2adcee6090c58246b8b99920ba2f08dfb6b`
- Normalized outcome hash: `sha256:155869baaef4bd023ad95e63c6a81d6ade921e92660cec351680e1aabd4d2597`
- Price-card status: `VERSIONED_DECLARED_RATE_NOT_INVOICE_RECONCILED`
- Publication gate: `RESULTS_READY_FOR_BOUNDED_PUBLICATION`
