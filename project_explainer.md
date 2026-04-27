# Project Explainer — Complete Personal Reference
## Respiratory Disease Prediction from Environmental Factors
**Team:** Gowrav Lakshmipathy | Priya Dilip Bajaria | Nandini Nandan Narvekar

*This document is my go-to reference for explaining every decision, number, and change in this project. Organized by notebook, then by likely question.*

---

## Table of Contents

1. [Project Summary (30-second version)](#1-project-summary)
2. [Data Sources](#2-data-sources)
3. [Notebook 1 — Data Profiling](#3-notebook-1--data-profiling)
4. [Notebook 2 — Data Cleaning](#4-notebook-2--data-cleaning)
5. [Notebook 3 — EDA](#5-notebook-3--eda)
6. [Notebook 4 — Modeling](#6-notebook-4--modeling)
7. [Changes from Check-In 1 (March)](#7-changes-from-check-in-1-march)
8. [All Key Numbers in One Place](#8-all-key-numbers-in-one-place)
9. [Likely Professor Questions — Full Answers](#9-likely-professor-questions--full-answers)

---

## 1. Project Summary

**What:** Predict the daily percentage of US emergency department visits attributed to Acute Respiratory Illness (ARI), using environmental data — temperature, humidity, NO₂, ozone, and PM2.5.

**Why it matters:** Respiratory illness is one of the top drivers of ED utilization. If you can predict surges from environmental data (temperature dropping, pollution rising), hospitals can pre-staff and public health systems can issue advisories.

**Data:** 3 years of daily national data (Sep 2022 – Oct 2025). 1,133 days after cleaning and inner-joining all datasets.

**Target variable:** `pct_respiratory` — the fraction of US ED visits that are ARI on a given day. Ranges from 7.09% (summer trough) to 26.58% (winter peak). A 3.7× seasonal swing.

**Best result:** Ridge Regression. Leave-last-year-out holdout test R² = **0.687**, RMSE = **2.39 percentage points**.

**Pipeline:** 4 notebooks in order: `data_profiling.ipynb` → `data_cleaning.ipynb` → `eda.ipynb` → `models.ipynb`

---

## 2. Data Sources

| Dataset | Source | File format | Granularity | Coverage |
|---|---|---|---|---|
| PM2.5 | EPA AQS `daily_88101_YYYY.csv` | One row per station per day | ~2,000 stations/day nationally | 2022–2025 |
| NO₂ | EPA AQS `daily_42602_YYYY.csv` | One row per station per hour | ~500 stations/day, urban-weighted | 2022–2025 |
| Ozone | EPA AQS `daily_44201_YYYY.csv` | One row per station per 8-hour window | ~1,200 stations/day | 2022–2025 |
| Temperature | EPA AQS `daily_TEMP_YYYY.csv` | One row per station per day | ~1,000 stations/day | 2022–2025 |
| Humidity | EPA AQS `daily_RH_DP_YYYY.csv` | Mixed: RH (%) and Dew Point (°F) in same file | ~600 stations/day | 2022–2025 |
| Respiratory illness | CDC NSSP | One row per pathogen per geography per day | National; multiple pathogens | Sep 2022–Oct 2025 |

**Why EPA AQS and CDC NSSP (not NYC data):** The original project proposal described NYC-specific data. The actual project pivoted to national EPA and CDC data because national coverage gives far more monitoring stations, more representative averages, and a longer date range than any single city's reporting. The README documents this scope change.

**Why national averages instead of city-level:** Respiratory illness surveillance data from CDC NSSP is published at the national level (pct_respiratory is US-wide). Matching it to city-level air quality would require an assumption about which city's air most influences national-level illness — not defensible. National-to-national is the correct pairing.

---

## 3. Notebook 1 — Data Profiling

**File:** `data_profiling.ipynb`  
**Purpose:** Understand each dataset *before* touching it. Identify issues, decide what to do about them, document those decisions. No data was modified in this notebook.

### What the profiling did

For each of the 6 datasets, it computed:
- Shape (rows × columns)
- Date range and gaps
- Value distribution (min, percentiles, max, mean, std)
- Specific issue checks (negatives, extreme values, duplicates, unparseable dates)
- Station coverage (how many stations report per day)

### Key findings per dataset

**PM2.5:**
- 2,915,841 raw rows. After aggregating: 1,412 unique dates across all years.
- 10,148 negative readings found — impossible (concentration can't be negative), caused by sensor calibration errors.
- 192 values above 200 µg/m³ — confirmed as real 2023 Canadian wildfire readings. Do NOT drop these.
- Max AQI value of 1,513 found — but we use `Arithmetic Mean` (raw concentration), not AQI, so irrelevant.
- Decision: drop negatives, cap at 99.5th percentile (preserves wildfire readings), use `format='mixed'` for dates.

**NO₂:**
- 562,605 raw rows. Hourly sampling (not daily like PM2.5).
- 3,254 negative readings — impossible. Drop.
- Max 64 ppb — below EPA 1-hour standard of 100 ppb. No extreme outliers.
- Structurally different from PM2.5: averaging across hours AND stations, urban-weighted (NO₂ monitors cluster near traffic).

**Ozone:**
- 1,412,282 raw rows. 8-hour running average per station.
- Only 18 negatives — cleanest pollutant dataset.
- Max 0.136 ppm observed; EPA 8-hour standard is 0.070 ppm. The observed max exceeds standard but is real.
- Final national daily average (0.045 ppm max) is well below the standard because it averages across all stations nationally.

**Temperature:**
- 1 sentinel value at −1,177.67°F — below absolute zero. Firmware error code. Drop.
- 79 values above 140°F — surface radiant heat artifacts (sensors on hot rooftops). Drop.
- 100% Fahrenheit confirmed. No unit conversion needed.
- Used physical bounds instead of percentile cap because extreme values here are definitively errors, not real measurements.

**Humidity:**
- Raw file contains BOTH Relative Humidity (%) AND Dew Point (°F) rows mixed together.
- Profiling found minimum value of −25% — impossible for humidity. Cause: Dew Point rows (which are in °F, not %) being mixed into the analysis.
- Fix: filter to RH rows only (`Parameter Name == 'Relative Humidity'`) before any analysis.
- After filtering, only 2 values above 100% (sensor calibration drift). Drop those.

**Respiratory (CDC NSSP):**
- 259,896 raw rows covering multiple pathogens (ARI, COVID, Flu, RSV, etc.) and multiple geographies (US, states, territories).
- Zero invalid values: no negatives, no values above 100%, zero IQR outliers.
- Decision: filter to `pathogen == 'ARI'` and `geography == 'United States'` (exact match, not contains()).
- Why ARI not COVID or Flu: ARI is the broadest respiratory category. Individual pathogens are subsets of ARI — using both would double-count.
- Why exact match for geography: `str.contains('United States')` with case-insensitive matching hit 'us' inside 'Massachusetts' and returned it as a false positive. Exact match required.

### Why we profile before cleaning

If you clean without profiling, you guess at what's wrong and may introduce new errors (clipping real values, dropping real rows). Profiling proves each cleaning decision is justified by actual data characteristics, not assumptions.

---

## 4. Notebook 2 — Data Cleaning

**File:** `data_cleaning.ipynb`  
**Purpose:** Apply exactly the cleaning decisions documented in profiling. Nothing improvised.

### Steps in order

| Step | What it does |
|---|---|
| Step 1 | Load all raw CSVs from each subdirectory |
| Step 2 | Clean PM2.5, NO₂, Ozone (negatives + percentile cap + date parse) |
| Step 3 | Clean Temperature (physical bounds) |
| Step 4 | Clean Humidity (filter to RH only, drop > 100%) |
| Step 5 | Clean Respiratory (filter ARI + United States) |
| Step 6 | Validate all 6 cleaned datasets (custom `validate()` function) |
| Step 7 | Save individual cleaned files to `data/processed/` |
| Step 8 | Merge all 6 into `master_daily.csv` via inner join on date |
| Step 9 | Visual verification (plot all variables, before/after PM2.5) |

### Critical implementation detail: percentile cap computed after date filter

The study period filter (`date >= 2022-09-25` and `date <= 2025-10-31`) is applied **before** computing the 99.5th percentile cap — not after. This matters because:
- If you compute the cap on the full raw dataset (Jan 2022 onward), the cap reflects values outside the study window.
- For PM2.5, this caused the cap to be 35.80 µg/m³ (full dataset) vs 38.00 µg/m³ (study period only).
- A cap of 35.80 would have incorrectly clipped real wildfire readings between 35.8 and 38.0 µg/m³ from the study period.
- Fix: filter first, then compute cap. The 38.00 µg/m³ cap now reflects only study-period distribution.

### Validation function

After each dataset is cleaned, `validate()` checks:
- No duplicate dates
- No missing values in key columns
- No negative values
- No humidity above 100%
- No temperature above 140°F (upper bound check added in revision)
- No respiratory above 100% (upper bound check added in revision)

All 6 datasets pass validation before merging.

### Merge result

Inner join on `date` across all 6 datasets. Only dates present in all 6 with non-null values are kept.

- **Start date:** 2022-09-25 — NSSP starts here, latest start among all datasets
- **End date:** 2025-10-31 — Temperature ends here, earliest end among all datasets
- **Rows:** 1,133 — exactly the number of calendar days from Sep 25, 2022 to Oct 31, 2025 inclusive
- **Columns:** 12 — date + 6 value columns + 5 station count columns (pm25_n_stations, no2_n_stations, ozone_n_stations, temp_n_stations, humidity_n_stations)

Station count columns were added (revision #3) because sparse-coverage days produce less representative national averages. Including station counts allows downstream analysis to weight or filter by data density.

### What was NOT done and why

| Skipped operation | Reason |
|---|---|
| Hard cap on PM2.5 > 200 µg/m³ | 192 values confirmed as real wildfire events in profiling |
| Interpolation of respiratory gaps | Target variable gaps may be real reporting failures; interpolating the outcome creates false signal |
| Smoothing weekly oscillation | Day-of-week pattern in ED visits is real behavioral signal, not noise |
| Temperature unit conversion | Profiling confirmed 100% Fahrenheit — no conversion needed |
| Imputing NO₂/Ozone end gap | Inner join handles coverage differences automatically |

### Final cleaned dataset statistics

| Variable | Min | Mean | Std | Max |
|---|---|---|---|---|
| pct_respiratory (%) | 7.09 | 13.24 | 4.08 | 26.58 |
| pm25 (µg/m³) | 3.58 | 7.61 | 2.05 | 21.15 |
| no2 (ppb) | 3.03 | 7.59 | 2.23 | 16.77 |
| ozone (ppm) | 0.019 | 0.032 | 0.006 | 0.045 |
| temperature (°F) | 21.81 | 57.72 | 14.58 | 80.90 |
| humidity (%) | 43.72 | 60.18 | 7.21 | 85.91 |

---

## 5. Notebook 3 — EDA

**File:** `eda.ipynb`  
**Input:** `data/processed/master_daily.csv` (1,133 rows, 12 columns)  
**Output:** `data/processed/features_daily.csv` (1,119 rows, 16 columns) + 3 figures

### Structure: 3 figures that answer 3 questions in sequence

| Figure | File | Question answered |
|---|---|---|
| 1 | `eda_01_time_series_key_relationships.png` | What do the dominant relationships look like over time? |
| 2 | `eda_02_lag_correlation_profiles.png` | Is there a delayed environmental effect, and for which features? |
| 3 | `eda_03_feature_correlation_ranking.png` | How strong is each feature at its best lag, ranked? |

### Figure 1 — Time Series

**Chart type:** Dual-axis line chart, 2 panels (stacked, shared x-axis).  
**Panel 1:** Respiratory % (left axis, red) + Temperature °F (right axis, blue)  
**Panel 2:** Respiratory % (left axis, red) + NO₂ ppb (right axis, orange)

**Why line chart:** Data is a 1,133-day consecutive time series. A line preserves temporal ordering and makes seasonal cycles immediately visible. Bar chart = 1,133 unreadable bars. Scatter = loses day-to-day connection.

**Why dual y-axis:** Respiratory % and temperature have incompatible units and scales. On a single axis, one signal would be collapsed to near-flat. Dual axis is necessary, not a visualization trick — both axes are labeled clearly and start/end anchored to their own min/max.

**Why temperature and NO₂ specifically:** Temperature (r = −0.812) is the strongest predictor. NO₂ (r = +0.640 at lag-0, rising to +0.743 at lag 12) illustrates the lag phenomenon. Ozone, humidity, PM2.5 all show patterns derivable from these two panels.

**Key findings:**
- Temperature and respiratory move in near-perfect inverse seasonal cycles. Every winter peak in illness = cold trough in temperature. Every summer trough = warm period. Near-mechanical relationship.
- The 2023 Canadian wildfire PM2.5 spike (Jun–Sep 2023) produces NO visible spike in respiratory illness. This directly foreshadows PM2.5 being a weak predictor.

### Figure 2 — Lag Correlation Profiles

**Chart type:** Single-panel line chart, one line per feature, x-axis = lag days (0–14), y-axis = Pearson r.

**Why lag analysis:** Environmental effects on health are often delayed. A person exposed to high NO₂ today doesn't necessarily go to the ED today — exposure leads to symptom onset, then care-seeking, over days. We test lags 0–14 to find the optimal delay.

**Why 0–14 days:** This covers the plausible biological window. Symptom onset for ARI typically 1–7 days; care-seeking delay adds more. Beyond 14 days, correlation is dominated by seasonal trend, not causal delay.

**How to read it:**
- Flat line across all lags → immediate relationship, no delay benefit (temperature, humidity)
- Rising curve peaking at lag N → delayed effect; use N-day lag in model
- Near-zero throughout → feature does not predict at any lag (PM2.5)

**Results:**

| Feature | Lag-0 r | Optimal lag | Best r | Improvement |
|---|---|---|---|---|
| Temperature (°F) | −0.812 | 0 days | −0.812 | None — immediate |
| Relative Humidity (%) | +0.530 | 0 days | +0.530 | None — immediate |
| NO₂ (ppb) | +0.640 | **12 days** | +0.743 | +0.103 |
| Ozone (ppm) | −0.656 | **13 days** | −0.732 | +0.076 |
| PM2.5 (µg/m³) | −0.142 | 14 days | −0.153 | +0.011 — negligible |

All p-values < 0.0001 across all features and all lags.

**Why are the lag improvements for NO₂ and ozone partially spurious?** Both NO₂ and ozone change slowly across the year (seasonal trend). A value at day N looks very similar to the value at day N+12 simply because both are in the same season. So part of the correlation improvement is the shared seasonal signal, not necessarily a causal 12-day delay. The EDA report acknowledges this. Both features are still included at their optimal lags because they provide real predictive value — but the lag magnitude may be overestimated due to this confound.

**Why PM2.5 is weak:** Seasonal confounding in the opposite direction. Wildfire smoke (summer) pushes PM2.5 up exactly when respiratory illness is at its annual low. This creates a negative correlation in the data, but it's spurious — wildfires don't protect against respiratory illness, the seasonal phasing just happens to align this way. The correlation is weak (r = −0.142) because the two effects partially cancel.

### Figure 3 — Feature Correlation Ranking

**Chart type:** Horizontal grouped bar chart.  
**What it shows:** For each feature, two bars side by side: lag-0 r and best-lag r. Sorted by best-lag |r| descending. Bars annotated with lag and r value.

**Why grouped bars over the other options:** Bar chart is the right choice for comparing a single metric (|r|) across discrete categories (features). Horizontal orientation because feature label text is long. Grouped (lag-0 vs best-lag) lets you see the improvement from lagging without needing to cross-reference Figure 2.

**Why this is the third figure and not the first:** The ranking is most meaningful after you've seen the time series (Figure 1) and the lag profiles (Figure 2). Knowing that temperature is #1 makes intuitive sense once you've seen the near-perfect inverse seasonal cycle.

### Feature engineering decisions

| Feature name | Source | Lag | Why |
|---|---|---|---|
| temperature | temperature | 0 | Strongest predictor (r = −0.812), immediate effect |
| humidity | humidity | 0 | r = +0.530, flat lag profile (no benefit from lagging) |
| no2_lag12 | no2 | 12 | r improves +0.103 from 0.640 → 0.743 |
| ozone_lag13 | ozone | 13 | r improves +0.076 from −0.656 → −0.732 |
| pm25_lag14 | pm25 | 14 | Weakest feature included for completeness |
| month | date | — | 81.4% of target variance is seasonal |
| month_sin | date | — | Cyclic encoding: sin(2π·month/12) |
| month_cos | date | — | Cyclic encoding: cos(2π·month/12) |
| day_of_week | date | — | Weekly oscillation in ED visits confirmed |
| is_weekend | date | — | Binary Sat/Sun indicator |
| season_num | date | — | 0=Winter, 1=Spring, 2=Summer, 3=Fall |

**Why 16 columns, 1,119 rows:** Features are computed with a 14-day lag for PM2.5. The first 14 rows (Oct 9 minus 14 = Sep 25 through Oct 8) have no valid pm25_lag14 value and are dropped. 1,133 − 14 = 1,119 rows.

**Why cyclic encoding for month:** Raw month integer (1–12) treats January and December as maximally distant (distance = 11). But they're seasonally adjacent — December and January are both deep winter. A linear model using raw month would have a discontinuity at the year boundary: it can't represent that Dec (=12) is near Jan (=1). Encoding as sin(2π·month/12) and cos(2π·month/12) maps the 12-month cycle onto a unit circle where December and January are close together. Tree models don't need this (they split by value, not distance), so month_sin/cos are only in the linear feature set.

---

## 6. Notebook 4 — Modeling

**File:** `models.ipynb`  
**Input:** `data/processed/features_daily.csv` (1,119 rows, 16 columns)  
**Target:** `pct_respiratory` (range 7.09%–26.58%)

### Three models

| Model | Type | Feature set | Why this model |
|---|---|---|---|
| Ridge Regression | Linear + L2 regularization | `month_sin`, `month_cos` (cyclic) | Baseline linear model. Regularization prevents overfitting on correlated seasonal features. Cyclic encoding lets it represent the annual cycle correctly. |
| Random Forest | Tree ensemble | Raw `month`, `season_num` | Captures non-linear interactions between temperature and season. Can learn that the same temperature means different things in summer vs winter. No cyclic encoding needed — trees split by value. |
| XGBoost | Gradient boosting | Same as Random Forest | Builds trees sequentially, each correcting the previous one's errors. Better at noisy tabular data than RF in many benchmarks. More hyperparameters = more tuning opportunity. |

### Evaluation strategy: two-tier

**Primary — Leave-last-year-out holdout:**
- Split at October 31, 2024
- Train: Oct 2022 – Oct 2024 (754 days, 2 full annual cycles)
- Test: Nov 2024 – Oct 2025 (365 days, all 12 months)
- The test set spans fall → winter peak → spring → summer. Every seasonal regime is evaluated. This gives a valid, interpretable test R².

**Why not 80/20 by row count:** An 80/20 cut of 1,119 rows falls in March 2025, making the test set entirely spring/summer. A model trained on 2 years of data predicts winter-level values (~20%) for a summer test set (~10%) → test R² = −0.09, RMSE inflated. The problem isn't the model — it's the biased test set. Leave-last-year-out is the standard approach for annual-cycle data.

**Secondary — 5-fold TimeSeriesSplit (robustness check):**
- `TimeSeriesSplit(n_splits=5)` produces 5 expanding folds
- Each fold trains on all data prior to the test window (no leakage)
- Fold 1: trains on only ~6 months of fall/winter → tests on spring/summer it's never seen → negative R² expected
- Results used as a diagnostic to show how performance degrades when training data is limited, not as the headline metric

### Holdout results (primary)

| Model | Test R² | RMSE (pp) | MAE (pp) |
|---|---|---|---|
| **Ridge Regression** | **0.687** | **2.394** | **1.880** |
| Random Forest | 0.570 | 2.806 | 2.126 |
| XGBoost | 0.548 | 2.875 | 2.154 |

**Best model: Ridge Regression.** Test R² = 0.687 means Ridge explains 68.7% of variance in respiratory illness on an unseen full year of data. RMSE = 2.39 percentage points.

**Why Ridge beats tree models on the holdout:** The dominant signal in this dataset is the annual seasonal cycle, which Ridge captures efficiently through the cyclic month features. With 2 years of training data, the seasonal coefficients (`month_sin`, `month_cos`) are well-estimated. The tree models can potentially capture non-linear weather–season interactions, but with a 3-year dataset they tend to overfit year-specific patterns without gaining generalization. On a balanced full-year test set, Ridge's clean seasonal representation wins.

**What RMSE = 2.39 pp means in context:** The target ranges 7–27%, so midpoint is ~17%. A 2.39 pp error is about 14% relative error at the midpoint. Since the target is a national aggregate across all US emergency departments, irreducible noise from daily administrative and reporting variation exists. 2.39 pp is approaching the practical floor for this problem with these features.

### Cross-validation results (robustness diagnostic)

| Model | CV R² (mean) | ± Std | RMSE (pp) | MAE (pp) |
|---|---|---|---|---|
| Ridge | −1.292 | ±2.366 | 2.484 | 2.033 |
| Random Forest | −0.773 | ±1.560 | 2.508 | 2.086 |
| XGBoost | −0.512 | ±0.768 | 2.468 | 1.997 |

**Why CV R² is negative — and why it's not model failure:**

R² = 1 − (SS_residual / SS_total). R² goes negative when SS_residual > SS_total — the model's errors are larger than just predicting the test set's mean every day.

This happens in early CV folds because of **seasonal distribution shift**:
- Fold 1 trains on only Oct 2022 – Apr 2023 (fall/winter only)
- Fold 1 tests on Apr – Oct 2023 (spring/summer — never seen by the model)
- The model predicts winter-level values (~20%) for summer test data (~10%)
- Errors are enormous: RMSE = 4.2 pp for Ridge in fold 1

The pattern is systematic and interpretable:

| Test season | Ridge | Random Forest | XGBoost |
|---|---|---|---|
| Winter folds (2, 4) | +0.47, +0.53 | +0.23, +0.03 | +0.06, −0.08 |
| Summer folds (1, 3, 5) | −5.19, −0.51, −1.76 | −3.41, +0.27, −1.00 | −1.79, −0.07, −0.68 |

Winter test folds → non-negative R² (model has seen prior winters). Summer test folds → negative R² in early folds where training has insufficient seasonal coverage. This is a **data volume constraint**, not a model architecture problem.

### Model hyperparameters

**Ridge:** `RidgeCV(alphas=[0.1, 1, 10, 100, 1000])` — selects best alpha via internal LOO-CV. `StandardScaler` applied per fold (fit on train only, transform both). Selected alpha: 10.0

**Random Forest:** `n_estimators=300` (enough trees for stable importances), `max_depth=8` (limits overfitting), `min_samples_leaf=10` (requires 10 samples to create a leaf — prevents memorizing noise), `max_features=0.6` (each split considers 60% of features — diversity without too much randomness), `random_state=42`

**XGBoost:** `n_estimators=300`, `learning_rate=0.05` (small — makes boosting conservative and robust), `max_depth=4` (shallower than RF — gradient boosting benefits from weaker individual trees), `subsample=0.8` (each tree sees 80% of rows — reduces variance), `colsample_bytree=0.8` (each tree sees 80% of features), `random_state=42`

### Feature importances

**Random Forest (mean decrease in impurity):**

| Feature | Importance |
|---|---|
| temperature | 0.440 |
| ozone_lag13 | 0.263 |
| month | 0.144 |
| no2_lag12 | 0.060 |
| season_num | 0.041 |
| humidity | 0.027 |
| day_of_week | 0.013 |
| pm25_lag14 | 0.007 |
| is_weekend | 0.005 |

**XGBoost (gain — how much each feature improves predictions when it splits):**

| Feature | Importance |
|---|---|
| temperature | 0.272 |
| ozone_lag13 | 0.269 |
| month | 0.194 |
| no2_lag12 | 0.079 |
| season_num | 0.050 |
| pm25_lag14 | 0.036 |
| day_of_week | 0.035 |
| is_weekend | 0.033 |
| humidity | 0.032 |

Both models agree: temperature #1, ozone_lag13 #2, month #3. This matches the EDA findings exactly.

**Why ozone_lag13 is more important than month in XGBoost:** XGBoost uses gain-based importance, which rewards features that make large improvements to predictions. Ozone has a moderate-to-strong lagged correlation and splits that partition the data into meaningfully different respiratory-illness levels. Month contributes less because ozone and temperature already carry the seasonal signal — month becomes somewhat redundant once those are included.

**Why humidity ranks low despite r = +0.530:** Humidity is strongly correlated with temperature (both seasonal). Once temperature and month are in the model, humidity adds little marginal information. Multicollinearity doesn't hurt prediction but it suppresses feature importance.

### Output figures

| File | What it shows |
|---|---|
| `model_01_actual_vs_predicted.png` | Ridge actual vs predicted time series, full date range, with train/test shading. Test period = Nov 2024 – Oct 2025. |
| `model_02_feature_importance.png` | RF and XGBoost feature importances side by side, horizontal bars, sorted by RF importance |
| `model_03_cv_fold_r2.png` | Per-fold R² for all three models, grouped bar chart with test date ranges on x-axis |

---

## 7. Changes from Check-In 1 (March)

### What was in the March baseline

- One combined notebook (`main.ipynb`) doing everything in one place
- Two OLS (linear regression) models: one with all features, one without PM2.5
- Single 80/20 time-ordered split: train R² = 0.79, test R² = −0.70
- Raw month integer (1–12) in the feature set
- README described the original NYC proposal (not the actual project)
- Several data quality bugs (wrong percentile cap timing, missing validation bounds, station counts dropped)

### What changed and why

**1. Restructured into 4 specialized notebooks**  
Why: Separation of concerns. Profiling is independent of cleaning. Cleaning is independent of EDA. This is standard data science practice. It also means each notebook can be re-run independently without re-running the entire pipeline.

**2. Fixed percentile cap order (cleaning fix #1)**  
The 99.5th percentile for PM2.5 was computed on the full raw dataset (Jan 2022 onward) instead of the study-period data (Sep 2022–Oct 2025 only). This caused the cap to be 35.80 µg/m³ instead of 38.00 µg/m³, incorrectly clipping real high-pollution readings (including wildfire events between 35.8 and 38.0 µg/m³). Fix: apply date filter first, then compute cap.

**3. Added missing validation bounds (cleaning fix #2)**  
The original `validate()` function checked humidity > 100% but had no upper bound on temperature or pct_respiratory. Added: temperature > 140°F → flag; pct_respiratory > 100% → flag.

**4. Station count columns included in master dataset (cleaning fix #3)**  
The 5 station count columns (pm25_n_stations, etc.) were being silently dropped at the merge step. Added them back. Master now has 12 columns instead of 7. Station counts are quality metadata for downstream use.

**5. Replaced 9-section EDA with 3 focused figures**  
Old EDA had 9 sections producing ~30 panels: heatmap, bar chart, scatter grid, seasonal decomposition, monthly boxplots, lag plots per feature (6 separate panels), overlay plots, 90-day rolling correlation, day-of-week charts. Many redundant.

New EDA: 3 figures that answer 3 questions in logical sequence (what does it look like → when do effects peak → how strong are they ranked). Each figure has explicit justification for chart type choice.

**6. Added cyclic month encoding**  
`month_sin = sin(2π·month/12)`, `month_cos = cos(2π·month/12)` added to `features_daily.csv`. This fixes the January/December discontinuity in linear models. Used only in Ridge; tree models use raw month.

**7. Replaced OLS with Ridge + Random Forest + XGBoost**  
OLS has no regularization — it will overfit when features are correlated (temperature and month are both seasonal). Ridge adds L2 regularization to handle this. Tree models are added to capture non-linear season–weather interactions that a linear model cannot express.

**8. Replaced single 80/20 split with leave-last-year-out + TimeSeriesSplit**  
The March 80/20 split (by row count, falling in March 2025) placed all summer data in the test set → test R² = −0.70. Leave-last-year-out (split at Oct 31, 2024) puts a full seasonal cycle in the test set → Ridge test R² = +0.687. TimeSeriesSplit CV added as a robustness diagnostic.

**9. README completely rewritten**  
Old README described the NYC proposal that was never executed. New README describes the actual project: EPA+CDC data, national scope, pipeline structure, key findings.

### Summary of number changes

| Metric | March baseline | Current |
|---|---|---|
| PM2.5 cap | 35.80 µg/m³ | 38.00 µg/m³ |
| PM2.5 negatives dropped | 10,148 | 8,306 |
| Master columns | 7 | 12 |
| EDA figures | ~30 panels across 9 sections | 3 focused figures |
| Features in model | 5 raw variables | 11 engineered features (16-column features CSV) |
| Best model | OLS, test R² = −0.70 | Ridge, test R² = +0.687 |
| Evaluation | Single 80/20 split | Leave-last-year-out (primary) + 5-fold CV (robustness) |

---

## 8. All Key Numbers in One Place

### Dataset sizes

| Dataset | Raw rows | Final daily rows |
|---|---|---|
| PM2.5 | 2,915,841 | 1,133 |
| NO₂ | 562,605 | 1,133 |
| Ozone | 1,412,282 | 1,133 |
| Temperature | 1,184,025 | 1,133 |
| Humidity | 579,258 | 1,133 |
| Respiratory | 259,896 | 1,133 |
| Master dataset | — | 1,133 rows, 12 columns |
| Features dataset | — | 1,119 rows, 16 columns |

### Cleaning numbers

| Dataset | Action | Count |
|---|---|---|
| PM2.5 | Negatives dropped | 8,306 |
| PM2.5 | Rows capped at 99.5th % | 11,344 |
| PM2.5 | Final cap value | 38.00 µg/m³ |
| NO₂ | Negatives dropped | 2,694 |
| NO₂ | Rows capped | 2,219 |
| NO₂ | Final cap value | 32.96 ppb |
| Ozone | Negatives dropped | 18 |
| Ozone | Rows capped | 5,540 |
| Ozone | Final cap value | 0.0623 ppm |
| Temperature | Rows dropped (below −80°F) | 1 |
| Temperature | Rows dropped (above 140°F) | 79 |
| Humidity | Dew Point rows removed | 43,518 |
| Humidity | Rows dropped (above 100%) | 2 |

### EDA correlations

| Feature | Lag-0 r | Optimal lag | Best r |
|---|---|---|---|
| Temperature | −0.812 | 0 days | −0.812 |
| Humidity | +0.530 | 0 days | +0.530 |
| NO₂ | +0.640 | 12 days | +0.743 |
| Ozone | −0.656 | 13 days | −0.732 |
| PM2.5 | −0.142 | 14 days | −0.153 |

### Modeling results — holdout (primary)

| Model | Test R² | RMSE (pp) | MAE (pp) |
|---|---|---|---|
| Ridge | **0.687** | **2.394** | **1.880** |
| Random Forest | 0.570 | 2.806 | 2.126 |
| XGBoost | 0.548 | 2.875 | 2.154 |

### Modeling results — CV (diagnostic)

| Model | CV R² mean | ± Std | RMSE (pp) | MAE (pp) |
|---|---|---|---|---|
| Ridge | −1.292 | ±2.366 | 2.484 | 2.033 |
| Random Forest | −0.773 | ±1.560 | 2.508 | 2.086 |
| XGBoost | −0.512 | ±0.768 | 2.468 | 1.997 |

---

## 9. Likely Professor Questions — Full Answers

### On data

**Q: Why did you switch from NYC data to national data?**  
A: The original proposal described NYC-specific health and air quality data. After trying to access it, we found that the national EPA AQS and CDC NSSP sources had better coverage, longer date ranges, and more consistent formatting. The README documents this scope change. The analytical question (do environmental factors predict respiratory illness?) is the same regardless of geography.

**Q: Why use national averages? Doesn't local air quality matter more?**  
A: The target variable (CDC NSSP pct_respiratory) is a national aggregate — it's the fraction of all US ED visits that are ARI on a given day. Matching it to a single city's air quality would require assuming that one city's conditions drive national illness rates, which is indefensible. National-to-national is the methodologically correct pairing.

**Q: Why include PM2.5 in the model if it's a weak predictor?**  
A: Two reasons. First, completeness — PM2.5 is the most policy-relevant air quality metric (EPA regulates it, public health agencies use it). Omitting it requires a strong justification. Second, the EDA reveals PM2.5's weakness is seasonal confounding (wildfires in summer when illness is low), not absence of any effect. Future work could try a PM2.5 metric that filters out wildfire-related readings.

**Q: How did you handle the 2023 wildfire spike?**  
A: We did not remove it. The percentile cap (38.00 µg/m³) operates at the station-reading level. After averaging 2,000+ stations nationally, the 2023 wildfire spike appears in the national daily PM2.5 as an elevated but not extreme value (around 15–20 µg/m³ nationally vs 200+ at individual stations). The before/after cleaning plot in `data_cleaning.ipynb` confirms the spike is preserved.

**Q: Why inner join for merging datasets?**  
A: An inner join keeps only dates present in all 6 datasets. Left-joining on any one dataset would create missing values in the others on days where that dataset had no coverage. Since we need non-null values for all features on every day (for model training), inner join is correct. The result (1,133 rows) matches the exact calendar count for the study period, confirming no spurious drops.

**Q: Why not interpolate missing days?**  
A: For weather/air quality data, interpolation is acceptable for short gaps (≤ 2 days). We found no gaps in the study period after inner-joining, so interpolation wasn't needed. For the respiratory target variable, we made a deliberate decision not to interpolate even if gaps existed — missing health outcome data may reflect real reporting failures, not random missingness. Interpolating a target variable would introduce false signal into the training data.

### On EDA

**Q: Why a dual y-axis in Figure 1? Isn't that misleading?**  
A: Dual y-axis is only misleading when used to exaggerate or minimize a relationship by cherry-picking scale. We use it because respiratory % and temperature are in incompatible units (percent vs. degrees Fahrenheit) and incompatible scales. On a single axis, one series would be compressed to near-flat. The chart includes labeled axes on both sides and a legend — the reader has all the information needed to interpret it correctly.

**Q: Why did you choose lags 0–14 for Figure 2?**  
A: This window covers the plausible biological range for ARI. From exposure to symptom onset is typically 1–7 days; from symptom onset to care-seeking at an ED is another 1–7 days. Beyond 14 days, any correlation is dominated by the shared seasonal trend (both NO₂ and respiratory illness are higher in winter), not by a causal delay.

**Q: Why is the NO₂ lag improvement partly spurious?**  
A: NO₂ and respiratory illness both have strong seasonal cycles that peak in winter and trough in summer. A value of NO₂ on day N looks nearly identical to the value on day N+12 because both are in the same seasonal phase. This means the lag-12 correlation partially picks up the shared seasonality rather than a true 12-day causal delay. The EDA report acknowledges this. The lagged feature is still useful — it outperforms lag-0 — but the 12-day number should not be interpreted as a precise biological mechanism.

**Q: How do you know 81.4% of variance is seasonal?**  
A: This is the R² of a regression of `pct_respiratory` on `month` alone (using cyclic or dummy encoding). A model with only month as a feature explains 81.4% of the variance in the target. This tells us that the seasonal cycle (captured by the calendar month) is the dominant signal. Environmental features in our model explain variance *on top of* this baseline.

**Q: Why include PM2.5 at lag 14 if it barely improves?**  
A: The improvement from lag-0 (r = −0.142) to lag-14 (r = −0.153) is 0.011 — negligible. PM2.5 is included in the feature set at lag-14 for completeness and for comparison in the feature importance plots. Both tree models confirm it has near-zero importance. In a production system, we would drop it.

### On modeling

**Q: Why Ridge instead of plain OLS?**  
A: Temperature and month are both seasonal — they're correlated. In OLS, collinear features produce inflated and unstable coefficients. Ridge adds L2 regularization (penalizes large coefficients), which shrinks correlated features toward each other rather than producing extreme opposite signs. `RidgeCV` selects the regularization strength automatically via internal cross-validation. The selected alpha was 10.0.

**Q: Why use cyclic encoding for Ridge but not for tree models?**  
A: Ridge is a linear model that uses the numeric distance between feature values. Raw month (1–12) implies December (12) and January (1) are as far apart as January and December are from July — maximally distant — when they're actually seasonally adjacent. Cyclic encoding (sin/cos) maps month onto a circle so December and January are adjacent. Tree models don't use numeric distance — they create binary splits (month ≤ 6 vs > 6). A tree can learn the seasonal pattern from raw month without the discontinuity problem.

**Q: Why leave-last-year-out instead of 80/20?**  
A: An 80/20 split by row count falls in March 2025, placing the test set entirely in spring/summer. This creates a seasonal mismatch: the model trains on 2 years including winter peaks, then tests on a spring/summer period where respiratory illness is at its annual low. The model predicts winter-level values → test R² = −0.09. This is not model failure — it's a biased test set. Leave-last-year-out (split at Oct 31, 2024) gives a test set covering all 12 months. Test R² = 0.687. Leave-last-year-out is the standard evaluation protocol for annual-cycle forecasting.

**Q: Why is CV R² negative if the model actually works?**  
A: CV R² is negative in the early folds because of seasonal distribution shift, not model failure. Fold 1 trains on only October 2022 – April 2023 (fall/winter only) and tests on April – October 2023 (spring/summer it has never seen). The model predicts ~20% (winter level) when actuals are ~10% (summer level). The pattern is consistent and interpretable: winter test folds (2, 4) produce near-zero or positive R² across all three models; summer test folds (1, 3, 5) produce negative R². The leave-last-year-out holdout (where training covers all seasons) gives R² = 0.687, confirming the model works when trained adequately.

**Q: Why is XGBoost best by CV but Ridge is best by holdout?**  
A: CV and holdout are measuring different things. CV mean R² is dominated by the most extreme folds (especially fold 1). XGBoost has lower variance across folds (±0.768 vs ±2.366 for Ridge) so its mean is less dragged down. But on the holdout — where the training set covers 2 full years and the test covers all seasons — the dominant signal is the annual cycle, which Ridge captures cleanly through cyclic month features. Trees overfit year-specific noise more readily with limited data. The holdout is the more reliable measure of real-world performance.

**Q: Could you improve results with more data?**  
A: Yes. The fundamental constraint is that 3 years of data gives only 3 complete seasonal cycles. Fold 1 in TimeSeriesSplit trains on 6 months before testing on a different season — essentially extrapolation. With 5+ years of data, every fold would start with at least 2 full years of training, and negative CV R² would disappear. Feature engineering could also help: interaction terms (temperature × month), regional-level data, or additional health determinants (influenza vaccination rates, healthcare access indices).

**Q: What does RMSE = 2.39 pp mean practically?**  
A: On average, our best model's predictions are 2.39 percentage points off the actual daily ARI percentage. Since the target ranges from 7% to 27%, a 2.39 pp error is about 14% relative error at the midpoint. In practical terms: if the actual ARI rate is 20% on a given day, our model's prediction would typically be between 17.6% and 22.4%. This is sufficient precision for coarse surge planning (anticipating a high-illness week) but too imprecise for operational staffing (exact patient count prediction).

**Q: What would you add next if you had more time?**  
A: (1) Skill score: `1 − RMSE_model / RMSE_seasonal_mean_baseline` — quantifies how much the model beats a naive seasonal predictor. (2) Regional-level modeling: national averages smooth out geographic variation. (3) Feature interactions: the relationship between temperature and illness likely varies by season — polynomial or interaction terms. (4) Additional health determinants: flu vaccination rates, school calendars, holiday travel patterns.

### On methodology

**Q: Why did you separate profiling and cleaning into two notebooks?**  
A: Profiling decisions must be made on the unmodified data. If you run cleaning code in the same notebook as profiling code, you risk accidentally profiling already-modified data, or the two phases interfere. Separation also means the profiling notebook can be re-run without triggering any data modification. Every cleaning decision in the cleaning notebook has a specific justification traceable back to a finding in the profiling notebook.

**Q: How do you know your cleaning decisions are correct?**  
A: Several ways. (1) The validation function runs after cleaning and confirms all constraints are met. (2) The visual verification plot (all variables over time) shows smooth, realistic patterns with no artifacts. (3) The before/after PM2.5 plot confirms the wildfire spike is preserved while the baseline is cleaned. (4) The REVISION.md documents every change made, including the specific data issue that motivated each change and the numbers that resulted.

**Q: Why document revisions in REVISION.md?**  
A: Any scientific work that goes through iterations should have an audit trail. REVISION.md documents 23 changes made after the March check-in, each with: what changed, where, and why. If a professor or reviewer asks "why is the PM2.5 cap 38 and not 35?", the answer is in entry #1. If they ask "why do you have two month features?", it's entry #20. It also protects us — if a mistake is found, we can trace it, explain it, and document the fix.
