"""opex_stats: Six Sigma and SPC statistics using only the Python standard library.

Modules
-------
capability      Cp, Cpk, Pp, Ppk, Cpm, DPMO, sigma level, yield
control_charts  I-MR, X-bar/R, X-bar/S, p, np, c, u charts and run rules
gage_rr         Crossed Gauge R&R (ANOVA method)
doe             Two-level full and fractional factorial designs and analysis
hypothesis      t-tests, ANOVA, F-test, chi-square, simple regression
normality       Anderson-Darling normality test
pareto          Pareto analysis
constants       Control chart constants (d2, d3, c4, A2, A3, D3, D4, B3, B4)
distributions   Normal, t, F, and chi-square distributions

Plotting functions need matplotlib; everything else needs nothing beyond Python 3.10+.
"""

__version__ = "0.1.0"
