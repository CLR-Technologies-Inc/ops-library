"""Run every tool on the sample data in ../../data and print the results.

    python examples/run_all.py            # text report
    python examples/run_all.py --plots    # also save PNG charts (needs matplotlib)
"""

import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
DATA = os.path.join(HERE, "..", "..", "data")

from opex_stats import capability, control_charts, doe, gage_rr, hypothesis, normality, pareto  # noqa: E402


def read(name):
    with open(os.path.join(DATA, name)) as f:
        return list(csv.DictReader(f))


def heading(text):
    print("\n" + text + "\n" + "-" * len(text))


def main(make_plots=False):
    # Capability
    values = [float(r["diameter_mm"]) for r in read("capability.csv")]
    heading("Process capability (capability.csv, LSL 9.9, USL 10.1, target 10.0)")
    cap = capability.capability(values, lsl=9.9, usl=10.1, target=10.0)
    for k in ("n", "mean", "sigma_within", "sigma_overall", "Cp", "Cpk", "Cpm", "Pp", "Ppk",
              "observed_ppm", "sigma_level_overall"):
        print("%-20s %.4f" % (k, cap[k]))
    print("%-20s %.1f" % ("expected ppm (overall)", cap["expected_overall"]["ppm_total"]))
    ad = normality.anderson_darling(values)
    print("%-20s A2* = %.3f, p = %.3f" % ("Anderson-Darling", ad["a2_adjusted"], ad["p"]))

    heading("Sigma level table")
    print("sigma  DPMO          yield %       Cpk(ST)  Cpk(LT)")
    for r in capability.sigma_table():
        print("%5d  %-12.3f  %-12.7f  %7.2f  %7.2f" % (r["sigma_level"], r["dpmo"], r["pct_yield"],
                                                      r["cpk_short_term"], r["cpk_long_term"]))

    # Control charts
    heading("I-MR chart (capability.csv)")
    imr = control_charts.imr_chart(values)
    i = imr["individuals"]
    print("I:  CL %.4f  UCL %.4f  LCL %.4f  signals %s" % (i["cl"], i["ucl"], i["lcl"], i["signals"]))
    m = imr["moving_range"]
    print("MR: CL %.4f  UCL %.4f  signals %s" % (m["cl"], m["ucl"], m["signals"]))

    groups = {}
    for r in read("subgroups.csv"):
        groups.setdefault(int(r["subgroup"]), []).append(float(r["diameter_mm"]))
    subgroups = [groups[k] for k in sorted(groups)]
    heading("X-bar / R chart (subgroups.csv, n = 5)")
    xr = control_charts.xbar_r_chart(subgroups)
    for key in ("xbar", "range"):
        c = xr[key]
        print("%-5s CL %.4f  UCL %.4f  LCL %.4f  signals %s" % (key, c["cl"], c["ucl"], c["lcl"],
                                                               c["signals"]))

    att = read("attribute.csv")
    heading("p chart and u chart (attribute.csv)")
    p = control_charts.p_chart([int(r["defective"]) for r in att], [int(r["inspected"]) for r in att])
    print("p: p-bar %.4f  signals %s" % (p["cl"], p["signals"]))
    u = control_charts.u_chart([int(r["defects"]) for r in att], [int(r["units"]) for r in att])
    print("u: u-bar %.4f  signals %s" % (u["cl"], u["signals"]))

    # Gage R&R
    heading("Gauge R&R, ANOVA method (gage_rr.csv, tolerance 4.0)")
    recs = [(int(r["part"]), r["operator"], float(r["measurement"])) for r in read("gage_rr.csv")]
    g = gage_rr.gage_rr_anova(recs, tolerance=4.0)
    print("interaction p = %.4f (%s)" % (g["interaction_p"], "pooled" if g["interaction_pooled"]
                                          else "kept"))
    print("%-18s %10s %8s %8s %8s" % ("source", "variance", "%contr", "%SV", "%tol"))
    for c in g["components"]:
        print("%-18s %10.6f %8.2f %8.2f %8.2f" % (c["source"], c["variance"], c["pct_contribution"],
                                                 c["pct_study_var"], c["pct_tolerance"]))
    print("ndc = %d, verdict: %s" % (g["ndc"], g["verdict"]))

    # DOE
    rows = read("doe_2k3.csv")
    names = ["A_temperature", "B_pressure", "C_time"]
    runs = [{"A": int(r[names[0]]), "B": int(r[names[1]]), "C": int(r[names[2]])} for r in rows]
    y = [float(r["yield_pct"]) for r in rows]
    heading("2^3 factorial, 2 replicates (doe_2k3.csv)")
    model = doe.analyze(runs, y, ["A", "B", "C"])
    print("%-7s %9s %9s %8s %8s" % ("term", "effect", "coef", "t", "p"))
    for e in model["effects"]:
        print("%-7s %9.4f %9.4f %8.3f %8.4f" % (e["term"], e["effect"], e["coefficient"], e["t"], e["p"]))
    print("R-squared %.4f" % model["r_squared"])

    # Hypothesis tests
    ts = read("two_sample.csv")
    before = [float(r["before"]) for r in ts]
    after = [float(r["after"]) for r in ts]
    heading("Before vs after (two_sample.csv)")
    w = hypothesis.two_sample_t(before, after)
    print("Welch t = %.4f, df = %.2f, p = %.5f, 95%% CI %.4f to %.4f" % (w["t"], w["df"], w["p"], *w["ci"]))
    pt = hypothesis.paired_t(before, after)
    print("Paired t = %.4f, p = %.5f" % (pt["t"], pt["p"]))

    # Pareto
    heading("Pareto (pareto.csv)")
    pr = pareto.pareto({r["defect"]: int(r["count"]) for r in read("pareto.csv")})
    for r in pr:
        print("%-16s %4d %6.1f%% %6.1f%% %s" % (r["category"], r["count"], r["percent"],
                                               r["cumulative_percent"], "vital few" if r["vital_few"] else ""))

    if make_plots:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        out = os.path.join(HERE, "output")
        os.makedirs(out, exist_ok=True)
        fig, axes = plt.subplots(2, 1, figsize=(10, 7))
        control_charts.plot(imr["individuals"], axes[0], "Individuals")
        control_charts.plot(imr["moving_range"], axes[1], "Moving range")
        fig.tight_layout()
        fig.savefig(os.path.join(out, "imr.png"))
        fig, ax = plt.subplots(figsize=(10, 4))
        pareto.plot(pr, ax)
        fig.tight_layout()
        fig.savefig(os.path.join(out, "pareto.png"))
        print("\nCharts saved to", out)


if __name__ == "__main__":
    main("--plots" in sys.argv)
