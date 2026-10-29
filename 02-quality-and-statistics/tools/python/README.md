# opex_stats (Python)

Six Sigma and SPC statistics using only the Python standard library (3.9+). See the [tools index](../README.md) for the full list.

| Module | Main functions |
| --- | --- |
| `capability` | `capability()`, `dpmo()`, `sigma_level_from_dpmo()`, `dpmo_from_sigma_level()`, `sigma_table()`, `rolled_throughput_yield()` |
| `control_charts` | `imr_chart()`, `xbar_r_chart()`, `xbar_s_chart()`, `p_chart()`, `np_chart()`, `c_chart()`, `u_chart()`, `run_rules()`, `plot()` |
| `gage_rr` | `gage_rr_anova(records, tolerance)` with records as `(part, operator, value)` |
| `doe` | `full_factorial()`, `fractional_factorial()`, `analyze()`, `predict()`, `decode()` |
| `hypothesis` | `one_sample_t()`, `two_sample_t()`, `paired_t()`, `one_way_anova()`, `f_test_variances()`, `chi_square_independence()`, `linear_regression()` |
| `normality` | `anderson_darling()` |
| `pareto` | `pareto()`, `plot()` |
| `constants` | `factors(n)`, `d2()`, `d3()`, `c4()` |
| `distributions` | normal, t, F, and χ² CDF, survival, and inverse functions |

```bash
python examples/run_all.py --plots   # report on the sample data; charts need matplotlib
python -m unittest discover -s tests
python examples/make_reference.py    # regenerate ../data/reference_results.*
```
