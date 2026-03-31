# Data Cleaning Report
## Respiratory Disease Prediction from Environmental Factors
**Team:** Gowrav Lakshmipathy | Priya Dilip Bajaria | Nandini Nandan Narvekar

---

## Overview

This report documents the cleaning operations applied to all six datasets.
Every decision references a specific finding from the profiling phase (`data_profiling_report.md`).
No cleaning decisions were made during this phase — only execution of decisions already made.

**Study period after cleaning:** September 25, 2022 to October 31, 2025
**Master dataset rows:** 1,133 daily rows
**Master dataset columns:** date, pct_respiratory, pm25, no2, ozone, temperature, humidity
**Missing values in master:** 0

---

## Dataset 1 — PM2.5

### Operations Applied

| Operation | Rows affected | Justification from profiling |
|---|---|---|
| Drop Arithmetic Mean < 0 | 10,148 | Physically impossible. PM2.5 concentration cannot be negative. Confirmed in profiling. |
| Cap at 99.5th percentile (35.80 µg/m³) | 14,515 station readings | Removes extreme tail while preserving 192 real wildfire readings above 200 µg/m³ |
| Parse dates with format='mixed' | All rows | EPA files use MM/DD/YYYY (2022) and YYYY-MM-DD (2023+) across yearly files |
| Group by date: national daily mean | 2.9M → 1,133 rows | One national value per day across all monitoring stations |
| No gap interpolation needed | 0 gaps found | Date sequence was complete for study period |

### Output

| Metric | Value |
|---|---|
| Final rows | 1,133 |
| Final range | 3.58 to 20.40 µg/m³ |
| Mean | 7.60 µg/m³ |
| Std | 2.03 µg/m³ |
| Missing values | 0 |
| Validation | PASS |

### Notes

The 99.5th percentile cap of 35.80 µg/m³ applies at the station-reading level, not the national
daily average level. After averaging across 2,000+ stations, the national daily max is 20.40 µg/m³.
The cap affected 14,515 out of 2.9M rows — 0.5% of station readings. The 2023 Canadian wildfire
spike visible in the before/after plot is preserved in the cleaned data, confirming the percentile
approach was correct over a hard threshold.

---

## Dataset 2 — NO2

### Operations Applied

| Operation | Rows affected | Justification from profiling |
|---|---|---|
| Drop Arithmetic Mean < 0 | 3,254 | Physically impossible. NO2 concentration cannot be negative. |
| Cap at 99.5th percentile (33.10 ppb) | 2,794 station readings | Standard tail cleanup. No meaningful impact — max 64 ppb was clean. |
| Parse dates with format='mixed' | All rows | Same mixed format issue as PM2.5 |
| Group by date: national daily mean | 562K → 1,133 rows | One national value per day |
| No gap interpolation needed | 0 gaps found | No missing days in study period |

### Output

| Metric | Value |
|---|---|
| Final rows | 1,133 |
| Final range | 3.03 to 16.77 ppb |
| Mean | 7.59 ppb |
| Std | 2.23 ppb |
| Missing values | 0 |
| Validation | PASS |

### Notes

NO2 is measured hourly (1-hour sample duration) unlike PM2.5 which is 24-hour integrated.
The daily mean averages across both stations and all 24 hours simultaneously.
National daily averages of 3-17 ppb are consistent with US urban background levels.
NO2 monitoring is more concentrated in urban areas than PM2.5, making the national
average slightly more urban-biased.

---

## Dataset 3 — Ozone

### Operations Applied

| Operation | Rows affected | Justification from profiling |
|---|---|---|
| Drop Arithmetic Mean < 0 | 18 | Physically impossible. Profiling found only 18 — cleanest pollutant dataset. |
| Cap at 99.5th percentile (0.0621 ppm) | 7,040 station readings | Standard tail cleanup. Max 0.136 ppm was real — no hard threshold needed. |
| Parse dates with format='mixed' | All rows | Same mixed format issue as PM2.5 and NO2 |
| Group by date: national daily mean | 1.4M → 1,133 rows | One national value per day |
| No gap interpolation needed | 0 gaps found | No missing days in study period |

### Output

| Metric | Value |
|---|---|
| Final rows | 1,133 |
| Final range | 0.019 to 0.045 ppm |
| Mean | 0.032 ppm |
| Std | 0.006 ppm |
| Missing values | 0 |
| Validation | PASS |

### Notes

Ozone is measured as an 8-hour running average. Each station contributes multiple
overlapping 8-hour window readings per day. The national daily mean averages across
all windows and all stations. The national daily max of 0.045 ppm is well below the
EPA 8-hour standard of 0.070 ppm — which is expected since that standard applies to
local 8-hour peaks, not national daily averages.

---

