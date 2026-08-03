# Governed and Non-Governed AI Cost Estimation for Ten Frontier Mathematics Results

**Status:** Preregistered protocol — results pending  
**Authors:** Rigel Randolph; StegVerse Ecosystem  
**Date:** 2026-08-02  
**License:** CC-BY-4.0

## Abstract

This study compares independent resource estimates for attempting ten frontier mathematical results across five execution lanes: OpenAI without StegVerse governance, OpenAI with StegVerse governance, Anthropic without StegVerse governance, Anthropic with StegVerse governance, and a StegVerse sandbox/ecosystem-only feasibility lane. The first phase asks each provider to estimate, rather than solve, each problem. The study measures predicted search cost, failed branches, verification cost, governance overhead, elapsed time, and probability of producing a publishable result. A bounded solve attempt may begin only after a StegVerse-only candidate passes an explicit feasibility and independent-verification gate.

## Research questions

1. How do OpenAI and Anthropic independently estimate the cost and feasibility of attempting the same ten mathematical research targets?
2. What measurable overhead is introduced by StegVerse governance?
3. Does governance improve the evidentiary value of an estimate by preserving task identity, branch history, assumptions, budget boundaries, and verification requirements?
4. Can the installed StegVerse sandbox and ecosystem attempt any bounded component without undeclared provider inference?
5. Which cost measure is most meaningful: token price, successful-path cost, total search cost, or cost per independently validated result?

## Experimental lanes

| Lane | Provider/runtime | Governance posture |
|---|---|---|
| OAI-R | OpenAI | Non-governed baseline |
| OAI-G | OpenAI | StegVerse-governed |
| ANT-R | Anthropic | Non-governed baseline |
| ANT-G | Anthropic | StegVerse-governed |
| SV-O | Installed StegVerse sandbox/ecosystem | Governed; no undeclared external inference |

The governed and non-governed provider lanes receive the same problem statement, target result, budget ceiling, and success criteria. Governance overhead is recorded separately from inference, search, and verification cost.

## Targets

The ten targets cover high-dimensional sphere packing; binary and spherical codes; non-sofic groups; Connes rigidity; arithmetic circuit complexity; quantum parallel repetition; closest-vector hardness; Ehrhart volume; multicolor Ramsey numbers; and extremal graph theory.

## Estimation procedure

Providers are instructed not to solve the target and not to anchor on a published aggregate cost. Each response must provide low, central, and high estimates for total cost and elapsed time; token and branch estimates; formalization and verification cost; success, reproduction, and independent-result probabilities; assumptions; uncertainty drivers; blockers; and minimum evidence required before the target may be called solved.

Raw provider responses are retained, hashed, normalized into a common schema, and validated. Provider estimates are explicitly labeled as estimates rather than observed costs.

## Governance controls

The governed lanes add:

- problem-identity hashing;
- fixed budgets and timeouts;
- branch and retry receipts;
- assumption and uncertainty capture;
- undeclared-provider denial;
- evidence preservation;
- independent-verification planning;
- separation of reproduction from independent discovery.

## StegVerse-only feasibility gate

A bounded StegVerse-only attempt is admissible only when the required tools are installed, hidden provider inference is prevented, branch history and evidence are preserved, a budget and timeout are declared, success criteria are machine-readable, and an independent verification route exists. Candidate selection is based on feasibility and verification tractability rather than prestige.

## Publication rule

No numerical conclusion will be published as a study result until all expected records are present, uncertainty intervals validate, raw-response hashes resolve, and the comparison can be reproduced from repository artifacts. A protocol publication does not imply that any target has been solved or that any provider estimate is accurate.

## Implementation

Canonical execution repository: `GCAT-BCAT-Engine/workflows`  
Canonical handoff: `docs/TEN_ADVANCES_COST_ESTIMATION_MIRROR_HANDOFF.md`  
Problem set: `experiments/ten-advances/problems.json`  
Workflow: `.github/workflows/ten-advances-estimation.yml`

## Planned result papers

1. **Provider Estimation Study:** OpenAI versus Anthropic estimates, governed and non-governed.
2. **Governance Overhead Study:** Cost and evidentiary effects of the StegVerse controls.
3. **StegVerse-Only Feasibility Study:** Installed capability inventory and bounded-candidate selection.
4. **Bounded Solve Report:** Published only if an admissible candidate is executed and independently verified.
