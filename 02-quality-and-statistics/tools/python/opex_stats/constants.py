"""Control chart constants for subgroup sizes n = 2..25.

d2 and c4 are computed exactly; d3 comes from the standard published tables
(ASTM E2587 / AIAG SPC manual). The derived factors (A2, A3, D3, D4, B3, B4)
are calculated from those, so they match the published tables to rounding.
"""

import math

# d3: standard deviation of the relative range W = R / sigma
_D3_TABLE = {
    2: 0.8525, 3: 0.8884, 4: 0.8798, 5: 0.8641, 6: 0.8480, 7: 0.8332, 8: 0.8198,
    9: 0.8078, 10: 0.7971, 11: 0.7873, 12: 0.7785, 13: 0.7704, 14: 0.7630,
    15: 0.7562, 16: 0.7499, 17: 0.7441, 18: 0.7386, 19: 0.7335, 20: 0.7287,
    21: 0.7242, 22: 0.7199, 23: 0.7159, 24: 0.7121, 25: 0.7084,
}


def _phi(x):
    return 0.5 * math.erfc(-x / math.sqrt(2.0))


def d2(n):
    """Expected value of the relative range of n standard normal values."""
    if n < 2:
        raise ValueError("subgroup size must be at least 2")
    # d2 = integral over x of 1 - (1 - Phi(x))^n - Phi(x)^n (Simpson's rule)
    lo, hi, steps = -10.0, 10.0, 4000
    h = (hi - lo) / steps
    total = 0.0
    for i in range(steps + 1):
        x = lo + i * h
        p = _phi(x)
        f = 1.0 - (1.0 - p) ** n - p ** n
        w = 1 if i in (0, steps) else (4 if i % 2 else 2)
        total += w * f
    return total * h / 3.0


def d3(n):
    if n not in _D3_TABLE:
        raise ValueError("d3 is tabulated for subgroup sizes 2 to 25")
    return _D3_TABLE[n]


def c4(n):
    """Bias correction for the sample standard deviation."""
    if n < 2:
        raise ValueError("subgroup size must be at least 2")
    return math.sqrt(2.0 / (n - 1)) * math.exp(math.lgamma(n / 2.0) - math.lgamma((n - 1) / 2.0))


def factors(n):
    """All chart factors for subgroup size n, as a dict."""
    _d2, _d3, _c4 = d2(n), d3(n), c4(n)
    b_spread = 3.0 * math.sqrt(1.0 - _c4 ** 2) / _c4
    return {
        "n": n,
        "d2": _d2,
        "d3": _d3,
        "c4": _c4,
        "A2": 3.0 / (_d2 * math.sqrt(n)),
        "A3": 3.0 / (_c4 * math.sqrt(n)),
        "D3": max(0.0, 1.0 - 3.0 * _d3 / _d2),
        "D4": 1.0 + 3.0 * _d3 / _d2,
        "B3": max(0.0, 1.0 - b_spread),
        "B4": 1.0 + b_spread,
    }
