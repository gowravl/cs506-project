# Data Profiling Report
## Respiratory Disease Prediction from Environmental Factors
**Team:** Gowrav Lakshmipathy | Priya Dilip Bajaria | Nandini Nandan Narvekar

---

## Overview

This report documents the findings from Phase 1 (Profiling) of the data cleaning process.
All six datasets were inspected before any cleaning was applied. Every cleaning decision
in Phase 2 is justified by a specific observation made here.

**Study period:** September 25, 2022 to October 31, 2025
(bound by the overlap of all six datasets after inner join)

**Approach:** Inspect first, clean based on findings. No blind application of standard practices.

---

## Dataset 1 — PM2.5 (Fine Particulate Matter)

**Source:** EPA AQS `daily_88101_YYYY.csv` (2022, 2023, 2024, 2025)
**Expected format:** One row per monitoring station per day, `Arithmetic Mean` in µg/m³

### Raw Profile

| Property | Value |
|---|---|
| Shape | 2,915,841 rows × 29 columns |
| Date range | 2022-01-01 to 2025-11-12 |
| Unique dates | 1,412 |
| Missing days in sequence | 0 |
| Unparseable dates | 0 |
| Duplicate rows | 0 |
| Duplicate date values | 2,914,429 (expected — one per station per day) |
| Unique states | 54 |
| Unique counties | 548 |
| Unique monitoring sites | 293 |

### Value Distribution

| Statistic | Arithmetic Mean (µg/m³) |
|---|---|
| Min | -7.775 |
| 25th percentile | 4.300 |
| Median | 6.408 |
| 75th percentile | 9.500 |
| Max | 833.843 |
| Mean | 7.722 |
| Std | 6.623 |

### Issues Found

| Issue | Count | Assessment |
|---|---|---|
| Negative values | 10,148 | Physically impossible — PM2.5 concentration cannot be negative. Sensor calibration errors. |
| Values above 200 µg/m³ | 192 | Real measurements — US wildfire smoke events (e.g. 2023 Canadian wildfires) |
| Values above 500 µg/m³ | 2 | Extreme but potentially real during severe wildfire events |
| Outliers by IQR (3x) | 43,124 | Distribution is a smooth heavy tail — these are real measurements, not errors |
| Pollutant Standard missing | 46.41% | Metadata column not used in model — no action needed |
| Event Type missing | 82.02% | Metadata column not used in model — no action needed |
| AQI max 1,513 | Several | AQI scale only goes to 500. However we use Arithmetic Mean, not AQI — no action needed |

### Station Coverage

| Metric | Value |
|---|---|
| Mean stations per day | 2,065 |
| Min stations per day | 6 |
| Max stations per day | 2,875 |
| Days with fewer than 100 stations | 12 (all in Nov 2025 — reporting lag) |

### Cleaning Decisions

| Decision | Justification |
|---|---|
| Drop rows where Arithmetic Mean < 0 | Physically impossible. 10,148 confirmed negatives. |
| Cap at 99.5th percentile | Removes extreme tail while preserving real wildfire signal. Hard threshold not appropriate because wildfire events produce legitimately extreme readings. |
| Parse dates with `format='mixed'` | EPA files use different date formats across years (MM/DD/YYYY vs YYYY-MM-DD) |
| Ignore AQI column | We use raw concentration (Arithmetic Mean), not the derived AQI index |
| Flag days with fewer than 50 stations | Sparse coverage days may produce less representative national averages |

---

## Dataset 2 — NO2 (Nitrogen Dioxide)

**Source:** EPA AQS `daily_42602_YYYY.csv` (2022, 2023, 2024, 2025)
**Expected format:** One row per monitoring station per hour, `Arithmetic Mean` in ppb

### Raw Profile

| Property | Value |
|---|---|
| Shape | 562,605 rows × 29 columns |
| Date range | 2022-01-01 to 2025-11-01 |
| Unique dates | 1,401 |
| Missing days in sequence | 0 |
| Duplicate date values | Expected (multiple stations + hourly readings) |
| Sample duration | 1 HOUR (unlike PM2.5 which is 24-hour) |

### Value Distribution

| Statistic | Arithmetic Mean (ppb) |
|---|---|
| Min | -4.579 |
| Max | 64.058 |
| Mean | 7.582 |
| Std | 6.653 |

