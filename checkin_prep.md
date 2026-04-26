# April Check-In Preparation
## Respiratory Disease Prediction from Environmental Factors
**Team:** Gowrav Lakshmipathy | Priya Dilip Bajaria | Nandini Nandan Narvekar

This document prepares answers to every likely professor question, organized by rubric category.

---

# SECTION 1 — DATA VISUALIZATIONS (15 points)

## The Three EDA Figures

---

### Figure 1 — Time Series: Respiratory vs Temperature and NO₂

**File:** `outputs/figures/eda_01_time_series_key_relationships.png`

---

**Q: Why a line chart and not a bar chart or scatter plot?**

The data is a 1,133-day consecutive daily time series. A line chart is the correct choice because:
- It preserves temporal ordering — the reader can see which values come before and after each other
- It makes recurring seasonal cycles (annual peaks and troughs) immediately visible
- A bar chart would produce 1,133 individual bars that are completely unreadable at this scale
- A scatter plot would show individual points without connecting them, breaking the visual continuity that makes the seasonal pattern legible

---

**Q: Why dual y-axes? Isn't that misleading?**

Dual y-axes are appropriate here because the two variables being plotted have incompatible units and ranges: respiratory visits are in % (range 7–27%) and temperature is in °F (range 22–81°F). If both were plotted on the same y-axis, one series would be squashed into a flat line because the scales differ by a factor of ~3. The dual axis does not distort the *shape* of either series — it only allows both shapes to be visible. The axis labels clearly identify which scale belongs to which series, and both axes start from non-zero values with equal justification.

The alternative — normalising both to z-scores — would work but obscures the actual units, making the chart harder to interpret in a presentation context.

---

**Q: Why did you choose temperature and NO₂ specifically? Why not ozone or PM2.5?**

- **Temperature** (r = −0.812) is the single strongest predictor in the entire dataset. Its inverse seasonal cycle against respiratory illness — cold temperatures in winter coincide with the highest illness, warm summers coincide with the lowest — is the dominant signal. Any visualization of this project must show temperature.
- **NO₂** (r = +0.640 at lag-0, improving to r = +0.743 at 12-day lag) was chosen as the second panel because it illustrates a different kind of relationship: a delayed effect. While temperature and respiratory illness move together immediately, NO₂ and illness appear to be offset in time. Showing this in the time series motivates why we compute lag correlations in Figure 2.
- **Ozone** would tell a similar story to NO₂ (seasonal co-movement, lag benefit) without adding new information.
- **PM2.5** would show almost no relationship (r = −0.142), making it a weak panel choice.

---

**Q: What specific claim does this figure support?**

The figure supports the claim that **environmental conditions predict respiratory illness, but the mechanism and timing differ by variable**. Temperature shows an immediate inverse relationship. NO₂ shows a co-directional relationship that improves with a 12-day lag, suggesting a delayed biological effect (exposure → symptom onset → care-seeking). This distinction directly motivates the lag analysis in Figure 2 and the lagged feature engineering in the model.

---

### Figure 2 — Lag Correlation Profiles

**File:** `outputs/figures/eda_02_lag_correlation_profiles.png`

---

**Q: Why a line chart for lag correlation? Why not a bar chart?**

Lag (0 to 14 days) is a continuous numeric variable. The line chart shows the *trajectory* — whether correlation is rising, flat, or falling as the lag increases. This trajectory is the key finding: temperature is flat (immediate effect), NO₂ and ozone are rising (delayed effect), PM2.5 is flat near zero (no effect at any lag). A bar chart would show individual values at each lag without communicating the trend. A heatmap would require transposing the question and is harder to read when five features are compared simultaneously.

---

**Q: Why 0 to 14 days? Why not 30 or 60 days?**

The 0–14 day window covers the biologically plausible range for respiratory illness causation:
- Exposure to a pollutant or cold temperature triggers an immune or inflammatory response
- Symptom onset typically occurs within 1–5 days for viral respiratory illness
- Patients seek emergency care within a further 1–7 days after symptom onset
- Beyond 14 days, the environmental signal becomes confounded with the next seasonal change — you are no longer asking "did yesterday's pollution cause today's hospital visit" but "did last month's weather cause this month's hospital visits," which is indistinguishable from seasonal co-movement

---

**Q: What is the grey band on Figure 2?**

