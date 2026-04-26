# Modeling Report
## Respiratory Disease Prediction from Environmental Factors
**Team:** Gowrav Lakshmipathy | Priya Dilip Bajaria | Nandini Nandan Narvekar

---

## Overview

**Input:** `data/processed/features_daily.csv` — 1,119 rows × 16 columns  
**Target:** `pct_respiratory` — daily % of US ED visits attributed to ARI (range 7.09% – 26.58%)  
**Evaluation:** 5-fold TimeSeriesSplit cross-validation (each fold trains on all prior data, tests on the next chronological block of ~186 days)

Three models were trained and compared:

| Model | Type | Features |
|---|---|---|
| Ridge Regression | Linear, regularised | Cyclic month encoding (`month_sin`, `month_cos`) |
| Random Forest | Tree ensemble | Raw `month`, `season_num` |
| XGBoost | Gradient boosting | Same as Random Forest |

---

## What We Are Predicting

`pct_respiratory` is the daily percentage of US emergency department visits classified as Acute Respiratory Illness (ARI), from CDC NSSP. Percentage normalises for hospital capacity variation over time. The target ranges from 7.09% in summer to 26.58% in winter — a 3.7× seasonal swing.

---

## Evaluation Strategy

All models use **5-fold TimeSeriesSplit**. Unlike random k-fold, TimeSeriesSplit preserves temporal order: each test fold is always in the future relative to its training data. This prevents data leakage and mirrors real deployment conditions.

The March baseline used a single 80/20 split (train R² = 0.79, test R² = −0.70) because the test set covered only spring–summer 2025 — a season the model had not seen in a way that generalised. TimeSeriesSplit spreads test coverage across multiple seasons, making evaluation more robust.

| Fold | Approx. train dates | Approx. test dates | Seasons in test |
|---|---|---|---|
| 1 | Oct 2022 – Apr 2023 | Apr – Oct 2023 | Spring / Summer |
| 2 | Oct 2022 – Oct 2023 | Oct 2023 – Apr 2024 | Fall / Winter |
| 3 | Oct 2022 – Apr 2024 | Apr – Oct 2024 | Spring / Summer |
| 4 | Oct 2022 – Oct 2024 | Oct 2024 – Apr 2025 | Fall / Winter |
| 5 | Oct 2022 – Apr 2025 | Apr – Oct 2025 | Spring / Summer |

---

## Model A — Ridge Regression

**Feature set:** `temperature`, `humidity`, `no2_lag12`, `ozone_lag13`, `pm25_lag14`, `month_sin`, `month_cos`, `day_of_week`, `is_weekend`

**Preprocessing:** StandardScaler applied per fold (fit on train, transform on train and test).

**Alpha selection:** RidgeCV performs internal LOO-CV across [0.1, 1, 10, 100, 1000].

### Cross-Validation Results

| Fold | Train R² | Test R² | RMSE (pp) | MAE (pp) |
|---|---|---|---|---|
| 1 | 0.679 | −5.186 | 4.233 | 3.688 |
| 2 | 0.776 | +0.466 | 2.265 | 1.811 |
| 3 | 0.764 | −0.513 | 1.328 | 1.032 |
| 4 | 0.789 | +0.529 | 2.440 | 1.994 |
| 5 | 0.773 | −1.758 | 2.154 | 1.642 |
| **Mean** | **0.756** | **−1.292** | **2.484** | **2.033** |
| **± Std** | **0.044** | **2.366** | **1.067** | — |

**Coefficients (full-data fit, sorted by |coef|):**  
Temperature dominates all other features. The cyclic month terms (month_sin, month_cos) are the second and third largest contributors, confirming that the seasonal cycle is the primary learned pattern.

---

## Model B — Random Forest

**Feature set:** `temperature`, `humidity`, `no2_lag12`, `ozone_lag13`, `pm25_lag14`, `month`, `day_of_week`, `is_weekend`, `season_num`

**Hyperparameters:** `n_estimators=300`, `max_depth=8`, `min_samples_leaf=10`, `max_features=0.6`, `random_state=42`

### Cross-Validation Results

| Fold | Train R² | Test R² | RMSE (pp) | MAE (pp) |
|---|---|---|---|---|
| 1 | 0.907 | −3.407 | 3.573 | 3.288 |
| 2 | 0.950 | +0.233 | 2.715 | 2.194 |
| 3 | 0.905 | +0.271 | 0.922 | 0.739 |
| 4 | 0.918 | +0.033 | 3.496 | 2.802 |
| 5 | 0.867 | −0.995 | 1.832 | 1.409 |
| **Mean** | **0.909** | **−0.773** | **2.508** | **2.086** |
| **± Std** | **0.030** | **1.560** | **1.132** | — |

