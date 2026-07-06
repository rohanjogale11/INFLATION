# 📈 Personal Inflation Impact Calculator

A data-driven web application that computes a **personalised inflation rate**
based on your own monthly spending, using city-level and category-level CPI
data structured around India's MOSPI/RBI reporting framework.

Built for the Major Project (8th semester, B.Tech IT) at Manipal University
Jaipur — Rohan Jogale (229302351), under the guidance of Dr. Shweta Sharma.

## Features

- **Personal Calculator** — enter your spending across 8 CPI sub-categories
  and see your Laspeyres-weighted personal inflation rate plotted against
  the official national CPI.
- **City Explorer** — browse CPI trends for 8 major Indian cities
  (Mumbai, Delhi, Chennai, Bengaluru, Kolkata, Hyderabad, Ahmedabad, Lucknow),
  or compare two cities side-by-side with a divergence band.
- **Future Simulator** — project your expenses 1/3/5 years out under
  Optimistic (3%), Baseline (6%), and Pessimistic (10%) inflation scenarios,
  or a custom rate via slider.

## Project Structure

```
personal-inflation-calculator/
├── app.py                        # Home page
├── pages/
│   ├── 1_Personal_Calculator.py
│   ├── 2_City_Explorer.py
│   └── 3_Future_Simulator.py
├── utils/
│   ├── data_loader.py             # cached data access + calculations
│   └── charts.py                  # shared Plotly chart builders
├── data/
│   ├── national_cpi.csv
│   ├── city_cpi.csv
│   └── generate_data.py           # (re)generates the CSVs above
├── .streamlit/config.toml         # theme
├── requirements.txt
└── README.md
```

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

The app opens at `http://localhost:8501`.

## Deploy on Streamlit Community Cloud

1. Push this folder to a new **public GitHub repository**.
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**.
3. Select your repo, branch `main`, and set the main file path to `app.py`.
4. Click **Deploy** — you'll get a public URL like
   `https://your-app-name.streamlit.app`.
5. Every future `git push` to `main` auto-redeploys the app.

## About the data

MOSPI (mospi.gov.in) and RBI DBIE (dbie.rbi.org.in) publish official CPI
figures but don't expose a stable, scrape-friendly public API — both require
interactive downloads. For a reproducible, fully offline-first app,
`data/generate_data.py` produces a realistic monthly CPI series
(Jan 2015–Dec 2025) calibrated to published MOSPI category weights and
typical inflation behaviour (food volatility, fuel tracking crude swings,
housing/education running persistently above headline CPI, etc.).

**To go fully live:** download cleaned MOSPI/DBIE CSVs with the same
`date, category, cpi` (national) and `date, city, category, cpi` (city-level)
shape, drop them into `data/national_cpi.csv` and `data/city_cpi.csv`, and the
rest of the app works unchanged — no code edits needed elsewhere.

## Tech Stack

Python 3.11 · Streamlit · pandas · Plotly · NumPy

## License

Academic project — free to reuse for educational purposes.
