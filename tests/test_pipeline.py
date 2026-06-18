"""
Pipeline robustness tests.
Run with: pytest tests/
"""

import json
import os
import sys
import pytest
import numpy as np
import pandas as pd
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from model import prepare_training_data


# --- Helpers ---

def _make_monthly(n=60):
    """Minimal monthly DataFrame with required series."""
    idx = pd.date_range("2015-01-01", periods=n, freq="MS")
    return pd.DataFrame({
        "CPIAUCSL": np.linspace(250, 310, n),
        "UNRATE":   np.random.uniform(3, 8, n),
        "INDPRO":   np.random.uniform(95, 110, n),
        "PAYEMS":   np.random.uniform(140000, 160000, n),
    }, index=idx)


def _make_daily(n=1500):
    idx = pd.date_range("2015-01-01", periods=n, freq="B")
    return pd.DataFrame({
        "T10YIE":     np.random.uniform(1, 3, n),
        "DTWEXBGS":   np.random.uniform(95, 130, n),
        "DCOILWTICO": np.random.uniform(40, 100, n),
    }, index=idx)


def _make_labels(monthly_df):
    cpi = monthly_df["CPIAUCSL"].dropna()
    return (cpi.pct_change(periods=12) * 100).dropna()


# --- Fix 1/2: fetch failures ---

def test_required_series_failure_raises():
    """A RuntimeError must be raised when a required FRED series fails."""
    from data_fetcher import fetch_data

    def fake_get_series(series_id, observation_start=None):
        if series_id == "CPIAUCSL":
            raise ConnectionError("FRED API timeout")
        return pd.Series(np.ones(100), index=pd.date_range("2015-01-01", periods=100, freq="MS"))

    mock_fred = MagicMock()
    mock_fred.get_series.side_effect = fake_get_series

    with patch("data_fetcher.get_fred_client", return_value=mock_fred):
        with pytest.raises(RuntimeError, match="required series CPIAUCSL"):
            fetch_data()


def test_optional_series_failure_is_skipped():
    """An optional series failure should be logged and skipped, not raised."""
    from data_fetcher import fetch_data

    monthly_idx = pd.date_range("2015-01-01", periods=100, freq="MS")
    daily_idx = pd.date_range("2015-01-01", periods=1500, freq="B")

    def fake_get_series(series_id, observation_start=None):
        if series_id == "MICH":
            raise ConnectionError("unavailable")
        if series_id in ("CPIAUCSL", "UNRATE", "INDPRO", "PAYEMS", "RSAFS",
                         "PPIACO", "HOUST", "AHETPI"):
            return pd.Series(np.ones(100), index=monthly_idx)
        return pd.Series(np.ones(1500), index=daily_idx)

    mock_fred = MagicMock()
    mock_fred.get_series.side_effect = fake_get_series

    with patch("data_fetcher.get_fred_client", return_value=mock_fred):
        data = fetch_data()

    assert "MICH" not in data["monthly"].columns
    assert not data["monthly"].empty


# --- Fix 4: NaN handling ---

def test_all_nan_column_is_dropped():
    """A feature column that is entirely NaN should be dropped, not filled."""
    monthly = _make_monthly()
    daily = _make_daily()
    labels = _make_labels(monthly)

    from ragged_edge import get_latest_available
    ragged = get_latest_available("2019-12-15", monthly, daily)

    # Inject a column that is completely NaN
    ragged["FAKE_SERIES"] = np.nan

    X, y, feature_names = prepare_training_data(ragged, labels)

    assert "FAKE_SERIES" not in feature_names
    assert not X.isnull().any().any(), "X should have no NaNs after cleaning"


def test_too_few_rows_raises():
    """Pipeline must raise if fewer than 12 usable training rows remain."""
    monthly = _make_monthly(n=10)  # Only 10 months — not enough after lag creation
    daily = _make_daily(n=100)
    labels = _make_labels(monthly)

    from ragged_edge import get_latest_available
    ragged = get_latest_available("2015-10-15", monthly, daily)

    with pytest.raises(RuntimeError, match="Not enough training rows"):
        prepare_training_data(ragged, labels)


# --- Fix 3: failure JSON ---

def test_pipeline_failure_writes_error_json(tmp_path, monkeypatch):
    """When the pipeline crashes, a JSON with an error field must be written."""
    import nowcast

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(nowcast, "fetch_data", MagicMock(side_effect=RuntimeError("FRED down")))

    with pytest.raises(RuntimeError):
        nowcast.run_nowcast()

    result_path = tmp_path / "data" / "nowcast.json"
    assert result_path.exists(), "nowcast.json should be written even on failure"

    with open(result_path) as f:
        result = json.load(f)

    assert result["nowcast"] is None
    assert "error" in result
