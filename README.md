# UK Housing Delivery Analysis

Analysis of housing delivery across England, with a focus on local authority performance, affordable housing, and the starts-vs-completions pipeline. Data from MHCLG Live Tables.

## Why this project

Housing delivery is a core function of every English district council. Councils are legally required to demonstrate they are meeting their Local Housing Need targets, and they report on completions and affordable housing delivery as key performance indicators. This project analyses the official government data that councils use internally.

## What the dashboard covers

- National housing delivery trends, 1946 to present
- Local authority comparison across England
- Affordable housing delivery by tenure (social rent, affordable rent, shared ownership)
- Huntingdonshire and East of England in context
- Starts vs completions: the development pipeline

## Data source

MHCLG Live Tables on housing supply — official government statistics published by the Ministry of Housing, Communities and Local Government:
- [Net additional dwellings](https://www.gov.uk/government/statistical-data-sets/live-tables-on-net-supply-of-housing)
- [Indicators of new supply](https://www.gov.uk/government/statistical-data-sets/live-tables-on-house-building)
- [Affordable housing supply](https://www.gov.uk/government/statistical-data-sets/live-tables-on-affordable-housing-supply)

## Stack

Python, pandas, SQLite, Plotly, Streamlit

## Running locally

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Project structure

```
data/raw/          MHCLG source files (not tracked in git)
data/processed/    cleaned CSVs and SQLite database
notebooks/         analysis notebooks
outputs/figures/   exported charts
app.py             Streamlit dashboard
```

## Related project

[NHS A&E Waiting Times Analysis](https://nhs-waiting-time-analysis-ftffjzfb52xgeqyn2mgc5d.streamlit.app/)
