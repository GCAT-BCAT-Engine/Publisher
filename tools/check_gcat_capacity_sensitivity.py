#!/usr/bin/env python3
"""Validate GCAT sensitivity studies and publication SVG generation."""

from __future__ import annotations

import importlib.util
import json
import math
import sys
import tempfile
from pathlib import Path
from typing import List, Mapping

ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = ROOT / "tools" / "gcat_capacity_sensitivity.py"
SPEC_PATH = ROOT / "data" / "gcat_capacity_sensitivity.json"


def load_module():
    spec = importlib.util.spec_from_file_location("gcat_capacity_sensitivity", TOOL_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load sensitivity module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def require(condition: bool, message: str, failures: List[str]) -> None:
    if not condition:
        failures.append(message)


def finite_positive(value: object) -> bool:
    number = float(value)
    return math.isfinite(number) and number > 0


def main() -> int:
    failures: List[str] = []
    module = load_module()
    spec = module.load_spec(SPEC_PATH)

    regime = module.regime_rows(spec)
    elasticity = module.elasticity_rows(spec)
    comparison = module.model_comparison_rows(spec)

    governance_count = int(spec["sweeps"]["governance_values"]["count"])
    pressure_count = int(spec["sweeps"]["pressure_values"]["count"])
    elasticity_count = int(spec["sweeps"]["elasticity_values"]["count"])
    function_count = len(spec["alternative_functions"])

    require(len(regime) == governance_count * pressure_count, "regime grid size mismatch", failures)
    require(len(elasticity) == elasticity_count * 3, "elasticity sweep size mismatch", failures)
    require(len(comparison) == function_count * 5, "model comparison size mismatch", failures)

    overload_count = 0
    governable_count = 0
    for index, row in enumerate(regime):
        for name in ("governance", "pressure", "effective_capacity", "omega"):
            require(finite_positive(row[name]), f"regime[{index}] {name} must be finite and positive", failures)
        require(math.isfinite(float(row["margin"])), f"regime[{index}] margin must be finite", failures)
        expected_margin = -math.log(float(row["omega"]))
        require(abs(float(row["margin"]) - expected_margin) < 1e-10, f"regime[{index}] margin identity failed", failures)
        expected_region = "governable" if float(row["omega"]) <= 1.0 else "overload"
        require(row["region"] == expected_region, f"regime[{index}] region mismatch", failures)
        require(row["synthetic"] is True, f"regime[{index}] synthetic marker missing", failures)
        require(row["calibrated"] is False, f"regime[{index}] calibration marker invalid", failures)
        if row["region"] == "overload":
            overload_count += 1
        else:
            governable_count += 1

    require(overload_count > 0, "regime grid must include overload states", failures)
    require(governable_count > 0, "regime grid must include governable states", failures)

    for index, row in enumerate(elasticity):
        for name in ("alpha", "beta", "gamma", "capacity", "omega"):
            require(finite_positive(row[name]), f"elasticity[{index}] {name} must be finite and positive", failures)
        require(row["synthetic"] is True, f"elasticity[{index}] synthetic marker missing", failures)
        require(row["calibrated"] is False, f"elasticity[{index}] calibration marker invalid", failures)

    functions = {row["function"] for row in comparison}
    require(functions == set(module.FUNCTIONS), "alternative function coverage mismatch", failures)
    for index, row in enumerate(comparison):
        require(finite_positive(row["capacity"]), f"comparison[{index}] capacity must be finite and positive", failures)
        require(finite_positive(row["omega"]), f"comparison[{index}] omega must be finite and positive", failures)
        require(row["synthetic"] is True, f"comparison[{index}] synthetic marker missing", failures)
        require(row["calibrated"] is False, f"comparison[{index}] calibration marker invalid", failures)

    bottleneck_rows = [row for row in comparison if row["function"] == "bottleneck_minimum"]
    cobb_rows = {row["state_id"]: row for row in comparison if row["function"] == "cobb_douglas"}
    require(len(bottleneck_rows) == 5, "bottleneck comparator row count mismatch", failures)
    for row in bottleneck_rows:
        if "bottleneck" in str(row["state_id"]):
            require(
                float(row["omega"]) >= float(cobb_rows[row["state_id"]]["omega"]),
                f"{row['state_id']}: bottleneck model should not show lower load than Cobb-Douglas",
                failures,
            )

    svg = module.svg_regime_map(spec, regime)
    require(svg.startswith("<svg"), "SVG must begin with an svg element", failures)
    require("Omega = 1" in svg, "SVG boundary label missing", failures)
    require("Synthetic, uncalibrated" in svg, "SVG provenance label missing", failures)
    require(svg.strip().endswith("</svg>"), "SVG closing element missing", failures)

    with tempfile.TemporaryDirectory(prefix="gcat-sensitivity-") as temp_dir:
        output = Path(temp_dir)
        manifest = module.generate(SPEC_PATH, output)
        expected_files = {
            "regime_grid.csv",
            "elasticity_sweep.csv",
            "production_function_comparison.csv",
            "gcat_regime_map.svg",
            "sensitivity_summary.json",
            "manifest.json",
        }
        require({path.name for path in output.iterdir()} == expected_files, "generated file set mismatch", failures)
        require(manifest["synthetic"] is True, "manifest synthetic marker missing", failures)
        require(manifest["calibrated"] is False, "manifest calibration marker invalid", failures)
        summary = json.loads((output / "sensitivity_summary.json").read_text(encoding="utf-8"))
        require(summary["regime_grid"]["overload_count"] == overload_count, "summary overload count mismatch", failures)
        require(summary["regime_grid"]["governable_count"] == governable_count, "summary governable count mismatch", failures)
        for item in manifest["files"]:
            file_path = output / item["path"]
            require(file_path.is_file(), f"manifest path missing: {item['path']}", failures)
            require(len(item["sha256"]) == 64, f"invalid digest length: {item['path']}", failures)

    if failures:
        print("GCAT capacity sensitivity validation: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    summary = module.summary_payload(spec, regime, elasticity, comparison)
    print("GCAT capacity sensitivity validation: PASS")
    print(f"- regime rows: {len(regime)}")
    print(f"- governable states: {governable_count}")
    print(f"- overload states: {overload_count}")
    print(f"- elasticity rows: {len(elasticity)}")
    print(f"- comparison rows: {len(comparison)}")
    print(f"- minimum omega: {summary['regime_grid']['minimum_omega']:.6f}")
    print(f"- maximum omega: {summary['regime_grid']['maximum_omega']:.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