### Issues Found

| Issue | Count | Assessment |
|---|---|---|
| Negative values | 3,254 | Physically impossible — NO2 concentration cannot be negative |
| Values above 200 ppb | 0 | No extreme outliers. EPA 1-hour standard is 100 ppb. Max 64 ppb is clean. |
| Missing dates vs PM2.5 | 11 days | NO2 ends Nov 1 vs PM2.5's Nov 12 — reporting lag, not a quality issue |

### Important Structural Note

NO2 is measured hourly (Sample Duration: 1 HOUR) while PM2.5 is measured on a 24-hour basis.
When grouping by date to compute a national daily average, NO2 averages across both stations
and hours of the day simultaneously. This is a valid daily mean but the aggregation basis
differs from PM2.5. Worth noting in methodology.

NO2 monitoring is concentrated in urban areas near traffic. The national average is therefore
more urban-biased than PM2.5.

### Cleaning Decisions

| Decision | Justification |
|---|---|
| Drop rows where Arithmetic Mean < 0 | Physically impossible. 3,254 confirmed negatives. |
| Cap at 99.5th percentile | Standard tail cleanup. No meaningful impact since max is only 64 ppb. |
| Parse dates with `format='mixed'` | Same mixed-format issue as PM2.5 |
| Accept 11-day coverage gap | Inner join handles this automatically. No imputation for coverage differences. |

---

## Dataset 3 — Ozone

**Source:** EPA AQS `daily_44201_YYYY.csv` (2022, 2023, 2024, 2025)
**Expected format:** One row per monitoring station per 8-hour window, `Arithmetic Mean` in ppm

### Raw Profile

| Property | Value |
|---|---|
| Shape | 1,412,282 rows × 29 columns |
| Date range | 2022-01-01 to 2025-11-01 |
| Unique dates | 1,401 |
| Missing days in sequence | 0 |
| Unparseable dates | 0 |
| Sample duration | 8-HR RUN AVG BEGIN HOUR |

### Value Distribution

| Statistic | Arithmetic Mean (ppm) |
|---|---|
| Min | -0.002 |
| Max | 0.136 |
| Mean | 0.033 |
| Std | 0.011 |

### Issues Found

| Issue | Count | Assessment |
|---|---|---|
| Negative values | 18 | Physically impossible — negligible count |
| Values above 0.2 ppm | 0 | No extreme outliers. EPA 8-hour standard is 0.070 ppm. Max 0.136 is high but real during severe summer pollution events. |
| Outliers by IQR (3x) | 68 | 0.005% of 1.4M rows — essentially no outlier problem |
| Same date gap as NO2 | 11 days | Same reporting lag explanation as NO2 |

### Important Structural Note

Ozone is measured as an 8-hour running average. Each station contributes multiple overlapping
8-hour window readings per day. When grouping by date, you average across all overlapping
windows and all stations. All three air quality variables (PM2.5, NO2, Ozone) have different
measurement time bases — a point worth noting in methodology.

### Cleaning Decisions

| Decision | Justification |
|---|---|
| Drop 18 negative values | Physically impossible |
| Cap at 99.5th percentile | Standard procedure. Max 0.136 ppm is real — no hard threshold needed. |
| Parse dates with `format='mixed'` | Same mixed-format issue as PM2.5 and NO2 |

---

## Dataset 4 — Temperature

**Source:** EPA AQS `daily_TEMP_YYYY.csv` (2022, 2023, 2024, 2025)
**Expected format:** One row per monitoring station per hour, `Arithmetic Mean` in degrees

### Raw Profile

| Property | Value |
|---|---|
| Shape | 1,184,025 rows × 29 columns |
| Date range | 2022-01-01 to 2025-10-31 |
| Unique dates | 1,400 |
| Missing days in sequence | 0 |
| Units of Measure | 100% Degrees Fahrenheit (all rows) |
| Pollutant Standard | 100% missing (expected — temperature is meteorological, not a pollutant) |
| AQI | 100% missing (expected — same reason) |
| Sample duration | 1 HOUR |

### Value Distribution

| Statistic | Arithmetic Mean (°F) |
|---|---|
| Min | -1,177.671 |
| Max | 179.596 |
| Mean | 57.790 |
| Std | 19.294 |

### Issues Found — Most Interesting Dataset

