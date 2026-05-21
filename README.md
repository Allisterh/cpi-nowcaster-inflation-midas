# CPI Nowcaster

Real-time nowcasting model for US Consumer Price Index (CPI) inflation.

[![Live Dashboard](https://img.shields.io/badge/Live-Dashboard-green?style=for-the-badge&logo=streamlit)](https://cpi-nowcaster-1.streamlit.app)

## What This Does

CPI stands for Consumer Price Index. It is a key economic metric that measures the average change over time in the prices paid by consumers for a representative "basket" of goods and services. It is the primary tool used by governments and economists to track inflation and evaluate the cost of living. Official CPI data is released monthly with a 2-week delay. Markets need to know
inflation *right now*. This project estimates current-month CPI using high-frequency
financial data combined with traditional economic indicators.

## How It Works

1. **Daily data pipeline** fetches market data (breakeven rates, oil, dollar index)
2. **Monthly macro data** (unemployment, retail sales, industrial production) incorporated on release days
3. **MIDAS + XGBoost model** handles the "ragged edge" of mixed-frequency data
4. **Streamlit dashboard** displays the live nowcast with uncertainty bands

## Project Structure

cpi-nowcaster/
├── src/
│ ├── data_fetcher.py # FRED API data download
│ ├── ragged_edge.py # Mixed-frequency alignment
│ ├── model.py # MIDAS + XGBoost model
│ └── nowcast.py # Daily nowcast orchestration
├── dashboard/
│ └── app.py # Streamlit web dashboard
├── data/ # Cached data (gitignored)
└── requirements.txt # Python dependencies

## Data Sources

- **FRED (Federal Reserve Economic Data)**: CPI, unemployment, industrial production, payrolls, retail sales
- **Daily financial indicators**: 5-Year breakeven inflation rate, trade-weighted dollar index, WTI crude oil

## Setup

```bash
git clone https://github.com/aarifah0/cpi-nowcaster.git
cd cpi-nowcaster
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
$env:FRED_API_KEY="your-key"
python src/data_fetcher.py