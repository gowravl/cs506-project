# Project Quick Reference
## Respiratory Disease Prediction from Environmental Factors
**Team:** Gowrav Lakshmipathy | Priya Dilip Bajaria | Nandini Nandan Narvekar

---

## Why We Changed the Dataset from New York to United States

The original proposal specified New York City as the geographic scope.
During data collection we discovered three problems that made NYC-level data
impractical:

**1. No daily respiratory count data exists for NYC at the required granularity.**
The NYC EpiQuery syndromic surveillance portal provides monthly aggregates,
not daily counts. A monthly target variable cannot be matched to daily
environmental readings from EPA.

**2. The best available daily respiratory data is national.**
The CDC NSSP dataset provides daily % of ED visits for Acute Respiratory Illness
at the US national level with complete daily coverage from September 2022 onwards.
No equivalent daily city-level dataset exists as a free public download anywhere.

**3. EPA air quality data aggregates naturally to national scale.**
The EPA AQS datasets contain readings from thousands of monitoring stations
across all 50 states. Averaging to a national daily value is statistically
robust (2,000+ stations per day for PM2.5). Filtering to NYC alone would give
fewer than 10 stations with inconsistent daily coverage.

**The scope change makes the project stronger, not weaker.**
A national model is more generalizable, uses more data, and avoids the
sparse-coverage problems of a single-city approach. The research question
— whether environmental conditions predict respiratory illness — is the same.

---

## Report Reference Guide

### data_profiling_report.md
**What it covers:** Phase 1 — inspection of all 6 raw datasets before any cleaning.

For each dataset it documents shape, date range, missing values, duplicates,
value distributions, and outlier counts. Every issue found is listed with an
assessment of whether it is real or an artifact. Ends with a cleaning decision
table that maps each finding to a specific planned fix.

**Key findings to mention:**
- Temperature had a sentinel value of -1,177°F (instrument firmware error)
- Humidity file contained two mixed parameters (RH % and Dew Point °F)
- PM2.5 had 10,148 negative values from sensor calibration errors
- NSSP data starts September 2022, 9 months later than EPA data

---

### data_cleaning_report.md
**What it covers:** Phase 2 — actual cleaning operations applied, with before/after counts.

Documents every row removed from every dataset and the exact justification
referencing the profiling finding. Includes visual verification that cleaning
preserved real signal (wildfire spike in PM2.5 before/after comparison).
Ends with the final master dataset specification.

**Key findings to mention:**
- Hard physical bounds used for temperature (-80°F to 140°F) — percentile cap
  would have missed the sentinel value
- Humidity dew point rows removed before averaging — without this step,
  the national average would be meaningless
- Respiratory data was NOT interpolated — health outcome gaps may be real
  reporting failures, not sensor noise
- Master dataset: 1,133 rows, Sep 25 2022 to Oct 31 2025, zero missing values

---

### eda_report.md
**What it covers:** Phase 3 — exploratory analysis of the cleaned master dataset.

Covers correlation analysis, scatter plots by season, seasonal decomposition,
monthly distributions, lag correlation analysis (0-14 days), dual-axis overlays,
90-day rolling correlations, and day-of-week effect quantification.
Ends with the feature engineering plan used to create the modeling dataset.

**Key findings to mention:**
- 81.4% of all variance in respiratory illness is explained by seasonality alone
- Temperature is the strongest predictor at r = -0.812
- NO2 and Ozone improve to r = 0.743 and -0.732 when lagged 12-13 days
- Rolling correlation shows NO2 and Ozone flip sign seasonally — their overall
  correlations are driven by shared seasonality, not independent daily effects
- PM2.5 is the weakest feature (r = -0.142) due to wildfire seasonal confounding

---

### modeling_report.md
**What it covers:** Phase 4 — baseline linear regression for the March check-in.

Two models trained: environmental features only (Model A) and full feature set
including month and day-of-week (Model B). Documents all coefficients, residual
analysis, and a detailed diagnosis of why test R² is negative.

**Key findings to mention:**
- Train R²: 0.79 — the model learns the seasonal pattern in training data
- Test R²: -0.70 — negative because test set is summer-only (distribution shift)
- The time-ordered 80/20 split is methodologically correct for time series but
  produced a test set that covers only spring-summer 2025 (low-illness season)
- Root cause is not model failure — it is a mismatch between train and test
  seasonal distributions
- Fix for April: cyclic month encoding (sin/cos), time-series cross-validation,
  Random Forest and XGBoost

---

## One-Line Summary Per Phase

| Phase | Report | One line |
|---|---|---|
| 1 — Profiling | data_profiling_report.md | Inspected all 6 raw datasets and documented every issue before touching any data |
| 2 — Cleaning | data_cleaning_report.md | Applied targeted fixes to each dataset based on profiling findings; produced clean 1,133-row master |
| 3 — EDA | eda_report.md | Found seasonality explains 81.4% of variance; identified 12-13 day lags for NO2 and Ozone |
| 4 — Modeling | modeling_report.md | Baseline linear regression; train R²=0.79; test R² negative due to summer-only test split |

---

## Files Produced

| File | Description |
|---|---|
| data/raw/\*/\*.csv | Original unmodified EPA and NSSP source files |
| data/processed/pm25_daily.csv | Cleaned national daily PM2.5 average |
| data/processed/no2_daily.csv | Cleaned national daily NO2 average |
| data/processed/ozone_daily.csv | Cleaned national daily Ozone average |
| data/processed/temperature_daily.csv | Cleaned national daily Temperature average |
| data/processed/humidity_daily.csv | Cleaned national daily Relative Humidity average |
| data/processed/respiratory_daily.csv | Cleaned daily ARI % ED visits (US) |
| data/processed/master_daily.csv | Merged dataset — 1,133 rows, 12 columns |
| data/processed/features_daily.csv | Engineered features — 1,119 rows, 14 columns |
| outputs/figures/profile_\*.png | Profiling distribution plots |
| outputs/figures/eda_\*.png | EDA correlation, scatter, lag, rolling plots |
| outputs/figures/model_\*.png | Actual vs predicted, residuals, coefficients |

---

## Notebooks

| Notebook | Purpose |
|---|---|
| data_profiling.ipynb | Inspect raw datasets, identify all issues |
| data_cleaning.ipynb | Apply targeted cleaning, produce master_daily.csv |
| eda.ipynb | Correlation, lag, seasonal decomposition, feature engineering |
| models.ipynb | Baseline linear regression, March check-in results |