The grey band marks the **95% significance threshold** for Pearson r at our sample size. The formula is ±1.96 / √(n − max_lag) = ±1.96 / √1105 ≈ ±0.059. Any correlation line inside the grey band has p > 0.05 and is statistically indistinguishable from zero. PM2.5 is almost entirely inside or near the band across all lags — confirming it is not a meaningful predictor. All other features are well outside the band.

---

**Q: What does the filled circle on each line represent?**

The filled circle marks the optimal lag — the lag value where the absolute Pearson r is highest for that feature. For temperature, the filled circle is at lag 0 (immediate). For NO₂ it is at lag 12, for ozone at lag 13. These optimal lag values are directly used in the feature engineering: `no2_lag12`, `ozone_lag13`, `pm25_lag14` are all created by shifting the column by that many days before modeling.

---

**Q: What claim does this figure support?**

The figure supports the claim that **environmental variables should not all be evaluated at the same time step**. Temperature's relationship with respiratory illness is immediate and does not improve with lag. NO₂ and ozone improve by r ≈ +0.10 when shifted 12–13 days forward. Using same-day NO₂ in a model underestimates its predictive power by about 15%. This directly justifies the decision to engineer lagged features rather than using raw same-day readings.

---

### Figure 3 — Feature Correlation Ranking

**File:** `outputs/figures/eda_03_feature_correlation_ranking.png`

---

**Q: Why a horizontal bar chart? Why not a table?**

A bar chart communicates magnitude visually — the reader can immediately see that temperature's bar is roughly twice as long as NO₂'s without reading numbers. A table requires reading each value individually and comparing mentally. Bars are also directional (the sign of the correlation is shown by colour: red = negative, blue = positive), giving two pieces of information at once. Horizontal bars were chosen over vertical because the feature labels are long and would require rotation or truncation on a vertical axis.

---

**Q: Why show both lag-0 and best-lag bars together?**

Showing both bars side by side communicates the *benefit of lagging* without requiring the reader to look at Figure 2. The improvement is substantial for NO₂ (+0.10) and ozone (+0.08) and absent for temperature and humidity. This grouped comparison directly justifies why only some features were lagged in the final feature set — it is visible at a glance that lagging helps some features and does nothing for others.

---

**Q: What claim does Figure 3 support?**

The figure supports two claims simultaneously:
1. **Feature ranking:** Temperature is the dominant predictor, followed by NO₂ and ozone, then humidity. PM2.5 is the weakest by a wide margin. This tells the reader which environmental factors matter most for respiratory illness at the national level.
2. **Lag justification:** The grouped bars make it visually clear that NO₂ and ozone benefit meaningfully from a lag shift, which directly validates the feature engineering decisions in the model.

---

# SECTION 2 — DATA PROCESSING (15 points)

---

**Q: Why did you switch from New York City to national data?**

Three reasons:
1. NYC EpiQuery provides monthly aggregates only, not daily counts. A monthly target variable cannot be matched to daily environmental readings.
2. CDC NSSP provides complete daily national coverage from September 2022 onwards with no gaps. No equivalent daily city-level dataset exists as a free public download.
3. EPA AQS data has 2,000+ monitoring stations nationally. A national daily average is statistically robust. Filtering to NYC alone gives fewer than 10 stations with inconsistent coverage — the standard error of the mean would be much larger.

The scope change makes the project stronger: more data, more stations, more generalisable findings.

---

**Q: Why did you apply the percentile cap after the study period filter, not before?**

If the cap is computed on all raw years (2022 full year onward) and then the study period filter is applied, the cap reflects a distribution that includes data outside the study window. For PM2.5, this produced a cap of 35.80 µg/m³ derived from the full dataset — but the study-period-only 99.5th percentile is 38.00 µg/m³. Computing the cap on the full dataset therefore clipped real high-pollution readings between 35.80 and 38.00 µg/m³ that existed during the study period, including readings from the 2023 Canadian wildfire events. Moving the filter before the cap computation ensures the cap reflects only the distribution we actually analyze.

---

**Q: Why did you include `n_stations` columns in the master dataset?**

Station count is quality metadata. On days where fewer monitoring stations report data, the national daily average is less representative — it may be dominated by a small geographic subset. Including `n_stations` for each variable allows downstream users (or future model iterations) to weight observations by data density or exclude low-coverage days. Without these columns, a day with 50 stations and a day with 2,000 stations would look identical in the master dataset.

---

**Q: Why did you add cyclic month encoding?**

