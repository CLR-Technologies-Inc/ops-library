# opex_stats.R: Six Sigma and SPC statistics in base R (no packages required).
#
#   source("opex_stats.R")
#
# Functions mirror the Python opex_stats package, so results match across tools:
#   chart_factors(n)            control chart constants (d2, d3, c4, A2, A3, D3, D4, B3, B4)
#   capability_study(x, ...)    Cp, Cpk, Pp, Ppk, Cpm, expected ppm, sigma level
#   sigma_table(), dpmo(), sigma_level_from_dpmo(), dpmo_from_sigma_level(), rty()
#   imr_chart(x), xbar_r_chart(m), xbar_s_chart(m)
#   p_chart(d, n), np_chart(d, n), c_chart(d), u_chart(d, n)
#   run_rules(points, cl, ucl, lcl)
#   gage_rr_anova(part, operator, y, tolerance)
#   full_factorial(k), analyze_factorial(design, y)
#   anderson_darling(x), pareto_table(counts)
#   plot_control_chart(chart), plot_pareto(tab)
#
# Hypothesis tests come built into R: t.test(), var.test(), aov(), chisq.test(), lm().

SIGMA_SHIFT <- 1.5

# ---------------------------------------------------------------- constants

.d3_table <- c(0.8525, 0.8884, 0.8798, 0.8641, 0.8480, 0.8332, 0.8198, 0.8078, 0.7971,
               0.7873, 0.7785, 0.7704, 0.7630, 0.7562, 0.7499, 0.7441, 0.7386, 0.7335,
               0.7287, 0.7242, 0.7199, 0.7159, 0.7121, 0.7084)  # n = 2..25

d2 <- function(n) {
  stopifnot(n >= 2)
  integrate(function(x) 1 - (1 - pnorm(x))^n - pnorm(x)^n, -Inf, Inf)$value
}

c4 <- function(n) sqrt(2 / (n - 1)) * exp(lgamma(n / 2) - lgamma((n - 1) / 2))

chart_factors <- function(n) {
  stopifnot(n >= 2, n <= 25)
  .d2 <- d2(n); .d3 <- .d3_table[n - 1]; .c4 <- c4(n)
  b <- 3 * sqrt(1 - .c4^2) / .c4
  list(n = n, d2 = .d2, d3 = .d3, c4 = .c4,
       A2 = 3 / (.d2 * sqrt(n)), A3 = 3 / (.c4 * sqrt(n)),
       D3 = max(0, 1 - 3 * .d3 / .d2), D4 = 1 + 3 * .d3 / .d2,
       B3 = max(0, 1 - b), B4 = 1 + b)
}

# --------------------------------------------------------------- capability

sigma_within_mr <- function(x) mean(abs(diff(x))) / d2(2)

sigma_within_subgroups <- function(m) mean(apply(m, 1, function(r) diff(range(r)))) / d2(ncol(m))

.indices <- function(mu, s, lsl, usl, target) {
  out <- list()
  if (!is.null(lsl) && !is.null(usl)) out$Cp <- (usl - lsl) / (6 * s)
  if (!is.null(usl)) out$CPU <- (usl - mu) / (3 * s)
  if (!is.null(lsl)) out$CPL <- (mu - lsl) / (3 * s)
  out$Cpk <- min(unlist(out[intersect(names(out), c("CPU", "CPL"))]))
  if (!is.null(target) && !is.null(lsl) && !is.null(usl))
    out$Cpm <- (usl - lsl) / (6 * sqrt(s^2 + (mu - target)^2))
  out
}

expected_ppm <- function(mu, s, lsl = NULL, usl = NULL) {
  below <- if (is.null(lsl)) 0 else pnorm((lsl - mu) / s) * 1e6
  above <- if (is.null(usl)) 0 else pnorm((usl - mu) / s, lower.tail = FALSE) * 1e6
  c(below = below, above = above, total = below + above)
}

