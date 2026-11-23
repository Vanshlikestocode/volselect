# VolSelect

**A volatility-aware NIFTY 50 portfolio** (Design Experience project, Portfolio Management).
Forecast when NIFTY volatility will rise, hold the NIFTY 50 stocks most likely to hold up, and test it on data the model never saw.

Vansh Dave · Karthik Agarwal · Guide: Sailesh Kulkarni. Academic research prototype; not investment advice.

## Deliverables in this folder

| File | What it is |
|---|---|
| `VolSelect_Project_Report.pdf` | Report: problem statement → background and literature → data → methodology → backtest results → limitations → conclusion → references |
| `VolSelect_Presentation.pptx` | 12 slides (problem, data, method, results, limitations, live demo), with speaker notes |
| `VIVA_GUIDE.md` | Where every number comes from, how to reproduce it in front of the examiner, and likely questions |
| Code, data, results | Everything below; `python verify.py` reproduces every number |

## Reproduce every number (one command, offline, about one minute)

```
pip install -r requirements.txt
python verify.py
```

`verify.py` checks the bundled data against `data/MANIFEST.sha256`, runs the unit tests, re-runs the whole study into a temporary folder and compares every file in `results/` number by number. Expected last line: `VERDICT: ALL RESULTS REPRODUCED`. Do not run `--download` first: Yahoo Finance revises adjusted prices over time, so fresh data moves the numbers slightly (the manifest check would report it).

## How the brief maps to this project

| Brief (Portfolio Management) | Here |
|---|---|
| Stock universe and selection logic | All 50 current NIFTY 50 stocks; regime switch: momentum in calm markets, resilience model when volatility is rising or high (`volselect/selection.py`) |
| Weighting and rebalancing | Top 10, weights inverse to 20-day volatility, rebalanced weekly at the open (`volselect/portfolio.py`) |
| Benchmark comparison | NIFTY 50 buy and hold, and equal-weight NIFTY 50 |
| Annualised return, volatility, Sharpe, max drawdown, beta/alpha | `results/table_*.csv` (formulas in `volselect/metrics.py`) |
| Portfolio value chart vs benchmark | `results/chart_1_equity.png`, report 5.3, slide 7, the dashboard's Research page |
| Build on one period, test on a later one | Walk-forward (models refitted every January on past data only); built on 2016–2021, tested on 2022 onward |
| Code and data behind every result | This folder; `python verify.py` |
| Data source, instruments, period, frequency | Yahoo Finance; 50 stocks + NIFTY 50 + India VIX; prices from 2012, test Jan 2016 – Oct 2026; **daily** candles |

## Commands

```
python run_vs.py                     # re-run the study, writes results/ (tables, 5 charts, audit log, report.md)
python -m pytest -q tests            # unit tests, including look-ahead tests
streamlit run volselect_app.py       # dashboard: overview, live market, research (the live demo)
python live_update.py                # fetch today's prices, extend the live paper-trading record in live/
python report/build_report.py        # rebuild the report PDF from results/ (checks every claim against the files)
python slides/deck_data.py && node slides/build_deck.js   # rebuild the slides (needs: npm install pptxgenjs)
```

## What is inside

| Path | Purpose |
|---|---|
| `volselect/data.py` | Defensive CSV reader (drops Yahoo's no-trade placeholder bars), synthetic data for offline tests |
| `volselect/universe.py` | NIFTY 50 list with sectors; download and load |
| `volselect/regime.py` | GARCH(1,1) fitted on past data only; logistic forecast of high volatility over the next 10 days; calm / rising / high |
| `volselect/features.py` | 19 per-stock measures as cross-stock ranks; the 10-day excess-return target |
| `volselect/selection.py` | One logistic model per regime (gradient boosting as an overfitting check); information coefficients |
| `volselect/portfolio.py` | Weekly top-10 inverse-volatility portfolio, costs, optional drawdown trigger |
| `volselect/metrics.py` | CAGR, volatility, Sharpe, Sortino, drawdown, beta, Jensen's alpha, calendar returns |
| `volselect/indicators.py` | EMA, SMA, RSI, ATR, MACD, ADX, stochastic, OBV, Bollinger %B |
| `volselect/live.py`, `live_update.py` | Live forward paper-trading record (append-only ledger), today's ranking and target portfolio |
| `run_vs.py` | The whole walk-forward study → `results/` |
| `verify.py` | Independent re-run check |
| `volselect_app.py`, `views/` | Dashboard |
| `tests/` | Unit tests |
| `data/` | The exact daily price data used (with `MANIFEST.sha256`) |
| `results/` | Every table, chart and audit log quoted in the report and slides |
| `live/` | Live record state (refreshed by `live_update.py`; `.github/workflows/live-update.yml` runs it every weekday at 18:00 IST when the folder is a GitHub repository) |

## Results in one paragraph

Over Jan 2016 – Oct 2026 the regime switch earned 17.0% a year against 10.4% for NIFTY 50 (Sharpe 0.60 vs 0.30), but equal-weight NIFTY 50 earned 20.3% (Sharpe 0.84). On the 2022+ test it earned 8.4% against 5.3% for NIFTY and 15.1% for equal weight, with a deeper worst fall than NIFTY. It lost clearly less than both benchmarks in the COVID crash and the 2022 sell-off, and the resilience model kept a low beta (0.70) out of sample. The volatility forecast is the weak link: right 73% of days on the test, but it catches only 11% of high-volatility days. Full detail, caveats (survivorship bias, dividends in stocks but not the index) and references are in the report.
