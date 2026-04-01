# Exploratory Data Analysis Report
## Respiratory Disease Prediction from Environmental Factors
**Team:** Gowrav Lakshmipathy | Priya Dilip Bajaria | Nandini Nandan Narvekar

---

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

## EDA 1 — Pearson Correlation Matrix

### Results

| Feature | Correlation with Respiratory % ED Visits | Direction |
|---|---|---|
| Temperature (F) | -0.812 | Negative — stronger |
| Ozone (ppm) | -0.656 | Negative |
| NO2 (ppb) | +0.640 | Positive |
| Relative Humidity (%) | +0.530 | Positive |
| PM2.5 (µg/m³) | -0.142 | Negative — weakest |

### Interpretation

**Temperature is the dominant predictor at r = -0.812.** As daily temperature rises,
respiratory ED visits fall sharply. Cold weather drives multiple mechanisms simultaneously:
people congregate indoors increasing pathogen transmission, cold dry air irritates airways,
and low temperatures promote viral survival in the environment.

**NO2 (r = +0.640) and Ozone (r = -0.656) show strong but opposite relationships.**
This is not contradictory — it reflects their opposite seasonal behavior. NO2 is higher
in winter because UV radiation is weaker and cannot break it down as efficiently.
Ozone is a photochemical pollutant that peaks in summer heat and sunlight. Since
respiratory illness peaks in winter and troughs in summer, NO2 correlates positively
and Ozone correlates negatively with the target.

**Humidity (r = +0.530) is moderately positive.** Higher humidity in cold winter months
promotes the airborne survival of respiratory pathogens (influenza, RSV).

**PM2.5 (r = -0.142) is the weakest feature and counterintuitively negative.**
This is a confounding effect — PM2.5 peaks in summer from wildfire smoke and heat
(the 2023 Canadian wildfire event is visible in the data), exactly when respiratory
illness is at its seasonal minimum. The true acute effect of PM2.5 on respiratory
illness is masked by this seasonal confounding. The lag analysis below addresses this.

### Notable inter-feature correlations

- Temperature and Ozone: r = +0.549 (both summer-peaking)
- Temperature and NO2: r = -0.624 (NO2 higher in winter when temperature is low)
- Ozone and Humidity: r = -0.585 (humid winters, dry summers)

---

## EDA 2 — Feature Correlation Bar Chart

The bar chart confirmed the ranking visually. Temperature and NO2/Ozone are the
three features with correlations above 0.6 in absolute value. PM2.5 stands alone
at -0.142, substantially weaker than all others. This chart is the clearest single
visual for explaining feature selection at the check-in.

---

## EDA 3 — Scatter Plots by Season

### Key finding: correlations are seasonally driven

The season-colored scatter plots revealed that most of the observed correlations
are not independent environmental effects — they are artifacts of shared seasonality.

**Temperature:** The scatter shows near-perfect seasonal stratification. Winter dots
(blue) occupy the top-left (cold + high illness). Summer dots (orange) occupy
bottom-right (warm + low illness). There is almost no within-season variation visible.
This means temperature is acting primarily as a proxy for season rather than as an
independent daily environmental driver.

**Ozone:** Same seasonal stratification pattern. Summer (high ozone) = low illness.
Winter (low ozone) = high illness. The negative correlation is driven by seasons
moving together, not by day-to-day ozone variation causing illness.

**NO2:** Cleaner positive trend but still season-stratified. Higher NO2 in winter
months correlates with higher winter illness levels.

**PM2.5:** The most scattered plot. No clear trend line within any season.
Confirms PM2.5 is genuinely the weakest predictor regardless of how you look at it.

**Implication for modeling:** A model without a season or month feature will
capture environmental correlations but miss the underlying mechanism. Month must
be included as a feature. This is confirmed quantitatively by the decomposition below.

---

## EDA 4 — Seasonal Decomposition

### Results

| Component | Variance explained |
|---|---|
| Seasonality | **81.4%** |
| Trend | 0.2% |
| Residual | 17.5% |

### Interpretation

**81.4% of all variance in respiratory illness is explained by annual seasonality alone.**
This is the most important single number from the entire EDA phase. It means:

