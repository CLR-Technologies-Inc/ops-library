"""Crossed Gauge R&R study by the ANOVA method (AIAG MSA, 4th edition).

Input is a list of (part, operator, measurement) records with the same number
of repeat trials for every part and operator combination.
"""

import math
from collections import defaultdict

from .distributions import f_sf

POOL_ALPHA = 0.25  # pool the part x operator term when its p-value exceeds this


def gage_rr_anova(records, tolerance=None, study_multiplier=6.0, pool_alpha=POOL_ALPHA):
    cells = defaultdict(list)
    for part, operator, y in records:
        cells[(part, operator)].append(float(y))
    parts = sorted({p for p, _ in cells})
    ops = sorted({o for _, o in cells})
    reps = {len(v) for v in cells.values()}
    if len(reps) != 1 or len(cells) != len(parts) * len(ops):
        raise ValueError("design must be balanced: every part measured by every operator "
                         "the same number of times")
    p, o, r = len(parts), len(ops), reps.pop()
    if r < 2:
        raise ValueError("need at least 2 trials per part and operator")

    ys = [y for v in cells.values() for y in v]
    grand = sum(ys) / len(ys)
    part_mean = {pt: sum(sum(cells[(pt, op)]) for op in ops) / (o * r) for pt in parts}
    op_mean = {op: sum(sum(cells[(pt, op)]) for pt in parts) / (p * r) for op in ops}
    cell_mean = {k: sum(v) / r for k, v in cells.items()}

    ss_total = sum((y - grand) ** 2 for y in ys)
    ss_part = o * r * sum((m - grand) ** 2 for m in part_mean.values())
    ss_op = p * r * sum((m - grand) ** 2 for m in op_mean.values())
    ss_cells = r * sum((m - grand) ** 2 for m in cell_mean.values())
    ss_int = ss_cells - ss_part - ss_op
    ss_err = ss_total - ss_cells

    df_part, df_op, df_int, df_err = p - 1, o - 1, (p - 1) * (o - 1), p * o * (r - 1)
    ms_part, ms_op = ss_part / df_part, ss_op / df_op
    ms_int, ms_err = ss_int / df_int, ss_err / df_err

    f_int = ms_int / ms_err
    p_int = f_sf(f_int, df_int, df_err)
    anova = [
        {"source": "Part", "df": df_part, "ss": ss_part, "ms": ms_part,
         "f": ms_part / ms_int, "p": f_sf(ms_part / ms_int, df_part, df_int)},
        {"source": "Operator", "df": df_op, "ss": ss_op, "ms": ms_op,
         "f": ms_op / ms_int, "p": f_sf(ms_op / ms_int, df_op, df_int)},
        {"source": "Part x Operator", "df": df_int, "ss": ss_int, "ms": ms_int,
         "f": f_int, "p": p_int},
        {"source": "Repeatability", "df": df_err, "ss": ss_err, "ms": ms_err},
        {"source": "Total", "df": p * o * r - 1, "ss": ss_total},
    ]

    pooled = p_int > pool_alpha
    if pooled:
        df_pool = df_int + df_err
        ms_pool = (ss_int + ss_err) / df_pool
        anova = [
            {"source": "Part", "df": df_part, "ss": ss_part, "ms": ms_part,
             "f": ms_part / ms_pool, "p": f_sf(ms_part / ms_pool, df_part, df_pool)},
            {"source": "Operator", "df": df_op, "ss": ss_op, "ms": ms_op,
             "f": ms_op / ms_pool, "p": f_sf(ms_op / ms_pool, df_op, df_pool)},
            {"source": "Repeatability", "df": df_pool, "ss": ss_int + ss_err, "ms": ms_pool},
            {"source": "Total", "df": p * o * r - 1, "ss": ss_total},
        ]
        var_rep = ms_pool
        var_int = 0.0
        var_op = max(0.0, (ms_op - ms_pool) / (p * r))
        var_part = max(0.0, (ms_part - ms_pool) / (o * r))
    else:
        var_rep = ms_err
        var_int = max(0.0, (ms_int - ms_err) / r)
        var_op = max(0.0, (ms_op - ms_int) / (p * r))
        var_part = max(0.0, (ms_part - ms_int) / (o * r))

    var_repro = var_op + var_int
    var_grr = var_rep + var_repro
    var_total = var_grr + var_part
    components = {
        "Total Gage R&R": var_grr,
        "Repeatability": var_rep,
        "Reproducibility": var_repro,
        "Operator": var_op,
        "Part x Operator": var_int,
        "Part-to-Part": var_part,
        "Total Variation": var_total,
    }
    table = []
    for name, var in components.items():
        sd = math.sqrt(var)
        row = {"source": name, "variance": var, "pct_contribution": 100 * var / var_total,
               "stdev": sd, "study_var": study_multiplier * sd,
               "pct_study_var": 100 * sd / math.sqrt(var_total)}
        if tolerance:
            row["pct_tolerance"] = 100 * study_multiplier * sd / tolerance
        table.append(row)

    ndc = math.floor(1.41 * math.sqrt(var_part) / math.sqrt(var_grr)) if var_grr > 0 else float("inf")
    pct_sv = 100 * math.sqrt(var_grr / var_total)
    verdict = ("acceptable" if pct_sv < 10 else
               "marginal: may be acceptable depending on the application and cost" if pct_sv <= 30
               else "unacceptable: improve the measurement system")
    return {"parts": p, "operators": o, "trials": r, "interaction_pooled": pooled,
            "interaction_p": p_int, "anova": anova, "components": table,
            "ndc": ndc, "pct_study_var_grr": pct_sv, "verdict": verdict}
