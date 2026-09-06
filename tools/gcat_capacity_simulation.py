#!/usr/bin/env python3
"""Reproducible GCAT capacity simulations using only the Python standard library.

The model integrates log-state dynamics so g, c, t, and a remain strictly
positive. Outputs are synthetic research artifacts and must not be represented
as calibrated empirical predictions.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Mapping, MutableMapping, Sequence, Tuple

STATE_NAMES = ("g", "c", "t", "a")


@dataclass(frozen=True)
class ModelParameters:
    K: float
    alpha: float
    beta: float
    gamma: float
    pressure_growth: float
    governance_adaptation: float
    constraint_adaptation: float
    continuity_adaptation: float
    governance_decay: float
    constraint_decay: float
    continuity_decay: float
    control_limit: float
    intervention_delay: float
    target_omega: float

    @classmethod
    def from_mapping(cls, raw: Mapping[str, float]) -> "ModelParameters":
        values = {field: float(raw[field]) for field in cls.__dataclass_fields__}
        params = cls(**values)
        params.validate()
        return params

    def validate(self) -> None:
        positive = ("K", "alpha", "beta", "gamma", "control_limit", "target_omega")
        for name in positive:
            if getattr(self, name) <= 0:
                raise ValueError(f"{name} must be > 0")
        if self.intervention_delay < 0:
            raise ValueError("intervention_delay must be >= 0")


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    description: str
    duration: float
    step: float
    initial_state: Mapping[str, float]
    parameters: ModelParameters

    @classmethod
    def from_mapping(cls, raw: Mapping[str, object]) -> "Scenario":
        initial = {name: float(raw["initial_state"][name]) for name in STATE_NAMES}  # type: ignore[index]
        if any(value <= 0 for value in initial.values()):
            raise ValueError("initial state values must be > 0")
        scenario = cls(
            scenario_id=str(raw["scenario_id"]),
            description=str(raw["description"]),
            duration=float(raw["duration"]),
            step=float(raw["step"]),
            initial_state=initial,
            parameters=ModelParameters.from_mapping(raw["parameters"]),  # type: ignore[arg-type]
        )
        if scenario.duration <= 0 or scenario.step <= 0:
            raise ValueError("duration and step must be > 0")
        if scenario.step > scenario.duration:
            raise ValueError("step must not exceed duration")
        return scenario


def effective_capacity(state: Mapping[str, float], p: ModelParameters) -> float:
    return p.K * state["g"] ** p.alpha * state["c"] ** p.beta * state["t"] ** p.gamma


def omega(state: Mapping[str, float], p: ModelParameters) -> float:
    return state["a"] / effective_capacity(state, p)


def margin(state: Mapping[str, float], p: ModelParameters) -> float:
    return -math.log(omega(state, p))


def control_signal(current_omega: float, time_value: float, p: ModelParameters) -> float:
    """Bounded proportional response activated after the declared delay."""
    if time_value < p.intervention_delay:
        return 0.0
    error = max(0.0, current_omega / p.target_omega - 1.0)
    return min(p.control_limit, error)


def log_derivative(time_value: float, y: Sequence[float], p: ModelParameters) -> Tuple[float, ...]:
    state = {name: math.exp(value) for name, value in zip(STATE_NAMES, y)}
    load = omega(state, p)
    intervention = control_signal(load, time_value, p)

    # Proportional rates. Because these are derivatives of logarithms, the
    # reconstructed state remains positive for every finite integration step.
    dlog_g = p.governance_adaptation * intervention - p.governance_decay * load
    dlog_c = p.constraint_adaptation * intervention - p.constraint_decay * load
    dlog_t = p.continuity_adaptation * intervention - p.continuity_decay * load

    # Intervention reduces pressure growth but cannot make pressure negative.
    dlog_a = p.pressure_growth - intervention
    return dlog_g, dlog_c, dlog_t, dlog_a


def rk4_step(
    derivative: Callable[[float, Sequence[float], ModelParameters], Tuple[float, ...]],
    time_value: float,
    y: Sequence[float],
    step: float,
    p: ModelParameters,
) -> Tuple[float, ...]:
    k1 = derivative(time_value, y, p)
    y2 = tuple(value + 0.5 * step * slope for value, slope in zip(y, k1))
    k2 = derivative(time_value + 0.5 * step, y2, p)
    y3 = tuple(value + 0.5 * step * slope for value, slope in zip(y, k2))
    k3 = derivative(time_value + 0.5 * step, y3, p)
    y4 = tuple(value + step * slope for value, slope in zip(y, k3))
    k4 = derivative(time_value + step, y4, p)
    return tuple(
        value + (step / 6.0) * (s1 + 2.0 * s2 + 2.0 * s3 + s4)
        for value, s1, s2, s3, s4 in zip(y, k1, k2, k3, k4)
    )


def simulate(scenario: Scenario) -> List[Dict[str, float]]:
    state_log = tuple(math.log(scenario.initial_state[name]) for name in STATE_NAMES)
    count = int(round(scenario.duration / scenario.step))
    records: List[Dict[str, float]] = []

    for index in range(count + 1):
        time_value = min(index * scenario.step, scenario.duration)
        state = {name: math.exp(value) for name, value in zip(STATE_NAMES, state_log)}
        capacity = effective_capacity(state, scenario.parameters)
        load = omega(state, scenario.parameters)
        records.append(
            {
                "time": time_value,
                **state,
                "effective_capacity": capacity,
                "omega": load,
                "margin": -math.log(load),
                "intervention": control_signal(load, time_value, scenario.parameters),
            }
        )
        if index < count:
            state_log = rk4_step(
                log_derivative,
                time_value,
                state_log,
                scenario.step,
                scenario.parameters,
            )
    return records


def summarize(scenario: Scenario, records: Sequence[Mapping[str, float]]) -> Dict[str, object]:
    crossing = next((record["time"] for record in records if record["omega"] > 1.0), None)
    minimum_margin = min(record["margin"] for record in records)
    maximum_omega = max(record["omega"] for record in records)
    final = records[-1]
    return {
        "schema_version": "1.0.0",
        "artifact_type": "synthetic-gcat-capacity-simulation",
        "scenario_id": scenario.scenario_id,
        "description": scenario.description,
        "synthetic": True,
        "calibrated": False,
        "integrator": "fixed-step-rk4-log-state",
        "duration": scenario.duration,
        "step": scenario.step,
        "sample_count": len(records),
        "first_overload_time": crossing,
        "maximum_omega": maximum_omega,
        "minimum_margin": minimum_margin,
        "final_state": {name: final[name] for name in STATE_NAMES},
        "final_effective_capacity": final["effective_capacity"],
        "final_omega": final["omega"],
        "claim_boundary": "Omega > 1 denotes modeled overload, not automatic proof of drift.",
    }


def canonical_digest(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def write_csv(path: Path, records: Sequence[Mapping[str, float]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "time", "g", "c", "t", "a", "effective_capacity", "omega", "margin", "intervention"
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_scenarios(path: Path) -> List[Scenario]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if raw.get("schema_version") != "1.0.0":
        raise ValueError("unsupported scenario schema_version")
    scenarios = [Scenario.from_mapping(item) for item in raw["scenarios"]]
    ids = [scenario.scenario_id for scenario in scenarios]
    if len(ids) != len(set(ids)):
        raise ValueError("scenario_id values must be unique")
    return scenarios


def run_all(config_path: Path, output_dir: Path) -> Dict[str, object]:
    scenarios = load_scenarios(config_path)
    manifest_entries: List[Dict[str, object]] = []

    for scenario in scenarios:
        records = simulate(scenario)
        summary = summarize(scenario, records)
        summary["scenario_digest_sha256"] = canonical_digest(
            {
                "scenario_id": scenario.scenario_id,
                "description": scenario.description,
                "duration": scenario.duration,
                "step": scenario.step,
                "initial_state": dict(scenario.initial_state),
                "parameters": scenario.parameters.__dict__,
            }
        )
        csv_path = output_dir / f"{scenario.scenario_id}.csv"
        json_path = output_dir / f"{scenario.scenario_id}.summary.json"
        write_csv(csv_path, records)
        write_json(json_path, summary)
        manifest_entries.append(
            {
                "scenario_id": scenario.scenario_id,
                "csv": csv_path.name,
                "summary": json_path.name,
                "summary_sha256": canonical_digest(summary),
            }
        )

    manifest = {
        "schema_version": "1.0.0",
        "artifact_type": "synthetic-gcat-capacity-simulation-manifest",
        "source_config": str(config_path),
        "synthetic": True,
        "calibrated": False,
        "scenarios": manifest_entries,
    }
    write_json(output_dir / "manifest.json", manifest)
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("data/gcat_capacity_scenarios.json"),
        help="Scenario configuration JSON.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("generated/gcat-capacity"),
        help="Destination for generated CSV and JSON artifacts.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    manifest = run_all(args.config, args.output_dir)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
