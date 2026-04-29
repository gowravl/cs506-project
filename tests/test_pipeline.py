"""
Smoke tests for the CS 506 respiratory prediction pipeline.
Reads the committed processed CSVs — no raw data or notebook execution required.
"""
import numpy as np
import pandas as pd
import pytest
from pathlib import Path
from sklearn.linear_model import RidgeCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score

ROOT = Path(__file__).parent.parent
MASTER   = ROOT / "data/processed/master_daily.csv"
FEATURES = ROOT / "data/processed/features_daily.csv"


@pytest.fixture(scope="module")
def master():
    return pd.read_csv(MASTER, parse_dates=["date"])


@pytest.fixture(scope="module")
def features():
    return pd.read_csv(FEATURES, parse_dates=["date"])


# master_daily.csv

def test_master_shape(master):
    assert master.shape == (1133, 12), f"Expected (1133, 12), got {master.shape}"


def test_master_no_missing(master):
    assert master.isnull().sum().sum() == 0, "master_daily.csv has missing values"


def test_master_date_range(master):
    assert master["date"].min().date().isoformat() == "2022-09-25"
    assert master["date"].max().date().isoformat() == "2025-10-31"


def test_target_range(master):
    lo, hi = master["pct_respiratory"].min(), master["pct_respiratory"].max()
    assert lo >= 0,   f"pct_respiratory has negative values: min={lo}"
    assert hi <= 100, f"pct_respiratory exceeds 100%: max={hi}"
    assert lo >= 5,   f"pct_respiratory implausibly low: {lo}"
    assert hi <= 35,  f"pct_respiratory implausibly high: {hi}"


def test_temperature_range(master):
    lo, hi = master["temperature"].min(), master["temperature"].max()
    assert lo > 0,   f"National average temperature below 0°F: {lo}"
    assert hi < 100, f"National average temperature above 100°F: {hi}"


def test_humidity_range(master):
    assert master["humidity"].between(0, 100).all(), "Humidity values outside 0-100%"


def test_pollutants_non_negative(master):
    for col in ["pm25", "no2", "ozone"]:
        assert (master[col] >= 0).all(), f"{col} has negative values"


# features_daily.csv

def test_features_shape(features):
    # 1133 master rows minus 14 dropped for pm25_lag14 NaN
    assert features.shape[0] == 1119, f"Expected 1119 rows, got {features.shape[0]}"


def test_features_no_missing(features):
    assert features.isnull().sum().sum() == 0, "features_daily.csv has missing values"


def test_cyclic_encoding(features):
    # sin² + cos² must equal 1 for every row
    total = features["month_sin"] ** 2 + features["month_cos"] ** 2
    assert np.allclose(total, 1.0, atol=1e-9), "Cyclic encoding violates sin²+cos²=1"


def test_lag_alignment(features):
    # Row 0 of features is 2022-10-09 (14 days after master start 2022-09-25).
    # pm25_lag14 on that row should equal the pm25 value from 2022-09-25 in master.
    master = pd.read_csv(MASTER, parse_dates=["date"])
    expected_pm25 = master.loc[master["date"] == "2022-09-25", "pm25"].iloc[0]
    actual_lag = features.iloc[0]["pm25_lag14"]
    assert abs(actual_lag - expected_pm25) < 1e-6, (
        f"pm25_lag14 mismatch: expected {expected_pm25}, got {actual_lag}"
    )


# Model smoke test

def test_ridge_positive_holdout_r2(features):
    LINEAR_FEATURES = [
        "temperature", "humidity", "no2_lag12", "ozone_lag13", "pm25_lag14",
        "month_sin", "month_cos", "day_of_week", "is_weekend",
    ]
    SPLIT_DATE = pd.Timestamp("2024-10-31")
    split_idx = features[features["date"] <= SPLIT_DATE].shape[0]

    X = features[LINEAR_FEATURES].values
    y = features["pct_respiratory"].values

    sc = StandardScaler()
    X_tr = sc.fit_transform(X[:split_idx])
    X_te = sc.transform(X[split_idx:])

    ridge = RidgeCV(alphas=[0.1, 1.0, 10.0, 100.0, 1000.0])
    ridge.fit(X_tr, y[:split_idx])

    r2 = r2_score(y[split_idx:], ridge.predict(X_te))
    assert r2 > 0.5, f"Ridge holdout R² = {r2:.3f}, expected > 0.5"
