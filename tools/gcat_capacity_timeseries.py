#!/usr/bin/env python3
"""Generate synthetic GCAT scenario time-series SVG figures.

Uses the committed simulation model and Python standard library only. Every SVG
is marked synthetic and uncalibrated and distinguishes overload from proven
drift.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
from pathlib import Path
from typing import Dict, List, Mapping, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
SIMULATION_PATH = ROOT / "tools" / "gcat_capacity_simulation.py"
DEFAULT_CONFIG = ROOT / "data" / "gcat_capacity_scenarios.json"


def load_simulation_module():
    spec = importlib.util.spec_from_file_location("gcat_capacity_simulation", SIMULATION_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load simulation module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def escape(text: object) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def digest_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def bounds(values: Sequence[float], include: Sequence[float] = ()) -> Tuple[float, float]:
    combined = list(values) + list(include)
    low, high = min(combined), max(combined)
    if math.isclose(low, high):
        padding = max(abs(low) * 0.1, 0.1)
        return low - padding, high + padding
    padding = (high - low) * 0.08
    return low - padding, high + padding


def points(
    records: Sequence[Mapping[str, float]],
    field: str,
    x: float,
    y: float,
    width: float,
    height: float,
    y_bounds: Tuple[float, float],
) -> str:
    t_min, t_max = records[0]["time"], records[-1]["time"]
    y_min, y_max = y_bounds
    coordinates = []
    for record in records:
        px = x + ((record["time"] - t_min) / (t_max - t_min)) * width
        py = y + height - ((record[field] - y_min) / (y_max - y_min)) * height
        coordinates.append(f"{px:.2f},{py:.2f}")
    return " ".join(coordinates)


def axis_elements(
    x: float,
    y: float,
    width: float,
    height: float,
    x_max: float,
    y_bounds: Tuple[float, float],
    y_label: str,
) -> List[str]:
    y_min, y_max = y_bounds
    parts = [
        f'<line x1="{x}" y1="{y+height}" x2="{x+width}" y2="{y+height}" class="axis-line"/>',
        f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y+height}" class="axis-line"/>',
    ]
    for index in range(5):
        fraction = index / 4
        px = x + fraction * width
        value = fraction * x_max
        parts.extend(
            [
                f'<line x1="{px:.2f}" y1="{y+height}" x2="{px:.2f}" y2="{y+height+6}" class="axis-line"/>',
                f'<text x="{px:.2f}" y="{y+height+24}" text-anchor="middle" class="tick">{value:.1f}</text>',
            ]
        )
    for index in range(5):
        fraction = index / 4
        py = y + height - fraction * height
        value = y_min + fraction * (y_max - y_min)
        parts.extend(
            [
                f'<line x1="{x-6}" y1="{py:.2f}" x2="{x}" y2="{py:.2f}" class="axis-line"/>',
                f'<text x="{x-10}" y="{py+4:.2f}" text-anchor="end" class="tick">{value:.2f}</text>',
            ]
        )
    parts.append(f'<text x="{x+width/2}" y="{y+height+50}" text-anchor="middle" class="axis-label">Time</text>')
    parts.append(
        f'<text x="{x-68}" y="{y+height/2}" text-anchor="middle" transform="rotate(-90 {x-68} {y+height/2})" class="axis-label">{escape(y_label)}</text>'
    )
    return parts


def scenario_svg(scenario, records: Sequence[Mapping[str, float]]) -> str:
    width, height = 1200, 820
    left, panel_width, panel_height = 105, 1010, 245
    top_one, top_two = 145, 485

    capacity_values = [record["effective_capacity"] for record in records]
    pressure_values = [record["a"] for record in records]
    capacity_bounds = bounds(capacity_values + pressure_values, include=(0.0,))
    omega_values = [record["omega"] for record in records]
    omega_bounds = bounds(omega_values, include=(1.0,))

    summary_load = max(omega_values)
    crossing = next((record["time"] for record in records if record["omega"] > 1.0), None)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:Arial,Helvetica,sans-serif;fill:#111827}.title{font-size:25px;font-weight:700}.subtitle{font-size:14px}.axis-label{font-size:15px;font-weight:600}.tick{font-size:12px}.legend{font-size:13px}.axis-line{stroke:#374151;stroke-width:1}.grid{stroke:#d1d5db;stroke-width:1;stroke-dasharray:4 5}.capacity{fill:none;stroke:#1f77b4;stroke-width:3}.pressure{fill:none;stroke:#d62728;stroke-width:3}.load{fill:none;stroke:#6a3d9a;stroke-width:3}.threshold{stroke:#111827;stroke-width:2;stroke-dasharray:8 6}.warning{font-size:13px;font-weight:700}</style>',
        f'<text x="{width/2}" y="38" text-anchor="middle" class="title">GCAT scenario: {escape(scenario.scenario_id)}</text>',
        f'<text x="{width/2}" y="65" text-anchor="middle" class="subtitle">{escape(scenario.description)}</text>',
        f'<text x="{width/2}" y="90" text-anchor="middle" class="warning">Synthetic and uncalibrated. Omega &gt; 1 denotes modeled overload, not automatic proof of drift.</text>',
    ]

    for panel_top in (top_one, top_two):
        for index in range(5):
            py = panel_top + index * panel_height / 4
            parts.append(f'<line x1="{left}" y1="{py:.2f}" x2="{left+panel_width}" y2="{py:.2f}" class="grid"/>')

    parts.extend(axis_elements(left, top_one, panel_width, panel_height, records[-1]["time"], capacity_bounds, "Magnitude"))
    parts.extend(axis_elements(left, top_two, panel_width, panel_height, records[-1]["time"], omega_bounds, "Governance load ratio (Omega)"))

    parts.append(
        f'<polyline points="{points(records, "effective_capacity", left, top_one, panel_width, panel_height, capacity_bounds)}" class="capacity"/>'
    )
    parts.append(
        f'<polyline points="{points(records, "a", left, top_one, panel_width, panel_height, capacity_bounds)}" class="pressure"/>'
    )
    parts.append(
        f'<polyline points="{points(records, "omega", left, top_two, panel_width, panel_height, omega_bounds)}" class="load"/>'
    )

    threshold_y = top_two + panel_height - ((1.0 - omega_bounds[0]) / (omega_bounds[1] - omega_bounds[0])) * panel_height
    parts.append(f'<line x1="{left}" y1="{threshold_y:.2f}" x2="{left+panel_width}" y2="{threshold_y:.2f}" class="threshold"/>')
    parts.append(f'<text x="{left+panel_width-5}" y="{threshold_y-8:.2f}" text-anchor="end" class="legend">Omega = 1 frontier</text>')

    parts.extend(
        [
            f'<line x1="{left+10}" y1="{top_one-25}" x2="{left+45}" y2="{top_one-25}" class="capacity"/>',
            f'<text x="{left+55}" y="{top_one-20}" class="legend">Effective governance capacity</text>',
            f'<line x1="{left+300}" y1="{top_one-25}" x2="{left+335}" y2="{top_one-25}" class="pressure"/>',
            f'<text x="{left+345}" y="{top_one-20}" class="legend">Execution pressure</text>',
            f'<text x="{left+panel_width}" y="{height-28}" text-anchor="end" class="subtitle">Peak Omega: {summary_load:.6f}; first overload: {crossing if crossing is not None else "none"}</text>',
            '</svg>',
        ]
    )
    return "\n".join(parts) + "\n"


def run(config_path: Path, output_dir: Path) -> Dict[str, object]:
    module = load_simulation_module()
    scenarios = module.load_scenarios(config_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    entries: List[Dict[str, object]] = []
    for scenario in scenarios:
        records = module.simulate(scenario)
        svg = scenario_svg(scenario, records)
        filename = f"{scenario.scenario_id}.svg"
        (output_dir / filename).write_text(svg, encoding="utf-8")
        summary = module.summarize(scenario, records)
        entries.append(
            {
                "scenario_id": scenario.scenario_id,
                "figure": filename,
                "figure_sha256": digest_text(svg),
                "maximum_omega": summary["maximum_omega"],
                "first_overload_time": summary["first_overload_time"],
            }
        )
    manifest = {
        "schema_version": "1.0.0",
        "artifact_type": "synthetic-gcat-capacity-timeseries-figure-manifest",
        "synthetic": True,
        "calibrated": False,
        "source_config": str(config_path),
        "claim_boundary": "Omega > 1 denotes modeled overload, not automatic proof of drift.",
        "figures": entries,
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=Path("generated/gcat-capacity-timeseries"))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    print(json.dumps(run(args.config, args.output_dir), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
