"""Shewhart control charts and run rules.

Every chart function returns a dict with the plotted statistic (`points`),
centre line (`cl`), control limits (`ucl`, `lcl`, either one value or one per
point), and `signals`: a list of (index, rule) pairs from the run rules.
"""

import math
import statistics

from .constants import factors


# ---------------------------------------------------------------- run rules

def run_rules(points, cl, ucl, lcl, rules=(1, 2, 3, 4)):
    """Western Electric / Nelson rules 1-4 on a series of points.

    1: one point beyond 3 sigma
    2: nine points in a row on one side of the centre line
    3: six points in a row steadily increasing or decreasing
    4: fourteen points in a row alternating up and down
    Limits may be scalars or per-point lists (for p and u charts).
    """
    n = len(points)
    ucl = ucl if isinstance(ucl, list) else [ucl] * n
    lcl = lcl if isinstance(lcl, list) else [lcl] * n
    signals = []

    if 1 in rules:
        for i, x in enumerate(points):
            if x > ucl[i] or x < lcl[i]:
                signals.append((i, 1))
    if 2 in rules:
        for i in range(8, n):
            window = points[i - 8:i + 1]
            if all(x > cl for x in window) or all(x < cl for x in window):
                signals.append((i, 2))
    if 3 in rules:
        for i in range(5, n):
            w = points[i - 5:i + 1]
            diffs = [b - a for a, b in zip(w, w[1:])]
            if all(d > 0 for d in diffs) or all(d < 0 for d in diffs):
                signals.append((i, 3))
    if 4 in rules:
        for i in range(13, n):
            w = points[i - 13:i + 1]
            diffs = [b - a for a, b in zip(w, w[1:])]
            if all(d != 0 for d in diffs) and all(
                    (diffs[k] > 0) != (diffs[k + 1] > 0) for k in range(len(diffs) - 1)):
                signals.append((i, 4))
    return sorted(signals)


def _chart(name, points, cl, ucl, lcl):
    return {"chart": name, "points": points, "cl": cl, "ucl": ucl, "lcl": lcl,
            "signals": run_rules(points, cl, ucl, lcl)}


# ---------------------------------------------------------- variables charts

def imr_chart(values):
    """Individuals and moving range (I-MR) charts."""
    values = [float(v) for v in values]
    mr = [abs(b - a) for a, b in zip(values, values[1:])]
    mr_bar = statistics.fmean(mr)
    x_bar = statistics.fmean(values)
    f = factors(2)
    sigma = mr_bar / f["d2"]
    individuals = _chart("I", values, x_bar, x_bar + 3 * sigma, x_bar - 3 * sigma)
    moving_range = _chart("MR", mr, mr_bar, f["D4"] * mr_bar, f["D3"] * mr_bar)
    # Moving ranges are autocorrelated, so only rule 1 applies to them.
    moving_range["signals"] = run_rules(mr, mr_bar, moving_range["ucl"], moving_range["lcl"], rules=(1,))
    return {"individuals": individuals, "moving_range": moving_range, "sigma_within": sigma}


def xbar_r_chart(subgroups):
    """X-bar and R charts for equal-size subgroups (n = 2..25)."""
    n = len(subgroups[0])
    if any(len(s) != n for s in subgroups):
        raise ValueError("subgroups must all be the same size")
    f = factors(n)
    means = [statistics.fmean(s) for s in subgroups]
    ranges = [max(s) - min(s) for s in subgroups]
    x_dbar, r_bar = statistics.fmean(means), statistics.fmean(ranges)
    xbar = _chart("Xbar", means, x_dbar, x_dbar + f["A2"] * r_bar, x_dbar - f["A2"] * r_bar)
    r = _chart("R", ranges, r_bar, f["D4"] * r_bar, f["D3"] * r_bar)
    r["signals"] = run_rules(ranges, r_bar, r["ucl"], r["lcl"], rules=(1,))
    return {"xbar": xbar, "range": r, "sigma_within": r_bar / f["d2"]}


def xbar_s_chart(subgroups):
    """X-bar and S charts for equal-size subgroups."""
    n = len(subgroups[0])
    if any(len(s) != n for s in subgroups):
        raise ValueError("subgroups must all be the same size")
    f = factors(n)
    means = [statistics.fmean(s) for s in subgroups]
    sds = [statistics.stdev(s) for s in subgroups]
    x_dbar, s_bar = statistics.fmean(means), statistics.fmean(sds)
    xbar = _chart("Xbar", means, x_dbar, x_dbar + f["A3"] * s_bar, x_dbar - f["A3"] * s_bar)
    s = _chart("S", sds, s_bar, f["B4"] * s_bar, f["B3"] * s_bar)
    s["signals"] = run_rules(sds, s_bar, s["ucl"], s["lcl"], rules=(1,))
    return {"xbar": xbar, "stdev": s, "sigma_within": s_bar / f["c4"]}


# --------------------------------------------------------- attribute charts

def p_chart(defectives, sample_sizes):
    """Proportion defective, with per-point limits for varying sample sizes."""
    p_bar = sum(defectives) / sum(sample_sizes)
    points = [d / n for d, n in zip(defectives, sample_sizes)]
    half = [3 * math.sqrt(p_bar * (1 - p_bar) / n) for n in sample_sizes]
    return _chart("p", points, p_bar, [min(1.0, p_bar + h) for h in half],
                  [max(0.0, p_bar - h) for h in half])


def np_chart(defectives, sample_size):
    """Number defective, constant sample size."""
    p_bar = sum(defectives) / (len(defectives) * sample_size)
    cl = sample_size * p_bar
    half = 3 * math.sqrt(cl * (1 - p_bar))
    return _chart("np", [float(d) for d in defectives], cl, cl + half, max(0.0, cl - half))


def c_chart(defects):
    """Count of defects per unit, constant area of opportunity."""
    c_bar = statistics.fmean(defects)
    half = 3 * math.sqrt(c_bar)
    return _chart("c", [float(d) for d in defects], c_bar, c_bar + half, max(0.0, c_bar - half))


def u_chart(defects, units):
    """Defects per unit, with per-point limits for varying inspection sizes."""
    u_bar = sum(defects) / sum(units)
    points = [d / n for d, n in zip(defects, units)]
    half = [3 * math.sqrt(u_bar / n) for n in units]
    return _chart("u", points, u_bar, [u_bar + h for h in half],
                  [max(0.0, u_bar - h) for h in half])


# ------------------------------------------------------------------ plotting

def plot(chart, ax=None, title=None):
    """Draw one chart with matplotlib (optional dependency)."""
    import matplotlib.pyplot as plt

    if ax is None:
        _, ax = plt.subplots(figsize=(10, 4))
    x = list(range(1, len(chart["points"]) + 1))
    ax.plot(x, chart["points"], marker="o", color="#1f4e79", linewidth=1)
    for key, style in (("ucl", "--"), ("lcl", "--")):
        lim = chart[key]
        if isinstance(lim, list):
            ax.step(x, lim, where="mid", linestyle=style, color="#c00000")
        else:
            ax.axhline(lim, linestyle=style, color="#c00000")
    ax.axhline(chart["cl"], color="#548235")
    flagged = sorted({i for i, _ in chart["signals"]})
    ax.scatter([x[i] for i in flagged], [chart["points"][i] for i in flagged],
               color="#c00000", zorder=3, s=60)
    ax.set_title(title or chart["chart"] + " chart")
    ax.set_xlabel("Sample")
    return ax
