# Excel / LibreOffice Calc workbooks

| Workbook | Sheets |
| --- | --- |
| [capability-and-imr.xlsx](capability-and-imr.xlsx) | Capability (up to 500 values), I-MR Chart |
| [xbar-r-chart.xlsx](xbar-r-chart.xlsx) | X-bar/R for up to 50 subgroups of size 2-10, Constants |
| [attribute-charts.xlsx](attribute-charts.xlsx) | p chart, u chart (limits vary with sample size), c and np |
| [gage-rr-anova.xlsx](gage-rr-anova.xlsx) | Crossed Gauge R&R by ANOVA, up to 30 parts and 10 operators |
| [doe-2k-factorial.xlsx](doe-2k-factorial.xlsx) | 2^3 factorial with replicates: effects, t, p, and effects chart |
| [hypothesis-tests.xlsx](hypothesis-tests.xlsx) | Welch, pooled, and paired t-tests, and the F-test |
| [sigma-level-calculator.xlsx](sigma-level-calculator.xlsx) | DPMO, sigma level, RTY, sigma table |
| [pareto-analysis.xlsx](pareto-analysis.xlsx) | Auto-sorted Pareto table and chart |
| [FMEA worksheet](../../../03-design-and-engineering/tools/excel/fmea-worksheet.xlsx) | PFMEA with RPN, highlighting, and rating scales |

Yellow cells are inputs and green cells are results. Charts cover the sample data range, so widen the chart's data range if you add more rows.

- `build_workbooks.py` generates every workbook from `../data/`. Edit it, then rerun it, rather than editing the formulas by hand.
- `check_workbooks.py` recalculates the workbooks in LibreOffice and compares them with the Python results.