# x: vector of individual values, or a matrix with one subgroup per row
capability_study <- function(x, lsl = NULL, usl = NULL, target = NULL) {
  stopifnot(!is.null(lsl) || !is.null(usl))
  if (is.matrix(x)) {
    s_within <- sigma_within_subgroups(x); v <- as.vector(t(x))
  } else {
    v <- as.numeric(x); s_within <- sigma_within_mr(v)
  }
  mu <- mean(v); s_overall <- sd(v)
  w <- .indices(mu, s_within, lsl, usl, target)
  o <- .indices(mu, s_overall, lsl, usl, target)
  ppm_o <- expected_ppm(mu, s_overall, lsl, usl)
  lo <- if (is.null(lsl)) -Inf else lsl
  hi <- if (is.null(usl)) Inf else usl
  list(n = length(v), mean = mu, sigma_within = s_within, sigma_overall = s_overall,
       Cp = w$Cp, Cpk = w$Cpk, Cpm = w$Cpm, Pp = o$Cp, Ppk = o$Cpk,
       observed_ppm = mean(v < lo | v > hi) * 1e6,
       expected_ppm_within = expected_ppm(mu, s_within, lsl, usl),
       expected_ppm_overall = ppm_o,
       sigma_level_overall = sigma_level_from_dpmo(ppm_o[["total"]]))
}

dpmo <- function(defects, units, opportunities = 1) defects / (units * opportunities) * 1e6
sigma_level_from_dpmo <- function(d, shift = SIGMA_SHIFT) qnorm(1 - d / 1e6) + shift
dpmo_from_sigma_level <- function(level, shift = SIGMA_SHIFT) pnorm(level - shift, lower.tail = FALSE) * 1e6
rty <- function(yields) prod(yields)

sigma_table <- function(levels = 1:7, shift = SIGMA_SHIFT) {
  d <- dpmo_from_sigma_level(levels, shift)
  data.frame(sigma_level = levels, with_shift = levels - shift, dpmo = d,
             pct_defective = d / 1e4, pct_yield = 100 - d / 1e4,
             cpk_short_term = levels / 3, cpk_long_term = (levels - shift) / 3)
}

# ----------------------------------------------------------- control charts

# Western Electric / Nelson rules 1-4. Returns a data frame of (index, rule).
run_rules <- function(points, cl, ucl, lcl, rules = 1:4) {
  n <- length(points)
  ucl <- rep_len(ucl, n); lcl <- rep_len(lcl, n)
  hits <- data.frame(index = integer(0), rule = integer(0))
  add <- function(i, r) hits <<- rbind(hits, data.frame(index = i, rule = r))
  if (1 %in% rules) for (i in which(points > ucl | points < lcl)) add(i, 1L)
  if (2 %in% rules && n >= 9) for (i in 9:n) {
    w <- points[(i - 8):i]
    if (all(w > cl) || all(w < cl)) add(i, 2L)
  }
  if (3 %in% rules && n >= 6) for (i in 6:n) {
    dw <- diff(points[(i - 5):i])
    if (all(dw > 0) || all(dw < 0)) add(i, 3L)
  }
  if (4 %in% rules && n >= 14) for (i in 14:n) {
    dw <- diff(points[(i - 13):i])
    if (all(dw != 0) && all(diff(sign(dw)) != 0)) add(i, 4L)
  }
  hits[order(hits$index, hits$rule), , drop = FALSE]
}

.chart <- function(name, points, cl, ucl, lcl, rules = 1:4)
  list(chart = name, points = points, cl = cl, ucl = ucl, lcl = lcl,
       signals = run_rules(points, cl, ucl, lcl, rules))

imr_chart <- function(x) {
  f <- chart_factors(2)
  mr <- abs(diff(x)); mr_bar <- mean(mr); s <- mr_bar / f$d2; xb <- mean(x)
  list(individuals = .chart("I", x, xb, xb + 3 * s, xb - 3 * s),
       moving_range = .chart("MR", mr, mr_bar, f$D4 * mr_bar, f$D3 * mr_bar, rules = 1),
       sigma_within = s)
}

# m: matrix, one subgroup per row
xbar_r_chart <- function(m) {
  f <- chart_factors(ncol(m))
  means <- rowMeans(m); ranges <- apply(m, 1, function(r) diff(range(r)))
  xdb <- mean(means); rb <- mean(ranges)
  list(xbar = .chart("Xbar", means, xdb, xdb + f$A2 * rb, xdb - f$A2 * rb),
       range = .chart("R", ranges, rb, f$D4 * rb, f$D3 * rb, rules = 1),
       sigma_within = rb / f$d2)
}

