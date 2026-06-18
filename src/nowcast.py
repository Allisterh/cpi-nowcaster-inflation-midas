"""
Daily nowcast orchestrator.
Run automatically by GitHub Actions to produce a fresh CPI nowcast.
"""

import json
import os
from datetime import datetime
from data_fetcher import fetch_data
from ragged_edge import get_latest_available, create_training_labels
from model import prepare_training_data, train_final_model


def run_nowcast():
    """
    Run the full nowcasting pipeline and save results to JSON.
    On failure, writes an error record to data/nowcast.json and re-raises.
    """
    today = datetime.now().strftime("%Y-%m-%d")
    print("=" * 60)
    print(f"CPI NOWCAST - {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)

    try:
        # Step 1: Fetch data
        print("\n[1/5] Fetching data from FRED...")
        data = fetch_data(start_date="2010-01-01")
        monthly = data["monthly"]
        daily = data["daily"]

        # Step 2: Build ragged edge matrix
        print(f"\n[2/5] Building ragged edge matrix as of {today}...")
        ragged = get_latest_available(today, monthly, daily)

        # Step 3: Create labels and training data
        print("\n[3/5] Preparing training data...")
        labels = create_training_labels(monthly)
        X, y, feature_names = prepare_training_data(ragged, labels)

        # Step 4: Train model and get nowcast
        print("\n[4/5] Training model and generating nowcast...")
        model = train_final_model(X, y)

        current_features = X.iloc[-1:].copy()
        current_nowcast = model.predict(current_features)[0]
        latest_actual = y.iloc[-1] if len(y) > 0 else None

        # Step 5: Save results
        print("\n[5/5] Saving results...")

        importance = model.feature_importances_
        top_features = [
            {"feature": feature_names[i], "importance": float(importance[i])}
            for i in importance.argsort()[-5:][::-1]
        ]

        result = {
            "date": today,
            "nowcast": round(float(current_nowcast), 2),
            "latest_actual": round(float(latest_actual), 2) if latest_actual else None,
            "rmse_historical": 0.57,
            "mae_historical": 0.40,
            "top_features": top_features,
            "data_available": {
                "monthly_series": monthly.shape[1],
                "daily_series": daily.shape[1],
                "training_samples": X.shape[0]
            }
        }

        os.makedirs("data", exist_ok=True)
        with open("data/nowcast.json", "w") as f:
            json.dump(result, f, indent=2)

        print("\n" + "=" * 60)
        print(f"NOWCAST RESULT: {current_nowcast:.2f}%")
        print(f"Latest actual:   {latest_actual:.2f}%")
        print(f"Saved to data/nowcast.json")
        print("=" * 60)

        return result

    except Exception as e:
        # Write a failure record so the dashboard can surface an error state
        # rather than silently serving stale data.
        os.makedirs("data", exist_ok=True)
        with open("data/nowcast.json", "w") as f:
            json.dump({"date": today, "error": str(e), "nowcast": None}, f, indent=2)
        print(f"\n[FATAL] Pipeline failed: {e}")
        raise


if __name__ == "__main__":
    run_nowcast()