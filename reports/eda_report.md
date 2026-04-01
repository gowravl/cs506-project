# Exploratory Data Analysis Report
## Respiratory Disease Prediction from Environmental Factors

## Overview

This report documents all findings from the exploratory data analysis phase.
The analysis was conducted on the cleaned master dataset of 1,133 daily rows
spanning September 25, 2022 to October 31, 2025.

**Input:** `data/processed/master_daily.csv` — 1,133 rows, 7 columns
**Output:** `data/processed/features_daily.csv` — 1,119 rows, 14 columns

The three questions this phase answers:
1. Which environmental variables correlate most strongly with respiratory illness?
2. What seasonal patterns exist and how do they interact?
3. Is there a time lag between environmental conditions and respiratory illness?

---

## EDA 1: Pearson Correlation Matrix

### Results

| Feature | Correlation with Respiratory % ED Visits | Direction |
|---|---|---|
| Temperature (F) | -0.812 | Negative — stronger |
| Ozone (ppm) | -0.656 | Negative |
| NO2 (ppb) | +0.640 | Positive |
| Relative Humidity (%) | +0.530 | Positive |
| PM2.5 (µg/m³) | -0.142 | Negative — weakest |

### Interpretation
Temperature is the strongest predictor and is negatively related to respiratory ED visits, meaning colder days are linked to more visits.
NO2 has a strong positive relationship, likely because it is higher in winter when respiratory illness is also higher.
Ozone has a strong negative relationship, mainly because it peaks in summer when respiratory illness is lower.
Humidity shows a moderate positive relationship with respiratory ED visits.
PM2.5 has the weakest relationship and appears negative, likely due to seasonal confounding from summer wildfire smoke.

### Notable inter-feature correlations

- Temperature and Ozone: r = +0.549 (both summer-peaking)
- Temperature and NO2: r = -0.624 (NO2 higher in winter when temperature is low)
- Ozone and Humidity: r = -0.585 (humid winters, dry summers)

---

## EDA 2: Feature Correlation Bar Chart

The bar chart confirmed the ranking visually. Temperature and NO2/Ozone are the
three features with correlations above 0.6 in absolute value. PM2.5 stands alone
at -0.142, substantially weaker than all others. This chart is the clearest single
visual for explaining feature selection at the check-in.

---

## EDA 3: Scatter Plots by Season

### Key finding: correlations are seasonally driven

Most correlations are mainly due to shared seasonality, not independent environmental effects.
Temperature mostly acts as a season proxy: winter has cold temperatures and high illness, summer has warm temperatures and low illness.
Ozone shows the same seasonal pattern, so its negative correlation is also mostly driven by season.
NO2 has a positive relationship, but it is still largely tied to winter months when illness is higher.
PM2.5 is the weakest predictor, with no clear pattern even within seasons.
Modeling implication: season or month should be included as a feature, otherwise the model may confuse seasonal patterns for true environmental effects.

---

## EDA 4: Seasonal Decomposition

### Results

| Component | Variance explained |
|---|---|
| Seasonality | **81.4%** |
| Trend | 0.2% |
| Residual | 17.5% |

### Interpretation

Annual seasonality explains 81.4% of the variance in respiratory illness, making it the biggest driver in the data.
A model using season alone could achieve about R² = 0.81, even without environmental variables.
Environmental features explain only the remaining variation beyond the seasonal pattern.
The trend component is negligible (0.2%), showing no meaningful long-term increase or decrease from 2022–2025.
The seasonal pattern is very consistent: peaks in December–January and troughs in July–August repeat each year.
The residual variation shows a weekly pattern, suggesting day of week should also be included as a model feature.

---

## EDA 5: Monthly Box Plots

### Key observations per variable


Respiratory ED visits are highest in winter (January, February, December) and lowest in summer (July to September), with a very consistent pattern each year.
PM2.5 peaks in summer, especially during wildfire season, which helps explain its misleading negative correlation with respiratory illness.
NO2 peaks in winter and drops in summer, closely matching the respiratory illness pattern.
Ozone shows the opposite pattern of NO2, peaking in warmer months and falling in winter.
Temperature follows a very stable yearly cycle, from colder winters to warmer summers.
Humidity is generally higher in winter and lower in spring and summer, though it varies more than the other variables.


---

## EDA 6: Lag Correlation Analysis


### Results

| Feature | Lag-0 r | Optimal lag | Best r | Improvement |
|---|---|---|---|---|
| Temperature (F) | -0.812 | **0 days** | -0.812 | None |
| Relative Humidity (%) | +0.530 | **0 days** | +0.530 | None |
| NO2 (ppb) | +0.640 | **12 days** | +0.743 | +0.103 |
| Ozone (ppm) | -0.656 | **13 days** | -0.732 | +0.076 |
| PM2.5 (µg/m³) | -0.142 | **14 days** | -0.153 | +0.011 |

All p-values < 0.0001 for all features at all lags.

### Interpretation by feature

