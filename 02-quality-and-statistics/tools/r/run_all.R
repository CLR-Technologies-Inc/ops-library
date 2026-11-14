# Run every tool on the sample data and print the results.
#   Rscript run_all.R           (from this folder)
#   Rscript run_all.R --plots   also writes output/*.png

source("opex_stats.R")
data_dir <- file.path("..", "data")
heading <- function(s) cat("\n", s, "\n", strrep("-", nchar(s)), "\n", sep = "")

x <- read.csv(file.path(data_dir, "capability.csv"))$diameter_mm
heading("Process capability (LSL 9.9, USL 10.1, target 10.0)")
cap <- capability_study(x, lsl = 9.9, usl = 10.1, target = 10)
print(unlist(cap[c("n", "mean", "sigma_within", "sigma_overall", "Cp", "Cpk", "Cpm", "Pp", "Ppk",
                   "sigma_level_overall")]))
print(cap$expected_ppm_overall)
print(unlist(anderson_darling(x)))

heading("Sigma level table")
print(sigma_table(), digits = 8)

heading("I-MR chart")
imr <- imr_chart(x)
cat(sprintf("I:  CL %.4f UCL %.4f LCL %.4f\n", imr$individuals$cl, imr$individuals$ucl, imr$individuals$lcl))
print(imr$individuals$signals)

heading("X-bar / R chart")
sg <- read.csv(file.path(data_dir, "subgroups.csv"))
xr <- xbar_r_chart(matrix(sg$diameter_mm, ncol = 5, byrow = TRUE))
cat(sprintf("Xbar: CL %.4f UCL %.4f LCL %.4f | R: CL %.4f UCL %.4f\n", xr$xbar$cl, xr$xbar$ucl,
            xr$xbar$lcl, xr$range$cl, xr$range$ucl))

heading("p chart")
att <- read.csv(file.path(data_dir, "attribute.csv"))
pc <- p_chart(att$defective, att$inspected)
print(pc$signals)

heading("Gauge R&R (ANOVA method, tolerance 4.0)")
g <- read.csv(file.path(data_dir, "gage_rr.csv"))
grr <- gage_rr_anova(g$part, g$operator, g$measurement, tolerance = 4)
print(grr$anova)
print(round(grr$components, 4))
cat("ndc =", grr$ndc, "|", grr$verdict, "\n")

heading("2^3 factorial (doe_2k3.csv)")
d <- read.csv(file.path(data_dir, "doe_2k3.csv"))
res <- analyze_factorial(data.frame(A = d$A_temperature, B = d$B_pressure, C = d$C_time), d$yield_pct)
print(res$summary$coefficients)
cat("Effects:\n"); print(res$effects)

heading("Before vs after (Welch and paired t-tests)")
ts <- read.csv(file.path(data_dir, "two_sample.csv"))
print(t.test(ts$before, ts$after))
print(t.test(ts$after, ts$before, paired = TRUE))

heading("Pareto")
pd <- read.csv(file.path(data_dir, "pareto.csv"))
pt <- pareto_table(setNames(pd$count, pd$defect))
print(pt)

if ("--plots" %in% commandArgs(trailingOnly = TRUE)) {
  dir.create("output", showWarnings = FALSE)
  png("output/imr.png", width = 1000, height = 700)
  par(mfrow = c(2, 1)); plot_control_chart(imr$individuals, "Individuals")
  plot_control_chart(imr$moving_range, "Moving range"); dev.off()
  png("output/p_chart.png", width = 1000, height = 400); plot_control_chart(pc); dev.off()
  png("output/pareto.png", width = 1000, height = 500); plot_pareto(pt); dev.off()
  cat("\nCharts saved to output/\n")
}
