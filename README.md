#  Fake Review Detection System

## Overview
This project focuses on identifying suspicious and potentially fake reviews in an e-commerce dataset using SQL, Python, and Excel.

The goal is to detect abnormal user behavior, suspicious products, and quantify the impact of fake reviews.

---
## Business Problem

Online platforms rely heavily on user reviews to influence customer purchasing decisions. However, fake or manipulated reviews can mislead customers, damage trust, and impact business credibility.

The challenge is to:
- Identify suspicious users who may be posting fake reviews
- Detect products that are targets of review manipulation
- Quantify the extent of fraudulent activity
- Provide actionable insights for monitoring and prevention

This project aims to address these challenges using data analytics techniques.

---
## Approach

- Cleaned and preprocessed raw review data (date conversion, text cleaning)
- Loaded dataset into MySQL for efficient querying
- Performed exploratory analysis on user behavior and product trends
- Built a rule-based fraud detection model using:
  - Extreme ratings (1 or 5)
  - High review frequency
  - Multiple reviews in a single day
- Identified suspicious users and products based on fraud score
- Calculated % of suspicious reviews to measure impact
- Visualized insights using Python and created a dashboard in Excel

---

## Dataset Used
Amazon Fine Food Reviews - https://www.kaggle.com/datasets/snap/amazon-fine-food-reviews

---

##  Objectives
- Detect suspicious users based on behavior patterns
- Identify products heavily impacted by fake reviews
- Analyze rating patterns and review spikes
- Present insights using an interactive dashboard

---

## Tools & Technologies
- SQL (MySQL)
- Python (Pandas, Matplotlib, Seaborn)
- Excel (Dashboard & Visualization)

---

## Key Analysis Performed

### 1. User Fraud Detection
- Users with extreme ratings (1 or 5)
- High number of reviews
- Multiple reviews in a single day

### 2. Fraud Scoring Model
Users were assigned a fraud score based on:
- Review count
- Rating behavior
- Daily activity

### 3. Product-Level Analysis
- Products with highest suspicious reviews
- Products with highest % of suspicious reviews

### 4. Text Analysis
- Duplicate review detection

### 5. Time-Based Analysis
- Detection of review spikes (burst activity)

---

## Dashboard Preview

![Dashboard](images/dashboard.png)

---

## Key Insights
- Certain products have more than 15% suspicious reviews
- High-risk users show extreme rating behavior (1 or 5)
- Review spikes of up to 50 reviews/day indicate coordinated activity
- Suspicious reviews account for a small percentage overall but are concentrated on specific products

---

## Business Impact
- Helps identify fraudulent users and prevent misuse
- Improves trust in review systems
- Enables targeted monitoring of high-risk products

---

## Project Structure
```
fake-review-detection-system/
│
├── data/
│   └── sample_review.csv
│
├── sql/
│   └── analysis.sql
|   └── creating_table.sql
│
├── python/
│   └── charts.py
|   └── basic_data_cleaning.py
│
├── dashboard/
│   └── review_fraud_detection.xlsx
│
├── images/
│   └── dashboard.png
|   └── dashboard2.png
|   └── fraud_score.png
|   └── rating_distribution.png
|   └── spike_detection.png
|   └── affected_products.png
|   └── percentage_suspicious_reviews.png
│
├── README.md
```
---

## How to Run

1. Load dataset into MySQL
2. Run SQL queries from `analysis.sql`
3. Run Python script: charts.py
4. Open Excel dashboard

---

## Conclusion
This project demonstrates how data analysis techniques can be used to detect fraudulent behavior and generate actionable business insights.
