"""Write ../../data/reference_results.json: key results on the sample data.

The R tests and the Excel check compare their own results against this file,
so all three implementations are held to the same numbers.
"""

import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
DATA = os.path.join(HERE, "..", "..", "data")

from opex_stats import capability, control_charts, doe, gage_rr, hypothesis, normality  # noqa: E402


def read(name):
    with open(os.path.join(DATA, name)) as f:
        return list(csv.DictReader(f))


def build():
    values = [float(r["diameter_mm"]) for r in read("capability.csv")]
    cap = capability.capability(values, lsl=9.9, usl=10.1, target=10.0)
    imr = control_charts.imr_chart(values)
    groups = {}
    for r in read("subgroups.csv"):
        groups.setdefault(int(r["subgroup"]), []).append(float(r["diameter_mm"]))
    xr = control_charts.xbar_r_chart([groups[k] for k in sorted(groups)])
    att = read("attribute.csv")
    p = control_charts.p_chart([int(r["defective"]) for r in att], [int(r["inspected"]) for r in att])
    recs = [(int(r["part"]), r["operator"], float(r["measurement"])) for r in read("gage_rr.csv")]
    g = gage_rr.gage_rr_anova(recs, tolerance=4.0)
    comp = {c["source"]: c for c in g["components"]}
    rows = read("doe_2k3.csv")
    runs = [{"A": int(r["A_temperature"]), "B": int(r["B_pressure"]), "C": int(r["C_time"])} for r in rows]
    model = doe.analyze(runs, [float(r["yield_pct"]) for r in rows], ["A", "B", "C"])
    ts = read("two_sample.csv")
    w = hypothesis.two_sample_t([float(r["before"]) for r in ts], [float(r["after"]) for r in ts])
    return {
        "capability": {k: cap[k] for k in ("mean", "sigma_within", "sigma_overall", "Cp", "Cpk",
                                           "Pp", "Ppk", "Cpm")},
        "capability_ppm_overall": cap["expected_overall"]["ppm_total"],
        "anderson_darling_a2": normality.anderson_darling(values)["a2"],
        "imr": {"cl": imr["individuals"]["cl"], "ucl": imr["individuals"]["ucl"],
                "lcl": imr["individuals"]["lcl"], "mr_bar": imr["moving_range"]["cl"],
                "mr_ucl": imr["moving_range"]["ucl"]},
        "xbar_r": {"xbar_cl": xr["xbar"]["cl"], "xbar_ucl": xr["xbar"]["ucl"],
                   "xbar_lcl": xr["xbar"]["lcl"], "r_bar": xr["range"]["cl"],
                   "r_ucl": xr["range"]["ucl"]},
        "p_chart": {"p_bar": p["cl"], "signals": [i + 1 for i, rule in p["signals"] if rule == 1]},
        "gage_rr": {"var_repeatability": comp["Repeatability"]["variance"],
                    "var_reproducibility": comp["Reproducibility"]["variance"],
                    "var_part": comp["Part-to-Part"]["variance"],
                    "pct_study_var_grr": g["pct_study_var_grr"], "ndc": g["ndc"],
                    "interaction_p": g["interaction_p"]},
        "doe": {e["term"]: e["effect"] for e in model["effects"]},
        "welch_t": {"t": w["t"], "df": w["df"], "p": w["p"]},
    }


if __name__ == "__main__":
    ref = build()
    out = os.path.join(DATA, "reference_results.json")
    with open(out, "w") as f:
        json.dump(ref, f, indent=2, sort_keys=True)
        f.write("\n")
    # Flat key,value copy for tools without a JSON reader (base R, spreadsheets)
    flat = os.path.join(DATA, "reference_results.csv")
    with open(flat, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["key", "value"])
        for group, vals in sorted(ref.items()):
            if isinstance(vals, dict):
                for k, v in sorted(vals.items()):
                    writer.writerow(["%s.%s" % (group, k), repr(v) if isinstance(v, float) else v])
            elif not isinstance(vals, list):
                writer.writerow([group, repr(vals)])
    print("wrote", os.path.normpath(out), "and", os.path.normpath(flat))
