# Data Profiling Report
## Respiratory Disease Prediction from Environmental Factors
**Team:** Gowrav Lakshmipathy | Priya Dilip Bajaria | Nandini Nandan Narvekar

---

## Overview

This report explains what we found during Phase 1 (Profiling) of the data cleaning process.
Every cleaning step done later in Phase 2 is based on observations and dataset analysis that we have set forth here.

**Study period:** September 25, 2022 to October 31, 2025
(This range comes from the overlapping time period across all six datasets after performing an inner join.)

**Approach:** First we understand the data, then clean it based on actual issues found.

---

## Dataset 1 - PM2.5 (Fine Particulate Matter)

**Source:** EPA AQS (United States Environmental Protection Agency Air Quality System) `daily_88101_YYYY.csv` (2022, 2023, 2024, 2025)

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
| Duplicate date values | 2,914,429 (expected - one per station per day) |
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
| Negative values | 10,148 | Not possible - PM2.5 concentration cannot be negative. Sensor calibration errors. |
| Values above 200 µg/m³ | 192 | High count due to US wildfire smoke events (e.g. 2023 Canadian wildfires) |
| Values above 500 µg/m³ | 2 | Extreme but potentially real during the severe wildfire events |
| Outliers by IQR (3x) | 43,124 | Distribution is a smooth heavy tail - these are real measurements, not errors |
| AQI max 1,513 | Several | AQI scale only goes to 500. However we use Arithmetic Mean, not AQI so no action needed |

### Station Coverage

| Metric | Value |
|---|---|
| Mean stations per day | 2,065 |
| Min stations per day | 6 |
| Max stations per day | 2,875 |
| Days with fewer than 100 stations | 12 (all in Nov 2025 - reporting lag) |

### Cleaning Decisions

| Decision | Justification |
|---|---|
| Drop rows where Arithmetic Mean < 0 | Negative mean not possible. (10,148 negatives in raw data.) |
| Cap at 99.5th percentile | Removes extreme high values while keeping real wildfire events intact. A hard threshold wouldn’t work here because wildfires naturally produce legitimately extreme PM2.5 readings. |
| Parse dates with `format='mixed'` | EPA files use different date formats across years (MM/DD/YYYY vs YYYY-MM-DD) |
| Ignore AQI column | We use raw concentration (Arithmetic Mean), not the derived AQI index |
| Track station counts via n_stations column in master dataset | Sparse coverage days may produce less representative national averages |

---

## Dataset 2 - NO2 (Nitrogen Dioxide)

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
| Sample duration | 1 hour (unlike PM2.5 which is 24-hour) |

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
| Negative values | 3,254 | Not possible as NO2 concentration cannot be negative |
| Values above 200 ppb | 0 | No extreme outliers. EPA 1-hour standard is 100 ppb. Max 64 ppb is clean. |
| Missing dates vs PM2.5 | 11 days | NO2 ends Nov 1 vs PM2.5's Nov 12 - reporting lag, not a quality issue |

### Important Structural Note

NO₂ is measured every hour (Sample Duration: 1 hour), while PM2.5 is measured over a 24-hour period.
So when we group the data by date to calculate a national daily average, the NO₂ values are averaged across both different monitoring stations and all hours in the day at the same time. This still gives a valid daily average, but it’s calculated differently compared to PM2.5. This difference should be clearly mentioned in the methodology.

Also, NO₂ monitoring stations are mostly located in urban areas, especially near traffic. Because of this, the national average for NO₂ is more influenced by urban conditions, unlike PM2.5, which is more evenly distributed.

### Cleaning Decisions

| Decision | Justification |
|---|---|
| Drop rows where Arithmetic Mean < 0 | Not possible. (3,254 negatives in raw data.) |
| Cap at 99.5th percentile | Standard tail cleanup. No meaningful impact since max is only 64 ppb. |
| Parse dates with `format='mixed'` | Same mixed-format issue as PM2.5 |
| Accept 11-day coverage gap | Inner join handles this automatically. No imputation for coverage differences. |

---

## Dataset 3 - Ozone

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
| Negative values | 18 | Not possible - negligible count |
| Values above 0.2 ppm | 0 | No extreme outliers. EPA 8-hour standard is 0.070 ppm. Max 0.136 is high but real during severe summer pollution events. |
| Outliers by IQR (3x) | 68 | 0.005% of 1.4M rows - essentially no outlier problem |
| Same date gap as NO2 | 11 days | Same reporting lag explanation as NO2 |

### Important Structural Note

Ozone is measured using an 8-hour running average, which means each station reports multiple overlapping 8-hour readings within a single day. When we group the data by date, we end up averaging across all these overlapping time windows as well as across all stations.

It’s important to note that all three air quality variables-PM2.5, NO₂, and ozone-are measured over different time intervals. This difference in measurement basis should be clearly mentioned in the methodology.