xbar_s_chart <- function(m) {
  f <- chart_factors(ncol(m))
  means <- rowMeans(m); sds <- apply(m, 1, sd)
  xdb <- mean(means); sb <- mean(sds)
  list(xbar = .chart("Xbar", means, xdb, xdb + f$A3 * sb, xdb - f$A3 * sb),
       stdev = .chart("S", sds, sb, f$B4 * sb, f$B3 * sb, rules = 1),
       sigma_within = sb / f$c4)
}

p_chart <- function(defective, n) {
  pb <- sum(defective) / sum(n); h <- 3 * sqrt(pb * (1 - pb) / n)
  .chart("p", defective / n, pb, pmin(1, pb + h), pmax(0, pb - h))
}

np_chart <- function(defective, n) {
  pb <- sum(defective) / (length(defective) * n); cl <- n * pb; h <- 3 * sqrt(cl * (1 - pb))
  .chart("np", defective, cl, cl + h, max(0, cl - h))
}

c_chart <- function(defects) {
  cb <- mean(defects); .chart("c", defects, cb, cb + 3 * sqrt(cb), max(0, cb - 3 * sqrt(cb)))
}

u_chart <- function(defects, units) {
  ub <- sum(defects) / sum(units); h <- 3 * sqrt(ub / units)
  .chart("u", defects / units, ub, ub + h, pmax(0, ub - h))
}

plot_control_chart <- function(ch, main = paste(ch$chart, "chart")) {
  x <- seq_along(ch$points)
  rng <- range(c(ch$points, ch$ucl, ch$lcl))
  plot(x, ch$points, type = "b", pch = 19, col = "#1f4e79", ylim = rng,
       xlab = "Sample", ylab = ch$chart, main = main)
  if (length(ch$ucl) > 1) {
    lines(x, ch$ucl, type = "s", lty = 2, col = "#c00000")
    lines(x, ch$lcl, type = "s", lty = 2, col = "#c00000")
  } else abline(h = c(ch$ucl, ch$lcl), lty = 2, col = "#c00000")
  abline(h = ch$cl, col = "#548235")
  flagged <- unique(ch$signals$index)
  points(flagged, ch$points[flagged], col = "#c00000", pch = 19, cex = 1.6)
}

# ----------------------------------------------------------------- Gage R&R

# Crossed study, ANOVA method (AIAG MSA). Interaction is pooled when p > 0.25.
gage_rr_anova <- function(part, operator, y, tolerance = NULL, k = 6, pool_alpha = 0.25) {
  part <- factor(part); operator <- factor(operator)
  p <- nlevels(part); o <- nlevels(operator)
  counts <- table(part, operator)
  stopifnot(length(unique(as.vector(counts))) == 1)
  r <- counts[1, 1]
  full <- anova(lm(y ~ part * operator))
  ms <- full[["Mean Sq"]]; names(ms) <- rownames(full)
  int_p <- full["part:operator", "Pr(>F)"]
  pooled <- int_p > pool_alpha
  if (pooled) {
    red <- anova(lm(y ~ part + operator))
    ms_e <- red["Residuals", "Mean Sq"]
    v_rep <- ms_e; v_int <- 0
    v_op <- max(0, (red["operator", "Mean Sq"] - ms_e) / (p * r))
    v_part <- max(0, (red["part", "Mean Sq"] - ms_e) / (o * r))
    table_out <- red
  } else {
    ms_i <- ms[["part:operator"]]; ms_e <- ms[["Residuals"]]
    v_rep <- ms_e; v_int <- max(0, (ms_i - ms_e) / r)
    v_op <- max(0, (ms[["operator"]] - ms_i) / (p * r))
    v_part <- max(0, (ms[["part"]] - ms_i) / (o * r))
    table_out <- full
    # Part and operator are tested against the interaction in the crossed random model
    table_out["part", "F value"] <- ms[["part"]] / ms_i
    table_out["part", "Pr(>F)"] <- pf(ms[["part"]] / ms_i, p - 1, (p - 1) * (o - 1), lower.tail = FALSE)
    table_out["operator", "F value"] <- ms[["operator"]] / ms_i
    table_out["operator", "Pr(>F)"] <- pf(ms[["operator"]] / ms_i, o - 1, (p - 1) * (o - 1), lower.tail = FALSE)
  }
  v_repro <- v_op + v_int; v_grr <- v_rep + v_repro; v_tot <- v_grr + v_part
  var <- c("Total Gage R&R" = v_grr, Repeatability = v_rep, Reproducibility = v_repro,
           Operator = v_op, "Part x Operator" = v_int, "Part-to-Part" = v_part,
           "Total Variation" = v_tot)
  comp <- data.frame(variance = var, pct_contribution = 100 * var / v_tot, stdev = sqrt(var),
                     study_var = k * sqrt(var), pct_study_var = 100 * sqrt(var / v_tot))
  if (!is.null(tolerance)) comp$pct_tolerance <- 100 * k * sqrt(var) / tolerance
  pct_sv <- 100 * sqrt(v_grr / v_tot)
  list(anova = table_out, interaction_p = int_p, interaction_pooled = pooled,
       components = comp, ndc = floor(1.41 * sqrt(v_part / v_grr)),
       pct_study_var_grr = pct_sv,
       verdict = if (pct_sv < 10) "acceptable" else if (pct_sv <= 30)
         "marginal: may be acceptable depending on the application and cost" else
         "unacceptable: improve the measurement system")
}

