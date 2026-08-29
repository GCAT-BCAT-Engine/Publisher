#!/usr/bin/env python3
"""Validate GCAT time-series SVG generation and provenance."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = ROOT / "tools" / "gcat_capacity_timeseries.py"
CONFIG_PATH = ROOT / "data" / "gcat_capacity_scenarios.json"


def load_module():
    spec = importlib.util.spec_from_file_location("gcat_capacity_timeseries", TOOL_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load time-series module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def require(condition: bool, message: str, failures: List[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> int:
    failures: List[str] = []
    module = load_module()
    with tempfile.TemporaryDirectory(prefix="gcat-timeseries-") as temp_dir:
        output = Path(temp_dir)
        manifest = module.run(CONFIG_PATH, output)
        require(manifest["synthetic"] is True, "manifest synthetic marker missing", failures)
        require(manifest["calibrated"] is False, "manifest calibrated marker invalid", failures)
        require(len(manifest["figures"]) == 4, "expected four scenario figures", failures)
        expected = {
            "balanced_adaptation",
            "delayed_intervention",
            "constraint_heavy_fragility",
            "bounded_recovery_failure",
        }
        observed = {item["scenario_id"] for item in manifest["figures"]}
        require(observed == expected, "scenario figure set mismatch", failures)
        manifest_path = output / "manifest.json"
        require(manifest_path.is_file(), "manifest.json not written", failures)
        if manifest_path.is_file():
            stored = json.loads(manifest_path.read_text(encoding="utf-8"))
            require(stored == manifest, "stored manifest differs from returned manifest", failures)

        for item in manifest["figures"]:
            figure_path = output / item["figure"]
            require(figure_path.is_file(), f"missing figure {item['figure']}", failures)
            require(len(item["figure_sha256"]) == 64, f"invalid digest for {item['figure']}", failures)
            require(float(item["maximum_omega"]) > 0, f"invalid peak Omega for {item['scenario_id']}", failures)
            if not figure_path.is_file():
                continue
            text = figure_path.read_text(encoding="utf-8")
            require(text.startswith("<svg"), f"{item['figure']} is not SVG", failures)
            require("Synthetic and uncalibrated" in text, f"{item['figure']} missing synthetic warning", failures)
            require("not automatic proof of drift" in text, f"{item['figure']} missing claim boundary", failures)
            require("Omega = 1 frontier" in text, f"{item['figure']} missing frontier label", failures)
            require("Effective governance capacity" in text, f"{item['figure']} missing capacity legend", failures)
            require("Execution pressure" in text, f"{item['figure']} missing pressure legend", failures)
            require("Governance load ratio" in text, f"{item['figure']} missing load axis", failures)
            require(module.digest_text(text) == item["figure_sha256"], f"digest mismatch for {item['figure']}", failures)

        summary = {item["scenario_id"]: item for item in manifest["figures"]}
        require(
            summary["balanced_adaptation"]["first_overload_time"] is None,
            "balanced scenario should remain below overload frontier",
            failures,
        )
        require(
            summary["bounded_recovery_failure"]["first_overload_time"] is not None,
            "bounded recovery scenario should cross overload frontier",
            failures,
        )

    if failures:
        print("GCAT time-series figure validation: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("GCAT time-series figure validation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
