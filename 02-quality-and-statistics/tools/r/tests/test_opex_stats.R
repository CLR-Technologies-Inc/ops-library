# Run from this folder's parent:  Rscript tests/test_opex_stats.R
# Checks the R tools against published constants and against the Python results
# in ../data/reference_results.csv. Exits non-zero on any failure.

source("opex_stats.R")
data_dir <- file.path("..", "data")
ref_tab <- read.csv(file.path(data_dir, "reference_results.csv"), stringsAsFactors = FALSE)
ref <- function(key) as.numeric(ref_tab$value[ref_tab$key == key])

failures <- 0
check <- function(label, got, expected, tol = 1e-6) {
  ok <- isTRUE(all.equal(as.numeric(got), as.numeric(expected), tolerance = tol, scale = 1)) ||
        isTRUE(abs(as.numeric(got) - as.numeric(expected)) <= tol * max(1, abs(as.numeric(expected))))
  cat(sprintf("%-4s %-36s got %-14.8g expected %.8g\n", if (ok) "ok" else "FAIL", label, got, expected))
  if (!ok) failures <<- failures + 1
}

# Constants vs published tables
f5 <- chart_factors(5); f10 <- chart_factors(10)
check("d2(5)", f5$d2, 2.326, 1e-3); check("A2(5)", f5$A2, 0.577, 1e-3)
check("D4(5)", f5$D4, 2.114, 1e-3); check("B4(5)", f5$B4, 2.089, 1e-3)
check("D3(10)", f10$D3, 0.223, 1e-3); check("c4(10)", f10$c4, 0.9727, 1e-3)

# Sigma table vs Wikipedia
st <- sigma_table(1:6)
check("DPMO at 3 sigma", st$dpmo[3], 66807, 1)
check("DPMO at 6 sigma", st$dpmo[6], 3.4, 0.01)
check("sigma level from 3.4 DPMO", sigma_level_from_dpmo(3.4), 6, 0.01)

# Capability vs Python
x <- read.csv(file.path(data_dir, "capability.csv"))$diameter_mm
cap <- capability_study(x, lsl = 9.9, usl = 10.1, target = 10)
for (k in c("mean", "sigma_within", "sigma_overall", "Cp", "Cpk", "Pp", "Ppk", "Cpm"))
  check(paste("capability", k), cap[[k]], ref(paste0("capability.", k)))
check("ppm overall", cap$expected_ppm_overall[["total"]], ref("capability_ppm_overall"), 1e-4)
check("Anderson-Darling A2", anderson_darling(x)$a2, ref("anderson_darling_a2"))

# Control charts vs Python
imr <- imr_chart(x)
check("I chart UCL", imr$individuals$ucl, ref("imr.ucl"))
check("I chart LCL", imr$individuals$lcl, ref("imr.lcl"))
check("MR UCL", imr$moving_range$ucl, ref("imr.mr_ucl"), 1e-5)
sg <- read.csv(file.path(data_dir, "subgroups.csv"))
m <- matrix(sg$diameter_mm, ncol = 5, byrow = TRUE)
xr <- xbar_r_chart(m)
check("Xbar UCL", xr$xbar$ucl, ref("xbar_r.xbar_ucl"), 1e-5)
check("R UCL", xr$range$ucl, ref("xbar_r.r_ucl"), 1e-5)
att <- read.csv(file.path(data_dir, "attribute.csv"))
pc <- p_chart(att$defective, att$inspected)
check("p-bar", pc$cl, ref("p_chart.p_bar"))
check("p chart rule-1 signal at sample 18", pc$signals$index[pc$signals$rule == 1][1], 18)

# Gage R&R vs Python
g <- read.csv(file.path(data_dir, "gage_rr.csv"))
grr <- gage_rr_anova(g$part, g$operator, g$measurement, tolerance = 4)
check("GRR repeatability var", grr$components["Repeatability", "variance"], ref("gage_rr.var_repeatability"))
check("GRR reproducibility var", grr$components["Reproducibility", "variance"], ref("gage_rr.var_reproducibility"))
check("GRR part var", grr$components["Part-to-Part", "variance"], ref("gage_rr.var_part"))
check("GRR %study var", grr$pct_study_var_grr, ref("gage_rr.pct_study_var_grr"))
check("GRR interaction p", grr$interaction_p, ref("gage_rr.interaction_p"), 1e-6)
check("GRR ndc", grr$ndc, ref("gage_rr.ndc"))

# DOE vs Python
d <- read.csv(file.path(data_dir, "doe_2k3.csv"))
design <- data.frame(A = d$A_temperature, B = d$B_pressure, C = d$C_time)
fx <- analyze_factorial(design, d$yield_pct)$effects
check("effect A", fx[["A"]], ref("doe.A")); check("effect B", fx[["B"]], ref("doe.B"))
check("effect A:B", fx[["A:B"]], ref("doe.A*B")); check("effect A:B:C", fx[["A:B:C"]], ref("doe.A*B*C"))
check("full_factorial rows", nrow(full_factorial(c("A", "B", "C"), 2)), 16)

# Welch t-test (built into R) vs Python
ts <- read.csv(file.path(data_dir, "two_sample.csv"))
w <- t.test(ts$before, ts$after)
check("Welch t", w$statistic, ref("welch_t.t")); check("Welch df", w$parameter, ref("welch_t.df"))
check("Welch p", w$p.value, ref("welch_t.p"), 1e-7)

# Pareto
pt <- pareto_table(setNames(read.csv(file.path(data_dir, "pareto.csv"))$count,
                            read.csv(file.path(data_dir, "pareto.csv"))$defect))
check("Pareto top category count", pt$count[1], 112)
check("Pareto vital few count", sum(pt$vital_few), 4)

cat(sprintf("\n%d failure(s)\n", failures))
if (failures > 0) quit(status = 1)