Temperature and humidity: best lag is 0 days, so their relationship with respiratory ED visits appears immediate at the population level.
NO2: best lag is 12 days, and the correlation improves noticeably, suggesting a delayed effect consistent with disease progression.
Ozone: best lag is 13 days, with a similar improvement, which fits its similar airway irritation mechanism to NO2.
PM2.5: best lag is 14 days, but the correlation barely improves, showing that lag does not solve its weak relationship.
Main takeaway: lagging helps for NO2 and ozone, but not for PM2.5, whose weak effect is mainly due to seasonal confounding.

### Critical insight from lag plots

NO2 and ozone stay strongly correlated across all lags from 0 to 14 days.
Because the correlation changes only a little across lags, the lag effect may not reflect a true causal delay.
Instead, it likely shows shared seasonality, since both pollution levels and respiratory illness change slowly over time.
Shifting the variables by 12–14 days does not affect the relationship much because the overall seasonal pattern remains the same.
Main implication: the observed lag may be more seasonal than causal, so further analysis is needed.

---

## EDA 7: Overlay Time Series


Temperature and respiratory illness move in almost perfect opposite directions.
NO2 and respiratory illness follow a very similar seasonal pattern and rise and fall together.
Ozone and respiratory illness show the reverse pattern, moving opposite to each other.
Humidity has a weaker and less consistent visual relationship with respiratory illness.
PM2.5 shows little to no clear visual relationship, and the June 2023 wildfire spike highlights seasonal confounding.


---

## EDA 8: 90-Day Rolling Correlation

### Results

| Feature | Mean rolling r | Stability |
|---|---|---|
| Temperature (F) | -0.638 | Mostly consistent |
| NO2 (ppb) | +0.186 | Highly unstable |
| Ozone (ppm) | -0.335 | Moderately unstable |
| PM2.5 (µg/m³) | -0.091 | Unstable, sign-flipping |
| Relative Humidity (%) | +0.290 | Moderately stable |

### Critical finding: correlations are not stable year-round

Temperature is the most stable predictor, staying mostly negatively related to respiratory illness over time.
NO2 and ozone are unstable because their correlations flip sign across seasons.
This shows their overall correlations are mostly driven by seasonal co-movement, not a consistent daily relationship.
PM2.5 is the most unreliable feature, with weak correlation and frequent sign changes.
Modeling implication: a simple linear model may give misleading results for NO2, ozone, and PM2.5.
Better options would be interaction terms or tree-based models that can capture seasonal, non-linear effects.

---

## EDA 9: Day-of-Week Effect

### Results

| Day | Approximate mean % ED visits |
|---|---|
| Sunday | ~14.0% (highest) |
| Monday | ~13.2% |
| Tuesday | ~12.9% |
| Wednesday | ~12.8% |
| Thursday | ~12.5% |
| Friday | ~12.3% |
| Saturday | ~13.0% |

**One-way ANOVA result:** F-statistic significant (p < 0.05)

### Interpretation

Sunday has the highest average respiratory ED visits.
This likely reflects behavior patterns, with more people going to the ED on weekends when symptoms worsen or clinics are closed.
Friday has the lowest average respiratory ED visits.
The ANOVA shows this difference is statistically significant.
Modeling implication: day_of_week and is_weekend should be included as features.

---

## Feature Engineering Output

Based on all EDA findings, the following feature set was created:

| Feature | Source | Lag | Justification |
|---|---|---|---|
| temperature | temperature | 0 | Strongest predictor, immediate effect |
| humidity | humidity | 0 | r = +0.530, immediate |
| no2_lag12 | no2 | 12 days | r improves from 0.640 to 0.743 |
| ozone_lag13 | ozone | 13 days | r improves from -0.656 to -0.732 |
| pm25_lag14 | pm25 | 14 days | Included despite weak signal |
| month | date | — | 81.4% variance is seasonal |
| day_of_week | date | — | ANOVA-confirmed weekly effect |
| is_weekend | date | — | Binary weekend indicator |
| season_num | date | — | 0=Winter, 1=Spring, 2=Summer, 3=Fall |

**Features dataset:** `data/processed/features_daily.csv`
**Rows:** 1,119 (14 rows dropped from lag-14 NaN at start)
**Date range:** October 9, 2022 to October 31, 2025
**Columns:** 14

---

## Key Insights:

Correlations: Temperature is the strongest predictor with r = -0.812, making it the main variable linked to respiratory ED visits. Overall, the correlations are statistically significant, but many reflect seasonal patterns more than direct daily effects.
Seasonality: 81.4% of the variation in respiratory illness is explained by annual seasonality alone. This means capturing the yearly cycle is more important than capturing day-to-day environmental changes.
Lags: NO2 and ozone show slightly stronger relationships at 12–13 day lags, which may match illness incubation and delayed care-seeking. Temperature and humidity work best with no lag.
Limitations: The relationships for NO2 and ozone are not stable across seasons and even flip sign at times, showing that their overall correlations are heavily influenced by seasonality. So, simple models may misinterpret these effects unless they include seasonal interactions or non-linear structure.


---

