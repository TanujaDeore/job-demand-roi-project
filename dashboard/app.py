"""
Interactive dashboard: job-market demand/salary trends, causal finding,
and ROI scenario calculator.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from roi_calculator import roi_calculator

st.set_page_config(page_title="Job Market Demand + ROI", layout="wide")
st.title("Job Market Demand Forecasting + ROI")
st.caption("Real data pulled from Adzuna's live API -- India tech/data roles")


@st.cache_data
def load_data():
    trend = pd.read_csv("../data/raw/adzuna_india_job_trends.csv")
    trend["month"] = pd.to_datetime(trend["month"])
    snap = pd.read_csv("../data/raw/adzuna_india_current_vacancies.csv")
    return trend, snap


trend_df, snap_df = load_data()
roles_with_history = sorted(trend_df["role"].unique())

# --- Section 1: current demand snapshot ---
st.header("1. Current demand snapshot")
colors = ["crimson" if r not in roles_with_history else "steelblue" for r in snap_df["role"]]
fig1, ax1 = plt.subplots(figsize=(9, 4))
ax1.bar(snap_df["role"], snap_df["current_open_vacancies"], color=colors)
ax1.set_ylabel("Open Vacancies")
ax1.set_title("Red = no salary history available from Adzuna")
plt.xticks(rotation=30, ha="right")
st.pyplot(fig1)

# --- Section 2: salary trend ---
st.header("2. Salary trend (roles with real history)")
selected_role = st.selectbox("Highlight a role", roles_with_history)

fig2, ax2 = plt.subplots(figsize=(9, 4))
for role in roles_with_history:
    subset = trend_df[trend_df["role"] == role].sort_values("month")
    lw = 3 if role == selected_role else 1
    alpha = 1.0 if role == selected_role else 0.4
    ax2.plot(subset["month"], subset["avg_salary_inr"], marker="o", label=role, linewidth=lw, alpha=alpha)
ax2.set_ylabel("Avg Salary (INR)")
ax2.legend()
plt.xticks(rotation=45)
st.pyplot(fig2)

# --- Section 3: causal finding (Python Developer) ---
st.header("3. Causal finding: did the June 2026 hiring slowdown shift Python Developer pay?")
st.markdown(
    "A June 2026 report found Indian tech job openings hit a 28-month low, with TCS/Infosys/Wipro "
    "adding near-zero net headcount. We tested this against Python Developer salary using a synthetic "
    "control built from Business Analyst + Data Analyst."
)

wide_df = trend_df.pivot(index="month", columns="role", values="avg_salary_inr").sort_index()
pre_df = wide_df.loc[:"2026-05-01"]
X_pre, y_pre = pre_df[["business analyst", "data analyst"]], pre_df["python developer"]
sc_model = LinearRegression().fit(X_pre, y_pre)
wide_df["synthetic"] = sc_model.predict(wide_df[["business analyst", "data analyst"]])

fig3, ax3 = plt.subplots(figsize=(9, 4))
ax3.plot(wide_df.index, wide_df["python developer"], marker="o", label="Actual", color="steelblue")
ax3.plot(wide_df.index, wide_df["synthetic"], marker="o", linestyle="--", label="Synthetic control", color="gray")
ax3.axvline(pd.Timestamp("2026-06-01"), color="red", linestyle=":", label="June 2026 slowdown reported")
ax3.legend()
plt.xticks(rotation=45)
st.pyplot(fig3)

latest_gap_pct = ((wide_df.loc["2026-08-01":, "python developer"] - wide_df.loc["2026-08-01":, "synthetic"])
                   / wide_df.loc["2026-08-01":, "synthetic"]).mean()
st.metric("Measured post-event pay gap (Aug-Sep avg)", f"{latest_gap_pct:.2%}")

# --- Section 4: ROI calculator ---
st.header("4. ROI scenario calculator")
st.caption("Scenario estimate using cited India 2026 benchmarks -- not measured company data")

team_size = st.slider("Team size (Python Developers)", 10, 200, 50)
latest_salary = wide_df.loc["2026-09-01", "python developer"]

result = roi_calculator(team_size=team_size, avg_annual_salary=latest_salary, pay_gap_pct=latest_gap_pct)

c1, c2, c3 = st.columns(3)
c1.metric("At-risk employees/year", result["at_risk_employees_per_year"])
c2.metric("Cost avoided", f"Rs {result['cost_avoided_inr']:,}")
c3.metric("Net ROI", f"Rs {result['net_roi_inr']:,}")