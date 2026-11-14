# Six Sigma toolkit by DMAIC phase

Links go to working tools. **Py** is the [Python package](../../02-quality-and-statistics/tools/python/), **R** is the [R script](../../02-quality-and-statistics/tools/r/opex_stats.R), and **XL** is an Excel / LibreOffice workbook.

| Phase | Tool | Py | R | XL |
| --- | --- | --- | --- | --- |
| Define | Project charter, SIPOC, CTQ tree | | | [charter](../templates-and-procedures/dmaic-project-charter.md) |
| Measure | Gauge R&R (ANOVA method) | `gage_rr` | `gage_rr_anova()` | [gage-rr-anova.xlsx](../../02-quality-and-statistics/tools/excel/gage-rr-anova.xlsx) |
| Measure | Capability (Cp, Cpk, Pp, Ppk, Cpm) | `capability` | `capability_study()` | [capability-and-imr.xlsx](../../02-quality-and-statistics/tools/excel/capability-and-imr.xlsx) |
| Measure | DPMO, sigma level, RTY | `capability` | `sigma_table()`, `rty()` | [sigma-level-calculator.xlsx](../../02-quality-and-statistics/tools/excel/sigma-level-calculator.xlsx) |
| Measure | Normality (Anderson-Darling) | `normality` | `anderson_darling()` | |
| Analyze | Pareto analysis | `pareto` | `pareto_table()` | [pareto-analysis.xlsx](../../02-quality-and-statistics/tools/excel/pareto-analysis.xlsx) |
| Analyze | t-tests, ANOVA, F-test, chi-square, regression | `hypothesis` | built into R | [hypothesis-tests.xlsx](../../02-quality-and-statistics/tools/excel/hypothesis-tests.xlsx) |
| Analyze | FMEA | | | [fmea-worksheet.xlsx](../../03-design-and-engineering/tools/excel/fmea-worksheet.xlsx) |
| Improve | Two-level factorial DOE | `doe` | `full_factorial()`, `analyze_factorial()` | [doe-2k-factorial.xlsx](../../02-quality-and-statistics/tools/excel/doe-2k-factorial.xlsx) |
| Control | I-MR, X-bar/R, X-bar/S charts | `control_charts` | `imr_chart()`, `xbar_r_chart()`, `xbar_s_chart()` | [capability-and-imr.xlsx](../../02-quality-and-statistics/tools/excel/capability-and-imr.xlsx), [xbar-r-chart.xlsx](../../02-quality-and-statistics/tools/excel/xbar-r-chart.xlsx) |
| Control | p, np, c, u charts | `control_charts` | `p_chart()`, `np_chart()`, `c_chart()`, `u_chart()` | [attribute-charts.xlsx](../../02-quality-and-statistics/tools/excel/attribute-charts.xlsx) |
| Control | Run rules (Western Electric / Nelson 1-4) | `control_charts.run_rules` | `run_rules()` | rule 1 only |

Other Six Sigma tools still to add here include the fishbone diagram, 5 Whys, check sheet, process map and VSM, QFD, the pick chart, and Taguchi loss.
