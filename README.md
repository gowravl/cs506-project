# Respiratory Disease Prediction from Environmental Factors

**Team Members:**
- Gowrav Lakshmipathy - U53940054
- Priya Dilip Bajaria - U08184333
- Nandini Nandan Narvekar - U25345416

## Project Description

We analyze the relationship between environmental conditions and respiratory disease outcomes using publicly available national health and air quality data. The project predicts the daily percentage of US emergency department visits attributed to Acute Respiratory Illness (ARI) based on air quality measurements and weather conditions.

Understanding how environmental factors influence respiratory health is critical for public health preparedness. By quantifying these relationships, hospitals can better anticipate patient surges, individuals with chronic respiratory conditions can take preventive measures on high-risk days, and public health officials can develop targeted interventions.

> **Note on scope:** The original proposal specified New York City. During data collection we found that no daily respiratory count data exists for NYC at the required granularity (NYC EpiQuery provides monthly aggregates only). The CDC NSSP dataset provides complete daily national coverage from September 2022 onwards, and EPA AQS data averages robustly to a national daily value across 2,000+ monitoring stations. See `project_reference.md` for the full rationale.

## Datasets

| Dataset | Source | Format | Coverage |
|---|---|---|---|
| PM2.5 | EPA AQS `daily_88101_YYYY.csv` | Station-day readings, µg/m³ | 2022–2025 |
| NO2 | EPA AQS `daily_42602_YYYY.csv` | Station-hour readings, ppb | 2022–2025 |
| Ozone | EPA AQS `daily_44201_YYYY.csv` | Station 8-hr avg, ppm | 2022–2025 |
| Temperature | EPA AQS `daily_TEMP_YYYY.csv` | Station-hour readings, °F | 2022–2025 |
| Relative Humidity | EPA AQS `daily_RH_DP_YYYY.csv` | Station-hour readings, % | 2022–2025 |
| Respiratory ARI | CDC NSSP `nssp_respiratory.csv` | Daily % of ED visits, US | Sep 2022–present |

**Study period:** September 25, 2022 to October 31, 2025 (1,133 days)
- Start: first date of NSSP data
- End: last date of EPA temperature data

## Repository Structure

```
project/
    data/
        raw/
            pm25/           daily_88101_YYYY.csv
            no2/            daily_42602_YYYY.csv
            ozone/          daily_44201_YYYY.csv
            temperature/    daily_TEMP_YYYY.csv
            humidity/       daily_RH_DP_YYYY.csv
            respiratory/    nssp_respiratory.csv
        processed/
            pm25_daily.csv
            no2_daily.csv
            ozone_daily.csv
            temperature_daily.csv
            humidity_daily.csv
            respiratory_daily.csv
            master_daily.csv        ← 1,133 rows × 12 columns
            features_daily.csv      ← engineered features for modeling
    outputs/figures/                ← profiling, EDA, and model plots
    reports/
        data_profiling_report.md
        data_cleaning_report.md
        eda_report.md
        modeling_report.md
    data_profiling.ipynb
    data_cleaning.ipynb
    eda.ipynb
    models.ipynb
    project_reference.md
    requirements.txt
```

## Notebooks

| Notebook | Purpose |
|---|---|
| `data_profiling.ipynb` | Inspect all 6 raw datasets, identify issues |
| `data_cleaning.ipynb` | Apply targeted cleaning, produce `master_daily.csv` |
| `eda.ipynb` | Correlation, lag, seasonal decomposition, feature engineering |
| `models.ipynb` | Predictive modeling and evaluation |

## Setup

```bash
git clone <repo-url>
cd cs506-project
make run        # creates venv, installs deps, runs eda + models
```

`make run` uses the processed CSVs already committed to the repo — no raw data download needed.
To see all available targets: `make help`

**Reproduce from raw data** (optional — files are 200–300 MB each):
```bash
make data       # shows download instructions for EPA AQS + CDC NSSP files
make all        # full pipeline: profiling → cleaning → eda → models
```

## Key Findings

- Temperature is the strongest predictor of respiratory illness (r = −0.812)
- Seasonality explains 81.4% of variance in respiratory ED visits
- NO2 and Ozone show stronger correlations when lagged 12–13 days
- PM2.5 wildfire spikes (e.g., 2023 Canadian wildfires) are preserved in the cleaned data

## Project Goals

- Predict daily ARI emergency department visit rates from environmental variables
- Identify and quantify which environmental factors most strongly influence respiratory health
- Evaluate model performance and assess prediction reliability across seasons