## Dataset 4 — Temperature

### Operations Applied

| Operation | Rows affected | Justification from profiling |
|---|---|---|
| Drop values below -80°F | 1 | Sentinel value at -1,177.67°F — firmware error code. Below absolute zero (-459.67°F). |
| Drop values above 140°F | 79 | Surface radiant heat artifacts. Sensors sited on hot rooftops. Above any recorded air temperature (max 130°F). |
| No unit conversion | 0 | Profiling confirmed 100% Degrees Fahrenheit across all rows. |
| Parse dates with format='mixed' | All rows | Same mixed format issue as pollutants |
| Group by date: national daily mean | 1.2M → 1,133 rows | One national value per day |
| No gap interpolation needed | 0 gaps found | No missing days in study period |

### Output

| Metric | Value |
|---|---|
| Final rows | 1,133 |
| Final range | 21.81°F to 80.90°F |
| Mean | 57.72°F |
| Std | 14.58°F |
| Missing values | 0 |
| Validation | PASS |

### Notes

Hard physical bounds were used instead of percentile capping — unlike the pollutants,
physical limits for temperature are well-defined and meaningful. This was the critical
difference: a 99.5th percentile cap only clips the upper tail and would have left the
-1,177.67°F sentinel value in the data, corrupting the national daily average for that
specific day. Profiling revealed this in advance.

The national daily average range of 22°F to 81°F is realistic. Individual station ranges
are much wider, but the national mean across all US stations naturally compresses the range.

---

## Dataset 5 — Humidity

### Operations Applied

| Operation | Rows affected | Justification from profiling |
|---|---|---|
| Filter to Relative Humidity rows only | 43,518 Dew Point rows removed | Dew Point values are in degrees (°F/°C), not percent. Averaging with RH % produces meaningless values. |
| Drop values above 100% | 2 | Physically impossible. Sensor calibration drift — 0.0004% of RH rows. |
| Drop values below 0% | 0 | Profiling confirmed zero negatives in RH-only rows. The -25% minimum in the raw profile came entirely from Dew Point rows. |
| Parse dates with format='mixed' | All rows | Same mixed format issue |
| Group by date: national daily mean | 535,740 → 1,133 rows | One national RH value per day |
| No gap interpolation needed | 0 gaps found | No missing days in study period |

### Output

| Metric | Value |
|---|---|
| Final rows | 1,133 |
| Final range | 43.72% to 85.91% |
| Mean | 60.18% |
| Std | 7.21% |
| Missing values | 0 |
| Validation | PASS |

### Notes

Filtering to Relative Humidity was the most structurally important cleaning step across
all datasets. Without it, the daily national averages would be a nonsensical blend of
percent and degree values. The -25% minimum in the raw profile was a misleading artifact
of the mixed file — entirely resolved by the parameter filter.

---

## Dataset 6 — Respiratory (NSSP)

### Operations Applied

| Operation | Rows affected | Justification from profiling |
|---|---|---|
| Filter pathogen == 'ARI' | ~195,000 rows removed | ARI (Acute Respiratory Illness) is the broadest category. Individual pathogens (COVID, Flu, RSV) are subsets — using them alongside ARI would double-count. |
| Filter geography == 'United States' | Exact match used | Profiling confirmed 'United States' is the correct exact label. Contains() match returned 'Massachusetts' as false positive. |
| No value cleaning | 0 | Profiling found zero invalid values: 0 below 0%, 0 above 100%, 0 IQR outliers. |
| No interpolation of missing days | 0 missing days found | Missing respiratory data may be real reporting failures, not sensor gaps. Interpolating the target variable would introduce false signal. |
| Preserve day-of-week oscillation | Not smoothed | Weekly pattern reflects real behavioral differences in ED utilization on weekends. Real signal to preserve. |

### Output

| Metric | Value |
|---|---|
| Final rows | 1,133 |
| Final range | 7.09% to 26.58% |
| Mean | 13.24% |
| Std | 4.08% |
| Missing values | 0 |
| Validation | PASS |

### Notes

The simplest dataset to clean — the filter was the only operation. All profiling predictions
were confirmed exactly: 0 unparseable dates, 0 duplicate dates, 0 invalid values.
The NSSP data had zero missing days within the study period, meaning the inner join
did not lose any rows due to respiratory reporting gaps.

---

## Merge Results

All six datasets were merged using an inner join on the date column.
Only dates present in all six datasets with non-null values are included.

| Property | Value |
|---|---|
| Join type | Inner join on date |
| Final rows | 1,133 |
| Date range | 2022-09-25 to 2025-10-31 |
| Columns | 7 (date + 6 variables) |
| Missing values | 0 |

### Why 1,133 rows