| Issue | Count | Assessment |
|---|---|---|
| Value at -1,177.67°F | 1 | Sentinel value from instrument firmware indicating a failed reading. Absolute zero is -459.67°F so this is physically impossible. |
| Values above 140°F | 79 | Surface radiant heat artifacts. EPA monitors are often sited on rooftops or near heat-radiating equipment. The sensor is working correctly but measuring surface heat, not ambient air temperature. The highest recorded air temperature on Earth is 130°F (Death Valley, 2021). |
| Unit question | Resolved | 100% Fahrenheit confirmed by `Units of Measure` column. No conversion needed. |

### Why This Matters

The minimum value of -1,177°F appears alarming but affects only 1 row out of 1,184,025.
However, if not removed, it would contaminate the national daily average for that specific day.
Similarly, the 79 surface-heat readings (141-160°F) are real sensor readings but do not
represent ambient air temperature and would slightly inflate summer averages.

### Key Insight

A generic 99.5th percentile cap would NOT have caught the -1,177°F sentinel value because
percentile caps only trim the upper tail. This is a specific case where profiling revealed
a cleaning approach (hard physical bounds) that a standard pipeline would have missed.

### Cleaning Decisions

| Decision | Justification |
|---|---|
| Drop values below -80°F | 1 sentinel value at -1,177°F. Absolute zero is -459.67°F. |
| Drop values above 140°F | 79 surface radiant heat artifacts. Above any recorded air temperature. |
| Use hard bounds, not percentile cap | Physical limits are known and meaningful for temperature |
| No unit conversion | 100% Fahrenheit confirmed |

---

## Dataset 5 — Relative Humidity

**Source:** EPA AQS `daily_RH_DP_YYYY.csv` (2022, 2023, 2024, 2025)
**Expected format:** Mixed file containing both Relative Humidity (%) and Dew Point readings

### Raw Profile (before parameter filter)

| Property | Value |
|---|---|
| Shape | 579,258 rows × 29 columns |
| Date range | 2022-01-01 to 2025-11-01 |
| Unique dates | 1,401 |
| Relative Humidity rows | 535,740 (92.5%) |
| Dew Point rows | 43,518 (7.5%) |

### Value Distribution — All Rows Combined (misleading without filter)

| Statistic | Value |
|---|---|
| Min | -25.0 |
| Max | 101.3 |
| Mean | 58.6 |
| Std | 20.5 |

### Value Distribution — Relative Humidity Rows Only (correct)

| Statistic | Value |
|---|---|
| Min | 0.0% |
| Max | 101.3% |
| Values below 0% | 0 |
| Values above 100% | 2 |

### Issues Found

| Issue | Count | Assessment |
|---|---|---|
| Dew Point rows mixed in | 43,518 | Must be filtered out. Dew Point is in different units (°F or °C) and cannot be averaged with RH (%). If included, the national daily average would be meaningless. |
| Values above 100% RH | 2 | Physically impossible. Sensor calibration drift — instruments occasionally read slightly above 100%. Negligible (0.0004% of RH rows). |
| Negative values (all rows) | Present in dew point rows only | After filtering to RH only, zero negative values remain. |
| Min -25.0 in raw profile | From dew point rows | Completely resolved by filtering to Relative Humidity only. |
| Outliers by IQR | 0 | Cleanest outlier profile of all five EPA datasets. |

### Key Insight

The -25% minimum that appears in the full profile is entirely caused by Dew Point rows,
not by RH sensor errors. This was only discovered by checking the `Parameter Name` column.
Filtering to Relative Humidity rows resolves the issue completely — no value-level
cleaning is needed for RH beyond the 2 rows above 100%.

### Cleaning Decisions

| Decision | Justification |
|---|---|
| Filter to Relative Humidity rows only | File contains mixed parameters. Dew Point rows are in different units and cannot be combined with RH. |
| Drop 2 rows above 100% RH | Physically impossible. Sensor calibration drift. |
| No further value cleaning needed | After parameter filter, RH data is perfectly clean (0 negatives, 0 IQR outliers). |

---

## Dataset 6 — NSSP Respiratory (CDC)

**Source:** CDC NSSP `nssp_respiratory.csv`
**Expected format:** Daily rows with pathogen, geography, and percent_visits

### Raw Profile

