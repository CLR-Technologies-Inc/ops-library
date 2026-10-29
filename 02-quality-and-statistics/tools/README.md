# Quality & Statistics: Tools

Working Six Sigma and SPC tools in three formats. All three are built on the same sample data and checked against each other, so a Cpk from the spreadsheet matches the Cpk from Python and from R.

| Tool | Python (`python/`) | R (`r/`) | Excel / LibreOffice (`excel/`) |
| --- | --- | --- | --- |
| Process capability: Cp, Cpk, Pp, Ppk, Cpm, expected and observed ppm | `capability.capability()` | `capability_study()` | [capability-and-imr.xlsx](excel/capability-and-imr.xlsx) |
| DPMO, sigma level, sigma table, rolled throughput yield | `capability` | `sigma_table()`, `dpmo()`, `rty()` | [sigma-level-calculator.xlsx](excel/sigma-level-calculator.xlsx) |
| I-MR chart | `control_charts.imr_chart()` | `imr_chart()` | [capability-and-imr.xlsx](excel/capability-and-imr.xlsx) |
| X-bar/R and X-bar/S charts | `xbar_r_chart()`, `xbar_s_chart()` | `xbar_r_chart()`, `xbar_s_chart()` | [xbar-r-chart.xlsx](excel/xbar-r-chart.xlsx) (X-bar/R) |
| p, np, c, u attribute charts | `p_chart()`, `np_chart()`, `c_chart()`, `u_chart()` | same names | [attribute-charts.xlsx](excel/attribute-charts.xlsx) |
| Run rules 1-4 (beyond 3σ, 9 on one side, 6 trending, 14 alternating) | `run_rules()` | `run_rules()` | rule 1 flag column |
| Control chart constants n = 2..25 (d2, d3, c4, A2, A3, D3, D4, B3, B4) | `constants.factors()` | `chart_factors()` | Constants sheet, n = 2..10 |
| Gauge R&R, crossed ANOVA method (AIAG), interaction pooling, %Contribution, %Study var, %Tolerance, ndc | `gage_rr.gage_rr_anova()` | `gage_rr_anova()` | [gage-rr-anova.xlsx](excel/gage-rr-anova.xlsx) |
| Two-level full and fractional factorial DOE: design, effects, coefficients, t and p, prediction | `doe` | `full_factorial()`, `analyze_factorial()` | [doe-2k-factorial.xlsx](excel/doe-2k-factorial.xlsx) (2^3) |
| t-tests (one-sample, Welch, pooled, paired), one-way ANOVA, F-test, chi-square, regression | `hypothesis` | built into R (`t.test`, `aov`, `var.test`, `chisq.test`, `lm`) | [hypothesis-tests.xlsx](excel/hypothesis-tests.xlsx) |
| Anderson-Darling normality test | `normality.anderson_darling()` | `anderson_darling()` | |
| Pareto analysis and chart | `pareto` | `pareto_table()`, `plot_pareto()` | [pareto-analysis.xlsx](excel/pareto-analysis.xlsx) |
| FMEA worksheet (RPN, S x O, rating scales) | | | [fmea-worksheet.xlsx](../../03-design-and-engineering/tools/excel/fmea-worksheet.xlsx) |

## Quick start

**Excel or LibreOffice Calc.** Open a workbook. Yellow cells are inputs and green cells are results. Each workbook ships with sample data, so paste your own data over it. Every result is a live formula, and the formulas use only functions that work in both Excel 2010+ and LibreOffice Calc. To rebuild the workbooks after editing the generator, run `python excel/build_workbooks.py` (needs `openpyxl`).

**Python 3.10+.** No installs needed: the package uses only the standard library. Plots are optional and need `matplotlib`.

```python
import sys; sys.path.insert(0, "python")
from opex_stats import capability, control_charts, gage_rr

capability.capability([10.01, 9.98, 10.03, 9.99, 10.02, 10.00, 9.97, 10.01], lsl=9.9, usl=10.1)
control_charts.xbar_r_chart([[10.0, 10.1, 9.9], [10.2, 10.0, 10.1], [9.9, 10.0, 10.0]])
```

```bash
cd python
python examples/run_all.py           # every tool on the sample data
python -m unittest discover -s tests # 19 tests
```

**R.** Base R only, with no packages.

```r
setwd("r"); source("opex_stats.R")
cap <- capability_study(read.csv("../data/capability.csv")$diameter_mm, lsl = 9.9, usl = 10.1)
```

```bash
cd r
Rscript run_all.R --plots            # every tool on the sample data, charts saved to output/
Rscript tests/test_opex_stats.R      # checks results against the Python reference
```

## Sample data (`data/`)

| File | Contents |
| --- | --- |
| `capability.csv` | 100 individual diameters (spec 10.0 ± 0.1 mm) |
| `subgroups.csv` | 25 subgroups of 5. The last 5 subgroups carry a small mean shift. |
| `attribute.csv` | 25 samples of inspected / defective counts and units / defects. Sample 18 is out of control. |
| `gage_rr.csv` | 10 parts × 3 operators × 3 trials |
| `doe_2k3.csv` | 2^3 factorial, 2 replicates, with a real A×B interaction |
| `two_sample.csv` | Paired before and after values |
| `pareto.csv` | Defect counts by category |
| `reference_results.json` / `.csv` | Python results that the R tests and the spreadsheet check compare against |

## How the tools are checked

- **Python:** unit tests compare against published values. These include t, F, and χ² quantiles; control chart constants from the AIAG and ASTM tables; and the Six Sigma DPMO table.
- **R:** `tests/test_opex_stats.R` checks the same published values plus every Python reference result.
- **Spreadsheets:** `excel/check_workbooks.py` recalculates each workbook in LibreOffice and compares 40 cells with the Python reference. It also confirms that no formula returns an error.
- **CI:** [GitHub Actions](../../.github/workflows/tools.yml) runs all three on every change.

## Other open-source tools

- **LibreOffice Calc** opens every workbook here, and the automated checks run in it.
- **Gnumeric**, **JASP**, **jamovi**, and **PSPP** can open the CSVs in `data/`. JASP and jamovi offer t-tests, ANOVA, and regression from menus.
- **Python:** `statsmodels` (DOE and regression), `scipy.stats`, and `pingouin` give fuller versions of the tests here.
- **R:** the `qcc` (control charts, capability), `SixSigma` (Gauge R&R, capability, DOE helpers), and `FrF2` (fractional factorials) packages go further than the base-R tools here.

## Methods and conventions

- Within (short-term) sigma comes from MR-bar/d2 for individuals or R-bar/d2 for subgroups. Overall (long-term) sigma is the sample standard deviation.
- The sigma level uses the conventional 1.5σ shift. See [Sigma levels, DPMO, and the 1.5σ shift](../methodologies/sigma-levels-and-dpmo.md).
- Gauge R&R follows the AIAG MSA 4th edition ANOVA method. The part × operator interaction is pooled into repeatability when its p-value is above 0.25. %Study var acceptance limits are 10% and 30%, and ndc = ⌊1.41 × PV / GRR⌋.
- Capability indices assume roughly normal, stable data. Check stability with a control chart and normality with Anderson-Darling first.
