"""
Streamlit dashboard: Financial Anomaly Detection using Benford's Law.

Upload a transactions CSV (columns: vendor, amount, ...) and the app
flags vendors whose transaction amounts deviate significantly from the
leading-digit distribution predicted by Benford's Law -- a real
screening technique used in forensic accounting and audit to surface
accounts worth a closer look.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from benford import chi_square_test, digit_distribution, vendor_risk_scores

st.set_page_config(page_title="Benford's Law Audit Tool", layout="wide")

st.title("Financial Anomaly Detection — Benford's Law")
st.caption(
    "Flags vendors/accounts whose transaction amounts deviate from the leading-digit "
    "distribution Benford's Law predicts for naturally occurring financial data."
)

uploaded = st.file_uploader("Upload a transactions CSV (needs `vendor` and `amount` columns)", type="csv")
df = pd.read_csv(uploaded) if uploaded else pd.read_csv("data/transactions.csv")

if uploaded is None:
    st.info("No file uploaded — showing the bundled sample dataset (`data/transactions.csv`).")

col1, col2, col3 = st.columns(3)
col1.metric("Total transactions", len(df))
col2.metric("Total vendors", df["vendor"].nunique())
chi2, pval = chi_square_test(df["amount"])
col3.metric("Overall dataset p-value", f"{pval:.4f}", help="p < 0.05 suggests the dataset overall deviates from Benford's Law")

st.subheader("Overall leading-digit distribution: observed vs. expected")
dist = digit_distribution(df["amount"])
fig = go.Figure()
fig.add_bar(x=dist["digit"], y=dist["observed_pct"], name="Observed")
fig.add_scatter(x=dist["digit"], y=dist["expected_pct"], name="Benford Expected", mode="lines+markers")
fig.update_layout(xaxis_title="Leading digit", yaxis_title="Proportion of transactions", xaxis=dict(dtick=1))
st.plotly_chart(fig, use_container_width=True)

st.subheader("Vendor risk ranking")
st.caption("Vendors sorted by deviation from Benford's Law. Flagged = statistically significant deviation (p < 0.05).")
risk_df = vendor_risk_scores(df)
st.dataframe(
    risk_df.style.apply(
        lambda row: ["background-color: #ffe0e0" if row["flagged"] else "" for _ in row], axis=1
    ),
    use_container_width=True,
)

flagged = risk_df[risk_df["flagged"]]
if len(flagged):
    st.warning(f"{len(flagged)} vendor(s) flagged for further review: {', '.join(flagged['vendor'])}")
else:
    st.success("No vendors show statistically significant deviation from Benford's Law.")

with st.expander("What is Benford's Law, and why does this matter for audit?"):
    st.markdown(
        """
        Benford's Law observes that in many naturally occurring sets of numbers
        (invoice amounts, expense claims, population figures), the **leading digit**
        is not uniformly distributed. The digit 1 appears first about **30%** of the
        time, while 9 appears first less than **5%** of the time.

        When someone fabricates or manipulates financial figures, they tend to
        (often unconsciously) use a much more uniform spread of leading digits than
        genuine transaction data does. Auditors and forensic accountants use
        deviation from Benford's Law as a **screening signal** — not proof of fraud
        by itself, but a way to prioritize which accounts or vendors deserve a
        closer manual look.

        This tool automates that first screening pass: upload a transactions
        export, and it ranks vendors by how much their amounts deviate from the
        expected distribution, using a chi-square goodness-of-fit test.
        """
    )
