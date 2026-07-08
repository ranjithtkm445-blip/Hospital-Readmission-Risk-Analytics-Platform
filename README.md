# Hospital Readmission Risk Analytics Platform

An end-to-end healthcare data analytics project built on the UCI Diabetes 130-US dataset 
(10 years of hospital admission records from 1999-2008).

## Project Overview

This project analyzes hospital readmission patterns for diabetic patients across 130 US 
hospitals. It cleans and structures raw admission data, performs SQL-based analytics, 
generates summary reports, and visualizes insights through an interactive Power BI dashboard.

## Dataset

- **Source:** UCI Machine Learning Repository — Diabetes 130-US Hospitals (1999-2008)
- **Size:** 101,766 patient records, 50 features
- **Tables:** diabetic_data.csv, IDS_mapping.csv

## Pipeline

1. **step1_data_loader.py** — Load raw CSV, handle missing values, remove duplicates
2. **step2_prepare_analysis_data.py** — Feature engineering, generate summary analytics tables, load into SQLite

## Dashboard Pages (Power BI)

- **Executive Summary** — Total patients, admissions, readmission rate KPIs
- **Patient Demographics** — Age, gender, race breakdown
- **Clinical Analytics** — A1C results, insulin, lab procedures
- **Admission Analytics** — Admission type, discharge disposition, length of stay
- **Readmission Trends** — Readmission patterns by department and diagnosis

## Tech Stack

- Python, Pandas, SQLite, SQL, Power BI

## Project Structure