The study period from Sep 25 2022 to Oct 31 2025 spans 1,132 calendar days.
The inner join produced 1,133 rows because the date range is inclusive on both ends.
The binding constraints were:
- **Start:** NSSP data begins September 25, 2022 (9 months after EPA datasets start)
- **End:** Temperature data ends October 31, 2025 (earliest EPA endpoint)

### Master Dataset Descriptive Statistics

| Column | Min | Mean | Std | Max |
|---|---|---|---|---|
| pct_respiratory (%) | 7.09 | 13.24 | 4.08 | 26.58 |
| pm25 (µg/m³) | 3.58 | 7.60 | 2.03 | 20.40 |
| no2 (ppb) | 3.03 | 7.59 | 2.23 | 16.77 |
| ozone (ppm) | 0.019 | 0.032 | 0.006 | 0.045 |
| temperature (°F) | 21.81 | 57.72 | 14.58 | 80.90 |
| humidity (%) | 43.72 | 60.18 | 7.21 | 85.91 |

---

## Visual Verification

Two plots were generated to confirm cleaning did not introduce artifacts:

### Plot 1 — All Variables (cleaned_master_all_variables.png)

All six variables plotted over the full study period. Key observations confirming correct cleaning:

- **Respiratory** shows three complete winter peaks (Dec 2022, Dec 2023, Dec 2024) and
  three summer troughs — consistent with known US respiratory illness seasonality
- **PM2.5** shows the 2023 Canadian wildfire spike (Jun-Sep 2023) preserved — confirms
  the percentile cap approach was correct over a hard threshold
- **NO2** peaks in winter months — consistent with less UV radiation to break down NO2
- **Ozone** peaks in summer — consistent with photochemical production in heat and sunlight
- **Temperature** shows clean seasonal cycles with no flat lines or spikes
- **Humidity** shows seasonal variation with higher values in summer and during weather events
- No flat lines, spikes, or discontinuities visible in any variable

### Plot 2 — PM2.5 Before vs After (pm25_before_after_cleaning.png)

Before: National daily average including the effects of negative station readings.
After: Same averages with negatives dropped and 99.5th percentile cap applied.

Key observation: The Jun-Sep 2023 wildfire spike is clearly visible in both plots,
confirming that meaningful high-pollution events are preserved after cleaning.
The after plot shows a slightly smoother baseline — the result of removing calibration
noise from negative station readings.

---

## What Was Not Applied and Why

| Operation skipped | Reason |
|---|---|
| Hard cap on PM2.5 above 200 µg/m³ | 192 values confirmed as real wildfire events in profiling |
| Interpolation of respiratory missing days | Health outcome gaps may be real reporting failures; interpolating target variable creates false signal |
| Temperature unit conversion | Profiling confirmed 100% Fahrenheit across all rows |
| Smoothing of weekly oscillation in respiratory | Day-of-week pattern is real behavioral signal, not noise |
| Imputation of NO2/Ozone 11-day end gap | Reporting lag at dataset end; inner join handles coverage differences automatically |

---

## Cleaning Impact Summary

| Dataset | Raw rows | Key rows removed | Reason | Final daily rows |
|---|---|---|---|---|
| PM2.5 | 2,915,841 | 10,148 negatives | Impossible concentration | 1,133 |
| NO2 | 562,605 | 3,254 negatives | Impossible concentration | 1,133 |
| Ozone | 1,412,282 | 18 negatives | Impossible concentration | 1,133 |
| Temperature | 1,184,025 | 80 (1 sentinel + 79 surface heat) | Impossible temperatures | 1,133 |
| Humidity | 579,258 | 43,518 dew point + 2 above 100% | Wrong parameter + impossible value | 1,133 |
| Respiratory | 259,896 | ~195,000 (by design) | Filter to ARI + US only | 1,133 |
| **Master** | — | — | Inner join on date | **1,133** |

---

## Output Files

| File | Size | Contents |
|---|---|---|
| data/processed/pm25_daily.csv | 37.6 KB | Daily national PM2.5 mean + station count |
| data/processed/no2_daily.csv | 36.5 KB | Daily national NO2 mean + station count |
| data/processed/ozone_daily.csv | 39.7 KB | Daily national Ozone mean + station count |
| data/processed/temperature_daily.csv | 36.5 KB | Daily national temperature mean + station count |
| data/processed/humidity_daily.csv | 36.5 KB | Daily national RH mean + station count |
| data/processed/respiratory_daily.csv | 18.5 KB | Daily US ARI percent ED visits |
| data/processed/master_daily.csv | 120.7 KB | Merged dataset, all 7 columns, 1,133 rows |

---

*Report generated after Phase 2 cleaning. All operations reference findings from data_profiling_report.md.*
*Next step: exploratory data analysis and feature engineering.*