The raw `month` integer (1–12) has a discontinuity at the year boundary: December = 12 and January = 1 are numerically 11 apart, but they are seasonally adjacent — both are winter months. A linear model treats the numeric distance as meaningful, so it cannot learn that the transition from December to January is smooth. By encoding month as `sin(2π·month/12)` and `cos(2π·month/12)`, we map the 12-month cycle onto a unit circle where December and January are close together. This is the standard approach for any cyclical temporal feature in a linear model.

Tree models (Random Forest, XGBoost) do not have this problem because they split on threshold values — month=11 < 11.5 is a valid split regardless of what month=12 means in relation to month=1. We still provided the cyclic columns in the features dataset for completeness, but the tree models were trained with raw `month`.

---

**Q: Why did you use an inner join for the master dataset? Could you have used an outer join?**

An inner join includes only dates present in all six datasets. An outer join would include dates where some variables are missing, which would require imputation. We chose not to impute for two reasons:
1. The target variable (`pct_respiratory`) is a health outcome. Interpolating a missing health outcome value introduces false signal — if data is missing on a particular day, that is potentially meaningful (a reporting failure) and should not be fabricated.
2. All six datasets have complete coverage for the study period (zero gaps after filtering), so the inner join does not drop any rows. The two datasets have different start and end dates, but within their overlap (Sep 25, 2022 to Oct 31, 2025) there are no gaps in any series.

---

**Q: Why is `pct_respiratory` used instead of a raw count of ED visits?**

Raw counts would be sensitive to the total number of ED visits on a given day, which varies with hospital capacity, reporting completeness, and seasonal overall ED utilization patterns. Using the percentage normalises for these factors — it represents the *fraction* of all ED visits that are respiratory-related, which is stable across changes in total visit volume. This is the standard metric in CDC syndromic surveillance literature for exactly this reason.

---

**Q: Why did you not interpolate missing days in the respiratory data?**

Missing days in health outcome data may reflect actual reporting failures — hospitals or surveillance systems that did not submit data on a specific day. Interpolating the target variable would introduce fabricated values into the thing we are trying to predict, which could mask systematic gaps in the surveillance system. For the predictor variables (environmental), interpolation is more defensible because a missing day of sensor data is more likely to be a technical gap than a meaningful event. No interpolation was needed in practice because neither dataset had missing days within the study period.

---

# SECTION 3 — MODELING METHODS (15 points)

---

**Q: Why three models? What does each one add?**

Each model answers a different question:
- **Ridge Regression** establishes the linear baseline with proper regularisation. It answers: "how much can a linear model do if given the right features?" It also produces interpretable coefficients — the sign and magnitude of each coefficient directly tells you the direction and strength of each feature's effect.
- **Random Forest** tests whether non-linear seasonal interactions improve predictions. The key EDA finding was that NO₂ and ozone correlations *flip sign* seasonally — they are positively correlated with illness in winter and negatively in summer. A linear model cannot express this. A tree model can, by learning a split like "if month is June–September, use a negative NO₂ coefficient; otherwise use a positive one."
- **XGBoost** tests whether sequential gradient boosting outperforms independent bagging (Random Forest). On tabular datasets of this size (1,119 rows), XGBoost typically achieves lower bias by sequentially correcting residuals, whereas Random Forest reduces variance through averaging independent trees.

---

**Q: Why TimeSeriesSplit instead of standard k-fold cross-validation?**

Standard k-fold randomly assigns data points to folds. For a time series, this means the model may be trained on data from 2025 and tested on 2023 — it has seen the "future" during training, which is data leakage. TimeSeriesSplit preserves temporal order: each test fold is always in the future relative to its training data, exactly as it would be in real deployment. This produces honest estimates of generalisation performance.

The March baseline used a single 80/20 split and achieved test R² = −0.70 because the test set happened to be summer-only. TimeSeriesSplit spreads test coverage across multiple seasons (some folds cover winter, some cover summer), making the evaluation more representative and the reported R² more reliable.

---

**Q: Why is the mean CV R² negative for all three models?**

The negative mean R² is not model failure — it is a **seasonal distribution shift** artefact that is specific to time series with strong seasonality evaluated on short test windows.

R² is negative when the model's predictions are worse than simply predicting the constant mean of the test set. This happens in our early folds because:

- **Fold 1** trains on only ~189 rows (≈6 months: Oct 2022 – Apr 2023). The training data covers only fall and winter. The test set covers spring and summer 2023 — a seasonal phase the model has never seen. The model predicts winter-level illness during summer, which is worse than just predicting the summer mean. Ridge R² for fold 1 = −5.19.

