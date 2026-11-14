"""Pareto analysis: rank categories and find the vital few."""


def pareto(counts, cutoff=80.0):
    """`counts` is a dict {category: count}. Returns rows sorted by count, with
    percent, cumulative percent, and whether each row is in the vital few
    (the categories needed to reach `cutoff` percent)."""
    total = sum(counts.values())
    rows, cum = [], 0.0
    for cat, n in sorted(counts.items(), key=lambda kv: (-kv[1], str(kv[0]))):
        before = cum
        cum += 100.0 * n / total
        rows.append({"category": cat, "count": n, "percent": 100.0 * n / total,
                     "cumulative_percent": cum, "vital_few": before < cutoff})
    return rows


def plot(rows, ax=None, title="Pareto chart"):
    import matplotlib.pyplot as plt

    if ax is None:
        _, ax = plt.subplots(figsize=(10, 4))
    cats = [str(r["category"]) for r in rows]
    ax.bar(cats, [r["count"] for r in rows], color="#1f4e79")
    ax2 = ax.twinx()
    ax2.plot(cats, [r["cumulative_percent"] for r in rows], color="#c00000", marker="o")
    ax2.set_ylim(0, 105)
    ax2.axhline(80, color="#7f7f7f", linestyle=":")
    ax.set_title(title)
    ax.tick_params(axis="x", rotation=45)
    return ax