### Cleaning Decisions

| Decision | Justification |
|---|---|
| Drop 18 negative values | Not possible |
| Cap at 99.5th percentile | Standard procedure. Max 0.136 ppm is real - no hard threshold needed. |
| Parse dates with `format='mixed'` | Same mixed-format issue as PM2.5 and NO2 |

---

## Dataset 4 - Temperature

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
| Pollutant Standard | 100% missing (expected - temperature is meteorological, not a pollutant) |
| AQI | 100% missing (expected - same reason) |
| Sample duration | 1 hour |

### Value Distribution

| Statistic | Arithmetic Mean (°F) |
|---|---|
| Min | -1,177.671 |
| Max | 179.596 |
| Mean | 57.790 |
| Std | 19.294 |

### Issues Found

| Issue | Count | Assessment |
|---|---|---|
| Value at -1,177.67°F | 1 | Sentinel value from instrument firmware indicating a failed reading. Absolute zero is -459.67°F so this is Not possible. |
| Values above 140°F | 79 | Some of the extreme temperature values are likely due to surface radiant heat effects. EPA monitors are often placed on rooftops or near equipment that gives off heat, so the sensors can end up capturing that surface heat instead of the actual ambient air temperature. For context, the highest recorded air temperature on Earth is 130°F (Death Valley, 2021), which helps show that some unusually high readings in the data may not reflect true air conditions. |
| Unit question | Resolved | 100% Fahrenheit confirmed by `Units of Measure` column. No conversion needed. |

### Why This Matters

The minimum value of -1,177°F (Not possible) only appears in 1 row out of 1,184,025.
Even though it’s just a single value, keeping it would distort the national daily average for that particular day, so it still needs to be handled.
Similarly, the 79 high temperature readings in the range of 141–160°F are actual sensor readings, but they likely capture surface heat rather than true air temperature. If left in the data, they could slightly push up the average temperatures during summer.

### Key Insight

Using a generic 99.5th percentile cap would not have caught the -1,177°F value, since percentile-based methods only remove extreme values from the upper end.
This is a clear example of why doing profiling first was important. It showed that we needed a different cleaning approach-setting hard physical limits-something a standard pipeline would have likely missed.

### Cleaning Decisions

| Decision | Justification |
|---|---|
| Drop values below -80°F | 1 sentinel value at -1,177°F. Absolute zero is -459.67°F. |
| Drop values above 140°F | 79 surface radiant heat artifacts. Above any recorded air temperature. |
| Use hard bounds, not percentile cap | Physical limits are known and meaningful for temperature |
| No unit conversion | 100% Fahrenheit confirmed |

---

## Dataset 5 - Relative Humidity

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

### Value Distribution - All Rows Combined (misleading without filter)

| Statistic | Value |
|---|---|
| Min | -25.0 |
| Max | 101.3 |
| Mean | 58.6 |
| Std | 20.5 |

### Value Distribution - Relative Humidity Rows Only 

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
| Values above 100% RH | 2 | Not possible. Sensor calibration drift - instruments occasionally read slightly above 100%. Negligible (0.0004% of RH rows). |
| Negative values (all rows) | Present in dew point rows only | After filtering to RH only, zero negative values remain. |
| Min -25.0 in raw profile | From dew point rows | Completely resolved by filtering to Relative Humidity only. |
| Outliers by IQR | 0 | Cleanest outlier profile of all five EPA datasets. |

### Key Insight

The -25% minimum in the full profile comes entirely from Dew Point rows, not from any error in the Relative Humidity sensors. Once we filter to just Relative Humidity rows, the problem goes away - no additional value-level cleaning is needed, aside from the two rows that exceed 100%.

### Cleaning Decisions

| Decision | Justification |
|---|---|
| Filter to Relative Humidity rows only | File contains mixed parameters. Dew Point rows are in different units and cannot be combined with RH. |
| Drop 2 rows above 100% RH | Not possible. Sensor calibration drift. |
| No further value cleaning needed | After parameter filter, RH data is perfectly clean (0 negatives, 0 IQR outliers). |

---

## Dataset 6 - NSSP Respiratory (CDC)

**Source:** CDC NSSP (Centers for Disease Control and Prevention National Syndromic Surveillance Program) `nssp_respiratory.csv`
**Expected format:** Daily rows with pathogen, geography, and percent_visits

### Raw Profile

