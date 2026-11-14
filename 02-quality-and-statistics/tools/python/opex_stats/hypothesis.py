"""Common hypothesis tests for improvement projects (Analyze and Improve phases)."""

import math
import statistics

from .distributions import chi2_sf, f_sf, t_ppf, t_sf


def _two_sided(t, df):
    return 2.0 * t_sf(abs(t), df)


def one_sample_t(values, mu0, alpha=0.05):
    n = len(values)
    mean, sd = statistics.fmean(values), statistics.stdev(values)
    se = sd / math.sqrt(n)
    t = (mean - mu0) / se
    half = t_ppf(1 - alpha / 2, n - 1) * se
    return {"n": n, "mean": mean, "stdev": sd, "t": t, "df": n - 1,
            "p": _two_sided(t, n - 1), "ci": (mean - half, mean + half)}


def two_sample_t(a, b, equal_var=False, alpha=0.05):
    """Welch's t-test by default; set equal_var=True for the pooled test."""
    na, nb = len(a), len(b)
    ma, mb = statistics.fmean(a), statistics.fmean(b)
    va, vb = statistics.variance(a), statistics.variance(b)
    if equal_var:
        df = na + nb - 2
        sp2 = ((na - 1) * va + (nb - 1) * vb) / df
        se = math.sqrt(sp2 * (1 / na + 1 / nb))
    else:
        se = math.sqrt(va / na + vb / nb)
        df = (va / na + vb / nb) ** 2 / ((va / na) ** 2 / (na - 1) + (vb / nb) ** 2 / (nb - 1))
    t = (ma - mb) / se
    half = t_ppf(1 - alpha / 2, df) * se
    return {"mean_a": ma, "mean_b": mb, "difference": ma - mb, "t": t, "df": df,
            "p": _two_sided(t, df), "ci": (ma - mb - half, ma - mb + half)}


def paired_t(before, after, alpha=0.05):
    diffs = [b - a for a, b in zip(before, after)]
    out = one_sample_t(diffs, 0.0, alpha)
    out["mean_difference"] = out.pop("mean")
    return out


def one_way_anova(*groups):
    allv = [v for g in groups for v in g]
    grand = statistics.fmean(allv)
    ss_between = sum(len(g) * (statistics.fmean(g) - grand) ** 2 for g in groups)
    ss_within = sum(sum((v - statistics.fmean(g)) ** 2 for v in g) for g in groups)
    df_b, df_w = len(groups) - 1, len(allv) - len(groups)
    f = (ss_between / df_b) / (ss_within / df_w)
    return {"ss_between": ss_between, "ss_within": ss_within, "df_between": df_b,
            "df_within": df_w, "f": f, "p": f_sf(f, df_b, df_w),
            "means": [statistics.fmean(g) for g in groups]}


def f_test_variances(a, b):
    """Two-sided F-test for equal variances (sensitive to non-normality)."""
    va, vb = statistics.variance(a), statistics.variance(b)
    f = va / vb
    d1, d2 = len(a) - 1, len(b) - 1
    p_upper = f_sf(f, d1, d2)
    return {"f": f, "df1": d1, "df2": d2, "p": min(1.0, 2 * min(p_upper, 1 - p_upper))}


def chi_square_independence(table):
    """Chi-square test on a contingency table (list of rows of counts)."""
    rows = [sum(r) for r in table]
    cols = [sum(c) for c in zip(*table)]
    total = sum(rows)
    chi2 = 0.0
    for i, r in enumerate(table):
        for j, obs in enumerate(r):
            exp = rows[i] * cols[j] / total
            chi2 += (obs - exp) ** 2 / exp
    df = (len(rows) - 1) * (len(cols) - 1)
    return {"chi2": chi2, "df": df, "p": chi2_sf(chi2, df)}


def linear_regression(x, y):
    """Simple least-squares line with R-squared and a t-test on the slope."""
    n = len(x)
    mx, my = statistics.fmean(x), statistics.fmean(y)
    sxx = sum((a - mx) ** 2 for a in x)
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    slope = sxy / sxx
    intercept = my - slope * mx
    resid = [b - (intercept + slope * a) for a, b in zip(x, y)]
    sse = sum(e * e for e in resid)
    sst = sum((b - my) ** 2 for b in y)
    se_slope = math.sqrt(sse / (n - 2) / sxx)
    t = slope / se_slope
    return {"slope": slope, "intercept": intercept, "r_squared": 1 - sse / sst,
            "se_slope": se_slope, "t": t, "p": _two_sided(t, n - 2)}
