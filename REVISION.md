# Revision Log
## Respiratory Disease Prediction from Environmental Factors

This file documents all post-submission corrections made to the notebooks, reports, and reference files, along with the reason for each change.

---

## data_cleaning.ipynb

### 1. Percentile cap computed before study period filter (methodological fix)

**Where:** `clean_pollutant()` function, Step 2  
**Change:** Moved the study period date filter (`df = df[(df['date'] >= STUDY_START) & (df['date'] <= STUDY_END)]`) to run **before** the 99.5th percentile cap is computed, not after.  
**Why:** The cap was previously derived from all raw years (2022 full year onward), including data outside the study window. This caused the cap to reflect a different distribution than the actual study period. For PM2.5, this lowered the cap from 38.00 to 35.80 µg/m³, which incorrectly clipped real high-pollution readings in the study period (including wildfire events between 35.8 and 38.0 µg/m³). Computing the cap after filtering ensures it reflects only the study-period distribution.

**Impact on numbers (study-period counts, not full-dataset):**
| Variable | Old negatives dropped | New | Old cap | New cap | Old capped rows | New |
|---|---|---|---|---|---|---|
| PM2.5 | 10,148 | 8,306 | 35.80 µg/m³ | 38.00 µg/m³ | 14,515 | 11,344 |
| NO2 | 3,254 | 2,694 | 33.10 ppb | 32.96 ppb | 2,794 | 2,219 |
| Ozone | 18 | 18 | 0.0621 ppm | 0.0623 ppm | 7,040 | 5,540 |

---

### 2. `validate()` missing upper-bound checks

**Where:** `validate()` function, Step 6  
**Change:** Added two bounds checks that were missing:
- `temperature > 140°F` → flags as `'temperature above 140F'`
- `pct_respiratory > 100%` → flags as `'pct_respiratory above 100%'`

**Why:** The original function only checked `humidity > 100%` as a special case but applied no upper-bound check to temperature (which has a physical maximum of 140°F per the cleaning decision) or to `pct_respiratory` (which cannot exceed 100% by definition). If bad values slipped through cleaning in future runs, the validation would have silently passed them as `PASS`.

---

### 3. `n_stations` columns included in master dataset

**Where:** Step 8 merge, `merge_inputs` list  
**Change:** Added `pm25_n_stations`, `no2_n_stations`, `ozone_n_stations`, `temp_n_stations`, and `humidity_n_stations` to the master merge. Master now has 12 columns instead of 7.  
**Why:** Each cleaned individual file already carried a station count column, but these were silently dropped when building the master. Station counts are quality metadata — days with fewer stations produce less representative national averages. Including them allows downstream modeling steps to weight or filter by data density.

---

### 4. Misleading comment about Massachusetts in `clean_respiratory()`

**Where:** `clean_respiratory()` function, Step 5  
**Change:** Replaced the comment `"Profiling finding: contains() match incorrectly caught 'Massachusetts'"` with `"Exact string match required: contains() would also match substrings like 'United States Virgin Islands' and similar geography names"`.  
**Why:** The original comment was misleading — 'Massachusetts' does not contain 'United States' as a substring. The actual false-positive found during profiling was caused by a different regex (`str.contains('US', case=False)`) matching 'us' inside 'Massachusetts'. The corrected comment gives an accurate and generalizable reason for using exact matching.

---

### 5. Row count comment in Step 8

**Where:** Markdown cell above the master merge  
**Change:** `"Expected: ~1,132 rows"` → `"Expected: 1,133 rows"`  
**Why:** The date range September 25, 2022 to October 31, 2025 inclusive is exactly 1,133 calendar days. The approximate figure was off by one.

---

### 6. Summary table updated (cell-0 intro and cell-22 summary)

**Where:** Opening decisions table and final summary table  
**Change:** Updated all negative-drop counts and cap values to study-period figures; added exact cap values (e.g., `38.00 µg/m³`) in the summary table instead of "Small tail" / "Negligible"; updated master columns list to include all 12 columns; added note that all counts are study-period only and caps are computed after the date filter.  
**Why:** The summary tables contained the old full-dataset counts (10,148, 3,254) which no longer matched what the code actually produces after fix #1.

---

## data_profiling.ipynb

### 7. `STUDY_START` / `STUDY_END` were unused and inconsistent

**Where:** Setup cell  
**Change:** Updated `STUDY_START` from `'2022-01-01'` to `'2022-09-25'` and `STUDY_END` from `'2025-12-31'` to `'2025-10-31'`. Added a comment clarifying these are reference-only values — the profiling notebook examines raw data across its full date range and does not apply these as filters.  
**Why:** The profiling notebook defined these variables but never used them to filter any data. The values were also inconsistent with the cleaning notebook's actual study window, which would confuse a reader comparing the two notebooks.

---

### 8. `profile_dataset` duplicate date message was misleading

