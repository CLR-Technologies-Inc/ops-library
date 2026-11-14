import csv
import math
import os
import random
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from opex_stats import (capability, constants, control_charts, distributions as d, doe,  # noqa: E402
                        gage_rr, hypothesis, normality, pareto)

DATA = os.path.join(os.path.dirname(__file__), "..", "..", "data")


def read(name):
    with open(os.path.join(DATA, name)) as f:
        return list(csv.DictReader(f))


class Distributions(unittest.TestCase):
    def test_known_values(self):
        self.assertAlmostEqual(d.t_ppf(0.975, 10), 2.228139, places=5)
        self.assertAlmostEqual(d.t_ppf(0.975, 1), 12.706205, places=4)
        self.assertAlmostEqual(d.f_sf(3.0, 2, 10), 1.6 ** -5, places=10)  # closed form for df1 = 2
        self.assertAlmostEqual(d.f_ppf(0.95, 3, 20), 3.098391, places=5)
        self.assertAlmostEqual(d.chi2_sf(3.841459, 1), 0.05, places=6)
        self.assertAlmostEqual(d.chi2_cdf(4.0, 2), 1 - math.exp(-2.0), places=10)
        self.assertAlmostEqual(d.chi2_ppf(0.95, 10), 18.307038, places=5)
        self.assertAlmostEqual(d.t_cdf(0.0, 7), 0.5, places=12)


class Constants(unittest.TestCase):
    PUBLISHED = {  # n: (d2, A2, D3, D4, c4, A3, B3, B4)
        2: (1.128, 1.880, 0, 3.267, 0.7979, 2.659, 0, 3.267),
        5: (2.326, 0.577, 0, 2.114, 0.9400, 1.427, 0, 2.089),
        8: (2.847, 0.373, 0.136, 1.864, 0.9650, 1.099, 0.185, 1.815),
        10: (3.078, 0.308, 0.223, 1.777, 0.9727, 0.975, 0.284, 1.716),
    }

    def test_against_published_tables(self):
        for n, expected in self.PUBLISHED.items():
            f = constants.factors(n)
            got = (f["d2"], f["A2"], f["D3"], f["D4"], f["c4"], f["A3"], f["B3"], f["B4"])
            for g, e in zip(got, expected):
                self.assertAlmostEqual(g, e, delta=0.0011, msg="n=%d" % n)


class SigmaLevels(unittest.TestCase):
    def test_standard_table(self):
        expected = {1: 691462, 2: 308538, 3: 66807, 4: 6210, 5: 233, 6: 3.4}
        for row in capability.sigma_table(range(1, 7)):
            self.assertAlmostEqual(row["dpmo"], expected[row["sigma_level"]],
                                   delta=max(0.6, 0.02 * expected[row["sigma_level"]]))
        self.assertAlmostEqual(capability.sigma_level_from_dpmo(3.4), 6.0, places=2)
        self.assertAlmostEqual(capability.dpmo(17, 1000, 5), 3400.0)
        self.assertAlmostEqual(capability.rolled_throughput_yield([0.98, 0.95, 0.99]), 0.92169)


class Capability(unittest.TestCase):
    def test_indices(self):
        values = [9.9, 10.1, 10.0, 9.95, 10.05, 10.0, 9.98, 10.02]
        r = capability.capability(values, lsl=9.7, usl=10.3, target=10.0)
        s = r["sigma_overall"]
        self.assertAlmostEqual(r["Pp"], 0.6 / (6 * s))
        self.assertAlmostEqual(r["Ppk"], min(10.3 - r["mean"], r["mean"] - 9.7) / (3 * s))
        mr_bar = sum(abs(b - a) for a, b in zip(values, values[1:])) / 7
        self.assertAlmostEqual(r["sigma_within"], mr_bar / constants.d2(2))

    def test_sample_file(self):
        values = [float(r["diameter_mm"]) for r in read("capability.csv")]
        r = capability.capability(values, lsl=9.9, usl=10.1)
        self.assertEqual(r["n"], 100)
        self.assertGreater(r["Cpk"], 0.5)


class ControlCharts(unittest.TestCase):
    def test_imr_limits(self):
        values = [10, 12, 11, 13, 12, 11, 10, 12]
        c = control_charts.imr_chart(values)["individuals"]
        mr_bar = sum(abs(b - a) for a, b in zip(values, values[1:])) / 7
        self.assertAlmostEqual(c["ucl"], sum(values) / 8 + 2.66 * mr_bar, delta=0.01)

    def test_rules(self):
        pts = [0.0] * 5 + [1.0] * 9 + [5.0]
        sig = control_charts.run_rules(pts, 0.5, 3.0, -3.0)
        self.assertIn((14, 1), sig)
        self.assertIn((13, 2), sig)
        trend = control_charts.run_rules([1, 2, 3, 4, 5, 6], 3.5, 10, -10)
        self.assertIn((5, 3), trend)

    def test_xbar_r_detects_shift(self):
        rows = read("subgroups.csv")
        groups = {}
        for r in rows:
            groups.setdefault(int(r["subgroup"]), []).append(float(r["diameter_mm"]))
        c = control_charts.xbar_r_chart([groups[k] for k in sorted(groups)])
        self.assertEqual(len(c["xbar"]["points"]), 25)
        self.assertGreater(c["xbar"]["ucl"], c["xbar"]["cl"])

    def test_attribute_charts(self):
        rows = read("attribute.csv")
        p = control_charts.p_chart([int(r["defective"]) for r in rows],
                                   [int(r["inspected"]) for r in rows])
        self.assertIn(17, [i for i, rule in p["signals"] if rule == 1])
        u = control_charts.u_chart([int(r["defects"]) for r in rows], [int(r["units"]) for r in rows])
        self.assertEqual(len(u["ucl"]), 25)
        c = control_charts.c_chart([4, 6, 5, 3, 7])
        self.assertAlmostEqual(c["ucl"], 5 + 3 * math.sqrt(5))


