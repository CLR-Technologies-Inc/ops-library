"""Two-level factorial designs: build the design, then estimate effects.

Factors are coded -1 (low) and +1 (high). A full 2^k design is built in
standard (Yates) order; a fractional 2^(k-p) design is built by giving
generators, for example {"D": "ABC"} for a 2^(4-1) design with D = ABC.
"""

import itertools
import math
import random
import statistics

from .distributions import f_sf, t_sf


def full_factorial(factors, replicates=1, randomize=False, seed=None):
    """Return the run list for a 2^k design as a list of dicts of coded levels."""
    k = len(factors)
    base = []
    for i in range(2 ** k):
        base.append({f: (1 if (i >> j) & 1 else -1) for j, f in enumerate(factors)})
    runs = [dict(r, std_order=i + 1, replicate=rep + 1)
            for rep in range(replicates) for i, r in enumerate(base)]
    if randomize:
        random.Random(seed).shuffle(runs)
    for i, r in enumerate(runs):
        r["run_order"] = i + 1
    return runs


def fractional_factorial(base_factors, generators, replicates=1, randomize=False, seed=None):
    """2^(k-p) design: a full factorial in `base_factors` plus generated columns."""
    runs = full_factorial(base_factors, replicates, randomize, seed)
    for r in runs:
        for new, word in generators.items():
            r[new] = math.prod(r[c] for c in word)
    return runs


def decode(level, low, high):
    """Convert a coded level (-1..+1) to natural units."""
    return (low + high) / 2.0 + level * (high - low) / 2.0


def _terms(factors, max_order):
    out = []
    for order in range(1, max_order + 1):
        out.extend(itertools.combinations(factors, order))
    return out


def analyze(runs, response, factors, max_order=None):
    """Estimate effects and coefficients for a two-level factorial.

    `runs` is the design (list of dicts of coded levels), `response` the matching
    list of results. With replicates, the residual from the fitted model gives
    t-tests on each effect; with a single replicate, use the effects (and a
    normal or Pareto plot of them) to judge which matter.
    """
    max_order = max_order or len(factors)
    y = [float(v) for v in response]
    n = len(y)
    grand = statistics.fmean(y)
    effects = []
    for term in _terms(factors, max_order):
        col = [math.prod(r[f] for f in term) for r in runs]
        contrast = sum(c * v for c, v in zip(col, y))
        effect = contrast / (n / 2.0)
        effects.append({"term": "*".join(term), "effect": effect, "coefficient": effect / 2.0,
                        "ss": contrast ** 2 / n, "column": col})

    ss_total = sum((v - grand) ** 2 for v in y)
    ss_model = sum(e["ss"] for e in effects)
    df_error = n - 1 - len(effects)
    result = {"mean": grand, "effects": effects, "ss_total": ss_total, "df_error": df_error}
    if df_error > 0:
        ss_error = ss_total - ss_model
        ms_error = ss_error / df_error
        se_coef = math.sqrt(ms_error / n)
        for e in effects:
            e["t"] = e["coefficient"] / se_coef if se_coef > 0 else float("inf")
            e["p"] = 2 * t_sf(abs(e["t"]), df_error)
            e["f"] = e["ss"] / ms_error if ms_error > 0 else float("inf")
        result.update(ss_error=ss_error, ms_error=ms_error, se_coefficient=se_coef,
                      r_squared=ss_model / ss_total if ss_total else 1.0)
        f_model = (ss_model / len(effects)) / ms_error if ms_error > 0 else float("inf")
        result["model_p"] = f_sf(f_model, len(effects), df_error)
    for e in effects:
        del e["column"]
    return result


def predict(model, levels):
    """Predicted response at coded `levels` (dict) from an `analyze` result."""
    y = model["mean"]
    for e in model["effects"]:
        y += e["coefficient"] * math.prod(levels[f] for f in e["term"].split("*"))
    return y
