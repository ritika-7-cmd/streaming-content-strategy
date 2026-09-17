# 🎬 Streaming Content Strategy Analysis

Comparative catalog analysis of **Netflix**, **Amazon Prime Video**, and **Disney+**, exploring how each platform's content mix, genre focus, ratings, and release patterns reflect a distinct catalog strategy. Includes an interactive Streamlit dashboard.

## Overview

Using public streaming-catalog datasets (Kaggle), this project compares the three platforms across:

- **Content mix** — Movie vs. TV Show split by platform
- **Volume over time** — title counts by release year
- **Genre focus** — top primary genres per platform
- **Content ratings** — distribution of age/content ratings
- **Movie runtime** — distribution of film lengths (40–240 min)

The dashboard surfaces a strategic read for each platform:

| Platform | Strategy | Catalog Strength |
|---|---|---|
| **Amazon Prime** | Volume-first | Largest catalog, heavy on Drama & Action movies |
| **Netflix** | Balanced originals + licensed | Strong Drama/Comedy/Documentary mix, higher TV share |
| **Disney+** | Franchise & family focus | Animation, Action-Adventure, Kids & Family content |

## Project Structure

```
streaming-content-strategy/
├── app.py              # Streamlit dashboard (entry point)
├── data/                # Cleaned dataset(s) used by the dashboard
├── notebooks/           # Exploratory analysis / data cleaning notebooks
├── reports/             # Generated reports, figures, or write-ups
├── src/                 # Supporting Python modules
└── requirements.txt     # Python dependencies
```

## Getting Started

### Prerequisites
- Python 3.9+

### Installation

```bash
git clone https://github.com/ritika-7-cmd/streaming-content-strategy.git
cd streaming-content-strategy
pip install -r requirements.txt
```

### Run the dashboard

```bash
streamlit run app.py
```

This launches the dashboard at `http://localhost:8501`, reading from `data/cleaned_streaming_titles.csv`. Use the sidebar to filter by platform, content type, and release year range.

## Tech Stack

- **pandas / numpy** — data wrangling
- **plotly** — interactive charts
- **streamlit** — dashboard app
- **matplotlib / seaborn** — static plots (notebooks)
- **jupyter** — exploratory analysis

## Data Sources

Public Kaggle streaming-catalog datasets. Note the limitations called out in the dashboard itself:
- No official "Originals" flags or true viewership numbers in the public data
- Catalog snapshots are historical (roughly up to 2021) — current libraries have since changed

