# Cost Tensor Reference Bundle

This bundle contains the first executable deterministic reference layer for the StegVerse Cost Tensor.

## Files

- `cost_tensor_reference.py` — minimal ALLOW / DENY / FAIL_CLOSED evaluator.
- `test_vectors/*.json` — minimum deterministic test vector set.
- `.github/workflows/cost-tensor-tests.yml` — GitHub Actions workflow.
- `brain_reports/` — generated test reports and receipt index.

## Run

```bash
python cost_tensor_reference.py --vectors test_vectors --out brain_reports
```

Expected result:

```json
{
  "failed": 0,
  "passed": 25,
  "skipped": 0,
  "total": 25
}
```