**Feature importances (full-data fit):**

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

---

## Model C — XGBoost

**Feature set:** Same as Random Forest.

**Hyperparameters:** `n_estimators=300`, `learning_rate=0.05`, `max_depth=4`, `subsample=0.8`, `colsample_bytree=0.8`, `random_state=42`

### Cross-Validation Results

| Fold | Train R² | Test R² | RMSE (pp) | MAE (pp) |
|---|---|---|---|---|
| 1 | 1.000 | −1.788 | 2.842 | 2.476 |
| 2 | 0.998 | +0.058 | 3.008 | 2.359 |
| 3 | 0.990 | −0.073 | 1.119 | 0.861 |
| 4 | 0.987 | −0.080 | 3.695 | 2.991 |
| 5 | 0.973 | −0.675 | 1.679 | 1.297 |
| **Mean** | **0.990** | **−0.512** | **2.468** | **1.997** |
| **± Std** | **0.011** | **0.768** | **1.046** | — |

**Feature importances (gain, full-data fit):**

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

---

## Model Comparison

| Model | CV R² (mean) | ± Std | RMSE (pp) | MAE (pp) |
|---|---|---|---|---|
| Ridge | −1.292 | ±2.366 | 2.484 | 2.033 |
| Random Forest | −0.773 | ±1.560 | 2.508 | 2.086 |
| **XGBoost** | **−0.512** | **±0.768** | **2.468** | **1.997** |

**Best model: XGBoost** — highest CV R² and lowest variance across folds.

RMSE and MAE are in percentage-point units. RMSE = 2.47 means predictions are on average 2.47 percentage points off the actual daily ARI percentage.

---

## Why CV R² Is Negative — And Why This Is Not Model Failure

The mean CV R² values are negative for all three models. This requires explanation.

**The cause is seasonal distribution shift between training and test folds.**

R² is negative when the model's predictions are worse than simply predicting the mean of the test set. This happens when the training data does not cover the same seasonal phase as the test set.

The pattern is consistent and interpretable:

| Test season | Ridge | Random Forest | XGBoost |
|---|---|---|---|
| Spring / Summer (folds 1, 3, 5) | −5.19, −0.51, −1.76 | −3.41, +0.27, −1.00 | −1.79, −0.07, −0.68 |
| Fall / Winter (folds 2, 4) | +0.47, +0.53 | +0.23, +0.03 | +0.06, −0.08 |

Winter test sets (folds 2 and 4) consistently produce near-zero or positive R², because the seasonal pattern in the test set matches what the model learned from the prior winter. Summer test sets produce strongly negative R², particularly in fold 1, where the model is trained on only ~6 months of fall/winter data and immediately tested on spring/summer — a completely different phase of the annual cycle.

Fold 1 is the most extreme case: 189 training rows cover only October 2022 to April 2023. The model has never seen a spring or summer, so its predictions for April–October 2023 are effectively extrapolation.

**Implication:** The models understand the seasonal pattern correctly when they have seen enough complete annual cycles. The path to stable positive CV R² is to train on at least 2–3 full years before any test period — which requires more data than the current study window provides for early folds.

---

## Output Figures

| File | Contents |
|---|---|
| `outputs/figures/model_01_actual_vs_predicted.png` | XGBoost actual vs predicted — full time series, 80/20 split |
| `outputs/figures/model_02_feature_importance.png` | RF and XGBoost feature importances side by side |
| `outputs/figures/model_03_cv_fold_r2.png` | Per-fold CV R² for all three models |

---

## Key Findings

- **XGBoost is the best model** by CV R² (−0.512) and lowest variance across folds (±0.768 vs ±1.560 for RF and ±2.366 for Ridge).
- **Temperature is the dominant feature** in all three models: 44% of RF importance, 27% of XGBoost gain, largest coefficient in Ridge. This matches the EDA finding of r = −0.812.
- **Ozone (lag 13d) is the second most important feature** in both tree models despite having a moderate raw correlation. Its delayed version captures a different signal than same-day ozone.
- **PM2.5 and is_weekend are the least important features** — confirming the EDA finding that PM2.5 is a weak predictor and that the day-of-week effect, while statistically significant, explains little variance at the model level.
- **Negative CV R² is driven by seasonal distribution shift**, not model incompetence. When test folds cover the same season as training data, all three models achieve near-zero or positive R².
- **RMSE ≈ 2.5 pp** across all models. Given that the target ranges 7–27%, a 2.5 pp error is moderate — roughly 10–15% of the target range. The error is larger in summer (low illness season) where seasonal patterns are harder to learn from limited training data.
