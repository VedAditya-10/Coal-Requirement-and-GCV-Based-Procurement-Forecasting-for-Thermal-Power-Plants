
# Coal Demand Forecasting System for Captive Power Plants

## Overview
This project focuses on building a data driven coal demand forecasting model for a captive thermal power plant supporting aluminium smelting operations. Coal is a critical input for power generation, and inaccurate demand estimation can lead to production disruptions or excess inventory costs. The objective is to forecast future coal demand using historical consumption, operational, and fuel quality data.

## Problem Statement
Aluminium smelters rely heavily on uninterrupted power supply from captive power plants. Coal demand fluctuates due to changes in power generation, plant efficiency, fuel quality, and operational conditions. Manual or heuristic based planning often fails to capture these dynamics, leading to inefficiencies. This project aims to provide a reliable forecasting framework to support better inventory and production planning.

## Data Description
The model uses cleaned and merged datasets including:
- Plant wise and time series coal consumption
- Power generation and capacity related features
- Fuel quality parameters such as Gross Calorific Value
- Normalized plant identifiers to enable consistent data merging

Special care is taken to handle inconsistent plant naming and heterogeneous data sources.

## Approach
- Data cleaning and feature selection
- Plant name normalization and key based dataset merging
- Exploratory data analysis to identify consumption patterns
- Regression based and time series based forecasting models
- Evaluation using appropriate error metrics

The system is designed to be extendable to more advanced models if required.

## Expected Outcome
- Accurate short term and medium term coal demand forecasts
- Improved inventory planning and reduced operational risk
- A practical, real world forecasting pipeline suitable for industrial use

## Tech Stack
- Python
- Pandas, NumPy
- Matplotlib, Seaborn
- Scikit learn

## Data Source 

This dataset created for this project contains plant-level monthly coal data for ***Indian thermal power plants***, compiled and standardised from 22 official monthly reports spanning January 2024 to October 2025.

The raw data was sourced from the National Power Portal (NPP), the Government of India’s official platform for power sector statistics. From here, you get datasets for daily, weekly and yearly consumption :
[https://npp.gov.in/dgrReports](url)

While the original reports are publicly available, they are released as complex, semi-structured Excel files with multi-row headers, regional groupings, embedded totals, and summary tables, making direct analysis difficult.

This dataset transforms those raw files into a single, clean, analysis-ready time-series dataset at the individual power plant level.
