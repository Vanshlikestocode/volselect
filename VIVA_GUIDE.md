# VolSelect viva guide

The brief says: *"No results without the code and data behind them. I will ask you to reproduce any number in the viva."* This sheet tells both of us where every number lives and how to show it in seconds.

## 1. Reproduce everything (say this first)

```
python verify.py
```

It checks the data fingerprints, runs the tests, re-runs the whole study from scratch and compares every result file. Ends with `VERDICT: ALL RESULTS REPRODUCED`. About one minute.

To show a single number live, open the CSV, or run the study and read the printed table:

```
python run_vs.py          # prints the full and 2022+ tables at the end
```

## 2. Where each headline number comes from

| Number (report / slides) | Value | File | Row → column |
|---|---|---|---|
| VolSelect annual return 2016–2026 | 17.0% | `results/table_full.csv` | Regime switch (LR), no trigger → CAGR % |
| NIFTY 50 annual return | 10.4% | `results/table_full.csv` | NIFTY 50 buy and hold → CAGR % |
| Equal-weight annual return | 20.3% | `results/table_full.csv` | Equal-weight NIFTY 50 → CAGR % |
| VolSelect volatility / Sharpe / max drawdown | 18.7% / 0.60 / −33.6% | `results/table_full.csv` | same row |
| VolSelect beta / alpha | 0.92 / +6.8% | `results/table_full.csv` | Beta, Alpha % a year |
| Resilience model beta (full / 2022+) | 0.75 / 0.70 | `table_full.csv`, `table_hold-out.csv` | Stress model only → Beta |
| Build period 2016–2021: VolSelect / equal weight / NIFTY | 24.3% / 24.4% / 14.3% | `results/table_development.csv` | CAGR % |
| Test period 2022+: VolSelect / equal weight / NIFTY | 8.4% / 15.1% / 5.3% | `results/table_hold-out.csv` | CAGR % |
| Test-period max drawdown: VolSelect / NIFTY | −30.4% / −16.5% | `results/table_hold-out.csv` | Max drawdown % |
| COVID crash return: VolSelect / NIFTY / equal weight | −11.5% / −18.6% / −19.4% | `results/table_covid.csv` | Period return % |
| 2022 sell-off: resilience / NIFTY | −4.0% / −10.5% | `results/table_2022.csv` | Period return % |
| Gross (no cost) 2022+: VolSelect / equal weight | 14.5% / 15.4% | `results/cost_sensitivity.csv` | "… \| 0.00%" → CAGR % 2022+ |
| Turnover | about 35× a year | `results/table_full.csv` | Turnover (x/yr) |
| Forecast on 2022+: hit rate / naive / precision / recall | 73% / 68% / 73% / 11% | `results/forecast_accuracy.csv` | Hold-out row |
| Indicators that held / failed after 2022 | defensive, RSI, %B, stochastic held; beta, downside beta failed | `results/overfitting_ic.csv` | Flag column |
| Stock-model accuracy (AUC, 0.5 = guessing) | gradient boosting 0.78 in sample, 0.52 next year; logistic regression 0.51 next year | `results/overfitting_auc.csv` | column means |
| Capacity | about Rs 85 crore | `results/capacity.csv` | last-but-one row |
| Value chart | Rs 10 lakh → 54.4 / 73.7 / 29.0 lakh | `results/equity_curves.csv` | last row |

## 3. How each metric is calculated (`volselect/metrics.py`)

- **Annual return (CAGR)** = (end value ÷ start value)^(1 / years) − 1.
- **Volatility** = standard deviation of daily returns × √252.
- **Sharpe** = (mean daily return − 6.5%/252) ÷ daily standard deviation × √252. 6.5% approximates the Indian 91-day T-bill.
- **Maximum drawdown** = the largest fall from a previous peak.
- **Beta** = covariance of the portfolio's daily excess returns with NIFTY's ÷ variance of NIFTY's.
- **Alpha (Jensen's)** = (mean portfolio excess return − beta × mean NIFTY excess return) × 252.
- **Turnover** = rupees traded in a year ÷ portfolio value.

## 4. Questions to expect, with short answers

**Why daily data?** The brief requires daily data for Portfolio Management groups; intraday is for Algo Trading groups.

**How do you know there is no look-ahead?** Signals use data up to the close; trades happen at the next open. `tests/test_vs.py` multiplies every price after a date by 3 and checks that the features, the forecast and the portfolio up to that date do not change.

**What is out-of-sample here?** All design choices were fixed on 2016–2021. Models are refitted each January on past data only. 2022 onward is reported separately (`table_hold-out.csv`).

**Your alpha is positive, so did you beat the market?** Against NIFTY, partly, but alpha is inflated by about 1.2–1.5% a year because the stock prices include dividends and the index does not. Equal weight's own 9% "alpha" shows that bias. Against the fair benchmark (equal weight) we did not win.

**Then why is this useful?** It loses less in sell-offs (COVID −11.5% vs NIFTY −18.6%), and the resilience model holds genuinely lower-beta stocks (0.70 out of sample). That is a risk tool, not a return engine. We say so in the report.

**Why does it trail equal weight?** Two reasons. (1) From 2022 there is no edge even before costs (14.5% vs 15.4%). (2) Weekly rebalancing costs about 6 points a year at 0.15% per side. DeMiguel et al. (2009) show 1/N is very hard to beat.

**Why inverse-volatility weights, not mean-variance?** Mean-variance needs expected returns, which are estimated badly and make optimisers overfit. Inverse volatility is a simple risk-parity-style rule with nothing to tune.

**Why weekly rebalancing?** So the portfolio can react to a regime change within days. The cost is high turnover; monthly rebalancing is our first next step.

**What about survivorship bias?** We use today's NIFTY 50 list for every year, which flatters every stock portfolio, the benchmark included. The fix is point-in-time index membership, which is not freely available.

**Why logistic regression and not machine learning?** We tested gradient boosting. It scored AUC 0.78 on training data but 0.52 the next year (0.5 is guessing), which is overfitting. The logistic regression is no better at predicting individual stocks (0.51 the next year), which matches picks beating NIFTY only about half the time. We kept it because it is simpler and its coefficients can be explained (`overfitting_auc.csv`). The value comes from the defensive tilt in stress (low beta), not from picking winners.

**How good is the volatility forecast?** On the 2022+ test it is right on 73% of days (a naive rule manages 68%), and 73% right when it says "high". But it catches only 11% of high-volatility days, so it is cautious and misses spikes. This is the weak link.

**What did you change since October?** Re-checking found real bugs, now fixed and tested: an indicator check that never computed its after-2022 column; Yahoo placeholder bars; a one-day misalignment in one table (that claim is withdrawn); the Sortino formula; and a rebalance edge case. See the report, Appendix B.

**Can you run it live?** Yes: `streamlit run volselect_app.py`. The live record (`live/ledger.csv`) is append-only and timestamped by git when the folder runs as a repository with the daily workflow.

## 5. Live demo script (2 minutes)

1. `streamlit run volselect_app.py`. **Overview**: today's regime, then the honest evidence.
2. **Live market**: quotes, the regime and ranking, the target portfolio for the next rebalance, and the forward record.
3. **Research**: the value chart against the benchmarks, then the 2022+ numbers.
4. In a terminal: `python verify.py`. Everything reproduces.
