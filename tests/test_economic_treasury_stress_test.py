import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import economic_treasury_stress_test as st  # noqa: E402

REF = "https://example.org/source"


def i(value, **extra):
    item = {"value": value, "source_ref": REF, "attribution": "test fixture", "synthetic": True}
    item.update(extra)
    return item


def scenario(**overrides):
    value = {
        "id": "base",
        "downturn": {"price_drop_per_period": i("0.1")},
        "selling_pressure": {"sold_share_per_period": i(0), "price_impact_per_unit_sold": i(0)},
        "redemption": {"redemption_rate_per_period": i("0.1")},
        "rewards": {"rewards_per_period": i(5)},
        "service_continuity": {"operating_cost_per_period": i(10), "minimum_runway_periods": i(6)},
    }
    value.update(overrides)
    return value


def document(**overrides):
    value = {
        "schema": st.SCHEMA, "benchmark_id": "S5_STRESS", "fixture": True, "periods": 1,
        "treasury": {"treasury_value": i(1000), "volatile_share": i("0.5"), "redeemable_claims": i(100),
                     "revenue_per_period": i(20), "coverage_floor": i(1)},
        "scenarios": [scenario()],
    }
    value.update(overrides)
    return value


class TreasuryStressTests(unittest.TestCase):
    def test_hand_computed_period(self):
        result = st.evaluate(document())
        row = result["scenarios"][0]["trajectory"][0]
        # 1000 - 1000*0.5*0.1 = 950; redeem 10 of 100; 950 + 20 - 10 - 5 - 10 = 945
        self.assertEqual((row["treasury"], row["redeemable_claims"]), ("945", "90"))
        self.assertEqual((row["coverage"], row["runway_periods"]), ("10.5", "94.5"))
        self.assertEqual(result["disposition"], "ALLOW")
        self.assertNotIn("failure_code", result)

    def test_each_predicate_fails_with_first_failing_period(self):
        cases = {
            "solvency": scenario(rewards={"rewards_per_period": i(2000)}),
            "coverage": scenario(downturn={"price_drop_per_period": i(1)}),
            "service_continuity": scenario(service_continuity={"operating_cost_per_period": i(10),
                                                               "minimum_runway_periods": i(100)}),
        }
        for predicate, sc in cases.items():
            with self.subTest(predicate=predicate):
                doc = document(scenarios=[sc], periods=3)
                if predicate == "coverage":
                    doc["treasury"]["coverage_floor"] = i(20)
                out = st.evaluate(doc)
                self.assertEqual(out["disposition"], "DENY")
                # WU-B review defect 2: a failing run is a standard non-ALLOW record with the six fields.
                self.assertEqual((out["failed_predicate"], out["failure_code"], out["evidence"]["first_failing_period"]),
                                 (predicate, f"S5_STRESS_{predicate.upper()}_NOT_MET", 1))
                for field in ("required_evidence_or_repair", "retry_entrypoint", "owning_existing_goal", "next_attempt"):
                    self.assertTrue(out[field], field)
                failures = {f["failed_predicate"]: f["first_failing_period"] for f in out["scenarios"][0]["failures"]}
                self.assertIn(predicate, failures)
                self.assertEqual(failures[predicate], 1)

    def test_values_render_exactly(self):
        # Lane B review nit 5: no float rounding.
        F = st.Fraction
        self.assertEqual([st._number(F(1, 3)), st._number(F(21, 2)), st._number(F(-1, 8)), st._number(F(7))],
                         ["1/3", "10.5", "-0.125", "7"])

    def test_result_never_grants_completion(self):
        out = st.evaluate(document())
        self.assertEqual((out["benchmark_completion_granted"], out["realism_owner_accepted"], out["authority_effect"],
                          out["evidence_class"]), (False, False, "NONE", "FIXTURE_NOT_EVIDENCE"))  # the test file is a fixture

    def test_deterministic_rendering(self):
        self.assertEqual(st.render(st.evaluate(document(periods=12))), st.render(st.evaluate(document(periods=12))))

    def test_missing_dimension_refused(self):
        for dimension in st.DIMENSIONS:
            with self.subTest(dimension=dimension):
                sc = scenario()
                sc.pop(dimension)
                with self.assertRaises(st.Refused) as raised:
                    st.evaluate(document(scenarios=[sc]))
                self.assertEqual(raised.exception.result["failure_code"], "REQUIRED_STRESS_DIMENSION_MISSING")

    def test_unattributable_and_out_of_range_inputs_refused(self):
        cases = [
            ("STRESS_INPUT_NOT_ATTRIBUTABLE", {"source_ref": "file:///etc/passwd"}),
            ("STRESS_INPUT_NOT_ATTRIBUTABLE", {"attribution": " "}),
            ("STRESS_INPUT_OUT_OF_RANGE", {"value": "1.5"}),
            ("STRESS_INPUT_OUT_OF_RANGE", {"value": 0.25}),
            ("STRESS_INPUT_OUT_OF_RANGE", {"value": True}),
        ]
        for code, change in cases:
            with self.subTest(code=code, change=change):
                doc = document()
                doc["treasury"]["volatile_share"] = {**doc["treasury"]["volatile_share"], **change}
                with self.assertRaises(st.Refused) as raised:
                    st.evaluate(doc)
                self.assertEqual(raised.exception.result["failure_code"], code)
                self.assertEqual(set(raised.exception.result) >= {"failure_code", "failed_predicate", "required_evidence_or_repair",
                                                                  "retry_entrypoint", "owning_existing_goal", "next_attempt"}, True)

    def test_synthetic_inputs_refused_outside_a_fixture(self):
        with self.assertRaises(st.Refused) as raised:
            st.evaluate(document(fixture=False))
        self.assertEqual(raised.exception.result["failure_code"], "STRESS_INPUT_SYNTHETIC")

    def test_identity_and_schema_refusals(self):
        for doc, code in ((document(schema="x/v1"), "STRESS_SCHEMA_MISMATCH"),
                          (document(benchmark_id="S4_COST"), "STRESS_BENCHMARK_IDENTITY"),
                          (document(periods=0), "STRESS_INPUT_OUT_OF_RANGE"),
                          (document(scenarios=[]), "STRESS_SCENARIOS_MISSING"),
                          (document(scenarios=[scenario(), scenario()]), "STRESS_SCENARIO_IDENTITY")):
            with self.subTest(code=code):
                with self.assertRaises(st.Refused) as raised:
                    st.evaluate(doc)
                self.assertEqual(raised.exception.result["failure_code"], code)

    def test_input_not_mutated(self):
        doc = document()
        snapshot = copy.deepcopy(doc)
        st.evaluate(doc)
        self.assertEqual(doc, snapshot)

    def test_cli_exit_codes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "s.json"
            for doc, code in ((document(), 0), (document(scenarios=[scenario(rewards={"rewards_per_period": i(2000)})]), 2),
                              (document(schema="x/v1"), 1)):
                path.write_text(json.dumps(doc), encoding="utf-8")
                done = subprocess.run([sys.executable, str(ROOT / "tools/economic_treasury_stress_test.py"), str(path)],
                                      capture_output=True, text=True)
                self.assertEqual(done.returncode, code, done.stdout)


if __name__ == "__main__":
    unittest.main()
