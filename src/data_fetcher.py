"""
Data fetcher module for CPI Nowcaster.
Downloads economic data from FRED.
"""

import os
import pandas as pd
from fredapi import Fred


def get_fred_client():
    """
    Initialize the FRED API client.
    Checks for FRED_API_KEY in environment variables.
    """
    api_key = os.getenv("FRED_API_KEY")
    if not api_key:
        raise ValueError(
            "FRED_API_KEY not found. Set it in your terminal with:\n"
            '  $env:FRED_API_KEY="your-key-here"\n'
            "Then try again."
        )
    return Fred(api_key=api_key)


def fetch_data(start_date="2010-01-01"):
    """
    Fetch all required data series from FRED.

    Parameters:
        start_date (str): Start date in 'YYYY-MM-DD' format.

    Returns:
        dict: Dictionary with keys 'monthly' and 'daily', each containing a DataFrame.
    """
    fred = get_fred_client()

    # Series marked True are required — a fetch failure raises immediately.
    # Series marked False are optional — logged and skipped if unavailable.
    monthly_series = {
        "CPIAUCSL": (True,  "Consumer Price Index (All Urban Consumers)"),
        "UNRATE":   (True,  "Civilian Unemployment Rate"),
        "INDPRO":   (True,  "Industrial Production Index"),
        "PAYEMS":   (True,  "All Employees: Total Nonfarm Payrolls"),
        "RSAFS":    (False, "Advance Retail Sales: Retail Trade"),
        "PPIACO":   (False, "Producer Price Index: All Commodities"),
        "HOUST":    (False, "Housing Starts: Total New Privately Owned"),
        "MICH":     (False, "U of Michigan: 1-Year Inflation Expectation"),
        "AHETPI":   (False, "Average Hourly Earnings: Total Private"),
    }

    print("=" * 50)
    print("FETCHING MONTHLY DATA FROM FRED")
    print("=" * 50)

    monthly_data = {}
    for series_id, (required, description) in monthly_series.items():
        try:
            series = fred.get_series(series_id, observation_start=start_date)
            monthly_data[series_id] = series
            print(f"  [OK] {series_id}: {description}")
        except Exception as e:
            if required:
                raise RuntimeError(f"Failed to fetch required series {series_id}: {e}") from e
            print(f"  [SKIP] {series_id}: {e}")

    df_monthly = pd.DataFrame(monthly_data)
    df_monthly.index = pd.to_datetime(df_monthly.index)
    df_monthly = df_monthly.resample("MS").last()

    if df_monthly.empty:
        raise RuntimeError("Monthly DataFrame is empty after fetch — no data was returned.")
    if "CPIAUCSL" not in df_monthly.columns or df_monthly["CPIAUCSL"].dropna().empty:
        raise RuntimeError("CPIAUCSL (CPI target) has no data — cannot train model.")

    daily_series = {
        "T10YIE":     (True,  "10-Year Breakeven Inflation Rate"),
        "T5YIE":      (False, "5-Year Breakeven Inflation Rate"),
        "DTWEXBGS":   (True,  "Trade Weighted U.S. Dollar Index: Broad"),
        "DCOILWTICO": (True,  "Crude Oil: West Texas Intermediate (WTI)"),
        "DHHNGSP":    (False, "Henry Hub Natural Gas Spot Price"),
    }

    print("\n" + "=" * 50)
    print("FETCHING DAILY DATA FROM FRED")
    print("=" * 50)

    daily_data = {}
    for series_id, (required, description) in daily_series.items():
        try:
            series = fred.get_series(series_id, observation_start=start_date)
            daily_data[series_id] = series
            print(f"  [OK] {series_id}: {description}")
        except Exception as e:
            if required:
                raise RuntimeError(f"Failed to fetch required series {series_id}: {e}") from e
            print(f"  [SKIP] {series_id}: {e}")

    df_daily = pd.DataFrame(daily_data)
    df_daily.index = pd.to_datetime(df_daily.index)

    if df_daily.empty:
        raise RuntimeError("Daily DataFrame is empty after fetch — no data was returned.")

    print("\n" + "=" * 50)
    print("DATA FETCH COMPLETE")
    print("=" * 50)
    print(f"  Monthly data shape: {df_monthly.shape}")
    print(f"  Daily data shape:   {df_daily.shape}")

    return {"monthly": df_monthly, "daily": df_daily}


if __name__ == "__main__":
    data = fetch_data()

    print("\n" + "=" * 50)
    print("PREVIEW: Monthly Data (last 5 rows)")
    print("=" * 50)
    print(data["monthly"].tail())

    print("\n" + "=" * 50)
    print("PREVIEW: Daily Data (last 5 rows)")
    print("=" * 50)
    print(data["daily"].tail())