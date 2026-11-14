# opex_stats.R

The same tools as the Python package, written in base R with no packages. See the [tools index](../README.md).

```r
source("opex_stats.R")
x <- read.csv("../data/capability.csv")$diameter_mm
capability_study(x, lsl = 9.9, usl = 10.1, target = 10)
plot_control_chart(imr_chart(x)$individuals)
```

```bash
Rscript run_all.R --plots
Rscript tests/test_opex_stats.R
```
