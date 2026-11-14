"""Process capability, sigma level, DPMO, and yield.

Within (short-term) sigma is estimated from the average moving range of
individual values (MR-bar / d2) or from subgroups (R-bar / d2). Overall
(long-term) sigma is the sample standard deviation of all the data.
"""

import math
import statistics

from .constants import d2
from .distributions import norm_cdf, norm_ppf

SIGMA_SHIFT = 1.5


def sigma_within_moving_range(values, span=2):
    """Short-term sigma from the average moving range (MR-bar / d2)."""
    if len(values) < span:
        raise ValueError("need at least %d values" % span)
    ranges = [max(values[i - span + 1:i + 1]) - min(values[i - span + 1:i + 1])
              for i in range(span - 1, len(values))]
    return statistics.fmean(ranges) / d2(span)


def sigma_within_subgroups(subgroups):
    """Short-term sigma from the average subgroup range (R-bar / d2), equal subgroup sizes."""
    sizes = {len(s) for s in subgroups}
    if len(sizes) != 1:
        raise ValueError("subgroups must all be the same size")
    n = sizes.pop()
    r_bar = statistics.fmean(max(s) - min(s) for s in subgroups)
    return r_bar / d2(n)


def _indices(mean, sigma, lsl, usl, target=None):
    out = {}
    if lsl is not None and usl is not None:
        out["Cp"] = (usl - lsl) / (6.0 * sigma)
    if usl is not None:
        out["CPU"] = (usl - mean) / (3.0 * sigma)
    if lsl is not None:
        out["CPL"] = (mean - lsl) / (3.0 * sigma)
    out["Cpk"] = min(v for k, v in out.items() if k in ("CPU", "CPL"))
    if target is not None and lsl is not None and usl is not None:
        out["Cpm"] = (usl - lsl) / (6.0 * math.sqrt(sigma ** 2 + (mean - target) ** 2))
    return out


def expected_ppm(mean, sigma, lsl=None, usl=None):
    """Expected parts per million outside each limit, assuming normality."""
    below = norm_cdf((lsl - mean) / sigma) * 1e6 if lsl is not None else 0.0
    above = (1.0 - norm_cdf((usl - mean) / sigma)) * 1e6 if usl is not None else 0.0
    return {"ppm_below_lsl": below, "ppm_above_usl": above, "ppm_total": below + above}


def capability(values, lsl=None, usl=None, target=None, subgroups=None):
    """Full capability study for a list of measurements.

    Pass `subgroups` (a list of equal-size lists) to estimate within sigma from
    subgroup ranges; otherwise the moving range of `values` is used.
    """
    if lsl is None and usl is None:
        raise ValueError("give at least one specification limit")
    if subgroups is not None:
        values = [v for s in subgroups for v in s]
    values = [float(v) for v in values]
    mean = statistics.fmean(values)
    s_overall = statistics.stdev(values)
    s_within = (sigma_within_subgroups(subgroups) if subgroups is not None
                else sigma_within_moving_range(values))

    within = _indices(mean, s_within, lsl, usl, target)
    overall = _indices(mean, s_overall, lsl, usl, target)
    observed_out = sum(1 for v in values
                       if (lsl is not None and v < lsl) or (usl is not None and v > usl))
    result = {
        "n": len(values),
        "mean": mean,
        "sigma_within": s_within,
        "sigma_overall": s_overall,
        "Cp": within.get("Cp"), "CPU": within.get("CPU"), "CPL": within.get("CPL"),
        "Cpk": within["Cpk"], "Cpm": within.get("Cpm"),
        "Pp": overall.get("Cp"), "PPU": overall.get("CPU"), "PPL": overall.get("CPL"),
        "Ppk": overall["Cpk"],
        "observed_ppm": observed_out / len(values) * 1e6,
        "expected_within": expected_ppm(mean, s_within, lsl, usl),
        "expected_overall": expected_ppm(mean, s_overall, lsl, usl),
    }
    result["sigma_level_overall"] = sigma_level_from_dpmo(result["expected_overall"]["ppm_total"])
    return result


def dpmo(defects, units, opportunities_per_unit=1):
    """Defects per million opportunities."""
    return defects / (units * opportunities_per_unit) * 1e6


def sigma_level_from_dpmo(dpmo_value, shift=SIGMA_SHIFT):
    """Short-term (reported) sigma level for a long-term DPMO, with the usual 1.5 shift."""
    if dpmo_value <= 0:
        return float("inf")
    if dpmo_value >= 1e6:
        return float("-inf")
    return norm_ppf(1.0 - dpmo_value / 1e6) + shift


def dpmo_from_sigma_level(level, shift=SIGMA_SHIFT):
    """Long-term DPMO implied by a short-term sigma level (one-sided, shifted)."""
    return (1.0 - norm_cdf(level - shift)) * 1e6


def sigma_table(levels=range(1, 8), shift=SIGMA_SHIFT):
    """The standard sigma-level table: DPMO, % defective, % yield, short- and long-term Cpk."""
    rows = []
    for s in levels:
        d = dpmo_from_sigma_level(s, shift)
        rows.append({
            "sigma_level": s, "with_shift": s - shift, "dpmo": d,
            "pct_defective": d / 1e4, "pct_yield": 100.0 - d / 1e4,
            "cpk_short_term": s / 3.0, "cpk_long_term": (s - shift) / 3.0,
        })
    return rows


def rolled_throughput_yield(step_yields):
    """RTY: probability a unit passes every step first time (yields as fractions)."""
    rty = 1.0
    for y in step_yields:
        rty *= y
    return rty


def first_pass_yield(units_in, defective_units):
    return (units_in - defective_units) / units_in
