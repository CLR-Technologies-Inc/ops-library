# Sigma levels, DPMO, and the 1.5σ shift

Calculators: [sigma-level-calculator.xlsx](../tools/excel/sigma-level-calculator.xlsx), `capability.sigma_level_from_dpmo()` in [Python](../tools/python/opex_stats/capability.py), and `sigma_level_from_dpmo()` in [R](../tools/r/opex_stats.R).

**Definitions**

- **DPMO** (defects per million opportunities) = defects ÷ (units × opportunities per unit) × 1,000,000
- **Sigma level** = the number of process standard deviations between the mean and the nearest specification limit
- **Reported (short-term) sigma level** = NORMSINV(1 − DPMO/10⁶) + 1.5
- **Long-term DPMO** = 10⁶ × (1 − Φ(sigma level − 1.5))

**The 1.5σ shift.** Mikel Harry proposed that a process drifts by about 1.5σ over the long run. On that assumption, a process that looks like six sigma in a short study performs like 4.5σ over time. That is where "3.4 DPMO" comes from: it is the one-sided tail beyond 4.5σ. Without the shift, a true two-sided 4.5σ process gives about 6.8 DPMO.

| Sigma level | With 1.5σ shift | DPMO | % defective | % yield | Short-term Cpk | Long-term Cpk |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | −0.5 | 691,462 | 69% | 31% | 0.33 | −0.17 |
| 2 | 0.5 | 308,538 | 31% | 69% | 0.67 | 0.17 |
| 3 | 1.5 | 66,807 | 6.7% | 93.3% | 1.00 | 0.50 |
| 4 | 2.5 | 6,210 | 0.62% | 99.38% | 1.33 | 0.83 |
| 5 | 3.5 | 233 | 0.023% | 99.977% | 1.67 | 1.17 |
| 6 | 4.5 | 3.4 | 0.00034% | 99.99966% | 2.00 | 1.50 |
| 7 | 5.5 | 0.019 | 0.0000019% | 99.9999981% | 2.33 | 1.83 |

All three toolkits reproduce this table, and the tests check it.

**Use it carefully**

- The shift is a convention, not a law of nature. Donald Wheeler and others call it arbitrary. Where you can, report short-term capability (Cp, Cpk) and long-term capability (Pp, Ppk) separately, as the capability tools do.
- These figures assume normal data. Check normality first with the Anderson-Darling test in the Python and R tools. For non-normal data, transform it (Box-Cox or Johnson) or fit a better distribution before you quote a sigma level.
- Use the sigma level to compare a process with itself over time. Not every process needs 3.4 DPMO.

---

**Source.** Based on the Wikipedia article [Six Sigma](https://en.wikipedia.org/wiki/Six_Sigma) and the references it cites, as of 2026-10-29, summarized in our own words. Wikipedia content is available under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
