# Respiratory Disease Prediction from Environmental Factors in New York City

**Team Members**:
- Gowrav Lakshmipathy - U53940054
- Priya Dilip Bajaria - U08184333
- Nandini Nandan Narvekar - U25345416

## Project Description

We aim to analyze the relationship between environmental conditions and respiratory disease outcomes using publicly available health and environmental data. For this, we will be using data collected from New York City to maintain data consistency. 

Understanding how environmental factors influence respiratory health is critical for public health preparedness. By quantifying these relationships, hospitals can better anticipate patient surges, individuals with chronic respiratory conditions can take preventive measures on high-risk days, and public health officials can develop targeted interventions. 

We will predict respiratory emergency department visits based on air quality measurements, weather conditions, and climate factors to identify which environmental variables most strongly correlate with respiratory illness spikes.


## Dataset
Most of our datasets will be collected from the NYC Department of Health and Mental Hygiene.

Link: https://www.nyc.gov/site/doh/data/tools.page

Further, we will be working on getting the dataset on how pollen leads to respiratory disorder surges.

## Project Timeline (8 weeks)

**Weeks 1-2: Data Collection and Initial Exploration**

Download datasets from NYC DOHMH and EpiQuery portals. Perform initial quality checks and document data structure.

**Week 3: Data Cleaning and Integration**

Standardize formats, handle missing values, and merge datasets by date into a unified analysis file.

**Week 4: Feature Engineering and Exploratory Data Analysis**

Engineer relevant features from raw data and compute descriptive statistics. Analyze patterns and relationships in the dataset.

**Weeks 5-6: Model Development and Training**

Implement and tune predictive models using various machine learning techniques. Perform cross-validation and compare performance metrics.

**Week 7: Model Evaluation and Analysis**

Evaluate models on test data and analyze feature importance. Investigate errors and document limitations.

**Week 8: Final Documentation and Presentation**

Complete repository documentation and prepare final report. Ensure reproducibility with automated testing workflows.


### Project Goals

- Develop a predictive model to forecast health outcomes based on environmental conditions.

- Identify and quantify the key environmental factors that influence public health trends.

- Generate risk forecasts to support public health situational awareness and help anticipate respiratory health outcome surges under adverse environmental conditions

- Evaluate model performance and assess the reliability of predictions across different conditions.

## Data Collection Plan

### Data Sources

All data will be sourced from the New York City Department of Health and Mental Hygiene public data portals, which provide verified, quality-controlled data that is freely accessible.

**URL:** https://www.nyc.gov/site/doh/data/tools.page

**1. Respiratory Emergency Department Visits**
Daily counts of emergency department visits categorized by respiratory syndromes.

**2. Air Quality Measurements**
Measurements of air pollutants including fine particulate matter and nitrogen dioxide.

**3. Weather and Climate Data**
Daily weather variables including temperature, precipitation, and humidity.

**4. Weather-Related Illness Indicators**
Emergency department visits for heat and cold-related health conditions.

### Data Collection Method

All datasets will be manually downloaded from NYC DOHMH web portals and saved as CSV files.

**Syndromic Surveillance Data**
Access the EpiQuery portal, select relevant health indicators for the target period, and export the data.

**Air Quality Data**
Download pollutant measurements from the Environment & Health Data Portal.

**Climate and Weather Data**
Download daily weather measurements from the Climate Data Explorer.

**Weather-Related Illness Data**
Download emergency department visit data for weather-related health conditions.

**Data Integration Process**

After collecting all individual datasets, we will:
1. Standardize date formats across all files 
2. Verify temporal alignment and identify any gaps in coverage
3. Merge datasets using date as the primary key
4. Create a master dataset with all environmental and health variables aligned by day
5. Document data provenance and any transformations applied
6. Store raw and processed data in separate directories within the GitHub repository