- A model that perfectly captures the seasonal cycle would achieve R² ≈ 0.81 with
  no environmental features at all
- Environmental features explain the remaining 17.5% residual variation — the
  day-to-day deviations from the seasonal pattern
- The trend component of 0.2% confirms there is no long-term upward or downward
  drift in the baseline level of respiratory illness over 2022-2025

The decomposition plot shows three complete identical seasonal cycles
(2022-23, 2023-24, 2024-25) with the December-January peak consistently
reaching +10 percentage points above the seasonal mean and the
July-August trough reaching -5 percentage points below.

**The residual panel** shows structured variation — the weekly oscillation
(day-of-week effect) is clearly visible as the high-frequency component,
confirming that day-of-week should be included as a model feature.

---

## EDA 5 — Monthly Box Plots

### Key observations per variable

**Respiratory % ED Visits:**
- Peak months: January (~18-20%), February (~17%), December (~17-18%)
- Trough months: July (~8%), August (~8%), September (~10%)
- Very tight IQR within most months — the seasonal pattern is highly consistent
  year over year with little inter-year variation

**PM2.5:**
- Elevated in June-August (wildfire season) — this is the summer peak that
  creates the seasonal confounding with respiratory illness
- January and February are moderate, not high
- Confirms why PM2.5 has a negative correlation with the target

**NO2:**
- Clear winter peak (Oct-Feb: ~9-10 ppb) and summer trough (May-Aug: ~5-6 ppb)
- Pattern closely mirrors respiratory illness — explains the r = +0.640

**Ozone:**
- Opposite to NO2 — peaks in April-August (~0.037-0.044 ppm)
- Lowest in December-January (~0.025 ppm)
- This inverse seasonal pattern explains the r = -0.656

**Temperature:**
- Tight IQR — national daily average temperature is very consistent year to year
- Range from ~38°F (January) to ~78°F (July)

**Humidity:**
- Higher in winter months (Jan-Feb: ~70%), lower in spring-summer (Apr-Aug: ~55%)
- Less seasonally consistent than other variables — wider box widths in autumn

---

## EDA 6 — Lag Correlation Analysis

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

**Temperature and Humidity: optimal lag = 0 days**

The relationship is immediate at the population level. Cold weather today corresponds
to elevated respiratory ED visits today — not because individuals develop illness
instantly, but because cold weather persistently drives indoor crowding, viral
transmission, and reduced immune function across the entire population simultaneously.
At the national scale, this population-level effect manifests as same-day correlation.

**NO2: optimal lag = 12 days (r improves from 0.640 to 0.743)**

A 12-day delayed effect is consistent with respiratory illness disease progression.
Exposure to elevated NO2 irritates airways and increases susceptibility to infection.
The subsequent illness takes approximately 3-5 days to incubate, a few more days
before symptoms become severe enough to warrant an ED visit, and reporting delays
add additional time. The improvement from r = 0.640 to 0.743 (+0.103) is meaningful
and justifies including the lagged version.

**Ozone: optimal lag = 13 days (r improves from -0.656 to -0.732)**

Nearly identical lag structure to NO2, which makes physiological sense — both
ozone and NO2 act through airway irritation mechanisms on similar timescales.
The improvement from -0.656 to -0.732 (+0.076) is also meaningful.

**PM2.5: optimal lag = 14 days (r barely changes from -0.142 to -0.153)**

The negligible improvement confirms that PM2.5's weak relationship with respiratory
illness is not a lag issue — it is a genuine confounding issue from the wildfire
seasonal overlap. Lagging does not resolve the fundamental problem.

### Critical insight from lag plots

The lag plots for NO2 and Ozone show correlations that are **consistently strong
across all lags 0-14** with only small variation between lags. This is a warning sign:
it suggests the lag effect may not be a true causal mechanism but rather another
manifestation of the shared seasonality. Both respiratory illness and NO2/Ozone
vary slowly at a seasonal timescale, so shifting them by 12 days does not change
the correlation much. The rolling correlation analysis below addresses this concern.

---

## EDA 7 — Overlay Time Series

The dual-axis overlays confirmed the visual patterns from the correlation analysis:

- **Temperature vs Respiratory:** Nearly perfect mirror image. When temperature
  peaks in summer, respiratory illness hits its minimum. The anti-correlation
  is visually striking.