- **Folds 2 and 4** have winter test sets and consistently produce near-zero or positive R² across all three models (+0.47/+0.53 for Ridge, +0.23/+0.03 for RF, +0.06/−0.08 for XGBoost). This shows the models *can* predict correctly when the test season is represented in training data.

The pattern is systematic: **winter test folds → positive R², summer test folds → negative R²**. This is not random noise. It demonstrates that the core challenge is not model architecture but the fundamental asymmetry in the data: 3 years of training data is only marginally sufficient for the first fold (which sees only 6 months before its first summer test).

In production with continuous retraining on 3+ years of data, all seasonal phases would be well-represented and this problem would not occur.

---

**Q: Why did you choose these specific hyperparameters for Random Forest?**

- `max_depth=8`: Limits each tree to 8 levels. Shallow trees prevent overfitting — without a depth limit, individual trees would memorise training data, producing high train R² (which we see: 0.91) but not generalising.
- `min_samples_leaf=10`: Requires at least 10 samples at each leaf. With 1,119 training rows, this means no leaf can represent less than ~1% of the data, preventing very fine-grained splits that would overfit.
- `max_features=0.6`: Each split considers only 60% of features. This decorrelates individual trees, so the ensemble average is more stable. If all trees see all features, the dominant ones (temperature) would appear in every tree, making the trees correlated and reducing the benefit of averaging.
- `n_estimators=300`: Enough trees for stable feature importance estimates. Diminishing returns set in around 200 trees; 300 provides a comfortable margin.

---

**Q: Why did you choose these hyperparameters for XGBoost?**

- `learning_rate=0.05`: Small learning rate requires more trees to converge but produces better generalisation than a large learning rate. The standard guidance is learning_rate × n_estimators ≈ 15–20 for adequate convergence; 0.05 × 300 = 15.
- `max_depth=4`: Shallower than the Random Forest `max_depth=8`. XGBoost trees are boosted (each corrects the previous), so individual trees do not need to be as complex to capture the same patterns. Shallow XGBoost trees reduce the risk of overfitting on the seasonal residuals.
- `subsample=0.8` + `colsample_bytree=0.8`: Row and feature subsampling add stochastic regularisation, similar to the role of `max_features` in Random Forest.

---

**Q: Why is temperature the most important feature in both tree models?**

Temperature has the strongest raw correlation with the target (r = −0.812), no beneficial lag, and a clear physical mechanism: cold air suppresses immune function, promotes indoor crowding which transmits respiratory viruses, and dries out mucous membranes. At the population level, the national daily temperature average is a near-perfect proxy for winter season — the coldest days are always the highest-illness days. This is reflected in both Random Forest importance (0.440 = 44% of total) and XGBoost gain (0.272 = 27%).

---

**Q: Why does ozone (lag 13) rank second in tree model importance, above NO₂?**

In the raw correlations, temperature (r = −0.812) > ozone (r = −0.732 at lag 13) > NO₂ (r = +0.743 at lag 12) ≈ ozone in absolute terms. Ozone's advantage in tree importance may be due to its interaction with temperature — ozone and temperature are positively correlated (r = +0.549, both summer-peaking), so in a tree model, ozone-lag-13 can capture some of the residual variance after temperature has already been split on. NO₂ is also correlated with temperature (r = −0.624), so it provides less independent information once temperature is already in the model.

---

**Q: Why is PM2.5 so weak?**

PM2.5 has the lowest correlation with respiratory illness (r = −0.142) because its dominant source of variation in the data is summer wildfire smoke (especially the 2023 Canadian wildfires). Summer is when respiratory illness is at its annual minimum. High PM2.5 from wildfires therefore co-occurs with low respiratory illness, creating a confounding negative correlation that is the opposite of the hypothesised positive effect. The true effect of PM2.5 on respiratory illness (positive, through airway irritation) is masked by this seasonal confounding. A longer time series with more wildfire events spread across seasons, or a finer geographic analysis targeting wildfire-affected regions, would likely recover the positive effect.

---

**Q: Why is the RMSE similar across all three models (≈2.47–2.51 pp) even though the R² differs?**

