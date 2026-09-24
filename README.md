# Financial Anomaly Detection — Benford's Law

A Streamlit tool that screens transaction data for signs of fabricated or manipulated
financial figures, using **Benford's Law** — a statistical pattern real auditors and
forensic accountants use as a first-pass fraud-risk signal.

## What it does

- Takes a transactions CSV (`vendor`, `amount` columns) and computes the leading-digit
  distribution of all transaction amounts.
- Compares that distribution against what Benford's Law predicts for naturally
  occurring financial data (digit 1 leads ~30% of the time, digit 9 leads <5% of the time).
- Runs a **chi-square goodness-of-fit test** per vendor to flag accounts whose amounts
  deviate significantly from the expected distribution — a common early screening
  technique in audit and forensic accounting.
- Visualizes observed vs. expected distribution and ranks vendors by deviation/risk.

## Why Benford's Law

People fabricating numbers tend to unconsciously use a more uniform spread of leading
digits than genuine, naturally-occurring transaction amounts do. Deviation from
Benford's Law doesn't prove fraud on its own, but it's a real, established way to
prioritize which accounts deserve closer manual review — used in actual forensic
accounting and IT audit work.

## Running it locally

```bash
pip install -r requirements.txt
python generate_data.py      # creates a sample dataset at data/transactions.csv
streamlit run app.py
```

Then open the local URL Streamlit prints (usually `http://localhost:8501`).

Upload your own CSV (needs `vendor` and `amount` columns) or use the bundled sample
dataset, which has a handful of vendors with deliberately fabricated-looking amounts
injected, to demonstrate the detector working.

## Project structure

```
├── app.py             # Streamlit dashboard
├── benford.py          # Core Benford's Law analysis (digit distribution, chi-square test, risk scoring)
├── generate_data.py    # Generates a synthetic sample dataset with injected anomalies
├── data/
│   └── transactions.csv
└── requirements.txt
```

## Tech stack

Python, Pandas, NumPy, SciPy (chi-square test), Plotly, Streamlit

## Limitations

- The chi-square test is noisy on vendors with very few transactions (fewer than
  ~8-10), so those are excluded from risk scoring.
- Deviation from Benford's Law is a *screening signal*, not proof of fraud — real
  audit work would follow up flagged accounts with manual review, not act on this
  alone.
