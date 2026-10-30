import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))

from landed_cost import calculate_route, compare  # noqa: E402

BASE = {"quantity": 100, "unit_cost": 10, "sale_price_per_unit": 20}


class CalculateRouteTest(unittest.TestCase):
    def test_cif_duty_and_vat(self):
        r = calculate_route(BASE, {
            "freight": 100, "insurance": 10, "duty_rate": 0.10,
            "vat_rate": 0.20, "vat_recoverable": False,
        })
        self.assertAlmostEqual(r["cif_value"], 1110)
        self.assertAlmostEqual(r["duty"], 111)
        self.assertAlmostEqual(r["vat"], (1110 + 111) * 0.20)
        self.assertAlmostEqual(r["landed_cost"], 1110 + 111 + 244.2)
        self.assertAlmostEqual(r["gross_profit"], 2000 - r["landed_cost"])

    def test_fob_basis_excludes_freight_from_duty_but_not_cost(self):
        r = calculate_route(BASE, {"freight": 200, "duty_rate": 0.10, "duty_basis": "FOB"})
        self.assertAlmostEqual(r["duty"], 100)
        self.assertAlmostEqual(r["landed_cost"], 1000 + 200 + 100)

    def test_recoverable_vat_not_in_cost(self):
        r = calculate_route(BASE, {"vat_rate": 0.20})
        self.assertAlmostEqual(r["vat"], 200)
        self.assertAlmostEqual(r["landed_cost"], 1000)

    def test_specific_duty_fees_and_financing(self):
        r = calculate_route({**BASE, "financing_rate_annual": 0.365}, {
            "duty_per_unit": 0.5, "origin_charges": [{"amount": 50}],
            "destination_charges": 25, "transit_days": 10,
        })
        self.assertAlmostEqual(r["duty"], 50)
        self.assertAlmostEqual(r["landed_cost"], 1050 + 50 + 25)
        self.assertAlmostEqual(r["financing_cost"], 1125 * 0.01)

    def test_insurance_rate_on_cif_plus_ten_percent(self):
        r = calculate_route(BASE, {"freight": 100, "insurance_rate": 0.01})
        self.assertAlmostEqual(r["insurance"], 1100 * 1.1 * 0.01)

    def test_route_overrides_sale_price(self):
        r = calculate_route(BASE, {"sale_price_per_unit": 30})
        self.assertAlmostEqual(r["revenue"], 3000)

    def test_bad_duty_basis(self):
        with self.assertRaises(ValueError):
            calculate_route(BASE, {"duty_basis": "EXW"})


class CompareTest(unittest.TestCase):
    def test_ranks_by_profit(self):
        results = compare({**BASE, "routes": [
            {"name": "expensive", "freight": 500},
            {"name": "cheap", "freight": 100},
        ]})
        self.assertEqual([r["name"] for r in results], ["cheap", "expensive"])
        self.assertEqual(results[0]["rank"], 1)


if __name__ == "__main__":
    unittest.main()
