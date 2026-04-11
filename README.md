# 📊 Earnings Reaction Intelligence Dashboard

A data-driven web application that analyzes post-earnings stock price reactions and attributes movement to either **idiosyncratic earnings effects** or broader **macro market conditions**.

This project combines event-study methodology, volatility analysis, and market-adjusted return modeling to provide actionable insights for traders and analysts.

---

## Project Overview

Stock prices often move sharply after earnings. However, determining whether a move is:

- A company-specific reaction  
- A broader market-driven move  
- A volatility shock  
- A sector rotation event  

...is not straightforward.

This dashboard solves that problem by computing:

- Raw earnings move
- Market-adjusted return (alpha)
- Beta-adjusted return
- Volatility context (VIX)
- Sector-relative performance

---

## 🎯 Core Features

### Earnings Event Tracker

For each earnings event:

- Close → Next Open Gap %
- Close → Next Close %
- Intraday high/low move

---

### Market Context Overlay

On the same earnings date:

- SPY return
- S&P 500 return
- VIX % change
- Sector ETF return

---

### Volatility Reaction Analysis

- Historical average earnings move
- Implied move vs realized move
- IV crush detection
- VIX shock overlay

---


## 🧠 Why This Matters

Most platforms show:
- Earnings date
- EPS beat/miss
- Price reaction

Very few quantify:

- Was the move abnormal?
- Did it underperform the market?
- Was volatility overpriced?
- Was this systematic risk?

This dashboard provides that context.

---

## 🏗 Architecture

### Backend
- Python (Flask or FastAPI)
- Requests / BeautifulSoup (scraping)
- Pandas / NumPy (analysis)
- PostgreSQL or SQLite (data storage)

### Frontend
- React
- Chart.js / Recharts
- Data tables & heatmaps

### Data Sources
- Earnings calendar
- Historical OHLC data
- SPY / S&P data
- VIX data
- Sector ETF data

---

## 📂 Project Structure
```
earnings-dashboard/
│
├── backend/
│   ├── app.py
│   ├── models.py
│   ├── scraper.py
│   ├── analytics.py
│   └── database.py
│
├── frontend/
│   ├── src/
│   ├── components/
│   └── dashboard/
│
├── data/
├── requirements.txt
└── README.md
```

## 🔥 Example Use Cases

- Identify companies with strong earnings-specific outperformance
- Detect exaggerated sell-offs during macro panic
- Evaluate whether implied volatility was overpriced
- Scan for asymmetric event risk

---