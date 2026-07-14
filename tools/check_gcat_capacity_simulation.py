#!/usr/bin/env python3
"""Repository-local validation gate for the GCAT capacity simulation."""

from __future__ import annotations

import importlib.util
import json
import math
import tempfile
from pathlib import Path
from typing import Dict, List, Mapping

ROOT = Path(__file__).resolve().parents[1]
SIMULATION_PATH = ROOT / "tools" / "gcat_capacity_simulation.py"
CONFIG_PATH = ROOT / "data" / "gcat_capacity_scenarios.json"


def load_module():
    spec = importlib.util.spec_from_file_location("gcat_capacity_simulation", SIMULATION_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load simulation module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def require(condition: bool, message: str, failures: List[str]) -> None:
    if not condition:
        failures.append(message)


def validate_record(record: Mapping[str, float], failures: List[str], prefix: str) -> None:
    for name in ("g", "c", "t", "a", "effective_capacity", "omega"):
        require(math.isfinite(record[name]), f"{prefix}: {name} must be finite", failures)
        require(record[name] > 0, f"{prefix}: {name} must remain positive", failures)
    require(math.isfinite(record["margin"]), f"{prefix}: margin must be finite", failures)
    require(record["intervention"] >= 0, f"{prefix}: intervention must be nonnegative", failures)


def main() -> int:
    failures: List[str] = []
    module = load_module()
    scenarios = module.load_scenarios(CONFIG_PATH)

    require(len(scenarios) == 4, "exactly four declared scenarios are required", failures)
    expected_ids = {
        "balanced_adaptation",
        "delayed_intervention",
        "constraint_heavy_fragility",
        "bounded_recovery_failure",
    }
    require({item.scenario_id for item in scenarios} == expected_ids, "scenario set mismatch", failures)

    summaries: Dict[str, Mapping[str, object]] = {}
    records_by_id = {}
    for scenario in scenarios:
        records = module.simulate(scenario)
        records_by_id[scenario.scenario_id] = records
        require(len(records) > 2, f"{scenario.scenario_id}: insufficient records", failures)
        require(abs(records[0]["time"]) < 1e-12, f"{scenario.scenario_id}: first time must be zero", failures)
        require(
            abs(records[-1]["time"] - scenario.duration) <= scenario.step + 1e-12,
            f"{scenario.scenario_id}: final time mismatch",
            failures,
        )
        previous_time = -1.0
        for index, record in enumerate(records):
            validate_record(record, failures, f"{scenario.scenario_id}[{index}]")
            require(record["time"] > previous_time, f"{scenario.scenario_id}: time must increase", failures)
            previous_time = record["time"]
            recomputed_margin = -math.log(record["omega"])
            require(
                abs(record["margin"] - recomputed_margin) < 1e-10,
                f"{scenario.scenario_id}[{index}]: margin identity failed",
                failures,
            )
        summary = module.summarize(scenario, records)
        summaries[scenario.scenario_id] = summary
        require(summary["synthetic"] is True, f"{scenario.scenario_id}: synthetic marker missing", failures)
        require(summary["calibrated"] is False, f"{scenario.scenario_id}: calibration marker invalid", failures)

    balanced = summaries["balanced_adaptation"]
    delayed = summaries["delayed_intervention"]
    fragile = summaries["constraint_heavy_fragility"]
    recovery = summaries["bounded_recovery_failure"]

    require(
        float(balanced["maximum_omega"]) < float(delayed["maximum_omega"]),
        "delayed intervention must generate more load than balanced adaptation",
        failures,
    )
    require(
        recovery["first_overload_time"] is not None,
        "bounded recovery failure must cross the overload boundary",
        failures,
    )
    require(
        fragile["first_overload_time"] is not None,
        "constraint-heavy fragility must cross the overload boundary",
        failures,
    )

    # Verify intervention latency is actually encoded in generated records.
    delayed_records = records_by_id["delayed_intervention"]
    require(
        all(record["intervention"] == 0.0 for record in delayed_records if record["time"] < 8.0),
        "delayed intervention activated before its declared delay",
        failures,
    )

    with tempfile.TemporaryDirectory(prefix="gcat-capacity-") as temp_dir:
        output = Path(temp_dir)
        manifest = module.run_all(CONFIG_PATH, output)
        require((output / "manifest.json").is_file(), "manifest was not written", failures)
        require(len(manifest["scenarios"]) == 4, "manifest scenario count mismatch", failures)
        for item in manifest["scenarios"]:
            require((output / item["csv"]).is_file(), f"missing CSV {item['csv']}", failures)
            summary_path = output / item["summary"]
            require(summary_path.is_file(), f"missing summary {item['summary']}", failures)
            if summary_path.is_file():
                payload = json.loads(summary_path.read_text(encoding="utf-8"))
                require(payload["synthetic"] is True, f"{item['summary']}: synthetic marker missing", failures)
                require(payload["calibrated"] is False, f"{item['summary']}: calibrated marker invalid", failures)

    if failures:
        print("GCAT capacity simulation validation: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("GCAT capacity simulation validation: PASS")
    for scenario_id in sorted(summaries):
        summary = summaries[scenario_id]
        print(
            f"- {scenario_id}: max_omega={float(summary['maximum_omega']):.6f}, "
            f"first_overload_time={summary['first_overload_time']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
