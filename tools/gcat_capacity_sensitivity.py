#!/usr/bin/env python3
"""Generate synthetic GCAT parameter sweeps, model comparisons, and SVG figures.

This tool uses only the Python standard library. All outputs are synthetic and
uncalibrated. The generated regime map visualizes modeled overload; it does not
establish empirical drift or causal validity.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Mapping, Sequence, Tuple


NumberMap = Mapping[str, float]


def linspace(start: float, stop: float, count: int) -> List[float]:
    if count < 2:
        raise ValueError("count must be >= 2")
    step = (stop - start) / (count - 1)
    return [start + index * step for index in range(count)]


def normalize_weights(alpha: float, beta: float, gamma: float) -> Tuple[float, float, float]:
    total = alpha + beta + gamma
    if total <= 0:
        raise ValueError("elasticity total must be > 0")
    return alpha / total, beta / total, gamma / total


def capacity_cobb_douglas(values: NumberMap, baseline: NumberMap, alternative: Mapping[str, object]) -> float:
    del alternative
    return (
        values["K"]
        * values["g"] ** values["alpha"]
        * values["c"] ** values["beta"]
        * values["t"] ** values["gamma"]
    )


def capacity_weighted_geometric(values: NumberMap, baseline: NumberMap, alternative: Mapping[str, object]) -> float:
    del baseline, alternative
    wa, wb, wg = normalize_weights(values["alpha"], values["beta"], values["gamma"])
    return values["K"] * values["g"] ** wa * values["c"] ** wb * values["t"] ** wg


def capacity_weighted_additive(values: NumberMap, baseline: NumberMap, alternative: Mapping[str, object]) -> float:
    del baseline, alternative
    wa, wb, wg = normalize_weights(values["alpha"], values["beta"], values["gamma"])
    return values["K"] * (wa * values["g"] + wb * values["c"] + wg * values["t"])


def capacity_bottleneck(values: NumberMap, baseline: NumberMap, alternative: Mapping[str, object]) -> float:
    del alternative
    normalized = (
        values["g"] / baseline["g"],
        values["c"] / baseline["c"],
        values["t"] / baseline["t"],
    )
    return values["K"] * min(normalized)


def capacity_ces(values: NumberMap, baseline: NumberMap, alternative: Mapping[str, object]) -> float:
    del baseline
    rho = float(alternative.get("rho", -0.5))
    if abs(rho) < 1e-12:
        return capacity_weighted_geometric(values, values, alternative)
    wa, wb, wg = normalize_weights(values["alpha"], values["beta"], values["gamma"])
    inner = wa * values["g"] ** rho + wb * values["c"] ** rho + wg * values["t"] ** rho
    if inner <= 0:
        raise ValueError("CES inner term must be > 0")
    return values["K"] * inner ** (1.0 / rho)


FUNCTIONS: Dict[str, Callable[[NumberMap, NumberMap, Mapping[str, object]], float]] = {
    "cobb_douglas": capacity_cobb_douglas,
    "weighted_geometric": capacity_weighted_geometric,
    "weighted_additive": capacity_weighted_additive,
    "bottleneck_minimum": capacity_bottleneck,
    "ces": capacity_ces,
}


def canonical_digest(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_spec(path: Path) -> Dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != "1.0.0":
        raise ValueError("unsupported schema_version")
    if payload.get("synthetic") is not True or payload.get("calibrated") is not False:
        raise ValueError("specification must declare synthetic=true and calibrated=false")
    baseline = payload["baseline"]
    for name in ("K", "alpha", "beta", "gamma", "g", "c", "t"):
        if float(baseline[name]) <= 0:  # type: ignore[index]
            raise ValueError(f"baseline {name} must be > 0")
    alternatives = payload["alternative_functions"]
    unknown = set(alternatives) - set(FUNCTIONS)  # type: ignore[arg-type]
    if unknown:
        raise ValueError(f"unsupported alternative functions: {sorted(unknown)}")
    return payload


def range_from_spec(raw: Mapping[str, object]) -> List[float]:
    return linspace(float(raw["start"]), float(raw["stop"]), int(raw["count"]))


def write_csv(path: Path, fieldnames: Sequence[str], rows: Iterable[Mapping[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def regime_rows(spec: Mapping[str, object]) -> List[Dict[str, object]]:
    baseline = {name: float(value) for name, value in spec["baseline"].items()}  # type: ignore[union-attr]
    sweep = spec["sweeps"]  # type: ignore[assignment]
    governance_values = range_from_spec(sweep["governance_values"])
    pressure_values = range_from_spec(sweep["pressure_values"])
    rows: List[Dict[str, object]] = []
    for pressure in pressure_values:
        for governance in governance_values:
            values = dict(baseline)
            values["g"] = governance
            capacity = capacity_cobb_douglas(values, baseline, {})
            load = pressure / capacity
            rows.append(
                {
                    "governance": governance,
                    "pressure": pressure,
                    "effective_capacity": capacity,
                    "omega": load,
                    "margin": -math.log(load),
                    "region": "governable" if load <= 1.0 else "overload",
                    "synthetic": True,
                    "calibrated": False,
                }
            )
    return rows


def elasticity_rows(spec: Mapping[str, object]) -> List[Dict[str, object]]:
    baseline = {name: float(value) for name, value in spec["baseline"].items()}  # type: ignore[union-attr]
    sweep = spec["sweeps"]  # type: ignore[assignment]
    elasticity_values = range_from_spec(sweep["elasticity_values"])
    rows: List[Dict[str, object]] = []
    test_states = [
        {"state_id": "governance_limited", "g": 0.65, "c": 1.4, "t": 1.2, "a": 1.0},
        {"state_id": "constraint_limited", "g": 1.4, "c": 0.65, "t": 1.2, "a": 1.0},
        {"state_id": "continuity_limited", "g": 1.4, "c": 1.2, "t": 0.65, "a": 1.0},
    ]
    for test_state in test_states:
        for elasticity in elasticity_values:
            values = dict(baseline)
            values.update({name: float(test_state[name]) for name in ("g", "c", "t")})
            values["alpha"] = elasticity
            capacity = capacity_cobb_douglas(values, baseline, {})
            rows.append(
                {
                    "state_id": test_state["state_id"],
                    "alpha": elasticity,
                    "beta": values["beta"],
                    "gamma": values["gamma"],
                    "capacity": capacity,
                    "omega": float(test_state["a"]) / capacity,
                    "synthetic": True,
                    "calibrated": False,
                }
            )
    return rows


def model_comparison_rows(spec: Mapping[str, object]) -> List[Dict[str, object]]:
    baseline = {name: float(value) for name, value in spec["baseline"].items()}  # type: ignore[union-attr]
    alternatives = spec["alternative_functions"]  # type: ignore[assignment]
    states = [
        {"state_id": "balanced", "g": 1.2, "c": 1.2, "t": 1.2, "a": 1.0},
        {"state_id": "governance_bottleneck", "g": 0.55, "c": 1.8, "t": 1.5, "a": 1.0},
        {"state_id": "constraint_bottleneck", "g": 1.8, "c": 0.55, "t": 1.5, "a": 1.0},
        {"state_id": "continuity_bottleneck", "g": 1.8, "c": 1.5, "t": 0.55, "a": 1.0},
        {"state_id": "high_scale", "g": 2.2, "c": 1.7, "t": 1.4, "a": 2.0},
    ]
    rows: List[Dict[str, object]] = []
    for state in states:
        values = dict(baseline)
        values.update({name: float(state[name]) for name in ("g", "c", "t")})
        for function_name, function_spec in alternatives.items():
            capacity = FUNCTIONS[function_name](values, baseline, function_spec)
            load = float(state["a"]) / capacity
            rows.append(
                {
                    "state_id": state["state_id"],
                    "function": function_name,
                    "capacity": capacity,
                    "omega": load,
                    "region": "governable" if load <= 1.0 else "overload",
                    "synthetic": True,
                    "calibrated": False,
                }
            )
    return rows


def xml_escape(text: object) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def svg_regime_map(spec: Mapping[str, object], rows: Sequence[Mapping[str, object]]) -> str:
    figure = spec["figure"]  # type: ignore[assignment]
    width = int(figure["width"])
    height = int(figure["height"])
    margin_left, margin_right, margin_top, margin_bottom = 90, 45, 100, 85
    plot_width = width - margin_left - margin_right
    plot_height = height - margin_top - margin_bottom

    governance_values = sorted({float(row["governance"]) for row in rows})
    pressure_values = sorted({float(row["pressure"]) for row in rows})
    min_g, max_g = governance_values[0], governance_values[-1]
    min_a, max_a = pressure_values[0], pressure_values[-1]
    cell_w = plot_width / len(governance_values)
    cell_h = plot_height / len(pressure_values)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:Arial,Helvetica,sans-serif;fill:#111827}.title{font-size:24px;font-weight:700}.subtitle{font-size:14px}.axis{font-size:15px;font-weight:600}.tick{font-size:12px}.label{font-size:14px;font-weight:700}</style>',
        f'<text x="{width/2}" y="38" text-anchor="middle" class="title">{xml_escape(figure["title"])}</text>',
        f'<text x="{width/2}" y="64" text-anchor="middle" class="subtitle">{xml_escape(figure["subtitle"])}</text>',
    ]

    for row in rows:
        governance = float(row["governance"])
        pressure = float(row["pressure"])
        load = float(row["omega"])
        gx = governance_values.index(governance)
        py = pressure_values.index(pressure)
        x = margin_left + gx * cell_w
        y = margin_top + plot_height - (py + 1) * cell_h
        intensity = min(1.0, abs(math.log(max(load, 1e-12))) / 2.5)
        if load <= 1.0:
            channel = int(245 - 80 * intensity)
            fill = f"rgb({channel},{245},{channel})"
        else:
            channel = int(245 - 95 * intensity)
            fill = f"rgb({245},{channel},{channel})"
        parts.append(
            f'<rect x="{x:.3f}" y="{y:.3f}" width="{cell_w+0.2:.3f}" height="{cell_h+0.2:.3f}" fill="{fill}"/>'
        )

    baseline = {name: float(value) for name, value in spec["baseline"].items()}  # type: ignore[union-attr]
    boundary_points = []
    for governance in governance_values:
        values = dict(baseline)
        values["g"] = governance
        boundary_pressure = capacity_cobb_douglas(values, baseline, {})
        if min_a <= boundary_pressure <= max_a:
            x = margin_left + ((governance - min_g) / (max_g - min_g)) * plot_width
            y = margin_top + plot_height - ((boundary_pressure - min_a) / (max_a - min_a)) * plot_height
            boundary_points.append(f"{x:.2f},{y:.2f}")
    if boundary_points:
        parts.append(
            f'<polyline points="{" ".join(boundary_points)}" fill="none" stroke="#111827" stroke-width="3" stroke-dasharray="8 5"/>'
        )

    parts.extend(
        [
            f'<rect x="{margin_left}" y="{margin_top}" width="{plot_width}" height="{plot_height}" fill="none" stroke="#111827" stroke-width="1.5"/>',
            f'<text x="{margin_left + plot_width/2}" y="{height-28}" text-anchor="middle" class="axis">Governance capacity input g</text>',
            f'<text x="24" y="{margin_top + plot_height/2}" text-anchor="middle" class="axis" transform="rotate(-90 24 {margin_top + plot_height/2})">Execution pressure a</text>',
            f'<text x="{margin_left + plot_width*0.23}" y="{margin_top + plot_height*0.82}" text-anchor="middle" class="label">Governable</text>',
            f'<text x="{margin_left + plot_width*0.70}" y="{margin_top + plot_height*0.22}" text-anchor="middle" class="label">Modeled overload</text>',
            f'<text x="{margin_left + plot_width*0.66}" y="{margin_top + plot_height*0.55}" text-anchor="middle" class="tick">Dashed line: Omega = 1</text>',
        ]
    )

    for fraction in (0.0, 0.25, 0.5, 0.75, 1.0):
        x = margin_left + fraction * plot_width
        value = min_g + fraction * (max_g - min_g)
        parts.append(f'<line x1="{x}" y1="{margin_top+plot_height}" x2="{x}" y2="{margin_top+plot_height+7}" stroke="#111827"/>')
        parts.append(f'<text x="{x}" y="{margin_top+plot_height+25}" text-anchor="middle" class="tick">{value:.2f}</text>')
        y = margin_top + plot_height - fraction * plot_height
        pressure = min_a + fraction * (max_a - min_a)
        parts.append(f'<line x1="{margin_left-7}" y1="{y}" x2="{margin_left}" y2="{y}" stroke="#111827"/>')
        parts.append(f'<text x="{margin_left-12}" y="{y+4}" text-anchor="end" class="tick">{pressure:.2f}</text>')

    parts.append(
        f'<text x="{width/2}" y="{height-6}" text-anchor="middle" class="tick">Synthetic, uncalibrated visualization. Overload is not automatic proof of drift.</text>'
    )
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def summary_payload(
    spec: Mapping[str, object],
    regime: Sequence[Mapping[str, object]],
    elasticity: Sequence[Mapping[str, object]],
    comparison: Sequence[Mapping[str, object]],
) -> Dict[str, object]:
    overload_count = sum(1 for row in regime if row["region"] == "overload")
    function_ranges: Dict[str, Dict[str, float]] = {}
    for function_name in FUNCTIONS:
        loads = [float(row["omega"]) for row in comparison if row["function"] == function_name]
        function_ranges[function_name] = {"minimum_omega": min(loads), "maximum_omega": max(loads)}
    return {
        "schema_version": "1.0.0",
        "artifact_type": "synthetic-gcat-capacity-sensitivity-summary",
        "synthetic": True,
        "calibrated": False,
        "regime_grid": {
            "row_count": len(regime),
            "overload_count": overload_count,
            "governable_count": len(regime) - overload_count,
            "minimum_omega": min(float(row["omega"]) for row in regime),
            "maximum_omega": max(float(row["omega"]) for row in regime),
        },
        "elasticity_row_count": len(elasticity),
        "model_comparison_row_count": len(comparison),
        "alternative_function_ranges": function_ranges,
        "specification_sha256": canonical_digest(spec),
        "claim_boundary": "Sensitivity outputs compare assumptions; they do not establish empirical validity or prove drift.",
    }


def generate(spec_path: Path, output_dir: Path) -> Dict[str, object]:
    spec = load_spec(spec_path)
    regime = regime_rows(spec)
    elasticity = elasticity_rows(spec)
    comparison = model_comparison_rows(spec)
    output_dir.mkdir(parents=True, exist_ok=True)

    write_csv(
        output_dir / "regime_grid.csv",
        ("governance", "pressure", "effective_capacity", "omega", "margin", "region", "synthetic", "calibrated"),
        regime,
    )
    write_csv(
        output_dir / "elasticity_sweep.csv",
        ("state_id", "alpha", "beta", "gamma", "capacity", "omega", "synthetic", "calibrated"),
        elasticity,
    )
    write_csv(
        output_dir / "production_function_comparison.csv",
        ("state_id", "function", "capacity", "omega", "region", "synthetic", "calibrated"),
        comparison,
    )
    svg_path = output_dir / "gcat_regime_map.svg"
    svg_path.write_text(svg_regime_map(spec, regime), encoding="utf-8")

    summary = summary_payload(spec, regime, elasticity, comparison)
    summary["outputs"] = {
        "regime_grid": "regime_grid.csv",
        "elasticity_sweep": "elasticity_sweep.csv",
        "production_function_comparison": "production_function_comparison.csv",
        "regime_map_svg": "gcat_regime_map.svg",
    }
    write_json(output_dir / "sensitivity_summary.json", summary)
    manifest = {
        "schema_version": "1.0.0",
        "artifact_type": "synthetic-gcat-capacity-sensitivity-manifest",
        "synthetic": True,
        "calibrated": False,
        "source_spec": str(spec_path),
        "files": [
            {"path": name, "sha256": hashlib.sha256((output_dir / name).read_bytes()).hexdigest()}
            for name in (
                "regime_grid.csv",
                "elasticity_sweep.csv",
                "production_function_comparison.csv",
                "gcat_regime_map.svg",
                "sensitivity_summary.json",
            )
        ],
    }
    write_json(output_dir / "manifest.json", manifest)
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--spec",
        type=Path,
        default=Path("data/gcat_capacity_sensitivity.json"),
        help="Sensitivity-study specification.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("generated/gcat-capacity-sensitivity"),
        help="Destination directory for CSV, JSON, and SVG outputs.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = generate(args.spec, args.output_dir)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