class GageRR(unittest.TestCase):
    def test_sample_study(self):
        recs = [(int(r["part"]), r["operator"], float(r["measurement"])) for r in read("gage_rr.csv")]
        g = gage_rr.gage_rr_anova(recs, tolerance=4.0)
        comp = {c["source"]: c for c in g["components"]}
        self.assertAlmostEqual(comp["Total Gage R&R"]["variance"],
                               comp["Repeatability"]["variance"] + comp["Reproducibility"]["variance"])
        self.assertAlmostEqual(comp["Total Variation"]["pct_contribution"], 100.0)
        ss = sum(row["ss"] for row in g["anova"][:-1])
        self.assertAlmostEqual(ss, g["anova"][-1]["ss"])
        self.assertGreaterEqual(g["ndc"], 5)

    def test_unbalanced_rejected(self):
        with self.assertRaises(ValueError):
            gage_rr.gage_rr_anova([(1, "A", 1.0), (1, "A", 1.1), (2, "A", 2.0)])


class DOE(unittest.TestCase):
    def test_recovers_coefficients(self):
        runs = doe.full_factorial(["A", "B", "C"], replicates=2)
        rng = random.Random(1)
        y = [50 + 3 * r["A"] - 2 * r["B"] + 1.5 * r["A"] * r["B"] + rng.gauss(0, 0.01) for r in runs]
        m = doe.analyze(runs, y, ["A", "B", "C"])
        coef = {e["term"]: e["coefficient"] for e in m["effects"]}
        self.assertAlmostEqual(coef["A"], 3, places=1)
        self.assertAlmostEqual(coef["B"], -2, places=1)
        self.assertAlmostEqual(coef["A*B"], 1.5, places=1)
        self.assertAlmostEqual(coef["C"], 0, places=1)
        self.assertAlmostEqual(doe.predict(m, {"A": 1, "B": 1, "C": -1}), 52.5, places=1)
        self.assertLess([e for e in m["effects"] if e["term"] == "A"][0]["p"], 0.001)

    def test_fractional_generator(self):
        runs = doe.fractional_factorial(["A", "B", "C"], {"D": "ABC"})
        self.assertEqual(len(runs), 8)
        self.assertTrue(all(r["D"] == r["A"] * r["B"] * r["C"] for r in runs))
        self.assertEqual(doe.decode(1, 150, 200), 200)


class Hypothesis(unittest.TestCase):
    def test_one_sample(self):
        r = hypothesis.one_sample_t([1, 2, 3, 4, 5], 2)
        self.assertAlmostEqual(r["t"], math.sqrt(2), places=6)
        self.assertAlmostEqual(r["p"], 0.230200, places=4)

    def test_welch_equals_pooled_for_equal_n_and_var(self):
        a, b = [1, 2, 3, 4, 5], [2, 3, 4, 5, 6]
        w = hypothesis.two_sample_t(a, b)
        p = hypothesis.two_sample_t(a, b, equal_var=True)
        self.assertAlmostEqual(w["t"], p["t"])
        self.assertAlmostEqual(w["df"], 8.0)

    def test_anova_and_chi_square(self):
        r = hypothesis.one_way_anova([1, 2, 3], [2, 3, 4], [5, 6, 7])
        self.assertAlmostEqual(r["f"], 13.0, places=6)
        self.assertAlmostEqual(r["p"], d.f_sf(13.0, 2, 6))
        c = hypothesis.chi_square_independence([[10, 20], [20, 10]])
        self.assertAlmostEqual(c["chi2"], 20 / 3, places=6)

    def test_regression(self):
        r = hypothesis.linear_regression([1, 2, 3, 4, 5], [2.1, 3.9, 6.2, 7.8, 10.1])
        self.assertAlmostEqual(r["slope"], 1.99, places=2)
        self.assertGreater(r["r_squared"], 0.99)


class Normality(unittest.TestCase):
    def test_normal_vs_skewed(self):
        rng = random.Random(7)
        # On normal data the test should reject about 5% of the time at alpha = 0.05.
        rejections = sum(normality.anderson_darling([rng.gauss(0, 1) for _ in range(50)])["p"] < 0.05
                         for _ in range(1000))
        self.assertTrue(30 <= rejections <= 75, rejections)
        self.assertLess(normality.anderson_darling([rng.expovariate(1) for _ in range(200)])["p"], 0.01)


class Pareto(unittest.TestCase):
    def test_sorting_and_vital_few(self):
        rows = pareto.pareto({r["defect"]: int(r["count"]) for r in read("pareto.csv")})
        self.assertEqual(rows[0]["category"], "Wrong dimension")
        self.assertAlmostEqual(rows[-1]["cumulative_percent"], 100.0)
        self.assertTrue(rows[0]["vital_few"])
        self.assertFalse(rows[-1]["vital_few"])


if __name__ == "__main__":
    unittest.main()