**Where:** `profile_dataset()` function, section [5]  
**Change:** Replaced `"Duplicate date values: 2,914,429"` with `"Unique date values: 1412 across 2,915,841 rows (ratio 2065.0 rows/date — expected: multiple stations per day)"`.  
**Why:** The old message printed a raw count of non-unique dates, which looked like a data quality problem. For multi-station EPA datasets, every date appears thousands of times (once per station), so this is expected behavior. The new format shows the ratio, making it immediately clear that this is normal.

---

### 9. Geography regex false-matched 'Massachusetts'

**Where:** Cell-24, exploratory geography search  
**Change:** Replaced regex `str.contains('unit|nation|all|US', case=False)` with `str.contains('United States', case=False)`.  
**Why:** The `US` component of the regex matches case-insensitively, so it matched 'us' inside 'Mass**ac**h**us**etts', returning both 'Massachusetts' and 'United States' as apparent national-level geographies. The output visibly showed this but there was no explanation. The fixed regex returns only 'United States'.

---

## reports/data_profiling_report.md

### 10. CDC name typo

**Where:** Dataset 6 source line  
**Change:** `"Centre for Disease COntrol"` → `"Centers for Disease Control"`  
**Why:** Two errors: "Centre" is the UK spelling (correct US form is "Centers"), and "COntrol" had an errant capital O.

---

### 11. Expected master row count

**Where:** Cross-Dataset Comparison section  
**Change:** `"Expected master rows: ~1,132 days"` → `"1,133 days"`  
**Why:** Same date arithmetic correction as cleaning notebook — the exact count is 1,133, not approximately 1,132.

---

### 12. Sparse station coverage cleaning decision

**Where:** PM2.5 Cleaning Decisions table  
**Change:** `"Flag days with fewer than 50 stations"` → `"Track station counts via n_stations column in master dataset"`  
**Why:** The original decision was never implemented as explicit flagging. After fix #3 above, station counts are now included in the master dataset, allowing downstream users to identify sparse-coverage days. The description is updated to match what was actually done.

---

## reports/data_cleaning_report.md

### 13. Stale numbers from cap-before-filter fix

**Where:** Multiple sections  
**Change:** Updated all numbers that changed as a result of fix #1:

| Location | Old value | New value |
|---|---|---|
| PM2.5 operations — negatives dropped | 10,148 | 8,306 |
| PM2.5 operations — cap value | 35.80 µg/m³ | 38.00 µg/m³ |
| PM2.5 operations — capped rows | 14,515 | 11,344 |
| PM2.5 output — final max | 20.40 µg/m³ | 21.15 µg/m³ |
| PM2.5 output — mean | 7.60 µg/m³ | 7.61 µg/m³ |
| PM2.5 output — std | 2.03 µg/m³ | 2.05 µg/m³ |
| PM2.5 notes paragraph | 35.80, 20.40, 14,515, 0.5% | 38.00, 21.15, 11,344, 0.4% |
| NO2 operations — negatives dropped | 3,254 | 2,694 |
| NO2 operations — cap value | 33.10 ppb | 32.96 ppb |
| NO2 operations — capped rows | 2,794 | 2,219 |
| Ozone operations — cap value | 0.0621 ppm | 0.0623 ppm |
| Ozone operations — capped rows | 7,040 | 5,540 |
| Master stats — PM2.5 max | 20.40 | 21.15 |
| Master stats — PM2.5 mean | 7.60 | 7.61 |
| Master stats — PM2.5 std | 2.03 | 2.05 |
| Cleaning impact — PM2.5 negatives | 10,148 | 8,306 |
| Cleaning impact — NO2 negatives | 3,254 | 2,694 |

**Why:** All of these values were derived from the cleaning notebook's output. After fix #1 changed when the study period filter is applied, the notebook output changed and the report needed to reflect the new numbers.

---

### 14. Master dataset column count and file size

**Where:** Merge Results table and Output Files table  
**Change:** Columns `7 (date + 6 variables)` → `12 (date, 6 value columns, 5 station count columns)`; file size `120.7 KB` → `144.5 KB`; description `"all 7 columns"` → `"12 columns"`.  
**Why:** Fix #3 added five station count columns to the master dataset, increasing both the column count and the file size.

---

## README.md

### 15. README described the original NYC proposal, not the actual project

**Where:** Entire file  
**Change:** Complete rewrite. Replaced all references to New York City, NYC Department of Health and Mental Hygiene, and NYC EpiQuery with the actual data sources (EPA AQS and CDC NSSP). Added actual dataset table, repository structure, setup instructions, and key findings. Added a note explaining the scope change from NYC to national.  
**Why:** The README described a proposal that was never executed. The project uses national EPA and CDC data, not NYC data. Anyone reading the README had no accurate description of what the project actually does or how to run it.

---

## project_reference.md

### 16. master_daily.csv column count

**Where:** Files Produced table  
**Change:** `"7 columns"` → `"12 columns"`  
**Why:** Same as fix #14 — master now includes station count columns.

---

### 17. Stale notebook filename