- **NO2 vs Respiratory:** Very similar seasonal shape — both peak in winter,
  trough in summer. Visually the two lines track together closely.
- **Ozone vs Respiratory:** Inverse shape — ozone peaks exactly when illness troughs.
- **Humidity vs Respiratory:** Rougher relationship — humidity is more variable day
  to day and the seasonal pattern is less clean than temperature or NO2.
- **PM2.5 vs Respiratory:** No visual relationship — the two lines appear independent.
  The June 2023 wildfire spike in PM2.5 occurs during the summer trough of respiratory
  illness, visually confirming the seasonal confounding.

---

## EDA 8 — 90-Day Rolling Correlation

### Results

| Feature | Mean rolling r | Stability |
|---|---|---|
| Temperature (F) | -0.638 | Mostly consistent |
| NO2 (ppb) | +0.186 | Highly unstable |
| Ozone (ppm) | -0.335 | Moderately unstable |
| PM2.5 (µg/m³) | -0.091 | Unstable, sign-flipping |
| Relative Humidity (%) | +0.290 | Moderately stable |

### Critical finding: correlations are not stable year-round

**Temperature** is the most stable feature — its rolling r remains negative
throughout most of the study period, though it weakens and occasionally turns
positive in the transition seasons (spring and fall) when both temperature and
illness are changing direction simultaneously.

**NO2 and Ozone flip sign seasonally.** Their 90-day rolling correlations with
respiratory illness oscillate between positive and negative throughout the year.
This confirms the concern from the lag analysis — the overall Pearson r values
(0.640 and -0.656) are driven by seasonal co-movement, not by a stable within-season
relationship between daily pollution levels and daily illness rates.

**PM2.5 is the most unstable** — mean r of only -0.091 with frequent sign flips.
This is the clearest evidence that PM2.5 does not have a reliable relationship
with respiratory illness in this national daily dataset.

**Implication for modeling:** A linear model that treats these relationships as
constant will produce unstable or misleading coefficients for NO2, Ozone, and PM2.5.
Interaction terms (e.g. NO2 × month) or tree-based models that can capture
non-linear seasonal interactions would better represent these features.
This is planned for the April check-in.

---

## EDA 9 — Day-of-Week Effect

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

Sunday shows the highest mean respiratory ED visits, approximately 0.8 percentage
points above the overall mean of 13.24%. This reflects a real behavioral pattern:
people who became ill during the week and avoided the ED (perhaps managing symptoms
with over-the-counter medication) tend to present on weekends when they have more
time or when symptoms have worsened. Additionally, some outpatient clinics are
closed on weekends, redirecting non-emergency respiratory patients to the ED.

Friday shows the lowest mean, consistent with people avoiding weekend ED visits
by seeking care earlier in the week.

The ANOVA confirms this effect is statistically significant and justifies including
`day_of_week` and `is_weekend` as model features.

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

## Key Insights for March Check-In

### What to say about correlations

Temperature is the strongest predictor at r = -0.812. Cold weather reduces
respiratory ED visits — or more precisely, cold weather is the dominant seasonal
driver of respiratory illness and the two track very closely. All correlations
are statistically significant at p < 0.001.

### What to say about seasonality

81.4% of all variance in the target variable is explained by annual seasonality.
This means the most important thing the model needs to capture is not the
environmental day-to-day variation but the annual cycle. Any model without
a season or month feature will be severely handicapped regardless of how
well it captures air quality effects.

### What to say about lags

NO2 and Ozone show improved correlations at 12-13 day lags, consistent with
respiratory illness incubation and care-seeking timelines. Temperature and Humidity
show no lag — their effects are immediate at the national population scale.

### What to say about limitations

The rolling correlation analysis showed that NO2 and Ozone relationships are
not stable across seasons — their correlations flip sign in summer. This suggests
the overall correlations are dominated by seasonal co-movement rather than
independent environmental effects. This is a known limitation of the current
feature set that more complex models (planned for April) will address through
interaction terms or non-linear methods.

---

*Report generated after Phase 3 EDA. All values are from actual notebook output.*
*Next phase: baseline linear regression modeling.*
