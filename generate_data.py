"""
Generates a synthetic transactions dataset for the Benford's Law audit demo.

Most amounts are drawn from a realistic, naturally-occurring distribution
(so their leading digits follow Benford's Law). A handful of vendors are
deliberately given fabricated-looking amounts (e.g. round numbers, or
digit patterns that violate Benford's Law) to simulate what manipulated
or fraudulent invoices might look like -- these are the ones the app
should flag.
"""

import numpy as np
import pandas as pd

np.random.seed(42)

N_NORMAL = 950
N_SUSPICIOUS = 50

vendors_normal = [f"Vendor_{i:03d}" for i in range(1, 61)]
vendors_suspicious = [f"Vendor_{i:03d}" for i in range(61, 66)]  # 5 "shady" vendors

rows = []

# Naturally occurring transaction amounts: a log-normal distribution
# genuinely produces leading digits that follow Benford's Law closely,
# similar to real invoice/expense amounts.
normal_amounts = np.round(np.random.lognormal(mean=7.5, sigma=1.3, size=N_NORMAL), 2)
for i, amt in enumerate(normal_amounts):
    rows.append({
        "transaction_id": f"TXN{10000 + i}",
        "vendor": np.random.choice(vendors_normal),
        "amount": float(amt),
        "date": pd.Timestamp("2025-01-01") + pd.to_timedelta(np.random.randint(0, 300), unit="D"),
    })

# Suspicious amounts: fabricated numbers people invent tend to overuse
# certain leading digits (5, 6, 7) and round numbers -- a classic
# real-world fraud signature that breaks Benford's expected distribution.
suspicious_leading_digits = [5, 6, 7, 8, 9]
for i in range(N_SUSPICIOUS):
    leading = np.random.choice(suspicious_leading_digits)
    amt = float(f"{leading}{np.random.randint(0, 999):03d}") * np.random.choice([1, 10, 100])
    rows.append({
        "transaction_id": f"TXN{20000 + i}",
        "vendor": np.random.choice(vendors_suspicious),
        "amount": round(amt, 2),
        "date": pd.Timestamp("2025-01-01") + pd.to_timedelta(np.random.randint(0, 300), unit="D"),
    })

df = pd.DataFrame(rows).sample(frac=1, random_state=1).reset_index(drop=True)
df.to_csv("data/transactions.csv", index=False)
print(f"Generated {len(df)} transactions -> data/transactions.csv")
