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

.PHONY: all run install profiling cleaning eda models test data clean clean-outputs help

## Full pipeline from scratch (requires raw data — see: make data)
all: install profiling cleaning eda models

## Quick start after cloning (processed CSVs are committed to git)
run: install
	@echo "Running eda.ipynb ..."
	$(NB_RUN) --ExecutePreprocessor.timeout=300 notebooks/eda.ipynb
	@echo "Running models.ipynb ..."
	$(NB_RUN) --ExecutePreprocessor.timeout=600 notebooks/models.ipynb
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
	$(NB_RUN) --ExecutePreprocessor.timeout=300 notebooks/data_profiling.ipynb
	@echo "Profiling complete."

cleaning: $(PROCESSED)

$(PROCESSED): notebooks/data_cleaning.ipynb venv/bin/activate
	@echo "Running data_cleaning.ipynb ..."
	$(NB_RUN) --ExecutePreprocessor.timeout=600 notebooks/data_cleaning.ipynb
	@echo "Cleaning complete → data/processed/master_daily.csv"

eda: $(FEATURES)

$(FEATURES): notebooks/eda.ipynb $(PROCESSED) venv/bin/activate
	@echo "Running notebooks/eda.ipynb ..."
	$(NB_RUN) --ExecutePreprocessor.timeout=300 notebooks/eda.ipynb
	@echo "EDA complete → data/processed/features_daily.csv"

models: $(FIGURES)

$(FIGURES): notebooks/models.ipynb $(FEATURES) venv/bin/activate
	@echo "Running notebooks/models.ipynb ..."
	$(NB_RUN) --ExecutePreprocessor.timeout=600 notebooks/models.ipynb
	@echo "Modeling complete → outputs/figures/"

test: venv/bin/activate
	venv/bin/pytest tests/ -v

# Utilities

data: venv/bin/activate
	$(PYTHON) download_data.py

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
	@echo "  make profiling  Run notebooks/data_profiling.ipynb  (needs raw data)"
	@echo "  make cleaning   Run notebooks/data_cleaning.ipynb   (needs raw data)"
	@echo "  make eda        Run notebooks/eda.ipynb"
	@echo "  make models     Run notebooks/models.ipynb"
	@echo ""
	@echo "  make test       Run pytest test suite (12 tests, ~1s)"
	@echo "  make data       Download raw EPA files"
	@echo "  make clean-outputs  Delete figures and features CSV"
	@echo "  make clean      Full reset including venv"
	@echo ""