RMSE and R² measure different things. R² measures the *proportion* of variance explained relative to the test set mean. When the test set mean is very different from the training set mean (seasonal distribution shift), R² penalises heavily — predicting 15% (winter-trained) when the test mean is 10% (summer) gives a large negative R² even if the absolute errors are not that large. RMSE only measures absolute prediction error in the original units, so it is not distorted by the mean shift. All three models make errors of similar magnitude (≈2.5 pp) regardless of which seasonal phase the test set covers, but R² varies widely depending on how well the test set mean is matched.

---

# SECTION 4 — RESULTS AND INTERPRETATION (5 points)

---

**Q: What do your results mean in practice?**

The models predict the daily percentage of US emergency department visits attributed to respiratory illness with a typical error of **±2.47 percentage points** (XGBoost RMSE). The target ranges from 7% to 27%, so this represents roughly a 10–12% relative error on a typical day.

In public health terms: if the actual ARI percentage on a given day is 15%, the model would predict somewhere between 12.5% and 17.5% on average. For hospital staffing decisions, knowing whether illness is at 15% vs 25% (a 10 pp gap) is more important than predicting the exact number — at that level of precision, a ±2.5 pp model is operationally useful.

---

**Q: Why do your models underperform compared to state-of-the-art?**

Several factors limit performance that are known and explainable:

1. **Small dataset:** 1,119 daily rows covering 3 years. Seasonal patterns repeat only 3 times. State-of-the-art syndromic surveillance models use 10–20 years of historical data, giving the model many more examples of each seasonal phase.

2. **National aggregation:** We are predicting a single national average per day. Spatial heterogeneity (wildfire smoke in the West while the Northeast has clean air) is averaged out, and the model cannot distinguish local high-pollution events from national trends.

3. **No lag-optimised tree features:** The tree models use raw `month` and same-day features. For a more competitive model, the lagged versions of NO₂ and ozone should be in the tree feature set alongside the raw versions.

4. **Seasonal distribution shift in early folds:** The first fold in TimeSeriesSplit has only 6 months of training data. Any model trained on 6 months of one season cannot generalise to the opposite season. This is a data volume constraint, not an architectural one.

---

**Q: What is the strongest result from your project?**

The strongest result is the **feature importance agreement between EDA and modeling**. In EDA (Figure 3), temperature was the dominant predictor (r = −0.812), ozone-lag-13 was second, NO₂-lag-12 was third. In the XGBoost model (Figure 2), temperature is the top feature (27% gain), ozone-lag-13 is second (27%), and NO₂-lag-12 is third (8%). The rankings are consistent across three completely different analytical approaches — Pearson correlation, Random Forest impurity decrease, and XGBoost gain. This cross-method consistency is evidence that the signal is real and not an artefact of any single method.

---

**Q: What would you do next to improve the model?**

1. **Skill score evaluation against a seasonal mean baseline** — compute RMSE of a model that just predicts the monthly average of the training set, then report `1 − RMSE_model / RMSE_baseline`. This contextualises whether the environmental features add any value beyond knowing the season.
2. **More data** — extending the study period backward to 2019–2020 (pre-COVID NSSP baseline) would give 5–6 full annual cycles, which would reduce the seasonal distribution shift problem dramatically.
3. **Spatial disaggregation** — predicting by region (Northeast, South, Midwest, West) instead of national average would allow the model to capture PM2.5 wildfire events that are regionally concentrated, potentially recovering PM2.5's positive effect on respiratory illness.
4. **Hyperparameter tuning** — a proper grid search or Bayesian optimisation over XGBoost hyperparameters using the TimeSeriesSplit CV instead of the current manually set values.

---

## Quick Reference — All Key Numbers

| Quantity | Value |
|---|---|
| Study period | Sep 25, 2022 – Oct 31, 2025 (1,133 days) |
| Feature rows (after lag trim) | 1,119 rows |
| Feature columns | 16 |
| Target range | 7.09% – 26.58% |
| Temperature correlation | r = −0.812 (strongest, lag 0) |
| NO₂ correlation | r = +0.640 → +0.743 at lag 12 |
| Ozone correlation | r = −0.656 → −0.732 at lag 13 |
| PM2.5 correlation | r = −0.142 (weakest) |
| Seasonality variance share | 81.4% |
| Best model | XGBoost |
| XGBoost CV R² | −0.512 ± 0.768 |
| XGBoost RMSE | 2.468 pp |
| XGBoost MAE | 1.997 pp |
| Top feature (both tree models) | temperature (RF: 44%, XGB: 27%) |
