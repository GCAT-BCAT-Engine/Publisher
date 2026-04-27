## AaCT-E Demo Verification — {{date}}

The Admissibility at Commit-Time Engine (AaCT-E) demo has completed another verification cycle, continuing to validate the core claim behind the GCAT/BCAT formalism:

> At the exact moment an action would become operationally real, the system can evaluate whether recovery remains available and deny the action if it would push the system into an unrecoverable or separation-violating state.

### This Run

| Scenario | Decision | Min Separation | Recovery |
|----------|----------|----------------|----------|
{{scenario_rows}}

### Reproducibility

```bash
git clone --branch v0.2.0 https://github.com/AaCT-E/demo.git
cd demo
python verify_demo.py
```

No external dependencies. No configuration. Same input → same trace → same decision.

### Ecosystem Context

- **Theory:** [GCAT-BCAT-Engine](https://github.com/GCAT-BCAT-Engine)
- **Demo:** [AaCT-E/demo](https://github.com/AaCT-E/demo)
- **Paper submissions:** Managed through this Publisher repository
