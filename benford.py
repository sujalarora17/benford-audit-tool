"""
Benford's Law analysis.

Benford's Law observes that in many naturally occurring collections of
numbers (transaction amounts, populations, physical constants), the
leading digit is not uniformly distributed -- digit 1 appears as the
leading digit about 30% of the time, digit 9 less than 5% of the time.
Auditors use deviation from this expected distribution as a screening
signal for manipulated or fabricated financial data: humans making up
numbers tend to use a much more uniform spread of leading digits than
naturally-occurring transaction amounts do.

This module computes the expected vs. observed leading-digit distribution
for a set of amounts, runs a chi-square goodness-of-fit test, and derives
a simple deviation-based risk score per vendor.
"""

import numpy as np
import pandas as pd
from scipy.stats import chisquare

# Benford's Law expected proportion for each leading digit 1-9
BENFORD_EXPECTED = {d: np.log10(1 + 1 / d) for d in range(1, 10)}


def leading_digit(amount: float) -> int:
    """Return the first significant digit of a positive amount."""
    amount = abs(amount)
    if amount == 0:
        return 0
    while amount < 1:
        amount *= 10
    while amount >= 10:
        amount /= 10
    return int(amount)


def digit_distribution(amounts: pd.Series) -> pd.DataFrame:
    """Observed vs. expected leading-digit distribution for a set of amounts."""
    digits = amounts.apply(leading_digit)
    digits = digits[digits.between(1, 9)]
    counts = digits.value_counts().reindex(range(1, 10), fill_value=0).sort_index()
    observed_pct = counts / counts.sum()
    expected_pct = pd.Series(BENFORD_EXPECTED)
    return pd.DataFrame({
        "digit": range(1, 10),
        "observed_count": counts.values,
        "observed_pct": observed_pct.values,
        "expected_pct": expected_pct.values,
    })


def chi_square_test(amounts: pd.Series):
    """
    Chi-square goodness-of-fit test comparing observed leading-digit
    counts against Benford's expected distribution.
    Returns (chi2_statistic, p_value). A low p-value (< 0.05) suggests
    the amounts deviate significantly from Benford's Law.
    """
    dist = digit_distribution(amounts)
    observed = dist["observed_count"].values
    total = observed.sum()
    expected = dist["expected_pct"].values * total
    return chisquare(f_obs=observed, f_exp=expected)


def vendor_risk_scores(df: pd.DataFrame, vendor_col="vendor", amount_col="amount", min_txns=8):
    """
    Per-vendor risk score based on how far that vendor's leading-digit
    distribution deviates from Benford's Law (mean absolute deviation
    between observed and expected proportions, in percentage points).
    Vendors with fewer than `min_txns` transactions are excluded --
    small samples are too noisy for this test to be meaningful.
    """
    results = []
    for vendor, group in df.groupby(vendor_col):
        if len(group) < min_txns:
            continue
        dist = digit_distribution(group[amount_col])
        mad = (dist["observed_pct"] - dist["expected_pct"]).abs().mean() * 100
        chi2, pval = chi_square_test(group[amount_col])
        results.append({
            "vendor": vendor,
            "transaction_count": len(group),
            "mean_abs_deviation_pct": round(mad, 2),
            "chi2_statistic": round(chi2, 2),
            "p_value": round(pval, 4),
            "flagged": pval < 0.05,
        })
    return pd.DataFrame(results).sort_values("mean_abs_deviation_pct", ascending=False)
