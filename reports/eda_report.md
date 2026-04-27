# Exploratory Data Analysis Report
## Respiratory Disease Prediction from Environmental Factors

## Overview

This report documents all findings from the exploratory data analysis phase.
The analysis was conducted on the cleaned master dataset of 1,133 daily rows
spanning September 25, 2022 to October 31, 2025.

**Input:** `data/processed/master_daily.csv` : 1,133 rows, 12 columns  
**Output:** `data/processed/features_daily.csv` : 1,119 rows, 16 columns


---

## Figure 1  Time Series: Key Environmental Relationships

**File:** `outputs/figures/eda_01_time_series_key_relationships.png`


### 

- **Temperature** (r = −0.812 at lag-0): the single strongest predictor. Its inverse seasonal cycle against respiratory illness is the dominant signal in the entire dataset.
- **NO₂** (r = +0.640 at lag-0, r = +0.743 at 12-day lag): illustrates that some relationships are delayed visible seasonal co-movement, with correlation improving when NO₂ is shifted forward 12 days.

The remaining three features (ozone, humidity, PM2.5) follow patterns derivable from these two panels and would add length without new information.

### Key findings

- Temperature and respiratory illness move in near-perfect inverse seasonal cycles: every winter peak in illness corresponds to a cold trough in temperature, and every summer illness trough corresponds to a warm period.
- NO₂ and respiratory illness track each other closely, both peaking in winter and falling in summer. The seasonal co-movement is visible even without lag adjustment.
- The 2023 Canadian wildfire PM2.5 spike (June–September 2023) does not produce a corresponding spike in respiratory illness, visually confirming PM2.5 is a weak predictor here.

---

## Figure 2 Lag Correlation Profiles

**File:** `outputs/figures/eda_02_lag_correlation_profiles.png`

### Results

| Feature | Lag-0 r | Optimal lag | Best r | Improvement |
|---|---|---|---|---|
| Temperature (°F) | −0.812 | **0 days** | −0.812 | None immediate |
| Relative Humidity (%) | +0.530 | **0 days** | +0.530 | None immediate |
| NO₂ (ppb) | +0.640 | **12 days** | +0.743 | +0.103 |
| Ozone (ppm) | −0.656 | **13 days** | −0.732 | +0.076 |
| PM2.5 (µg/m³) | −0.142 | **14 days** | −0.153 | +0.011 negligible |

All p-values < 0.0001 across all features and all lags.

### Interpretation

Temperature and humidity profiles are flat across all 14 lags, confirming the relationship is immediate at the national population level. Temperature is also the highest-magnitude line on the chart at every lag point.

NO₂ and ozone rise steadily to a peak at lag 12–13 days before declining slightly. The improvement (+0.10 and +0.08) is meaningful and justifies using lagged versions in the model. However, because both series change slowly over the year, part of the apparent lag improvement reflects shared seasonality rather than a causal delay the seasonal pattern at day N closely resembles the pattern 12 days later.

PM2.5 starts near zero and remains near zero across all lags, never reaching the significance band. Lag adjustment does not salvage this feature. Its weak relationship is explained by seasonal confounding: wildfire smoke (summer) pushes PM2.5 up exactly when respiratory illness is at its annual low.

---

## Figure 3  Feature Correlation Ranking

**File:** `outputs/figures/eda_03_feature_correlation_ranking.png`

### Results

Sorted by best-lag |r| (strongest to weakest):

| Feature | Lag-0 r | Best-lag r | Optimal lag |
|---|---|---|---|
| Temperature (°F) | −0.812 | −0.812 | 0 days |
| NO₂ (ppb) | +0.640 | +0.743 | 12 days |
| Ozone (ppm) | −0.656 | −0.732 | 13 days |
| Relative Humidity (%) | +0.530 | +0.530 | 0 days |
| PM2.5 (µg/m³) | −0.142 | −0.153 | 14 days |

### Interpretation

Temperature stands alone as the dominant predictor its best-lag r is unchanged from lag-0 and is substantially higher than all other features. NO₂ and ozone are the second tier: both benefit from lagging, and with optimal lag applied they nearly match the strength of the no-lag temperature correlation. Humidity is the fourth feature and shows no lag benefit. PM2.5 is the weakest by a wide margin and shows essentially no improvement from lagging.

The chart directly justifies the feature engineering choices in the next section: temperature and humidity are used same-day; NO₂ and ozone are shifted 12 and 13 days respectively; PM2.5 is shifted 14 days but its weak signal is acknowledged.

---

## Feature Engineering Output

Based on all EDA findings, the following feature set was created:

| Feature | Source | Lag | Justification |
|---|---|---|---|
| temperature | temperature | 0 days | Strongest predictor (r = −0.812), immediate effect |
| humidity | humidity | 0 days | r = +0.530, no benefit from lagging |
| no2_lag12 | no2 | 12 days | r improves from +0.640 to +0.743 |
| ozone_lag13 | ozone | 13 days | r improves from −0.656 to −0.732 |
| pm25_lag14 | pm25 | 14 days | Weakest feature included for completeness; r = −0.153 |
| month | date | — | 81.4% of variance is seasonal |
| day_of_week | date | — | Weekly oscillation in ED utilization confirmed |
| is_weekend | date | — | Binary indicator for Sat/Sun |
| season_num | date | — | 0=Winter, 1=Spring, 2=Summer, 3=Fall |

**Features dataset:** `data/processed/features_daily.csv`  
**Rows:** 1,119 (14 rows dropped from the first 14 days due to lag-14 NaN)  
**Date range:** October 9, 2022 to October 31, 2025  
**Columns:** 16 (includes `month_sin` and `month_cos` cyclic encodings)

---

## Key Findings

- **Temperature dominates:** r = −0.812, the single strongest predictor and the only one that needs no lag adjustment. Cold temperature → more respiratory ED visits, directly and immediately.
- **Seasonality explains 81.4% of variance:** A model using season alone could achieve approximately R² = 0.81. Environmental features explain only the residual variation beyond the seasonal cycle.
- **NO₂ and ozone benefit from lagging:** Shifting forward 12–13 days improves their correlations by +0.10 and +0.08. The improvement is partly causal (disease progression delay) and partly seasonal (slow-changing variables look similar 12 days apart).
- **PM2.5 is the weakest feature:** r = −0.142 at lag-0 and −0.153 at best lag. The near-zero correlation is due to seasonal confounding  wildfire smoke spikes occur in summer when respiratory illness is low.
- **Correlations for NO₂ and ozone are not stable across seasons:** Their correlations flip sign in different seasons (visible in rolling correlation analysis from the prior EDA run), meaning their overall correlations are heavily seasonality-driven. Simple linear models may misinterpret these effects without seasonal interaction terms or non-linear structure.
