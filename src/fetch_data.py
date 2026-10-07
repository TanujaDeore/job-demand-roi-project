"""
Pulls real monthly average-salary trend data (+ current open-vacancy snapshot)
for several tech/data roles in India, directly from Adzuna's live public API.
Reads credentials from .env -- never hardcode keys in this file.
"""

import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()  # reads the .env file in the project root

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")
COUNTRY = "in"  # India

if not APP_ID or not APP_KEY:
    raise ValueError("Missing ADZUNA_APP_ID or ADZUNA_APP_KEY -- check your .env file")

ROLES = [
    "data scientist",
    "data analyst",
    "machine learning engineer",
    "ai engineer",
    "python developer",
    "business analyst",
]

BASE_URL = f"https://api.adzuna.com/v1/api/jobs/{COUNTRY}"


def fetch_history():
    """Real monthly average-salary trend per role."""
    rows = []
    for role in ROLES:
        resp = requests.get(
            f"{BASE_URL}/history",
            params={"app_id": APP_ID, "app_key": APP_KEY, "what": role},
        )
        resp.raise_for_status()
        month_data = resp.json().get("month", {})
        for month, avg_salary in month_data.items():
            rows.append({"role": role, "month": month, "avg_salary_inr": avg_salary})
        print(f"[history] {role}: {len(month_data)} months fetched")
        time.sleep(1)
    return pd.DataFrame(rows)


def fetch_snapshot():
    """Current open-vacancy count per role, right now."""
    rows = []
    for role in ROLES:
        resp = requests.get(
            f"{BASE_URL}/search/1",
            params={"app_id": APP_ID, "app_key": APP_KEY, "what": role, "results_per_page": 1},
        )
        resp.raise_for_status()
        count = resp.json().get("count")
        rows.append({"role": role, "current_open_vacancies": count})
        print(f"[snapshot] {role}: {count} open vacancies right now")
        time.sleep(1)
    return pd.DataFrame(rows)


if __name__ == "__main__":
    trend_df = fetch_history()
    trend_df.to_csv("data/raw/adzuna_india_job_trends.csv", index=False)
    print(f"\nSaved data/raw/adzuna_india_job_trends.csv -- {trend_df.shape}")

    snap_df = fetch_snapshot()
    snap_df.to_csv("data/raw/adzuna_india_current_vacancies.csv", index=False)
    print(f"Saved data/raw/adzuna_india_current_vacancies.csv -- {snap_df.shape}")
