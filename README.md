# Job Market Demand Forecasting + ROI Attribution

Forecasts salary/demand trends for data & AI roles in India using live job-market
data, tests whether a real market event actually caused a measurable shift using
causal inference, and translates the finding into an estimated business value —
not just "here's a model," but "here's what the model is worth."

**Live demo:** https://job-demand-roi-project-yac2awztd4vgftjbyms6pk.streamlit.app/

## Problem

Most ML portfolios stop at a trained model's accuracy. This project goes one step
further: does the model's insight translate into money, and is any observed
pattern real or just noise? Those are the two questions most portfolios skip,
and the two most enterprise AI initiatives fail to answer according to
McKinsey's 2025 State of AI report (only 6% of AI-using organizations can
attribute measurable EBIT impact to it).

## Data

Pulled live from [Adzuna's public API](https://developer.adzuna.com/) — real
monthly average-salary trends and current vacancy counts for Data Scientist,
Data Analyst, ML Engineer, AI Engineer, Python Developer, and Business Analyst
roles in India. Not a static Kaggle file — `src/fetch_data.py` re-pulls current
data on every run.

**Data quality finding:** Adzuna's salary-history endpoint returned 12 months of
real data for Data Analyst, Python Developer, and Business Analyst, but zero
months for Data Scientist, ML Engineer, and AI Engineer — despite those roles
having the *highest* current vacancy counts (10,051 and 9,266 openings
respectively). This reflects genuinely low salary-transparency in job postings
for newer/specialized AI roles in India's market. The forecasting model uses the
3 roles with real history; all 6 appear in the demand snapshot.

## Methodology

1. **Forecasting** — a pooled lag-regression model (role as a categorical
   feature + lag-1, lag-2, 3-month rolling average), validated with a proper
   walk-forward split. Achieved **2.17% MAPE**. Prophet was tested and rejected:
   with only 12 months of data, its "yearly seasonality" component swung
   ±Rs 3-4 crore — over 30x the entire real salary range — clear evidence it
   was fitting noise, not a real pattern.

2. **Causal analysis** — tested whether a real, reported event (a June 2026
   industry report of a 28-month low in Indian tech hiring, with TCS/Infosys/
   Wipro adding near-zero net headcount) actually shifted Python Developer
   salaries, using a synthetic control built from Business Analyst + Data
   Analyst (fit on pre-event data only). Found a real divergence 2 months
   post-event (+Rs 45,602 and +Rs 57,829 — 7-8x the normal noise band),
   validated with a placebo test on a fake earlier event date (which produced
   only small, noise-level gaps). Interesting finding: salaries rose, not fell
   — consistent with reported "fewer, pricier hires" behavior in a selective
   hiring market.

3. **ROI translation** — a scenario calculator estimating the value of acting
   on this signal 2 months early vs. a typical 4-month reactive comp-review
   cycle, using cited India-specific 2026 benchmarks (22.5% IT attrition,
   37% of exits being compensation-driven, Rs 7.5L replacement cost). Result:
   ~Rs 6,688 per employee per year — a deliberately modest, defensible
   estimate, not an inflated headline number.

## Honest limitations

- 12 months of data is thin for any time-series method; the walk-forward
  validation and the Prophet stress-test are both there specifically to avoid
  overclaiming on limited data.
- The causal analysis uses one treated series against a 2-series control over
  a short window — suggestive evidence, not definitive proof.
- The ROI calculator is a cited scenario model, not measured company data —
  labeled as such throughout.

## Tech stack

Python, pandas, scikit-learn, Prophet, matplotlib/seaborn, Streamlit, Adzuna API

## How to run

```bash
pip install -r requirements.txt
python src/fetch_data.py        # pulls live data, needs a free Adzuna API key in .env
jupyter notebook notebooks/full_walkthrough.ipynb   # full analysis, explained step by step
streamlit run dashboard/app.py  # interactive dashboard
```