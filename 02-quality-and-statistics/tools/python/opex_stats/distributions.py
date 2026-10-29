"""Probability distributions implemented with the Python standard library only.

These cover what the rest of the toolkit needs (normal, Student t, F, chi-square),
so the tools run anywhere Python 3.9+ runs, without SciPy.
"""

import math
from statistics import NormalDist

_STD_NORMAL = NormalDist()
_EPS = 1e-14
_TINY = 1e-300


def norm_cdf(x, mu=0.0, sigma=1.0):
    return NormalDist(mu, sigma).cdf(x)


def norm_ppf(p, mu=0.0, sigma=1.0):
    return NormalDist(mu, sigma).inv_cdf(p)


def _betacf(a, b, x):
    """Continued fraction for the incomplete beta function (modified Lentz)."""
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > _TINY else _TINY)
    h = d
    for m in range(1, 1000):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > _TINY else _TINY)
        c = 1.0 + aa / c
        c = c if abs(c) > _TINY else _TINY
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > _TINY else _TINY)
        c = 1.0 + aa / c
        c = c if abs(c) > _TINY else _TINY
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < _EPS:
            break
    return h


def betainc(a, b, x):
    """Regularized incomplete beta function I_x(a, b)."""
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    ln_front = (math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
                + a * math.log(x) + b * math.log1p(-x))
    front = math.exp(ln_front)
    if x < (a + 1.0) / (a + b + 2.0):
        return front * _betacf(a, b, x) / a
    return 1.0 - front * _betacf(b, a, 1.0 - x) / b


def gammainc(a, x):
    """Regularized lower incomplete gamma function P(a, x)."""
    if x <= 0.0:
        return 0.0
    if x < a + 1.0:
        term = total = 1.0 / a
        n = a
        for _ in range(10000):
            n += 1.0
            term *= x / n
            total += term
            if abs(term) < abs(total) * _EPS:
                break
        return total * math.exp(-x + a * math.log(x) - math.lgamma(a))
    # Continued fraction for the upper tail
    b = x + 1.0 - a
    c = 1.0 / _TINY
    d = 1.0 / b
    h = d
    for i in range(1, 10000):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        d = 1.0 / (d if abs(d) > _TINY else _TINY)
        c = b + an / c
        c = c if abs(c) > _TINY else _TINY
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < _EPS:
            break
    return 1.0 - math.exp(-x + a * math.log(x) - math.lgamma(a)) * h


def t_cdf(t, df):
    x = df / (df + t * t)
    tail = 0.5 * betainc(df / 2.0, 0.5, x)
    return 1.0 - tail if t >= 0 else tail


def t_sf(t, df):
    return 1.0 - t_cdf(t, df)


def f_cdf(f, df1, df2):
    if f <= 0:
        return 0.0
    return betainc(df1 / 2.0, df2 / 2.0, df1 * f / (df1 * f + df2))


def f_sf(f, df1, df2):
    if f <= 0:
        return 1.0
    return betainc(df2 / 2.0, df1 / 2.0, df2 / (df2 + df1 * f))


def chi2_cdf(x, df):
    return gammainc(df / 2.0, x / 2.0)


def chi2_sf(x, df):
    return 1.0 - chi2_cdf(x, df)


def _invert(cdf, p, lo, hi):
    """Bisection inverse for a monotone CDF."""
    while cdf(hi) < p:
        hi *= 2.0
    while cdf(lo) > p:
        lo = lo * 2.0 if lo < 0 else lo / 2.0 - 1.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if cdf(mid) < p:
            lo = mid
        else:
            hi = mid
        if hi - lo < 1e-12 * max(1.0, abs(mid)):
            break
    return 0.5 * (lo + hi)


def t_ppf(p, df):
    return _invert(lambda v: t_cdf(v, df), p, -10.0, 10.0)


def f_ppf(p, df1, df2):
    return _invert(lambda v: f_cdf(v, df1, df2), p, 0.0, 10.0)


def chi2_ppf(p, df):
    return _invert(lambda v: chi2_cdf(v, df), p, 0.0, max(10.0, 2.0 * df))
