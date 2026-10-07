"""
ROI scenario calculator: translates early demand/salary-shift detection into
an estimated business value, using India-specific 2026 benchmarks.

Cited assumptions (all overridable):
- IT sector attrition in India, 2026: 20-25% (Aon / ACEngage / SalaryBox) -> 22.5% midpoint
- Share of attrition that's compensation-driven: 37% (Taggd Decoding Jobs Report 2026,
  based on 10,000+ exit interviews)
- Replacement cost per mid-level hire: Rs 7.5 lakh (SalaryBox India, 2025)
"""


def roi_calculator(
    team_size,
    avg_annual_salary,
    pay_gap_pct,
    reactive_lag_months=4,
    proactive_lead_months=2,
    it_attrition_rate=0.225,
    pay_driven_share=0.37,
    replacement_cost=750_000,
):
    """
    Estimates the net value of acting on an early demand/salary-shift signal
    `proactive_lead_months` months into a shift, versus a reactive company that
    only adjusts compensation after `reactive_lag_months`.

    Both the benefit (avoided replacement cost) and the cost (targeted retention
    raise) are scoped to the same at-risk population -- employees whose likely
    departure reason is compensation misalignment -- not the whole team.
    """
    avoided_months = max(reactive_lag_months - proactive_lead_months, 0)
    monthly_pay_driven_attrition = (it_attrition_rate * pay_driven_share) / 12

    prevented_departures = team_size * monthly_pay_driven_attrition * avoided_months
    cost_avoided = prevented_departures * replacement_cost

    annual_at_risk_count = team_size * it_attrition_rate * pay_driven_share
    months_remaining = 12 - proactive_lead_months
    cost_of_targeted_raise = annual_at_risk_count * avg_annual_salary * pay_gap_pct * (months_remaining / 12)

    net_roi = cost_avoided - cost_of_targeted_raise

    return {
        "at_risk_employees_per_year": round(annual_at_risk_count, 2),
        "prevented_departures": round(prevented_departures, 2),
        "cost_avoided_inr": round(cost_avoided),
        "cost_of_targeted_raise_inr": round(cost_of_targeted_raise),
        "net_roi_inr": round(net_roi),
    }


if __name__ == "__main__":
    # Quick sanity-check run using our actual measured findings
    result = roi_calculator(team_size=100, avg_annual_salary=1_288_796, pay_gap_pct=0.0407)
    for k, v in result.items():
        print(f"{k}: {v:,}")