# ---------------------------------------------------------------------- DOE

# 2^k design in standard order, coded -1/+1
full_factorial <- function(factors = c("A", "B", "C"), replicates = 1, randomize = FALSE) {
  k <- length(factors)
  base <- as.data.frame(sapply(seq_len(k), function(j) ifelse(((0:(2^k - 1)) %/% 2^(j - 1)) %% 2 == 1, 1, -1)))
  names(base) <- factors
  d <- do.call(rbind, lapply(seq_len(replicates), function(rep)
    cbind(std_order = seq_len(2^k), replicate = rep, base)))
  if (randomize) d <- d[sample(nrow(d)), ]
  d$run_order <- seq_len(nrow(d))
  rownames(d) <- NULL
  d
}

# Effects (difference of means, high minus low) plus the full lm() fit
analyze_factorial <- function(design, y, factors = setdiff(names(design), c("std_order", "replicate", "run_order"))) {
  f <- as.formula(paste("y ~", paste(factors, collapse = " * ")))
  fit <- lm(f, data = cbind(design[factors], y = y))
  coefs <- coef(fit)[-1]
  list(fit = fit, effects = 2 * coefs, coefficients = coefs, summary = summary(fit))
}

# ------------------------------------------------------------------ others

anderson_darling <- function(x) {
  x <- sort(x); n <- length(x); stopifnot(n >= 8)
  z <- pmin(pmax(pnorm((x - mean(x)) / sd(x)), 1e-15), 1 - 1e-15)
  i <- seq_len(n)
  a2 <- -n - sum((2 * i - 1) * (log(z) + log(1 - rev(z)))) / n
  a2s <- a2 * (1 + 0.75 / n + 2.25 / n^2)
  p <- if (a2s >= 0.6) exp(1.2937 - 5.709 * a2s + 0.0186 * a2s^2) else
    if (a2s >= 0.34) exp(0.9177 - 4.279 * a2s - 1.38 * a2s^2) else
    if (a2s >= 0.2) 1 - exp(-8.318 + 42.796 * a2s - 59.938 * a2s^2) else
    1 - exp(-13.436 + 101.14 * a2s - 223.73 * a2s^2)
  list(n = n, a2 = a2, a2_adjusted = a2s, p = min(max(p, 0), 1))
}

# counts: named numeric vector
pareto_table <- function(counts, cutoff = 80) {
  counts <- counts[order(-counts, names(counts))]
  pct <- 100 * counts / sum(counts); cum <- cumsum(pct)
  data.frame(category = names(counts), count = as.numeric(counts), percent = as.numeric(pct),
             cumulative_percent = as.numeric(cum),
             vital_few = c(0, head(as.numeric(cum), -1)) < cutoff, row.names = NULL)
}

plot_pareto <- function(tab, main = "Pareto chart") {
  op <- par(mar = c(7, 4, 3, 4)); on.exit(par(op))
  b <- barplot(tab$count, names.arg = tab$category, las = 2, col = "#1f4e79",
               ylim = c(0, sum(tab$count)), main = main, ylab = "Count")
  lines(b, tab$cumulative_percent / 100 * sum(tab$count), type = "b", pch = 19, col = "#c00000")
  axis(4, at = seq(0, 1, 0.2) * sum(tab$count), labels = paste0(seq(0, 100, 20), "%"))
  abline(h = 0.8 * sum(tab$count), lty = 3, col = "grey50")
}
