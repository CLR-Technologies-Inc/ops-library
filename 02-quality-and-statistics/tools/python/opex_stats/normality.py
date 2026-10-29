"""Anderson-Darling normality test (check before trusting normal-based capability)."""

import math
import statistics

from .distributions import norm_cdf


def anderson_darling(values):
    """A-squared, the small-sample adjusted A*-squared, and an approximate p-value.

    The p-value uses D'Agostino and Stephens (1986) for the case where the mean
    and standard deviation are estimated from the data.
    """
    x = sorted(float(v) for v in values)
    n = len(x)
    if n < 8:
        raise ValueError("need at least 8 values")
    mean, sd = statistics.fmean(x), statistics.stdev(x)
    z = [min(max(norm_cdf((v - mean) / sd), 1e-15), 1 - 1e-15) for v in x]
    s = sum((2 * i + 1) * (math.log(z[i]) + math.log(1 - z[n - 1 - i])) for i in range(n))
    a2 = -n - s / n
    a2s = a2 * (1 + 0.75 / n + 2.25 / n ** 2)
    if a2s >= 0.6:
        p = math.exp(1.2937 - 5.709 * a2s + 0.0186 * a2s ** 2)
    elif a2s >= 0.34:
        p = math.exp(0.9177 - 4.279 * a2s - 1.38 * a2s ** 2)
    elif a2s >= 0.2:
        p = 1 - math.exp(-8.318 + 42.796 * a2s - 59.938 * a2s ** 2)
    else:
        p = 1 - math.exp(-13.436 + 101.14 * a2s - 223.73 * a2s ** 2)
    return {"n": n, "a2": a2, "a2_adjusted": a2s, "p": min(max(p, 0.0), 1.0)}