**Where:** Notebooks table  
**Change:** `modeling_checkin1.ipynb` → `models.ipynb`  
**Why:** The notebook was renamed. The reference pointed to a file that does not exist in the repository.

---

## eda.ipynb

### 18. Reduced from 9 EDA sections (~30 panels) to 3 focused figures

**Where:** Entire notebook restructured  
**Change:** Deleted EDA sections 5–9 (monthly boxplots, duplicate lag computation, per-feature overlay plots, 90-day rolling correlation, day-of-week bar/box plots). Replaced the original sections 1–4 (heatmap, bar chart, scatter grid, seasonal decomposition) with three new figures that cover the complete analytical story.

**New figures:**
- **Figure 1 — Time Series** (`eda_01_time_series_key_relationships.png`): 2-panel dual-axis line chart. Respiratory + Temperature (top), Respiratory + NO₂ (bottom). `sharex=True`, quarterly x-axis ticks, Pearson r in panel titles.
- **Figure 2 — Lag Correlation Profiles** (`eda_02_lag_correlation_profiles.png`): Single-panel line chart, one line per feature (lags 0–14 days), filled circle at optimal lag, 95% significance band.
- **Figure 3 — Feature Correlation Ranking** (`eda_03_feature_correlation_ranking.png`): Horizontal grouped bar chart, sorted by best-lag |r|, paired lag-0 vs best-lag bars, annotated with lag and r value.

**Why:** The original 9 sections produced redundant information. Sections 4 (seasonal decomposition), 7 (overlay plots), and 8 (rolling correlation) all showed the same seasonal co-movement without adding unique insight. Section 6 (lag plots) was replaced by Figure 2, which shows all features on a single axis for direct comparison instead of 6 separate small-multiples panels. The 3-figure structure answers the three key questions in a logical sequence: what do the relationships look like → when do they peak → how strong are they ranked.

Each figure includes a markdown cell explaining the chart-type choice (line vs bar vs grouped bar) and what to look for when reading it.

---

## reports/eda_report.md

### 19. Complete rewrite to match 3-figure structure

**Where:** Entire file  
**Change:** Replaced the 9-section report (EDA 1–9) with a 3-figure report aligned to the new notebook structure. Each section documents: figure filename, chart-type reasoning (why line/bar/grouped bar, why those variables), results table, and interpretation. Added key findings summary at the end.  
**Why:** The old report described analyses that no longer exist in the notebook (heatmap, scatter grid, seasonal decomposition, rolling correlation, day-of-week). After the notebook restructure, the report had to match what the notebook actually produces. The new report also explicitly documents why each chart type was chosen, which was a requirement of the revision.

---

## eda.ipynb + features_daily.csv

### 20. Cyclic month encoding added to feature set

**Where:** Feature engineering cell (cell index 14), `data/processed/features_daily.csv`  
**Change:** Added `month_sin = sin(2π·month/12)` and `month_cos = cos(2π·month/12)` to the features dataset. Dataset now has 16 columns instead of 14. `requirements.txt` updated to add `xgboost>=2.0.0`.  
**Why:** Raw month integer (1–12) treats January and December as maximally distant values. On a linear model this creates a discontinuity at the year boundary that prevents the model from learning that December and January are seasonally adjacent. Encoding month as a sine/cosine pair maps the 12-month cycle onto a unit circle so any linear model can represent the seasonal transition continuously.

---

## models.ipynb

### 21. Full rebuild of modeling notebook

**Where:** Entire file (replaced March baseline)  
**Change:** Replaced the two-model OLS baseline (single 80/20 split, raw month integer) with three models evaluated using 5-fold TimeSeriesSplit cross-validation:
- **Ridge Regression** — cyclic month features, StandardScaler per fold, RidgeCV alpha search [0.1–1000]
- **Random Forest** — `n_estimators=300`, `max_depth=8`, `min_samples_leaf=10`, `max_features=0.6`
- **XGBoost** — `n_estimators=300`, `learning_rate=0.05`, `max_depth=4`, `subsample=0.8`

Three output figures: actual vs predicted time series (XGBoost, 80/20 split), feature importance (RF and XGBoost side by side), CV fold R² comparison across all three models.

**Why:** The March baseline had train R² = 0.79 but test R² = −0.70 because a single 80/20 cut placed all summer data in the test set. TimeSeriesSplit spreads test coverage across multiple seasons so no single fold is responsible for all evaluation. The two tree models were added to capture seasonal interaction effects that a linear model cannot express — specifically the sign-flip in NO₂ and ozone correlations across seasons.

---

## reports/modeling_report.md

### 22. Rewritten for April check-in

**Where:** Entire file  
**Change:** Replaced March check-in content (OLS baseline) with full April report covering all three models. Includes per-fold CV tables, feature importance tables, model comparison, and a detailed explanation of why CV R² is negative and why this is attributable to seasonal distribution shift rather than model failure.  
**Why:** The March report described two OLS models with a single-split evaluation that is no longer used. The April report reflects the new three-model setup and provides the interpretation required by the check-in rubric.