| Property | Value |
|---|---|
| Shape (raw) | 259,896 rows × 4 columns |
| Columns | date, pathogen, geography, percent_visits |
| Unique pathogens | 4 (ARI, COVID, Influenza, RSV) |
| Unique geographies | 51 (50 states + United States national) |
| Rows per pathogen | 64,974 (perfectly balanced) |
| Rows per geography | 5,096 (perfectly balanced) |

### After Filtering to ARI + United States

| Property | Value |
|---|---|
| Rows | 1,274 |
| Date range | 2022-09-25 to 2026-03-21 |
| Unique dates | 1,274 |
| Missing days in sequence | 0 |
| Missing values | None |
| Duplicate dates | 0 |

### Value Distribution (percent_visits)

| Statistic | Value |
|---|---|
| Min | 7.09% |
| Max | 26.58% |
| Mean | 13.47% |
| Std | 4.02% |
| Values below 0% | 0 |
| Values above 100% | 0 |
| Outliers by IQR | 0 |

### Time Series Visual Findings

The raw time series plot revealed:
- **Clear annual seasonality** — strong winter peaks every December-January, summer troughs every July-August
- **Three complete seasonal cycles** — 2022-23, 2023-24, 2024-25
- **Consistent amplitude** — each winter peak reaches roughly 25-26%, each summer trough drops to roughly 7-8%
- **No anomalies** — no sudden spikes, no flat-line periods, no obvious data gaps
- **Weekly oscillation** — the high-frequency jagged pattern within each season reflects the day-of-week effect (fewer ED visits on weekends). This is real signal, not noise, and should be preserved.

### Geography Check

`United States` confirmed as an exact match geography label. The regex search that
returned `Massachusetts` was a false positive from the substring "us" in "massachUSettS".
The filter must use exact string matching (`== 'United States'`), not a contains pattern.

### Binding Constraint

NSSP data starts September 25, 2022 — later than all EPA datasets which start January 1, 2022.
After the inner join, the master dataset will begin on September 25, 2022, losing approximately
9 months of EPA data. This is an inherent limitation of the data source and cannot be resolved
without a different respiratory outcome dataset.

### Cleaning Decisions

| Decision | Justification |
|---|---|
| Filter to ARI pathogen only | ARI (Acute Respiratory Illness) is the broadest category covering all respiratory diagnoses. Using individual pathogen rows (COVID, Flu, RSV) would cause double-counting since ARI already includes them. |
| Filter to United States geography | National aggregate provides maximum completeness and avoids state-level reporting variations. |
| Do NOT interpolate missing days | Unlike environmental sensor data, missing ED visit data could represent real reporting gaps (hospital outages, data submission delays). Interpolating health outcomes could introduce false signals into the target variable. |
| Preserve day-of-week oscillation | The weekly pattern is real signal reflecting genuine behavioral differences in ED utilization. Smoothing it out would remove information the model could learn from. |

---

## Cross-Dataset Comparison

### Coverage Summary

| Dataset | Date range | Days | Ends |
|---|---|---|---|
| PM2.5 | 2022-01-01 to 2025-11-12 | 1,412 | Nov 12, 2025 |
| NO2 | 2022-01-01 to 2025-11-01 | 1,401 | Nov 1, 2025 |
| Ozone | 2022-01-01 to 2025-11-01 | 1,401 | Nov 1, 2025 |
| Temperature | 2022-01-01 to 2025-10-31 | 1,400 | Oct 31, 2025 |
| Humidity | 2022-01-01 to 2025-11-01 | 1,401 | Nov 1, 2025 |
| Respiratory | 2022-09-25 to 2026-03-21 | 1,274 | Ongoing |

**Effective master dataset range after inner join:** 2022-09-25 to 2025-10-31
**Expected master rows:** ~1,132 days

### Data Quality Summary

| Dataset | Raw rows | Rows to remove | Removal reason | Quality rating |
|---|---|---|---|---|
| PM2.5 | 2,915,841 | ~10,150 | Negative concentrations | Good |
| NO2 | 562,605 | ~3,254 | Negative concentrations | Good |
| Ozone | 1,412,282 | 18 | Negative concentrations | Excellent |
| Temperature | 1,184,025 | 80 | 1 sentinel value + 79 surface heat artifacts | Excellent |
| Humidity | 579,258 | ~43,520 | 43,518 dew point rows + 2 above 100% | Excellent |
| Respiratory | 259,896 | ~195,672 | Filter to ARI + US (by design, not errors) | Excellent |

