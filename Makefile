PYTHON  := venv/bin/python
PIP     := venv/bin/pip
NB_RUN  := venv/bin/jupyter nbconvert --to notebook --execute --inplace

PROCESSED := data/processed/pm25_daily.csv \
             data/processed/no2_daily.csv \
             data/processed/ozone_daily.csv \
             data/processed/temperature_daily.csv \
             data/processed/humidity_daily.csv \
             data/processed/respiratory_daily.csv \
             data/processed/master_daily.csv

FEATURES := data/processed/features_daily.csv

FIGURES  := outputs/figures/eda_01_time_series_key_relationships.png \
            outputs/figures/eda_02_lag_correlation_profiles.png \
            outputs/figures/eda_03_feature_correlation_ranking.png \
            outputs/figures/model_01_actual_vs_predicted.png \
            outputs/figures/model_02_feature_importance.png \
            outputs/figures/model_03_cv_fold_r2.png

.PHONY: all run install profiling cleaning eda models data clean clean-outputs help

## Full pipeline from scratch (requires raw data — see: make data)
all: install profiling cleaning eda models

## Quick start after cloning (processed CSVs are committed to git)
run: install
	@echo "Running eda.ipynb ..."
	$(NB_RUN) --ExecutePreprocessor.timeout=300 eda.ipynb
	@echo "Running models.ipynb ..."
	$(NB_RUN) --ExecutePreprocessor.timeout=600 models.ipynb
	@echo "Done. Figures saved to outputs/figures/"

# Dependencies

install: venv/bin/activate

venv/bin/activate: requirements.txt
	python3 -m venv venv
	$(PIP) install --upgrade pip -q
	$(PIP) install -r requirements.txt -q
	@touch venv/bin/activate
	@echo "venv ready."

# Pipeline stages

profiling: venv/bin/activate
	@echo "Running data_profiling.ipynb ..."
	$(NB_RUN) --ExecutePreprocessor.timeout=300 data_profiling.ipynb
	@echo "Profiling complete."

cleaning: $(PROCESSED)

$(PROCESSED): data_cleaning.ipynb venv/bin/activate
	@echo "Running data_cleaning.ipynb ..."
	$(NB_RUN) --ExecutePreprocessor.timeout=600 data_cleaning.ipynb
	@echo "Cleaning complete → data/processed/master_daily.csv"

eda: $(FEATURES)

$(FEATURES): eda.ipynb $(PROCESSED) venv/bin/activate
	@echo "Running eda.ipynb ..."
	$(NB_RUN) --ExecutePreprocessor.timeout=300 eda.ipynb
	@echo "EDA complete → data/processed/features_daily.csv"

models: $(FIGURES)

$(FIGURES): models.ipynb $(FEATURES) venv/bin/activate
	@echo "Running models.ipynb ..."
	$(NB_RUN) --ExecutePreprocessor.timeout=600 models.ipynb
	@echo "Modeling complete → outputs/figures/"

# Utilities

data:
	@echo ""
	@echo "Raw data is NOT in git (200–300 MB per file)."
	@echo "Committed processed CSVs in data/processed/ are enough to run: make run"
	@echo ""
	@echo "To fully reproduce from raw data, download these files and place them in data/raw/:"
	@echo ""
	@echo "  EPA AQS Pre-Generated Data  →  https://aqs.epa.gov/aqsweb/airdata/download_files.html"
	@echo "    data/raw/pm25/         daily_88101_{2022,2023,2024,2025}.csv"
	@echo "    data/raw/no2/          daily_42602_{2022,2023,2024,2025}.csv"
	@echo "    data/raw/ozone/        daily_44201_{2022,2023,2024,2025}.csv"
	@echo "    data/raw/temperature/  daily_TEMP_{2022,2023,2024,2025}.csv"
	@echo "    data/raw/humidity/     daily_RH_DP_{2022,2023,2024,2025}.csv"
	@echo ""
	@echo "  CDC NSSP Respiratory  →  https://www.cdc.gov/nssp/php/surveillance-data-platform.html"
	@echo "    data/raw/respiratory/  nssp_respiratory.csv"
	@echo ""
	@echo "Then run: make all"
	@echo ""

clean-outputs:
	rm -f $(FEATURES)
	rm -f outputs/figures/eda_*.png outputs/figures/model_*.png \
	      outputs/figures/cleaned_*.png outputs/figures/pm25_*.png \
	      outputs/figures/profile_*.png
	@echo "Cleaned: figures and features_daily.csv removed (master_daily.csv preserved)."

clean: clean-outputs
	rm -rf venv
	@echo "Cleaned: venv removed. Run 'make install' to reinstall."

help:
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "  make run        Quick start after cloning: install + eda + models"
	@echo "  make all        Full pipeline from scratch (needs raw data — see: make data)"
	@echo ""
	@echo "  make install    Create venv, install requirements.txt"
	@echo "  make profiling  Run data_profiling.ipynb  (needs raw data)"
	@echo "  make cleaning   Run data_cleaning.ipynb   (needs raw data)"
	@echo "  make eda        Run eda.ipynb"
	@echo "  make models     Run models.ipynb"
	@echo ""
	@echo "  make data       Show raw data download instructions"
	@echo "  make clean-outputs  Delete figures and features CSV"
	@echo "  make clean      Full reset including venv"
	@echo ""
