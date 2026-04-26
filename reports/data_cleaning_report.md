# Data Cleaning Report
## Respiratory Disease Prediction from Environmental Factors
**Team:** Gowrav Lakshmipathy | Priya Dilip Bajaria | Nandini Nandan Narvekar

---

## Overview

This report describes the data cleaning steps we applied to all six datasets. Each step was based on issues identified earlier in the profiling report (data_profiling_report.md). In this phase, we did not make any new cleaning decisions. We simply carried out the cleaning actions that had already been planned.

After cleaning, the final study period runs from September 25, 2022 to October 31, 2025. The final master dataset contains 1,133 rows in total, with each row representing one day. It includes the columns date, pct_respiratory, pm25, no2, ozone, temperature, and humidity. The final merged dataset has no missing values.

---

## Dataset 1: PM2.5

### Operations Applied

| Operation | Rows affected | Justification from profiling |
|---|---|---|
| Drop Arithmetic Mean < 0 | 8,306 | Physically impossible. PM2.5 concentration cannot be negative. Confirmed in profiling. |
| Cap at 99.5th percentile (38.00 µg/m³) | 11,344 station readings | Removes extreme tail while preserving real wildfire readings above 200 µg/m³ |
| Parse dates with format='mixed' | All rows | EPA files use MM/DD/YYYY (2022) and YYYY-MM-DD (2023+) across yearly files |
| Group by date: national daily mean | 2.9M → 1,133 rows | One national value per day across all monitoring stations |
| No gap interpolation needed | 0 gaps found | Date sequence was complete for study period |

### Output

| Metric | Value |
|---|---|
| Final rows | 1,133 |
| Final range | 3.58 to 21.15 µg/m³ |
| Mean | 7.61 µg/m³ |
| Std | 2.05 µg/m³ |
| Missing values | 0 |
| Validation | PASS |

### Notes

The 99.5th percentile cap of 38.00 µg/m³ applies at the station-reading level, not the national
daily average level. After averaging across 2,000+ stations, the national daily max is 21.15 µg/m³.
The cap affected 11,344 out of 2.9M rows — 0.4% of station readings. The 2023 Canadian wildfire
spike visible in the before/after plot is preserved in the cleaned data, confirming the percentile
approach was correct over a hard threshold.

---

## Dataset 2: NO2

### Operations Applied

| Operation | Rows affected | Justification from profiling |
|---|---|---|
| Drop Arithmetic Mean < 0 | 2,694 | Physically impossible. NO2 concentration cannot be negative. |
| Cap at 99.5th percentile (32.96 ppb) | 2,219 station readings | Standard tail cleanup. No meaningful impact — max 64 ppb was clean. |
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

Unlike PM2.5, NO2 is measured hourly using a 1-hour sample duration. As a result, the daily value in our cleaned dataset reflects an average across all available hourly readings from all reporting stations on a given day. The final national daily values, which range from 3 to 17 ppb, are reasonable for broad US background conditions. Since NO2 monitoring is more concentrated in urban locations, the national average is likely to be somewhat more influenced by urban areas than the PM2.5 average.

---

## Dataset 3: Ozone

### Operations Applied

| Operation | Rows affected | Justification from profiling |
|---|---|---|
| Drop Arithmetic Mean < 0 | 18 | Physically impossible. Profiling found only 18 — cleanest pollutant dataset. |
| Cap at 99.5th percentile (0.0623 ppm) | 5,540 station readings | Standard tail cleanup. Max 0.136 ppm was real — no hard threshold needed. |
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

Ozone is reported as an 8-hour running average, so each station can contribute several overlapping 8-hour measurements within the same day. Our daily national value was calculated by averaging across all of those readings from all stations. The final national daily maximum of 0.045 ppm is well below the EPA 8-hour standard of 0.070 ppm, which is expected because the EPA limit applies to local peak exposure levels, not to a national daily average.

---

## Dataset 4: Temperature

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


For temperature, we used physical limits instead of percentile capping because unrealistic temperature values are easier to identify directly. This was important because a percentile cap would not have fixed the extreme negative sensor error. The final daily range looked realistic for a national average.

---

## Dataset 5: Humidity

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

Filtering to Relative Humidity was the most important cleaning step for this dataset. Without it, the daily national averages would have mixed percentage values with dew point values in degrees, which would not be meaningful. The -25% minimum seen in the raw profile was not a real humidity issue, but a misleading result caused by the mixed file structure. Once we filtered to the correct parameter, that issue was fully resolved.

---

## Dataset 6: Respiratory (NSSP)

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


This was the simplest dataset to clean, since filtering was the only step required. The profiling results were fully confirmed, with no unparseable dates, no duplicate dates, and no invalid values. The NSSP data also had no missing days during the study period, so the inner join did not drop any rows because of respiratory data gaps.


---

## Merge Results

All six datasets were merged using an inner join on the date column.
Only dates present in all six datasets with non-null values are included.

| Property | Value |
|---|---|
| Join type | Inner join on date |
| Final rows | 1,133 |
| Date range | 2022-09-25 to 2025-10-31 |
| Columns | 12 (date, 6 value columns, 5 station count columns) |
| Missing values | 0 |

### Why 1,133 rows

The study period runs from September 25, 2022 to October 31, 2025. Since both the start date and end date are included, this gives a total of 1,133 calendar days, which is why the inner join also produced 1,133 rows.

The final date range was limited by the overlap across datasets:

Start: The NSSP data begins on September 25, 2022, which is later than the EPA datasets.
End: The temperature data ends on October 31, 2025, which is the earliest end date among the EPA datasets.


### Master Dataset Descriptive Statistics

| Column | Min | Mean | Std | Max |
|---|---|---|---|---|
| pct_respiratory (%) | 7.09 | 13.24 | 4.08 | 26.58 |
| pm25 (µg/m³) | 3.58 | 7.61 | 2.05 | 21.15 |
| no2 (ppb) | 3.03 | 7.59 | 2.23 | 16.77 |
| ozone (ppm) | 0.019 | 0.032 | 0.006 | 0.045 |
| temperature (°F) | 21.81 | 57.72 | 14.58 | 80.90 |
| humidity (%) | 43.72 | 60.18 | 7.21 | 85.91 |

---

## Visual Verification

Two plots were generated to confirm cleaning did not introduce artifacts:

### Plot 1: All Variables (cleaned_master_all_variables.png)


All six variables were plotted across the full study period to visually check that the cleaning steps had not distorted the data. The overall patterns looked realistic and consistent with what we would expect. Respiratory values showed clear winter peaks and summer lows, PM2.5 still captured the 2023 Canadian wildfire spike, NO2 was generally higher in winter, and ozone peaked in summer. Temperature and humidity also followed smooth seasonal patterns. Overall, there were no obvious flat lines, sudden spikes, or discontinuities in any of the variables.



### Plot 2: PM2.5 Before vs After (pm25_before_after_cleaning.png)

The second plot compares the PM2.5 series before and after cleaning. The main June to September 2023 wildfire spike is clearly visible in both versions, which shows that the cleaning process preserved this real pollution event. At the same time, the cleaned series has a slightly smoother baseline because the negative station readings and a small number of extreme values were removed.


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
| PM2.5 | 2,915,841 | 8,306 negatives | Impossible concentration | 1,133 |
| NO2 | 562,605 | 2,694 negatives | Impossible concentration | 1,133 |
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
| data/processed/master_daily.csv | 144.5 KB | Merged dataset, 12 columns, 1,133 rows |

-