### Measurement Basis Comparison

| Dataset | Sampling basis | Implication for daily average |
|---|---|---|
| PM2.5 | 24-hour integrated sample | One reading per station per day |
| NO2 | 1-hour readings | 24 readings per station per day averaged |
| Ozone | 8-hour running average | Multiple overlapping windows per station per day averaged |
| Temperature | 1-hour readings | 24 readings per station per day averaged |
| Humidity | 1-hour readings | 24 readings per station per day averaged |
| Respiratory | Daily aggregate | Already a daily value, no further aggregation |

### Key Insights Discovered During Profiling

1. **Temperature sentinel value would have survived percentile capping.** The -1,177°F value is at the extreme lower tail. A 99.5th percentile cap only trims the upper tail. Only hard physical bounds catch this type of error. Without profiling this would have contaminated the national daily temperature average.

2. **Humidity negative values were entirely from Dew Point rows.** After filtering to Relative Humidity only, zero negative values remain. The -25% minimum in the raw profile was completely misleading without the parameter filter context.

3. **PM2.5 extreme values (above 200 µg/m³) are real wildfire events, not errors.** A naive outlier removal would have deleted legitimate pollution signal from the 2023 Canadian wildfire events. These are scientifically meaningful data points for a respiratory illness model.

4. **All three air quality datasets use different measurement time bases** (24-hour, 1-hour, 8-hour). All produce valid daily national averages after grouping by date, but the aggregation mechanism differs. Worth one sentence of methodological explanation.

5. **NSSP is the binding constraint on the master dataset.** It starts 9 months later than the EPA datasets. Nothing can be done about this — it reflects when CDC began publishing this particular data product. The study period effectively begins September 2022.

6. **The weekly oscillation in respiratory data is signal, not noise.** The day-of-week pattern visible in the time series reflects real behavioral differences in ED utilization on weekends. This should be preserved and could even be added as a feature (day-of-week indicator) in the model.

---

## Cleaning Decision Reference Table

| Dataset | Step | Operation | Justification |
|---|---|---|---|
| PM2.5 | 1 | Drop Arithmetic Mean < 0 | 10,148 negatives — physically impossible |
| PM2.5 | 2 | Cap at 99.5th percentile | Removes extreme tail while preserving wildfire signal |
| PM2.5 | 3 | Parse dates with format='mixed' | Mixed date formats across yearly files |
| NO2 | 1 | Drop Arithmetic Mean < 0 | 3,254 negatives — physically impossible |
| NO2 | 2 | Cap at 99.5th percentile | Standard cleanup — no meaningful impact (max 64 ppb) |
| NO2 | 3 | Parse dates with format='mixed' | Same as PM2.5 |
| Ozone | 1 | Drop 18 negative values | Physically impossible |
| Ozone | 2 | Cap at 99.5th percentile | Standard cleanup — max 0.136 ppm is real |
| Ozone | 3 | Parse dates with format='mixed' | Same as PM2.5 |
| Temperature | 1 | Drop values below -80°F | 1 sentinel value at -1,177°F — below absolute zero |
| Temperature | 2 | Drop values above 140°F | 79 surface heat artifact readings |
| Temperature | 3 | Parse dates with format='mixed' | Same as PM2.5 |
| Humidity | 1 | Filter to Relative Humidity rows | 43,518 Dew Point rows are different units |
| Humidity | 2 | Drop values above 100% RH | 2 rows — physically impossible |
| Respiratory | 1 | Filter pathogen == 'ARI' | Broadest category; individual pathogens would double-count |
| Respiratory | 2 | Filter geography == 'United States' | National aggregate for maximum completeness |
| Respiratory | 3 | No value cleaning | Zero invalid values found after filter |
| Respiratory | 4 | No interpolation of missing days | Health outcome gaps may be real reporting failures |
| All EPA | — | Group by date, take mean | Reduces multiple station readings to one national daily value |
| All EPA | — | Filter to 2022-09-25 to 2025-10-31 | Study period bound by NSSP and Temperature coverage |

---

*Report generated after Phase 1 profiling. All findings are based on direct inspection of raw data.*
*Phase 2 cleaning code applies exactly the decisions documented in this report.*