| Property | Value |
|---|---|
| Shape (raw) | 259,896 rows × 4 columns |
| Columns | date, pathogen, geography, percent_visits |
| Unique pathogens | 4 (ARI, COVID, Influenza, RSV) |
| Unique geographies | 51 (50 states + United States national) |
| Rows per pathogen | 64,974 |
| Rows per geography | 5,096 |

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
- **Clear annual seasonality** - strong peaks during winter (December–January) and low points in summer (July–August)
- **Three complete seasonal cycles** - covering 2022–23, 2023–24, and 2024–25
- **Consistent amplitude** - winter peaks are around 25–26%, while summer lows drop to about 7–8%
- **No anomalies** - there are no sudden spikes, flat-line sections, or obvious missing data
- **Weekly oscillation** - the small, frequent ups and downs within each season are due to day-of-week effects (fewer ED visits on weekends). This is actual signal, not noise, so it should be kept as is

### Geography Check

`United States` was the correct geography label. The  regex match that returned `Massachusetts` was actually a false positive, caused by the substring `US` inside the word `massachUSettS`.
So, the filter should use exact string matching `(== 'United States') `instead of a contains-based pattern to avoid these kinds of mistakes.

### Binding Constraint

The NSSP data starts on September 25, 2022, which is later than the EPA datasets that begin on January 1, 2022.
Because of this, after performing the inner join, the final combined dataset will also start from September 25, 2022. This means we lose about 9 months of EPA data.
This is a limitation of the data itself and can’t really be fixed unless we use a different dataset for respiratory outcomes.

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
**Expected master rows:** 1,133 days

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

1. **Extreme low temperature needed hard bounds**: The -1,177°F reading sits way below realistic values. A 99.5th percentile filter only removes extreme high values, so this kind of error would have slipped through. Hard physical limits were needed to catch it-otherwise it would have skewed the national daily temperature average.

2. **Negative humidity values were misleading**: All negative values came from Dew Point rows. Once we focused only on Relative Humidity, there were no negative numbers left. That -25% minimum in the raw profile looked alarming but was completely misleading without filtering by parameter.

3. **High PM2.5 readings are real events, not mistakes.**: Values above 200 µg/m³ correspond to actual wildfire events, like the 2023 Canadian wildfires. Removing them as outliers would have deleted meaningful pollution signals that are important for a respiratory illness model.

4. **Different Air Quality Metrics Have Different Time Bases**: PM2.5 is 24-hour, NO₂ is 1-hour, and ozone is 8-hour running averages. They all give valid daily national averages after grouping by date, but the way the averages are calculated differs. It’s worth noting this in the methodology.

5. **NSSP Limits the Study Period**: NSSP data starts September 25, 2022, about 9 months after the EPA datasets. This sets the effective start of the master dataset and can’t be changed-it reflects when the CDC began publishing this data product.

6. **Weekly Patterns in Respiratory Data Are Real**: The jagged ups and downs in the time series come from day-of-week effects-fewer ED visits on weekends. This is real signal, not noise, and should be preserved. It could even be included as a model feature (day-of-week indicator).

---

## Cleaning Decision Reference Table

| Dataset | Step | Operation | Justification |
|---|---|---|---|
| PM2.5 | 1 | Drop Arithmetic Mean < 0 | 10,148 negatives - Not possible |
| PM2.5 | 2 | Cap at 99.5th percentile | Removes extreme tail while preserving wildfire signal |
| PM2.5 | 3 | Parse dates with format='mixed' | Mixed date formats across yearly files |
| NO2 | 1 | Drop Arithmetic Mean < 0 | 3,254 negatives - Not possible |
| NO2 | 2 | Cap at 99.5th percentile | Standard cleanup - no meaningful impact (max 64 ppb) |
| NO2 | 3 | Parse dates with format='mixed' | Same as PM2.5 |
| Ozone | 1 | Drop 18 negative values | Not possible |
| Ozone | 2 | Cap at 99.5th percentile | Standard cleanup - max 0.136 ppm is real |
| Ozone | 3 | Parse dates with format='mixed' | Same as PM2.5 |
| Temperature | 1 | Drop values below -80°F | 1 sentinel value at -1,177°F - below absolute zero |
| Temperature | 2 | Drop values above 140°F | 79 surface heat artifact readings |
| Temperature | 3 | Parse dates with format='mixed' | Same as PM2.5 |
| Humidity | 1 | Filter to Relative Humidity rows | 43,518 Dew Point rows are different units |
| Humidity | 2 | Drop values above 100% RH | 2 rows - Not possible |
| Respiratory | 1 | Filter pathogen == 'ARI' | Broadest category; individual pathogens would double-count |
| Respiratory | 2 | Filter geography == 'United States' | National aggregate for maximum completeness |
| Respiratory | 3 | No value cleaning | Zero invalid values found after filter |
| Respiratory | 4 | No interpolation of missing days | Health outcome gaps may be real reporting failures |
| All EPA | - | Group by date, take mean | Reduces multiple station readings to one national daily value |
| All EPA | - | Filter to 2022-09-25 to 2025-10-31 | Study period bound by NSSP and Temperature coverage |

---