# Volatility-aware NIFTY 50 stock selection: walk-forward results

**Academic research prototype. Not investment advice.** Past backtest results do not predict future returns.

50 current NIFTY 50 stocks, data to 2026-10-23. Models refitted every 1 January on past data only. Weekly rebalance, top 10, inverse-volatility weights, 0.15% cost per side, signals at the close, fills at the next open. Drawdown trigger chosen on 2016–2021 Calmar only: 12%.

## Full walk-forward 2016–2026

| Approach | CAGR % | Volatility % | Sharpe | Max drawdown % | Beta | Alpha % a year | Days below -2% (count) | Calmar | Turnover (x/yr) |
|---|---|---|---|---|---|---|---|---|---|
| Regime switch (LR), no trigger | 16.98 | 18.74 | 0.60 | -33.59 | 0.92 | 6.82 | 102.00 | 0.51 | 35.33 |
| Regime switch (LR) + 8% trigger | 13.28 | 16.53 | 0.46 | -43.13 | 0.84 | 3.51 | 68.00 | 0.31 | 25.81 |
| Regime switch (LR) + 10% trigger | 14.52 | 17.03 | 0.52 | -44.54 | 0.86 | 4.59 | 76.00 | 0.33 | 23.11 |
| Regime switch (LR) + 12% trigger | 15.67 | 17.67 | 0.56 | -38.57 | 0.92 | 5.47 | 88.00 | 0.41 | 29.71 |
| Regime switch (GB), no trigger | 18.13 | 18.92 | 0.65 | -34.04 | 0.94 | 7.73 | 107.00 | 0.53 | 36.81 |
| Momentum only | 19.40 | 18.99 | 0.71 | -36.50 | 0.92 | 8.95 | 113.00 | 0.53 | 22.37 |
| Stress model only | 15.49 | 15.57 | 0.61 | -33.86 | 0.75 | 5.76 | 45.00 | 0.46 | 33.51 |
| Low volatility only | 12.00 | 14.74 | 0.42 | -37.40 | 0.78 | 2.36 | 42.00 | 0.32 | 32.35 |
| Equal-weight NIFTY 50 (benchmark) | 20.32 | 16.50 | 0.84 | -38.40 | 0.97 | 9.05 | 61.00 | 0.53 | 1.45 |
| NIFTY 50 buy and hold (benchmark) | 10.36 | 16.14 | 0.30 | -38.44 | 1.00 | -0.00 | 61.00 | 0.27 | nan |

## Development 2016–2021

| Approach | CAGR % | Volatility % | Sharpe | Max drawdown % | Beta | Alpha % a year | Days below -2% (count) | Calmar | Turnover (x/yr) |
|---|---|---|---|---|---|---|---|---|---|
| Regime switch (LR), no trigger | 24.29 | 20.34 | 0.88 | -33.59 | 0.92 | 9.80 | 68.00 | 0.72 | 34.17 |
| Regime switch (LR) + 8% trigger | 17.93 | 18.03 | 0.67 | -43.13 | 0.80 | 4.95 | 46.00 | 0.42 | 35.04 |
| Regime switch (LR) + 10% trigger | 20.52 | 18.65 | 0.77 | -44.54 | 0.83 | 7.05 | 49.00 | 0.46 | 29.67 |
| Regime switch (LR) + 12% trigger | 22.52 | 19.55 | 0.83 | -38.57 | 0.91 | 8.25 | 57.00 | 0.58 | 38.42 |
| Regime switch (GB), no trigger | 26.08 | 20.56 | 0.94 | -34.04 | 0.94 | 11.09 | 71.00 | 0.77 | 36.57 |
| Momentum only | 28.19 | 20.43 | 1.03 | -36.50 | 0.91 | 13.04 | 71.00 | 0.77 | 21.03 |
| Stress model only | 22.60 | 17.42 | 0.91 | -33.86 | 0.78 | 9.05 | 30.00 | 0.67 | 36.10 |
| Low volatility only | 17.74 | 16.01 | 0.72 | -37.40 | 0.76 | 4.79 | 25.00 | 0.47 | 30.30 |
| Equal-weight NIFTY 50 (benchmark) | 24.43 | 18.07 | 0.97 | -38.40 | 0.96 | 9.07 | 40.00 | 0.64 | 1.61 |
| NIFTY 50 buy and hold (benchmark) | 14.30 | 17.81 | 0.49 | -38.44 | 1.00 | 0.00 | 41.00 | 0.37 | nan |

## Hold-out 2022–2026

| Approach | CAGR % | Volatility % | Sharpe | Max drawdown % | Beta | Alpha % a year | Days below -2% (count) | Calmar | Turnover (x/yr) |
|---|---|---|---|---|---|---|---|---|---|
| Regime switch (LR), no trigger | 8.36 | 16.54 | 0.19 | -30.43 | 0.92 | 3.31 | 34.00 | 0.27 | 36.85 |
| Regime switch (LR) + 8% trigger | 7.61 | 14.47 | 0.14 | -25.02 | 0.92 | 2.29 | 22.00 | 0.30 | 14.35 |
| Regime switch (LR) + 10% trigger | 7.34 | 14.77 | 0.12 | -23.93 | 0.93 | 2.08 | 27.00 | 0.31 | 14.98 |
| Regime switch (LR) + 12% trigger | 7.55 | 15.02 | 0.14 | -24.35 | 0.94 | 2.32 | 31.00 | 0.31 | 18.90 |
| Regime switch (GB), no trigger | 8.82 | 16.64 | 0.21 | -30.25 | 0.95 | 3.77 | 36.00 | 0.29 | 37.18 |
| Momentum only | 9.18 | 17.03 | 0.23 | -27.04 | 0.95 | 4.17 | 42.00 | 0.34 | 24.08 |
| Stress model only | 7.18 | 12.90 | 0.11 | -21.74 | 0.70 | 1.60 | 15.00 | 0.33 | 30.35 |
| Low volatility only | 5.11 | 12.98 | -0.04 | -21.67 | 0.81 | -0.35 | 17.00 | 0.24 | 34.97 |
| Equal-weight NIFTY 50 (benchmark) | 15.13 | 14.32 | 0.62 | -16.30 | 0.98 | 9.18 | 21.00 | 0.93 | 1.24 |
| NIFTY 50 buy and hold (benchmark) | 5.31 | 13.76 | -0.02 | -16.47 | 1.00 | 0.00 | 20.00 | 0.32 | nan |

## COVID crash (14 Feb–30 Apr 2020)

| Approach | CAGR % | Volatility % | Sharpe | Max drawdown % | Beta | Alpha % a year | Days below -2% (count) | Calmar | Turnover (x/yr) | Period return % |
|---|---|---|---|---|---|---|---|---|---|---|
| Regime switch (LR), no trigger | -44.53 | 59.38 | -0.90 | -32.99 | 0.93 | 35.55 | 12.00 | -1.35 | 51.37 | -11.54 |
| Regime switch (LR) + 8% trigger | -53.81 | 55.69 | -1.35 | -35.88 | 0.84 | 4.78 | 9.00 | -1.50 | 28.66 | -14.85 |
| Regime switch (LR) + 10% trigger | -53.81 | 55.69 | -1.35 | -35.88 | 0.84 | 4.78 | 9.00 | -1.50 | 28.66 | -14.85 |
| Regime switch (LR) + 12% trigger | -59.52 | 60.37 | -1.44 | -38.57 | 0.95 | 4.04 | 15.00 | -1.54 | 47.80 | -17.15 |
| Regime switch (GB), no trigger | -36.80 | 60.23 | -0.64 | -33.71 | 0.93 | 50.30 | 13.00 | -1.09 | 57.98 | -9.10 |
| Momentum only | -55.81 | 56.00 | -1.43 | -36.50 | 0.84 | 0.54 | 10.00 | -1.53 | 17.13 | -15.63 |
| Stress model only | -40.05 | 59.05 | -0.76 | -32.40 | 0.93 | 43.47 | 11.00 | -1.24 | 47.48 | -10.10 |
| Low volatility only | -47.54 | 56.67 | -1.07 | -35.16 | 0.87 | 22.68 | 8.00 | -1.35 | 43.13 | -12.56 |
| Equal-weight NIFTY 50 (benchmark) | -64.61 | 58.52 | -1.75 | -37.68 | 0.95 | -12.11 | 13.00 | -1.71 | 2.57 | -19.44 |
| NIFTY 50 buy and hold (benchmark) | -62.81 | 61.13 | -1.56 | -37.24 | 1.00 | 0.00 | 14.00 | -1.69 | nan | -18.60 |

## 2022 sell-off (Jan–Jun 2022)

| Approach | CAGR % | Volatility % | Sharpe | Max drawdown % | Beta | Alpha % a year | Days below -2% (count) | Calmar | Turnover (x/yr) | Period return % |
|---|---|---|---|---|---|---|---|---|---|---|
| Regime switch (LR), no trigger | -14.01 | 20.77 | -0.94 | -14.72 | 0.87 | 4.07 | 8.00 | -0.95 | 49.49 | -7.09 |
| Regime switch (LR) + 8% trigger | -24.14 | 21.59 | -1.48 | -18.92 | 0.93 | -6.62 | 8.00 | -1.28 | 21.74 | -12.60 |
| Regime switch (LR) + 10% trigger | -24.22 | 22.08 | -1.45 | -19.04 | 0.99 | -5.15 | 10.00 | -1.27 | 26.60 | -12.64 |
| Regime switch (LR) + 12% trigger | -23.12 | 22.37 | -1.36 | -18.79 | 1.01 | -3.10 | 10.00 | -1.23 | 24.07 | -12.03 |
| Regime switch (GB), no trigger | -12.46 | 21.22 | -0.83 | -16.58 | 0.90 | 6.90 | 8.00 | -0.75 | 56.32 | -6.28 |
| Momentum only | -24.89 | 22.45 | -1.46 | -19.73 | 0.85 | -9.64 | 11.00 | -1.26 | 27.76 | -13.02 |
| Stress model only | -8.05 | 18.73 | -0.71 | -10.09 | 0.80 | 8.45 | 6.00 | -0.80 | 32.12 | -4.01 |
| Low volatility only | -25.99 | 18.21 | -1.93 | -17.85 | 0.81 | -13.08 | 4.00 | -1.46 | 35.11 | -13.64 |
| Equal-weight NIFTY 50 (benchmark) | -15.90 | 21.24 | -1.02 | -14.22 | 0.98 | 5.13 | 8.00 | -1.12 | 1.56 | -8.09 |
| NIFTY 50 buy and hold (benchmark) | -20.30 | 20.64 | -1.32 | -16.47 | 1.00 | -0.00 | 9.00 | -1.23 | nan | -10.47 |

## Days traded under a rising or high forecast

Return on day t when the forecast made at the close of t-1 said rising or high (the forecast the portfolio actually acted on).

| Approach | Annualised return on days after a rising/high forecast % | Days |
|---|---|---|
| Regime switch (LR), no trigger | 42.8 | 548.0 |
| Regime switch (LR) + 8% trigger | 35.2 | 548.0 |
| Regime switch (LR) + 10% trigger | 43.1 | 548.0 |
| Regime switch (LR) + 12% trigger | 40.9 | 548.0 |
| Regime switch (GB), no trigger | 50.7 | 548.0 |
| Momentum only | 50.9 | 548.0 |
| Stress model only | 38.7 | 548.0 |
| Low volatility only | 27.7 | 548.0 |
| Equal-weight NIFTY 50 (benchmark) | 47.8 | 548.0 |
| NIFTY 50 buy and hold (benchmark) | 37.1 | 548.0 |

## Win/loss (2016–2026)

Weeks end on Friday, months on the last trading day. A pick is one stock held from one rebalance open to the next; it wins if it beat NIFTY 50 over that span.

| Approach | Weeks up % | Weeks beating NIFTY % | Weeks beating equal weight % | Months up % | Months beating NIFTY % | Months beating equal weight % | Avg up week % | Avg down week % | Picks | Picks beating NIFTY % | Avg pick excess vs NIFTY % |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Regime switch (LR), no trigger | 56.5 | 51.7 | 48.0 | 65.1 | 54.3 | 48.1 | 1.9 | -1.8 | 5620.0 | 50.0 | 0.2 |
| Regime switch (LR) + 8% trigger | 58.8 | 52.2 | 43.2 | 64.3 | 54.3 | 40.3 | 1.6 | -1.6 | 12029.0 | 50.2 | 0.2 |
| Regime switch (LR) + 10% trigger | 58.3 | 51.9 | 41.9 | 63.6 | 52.7 | 38.0 | 1.7 | -1.6 | 11212.0 | 50.1 | 0.2 |
| Regime switch (LR) + 12% trigger | 57.5 | 54.9 | 44.4 | 63.6 | 60.5 | 45.0 | 1.8 | -1.8 | 10494.0 | 50.7 | 0.2 |
| Regime switch (GB), no trigger | 56.5 | 52.4 | 47.4 | 62.0 | 55.0 | 49.6 | 2.0 | -1.8 | 5620.0 | 50.7 | 0.3 |
| Momentum only | 56.7 | 54.2 | 49.9 | 65.9 | 56.6 | 49.6 | 2.0 | -1.8 | 5620.0 | 50.6 | 0.2 |
| Stress model only | 56.5 | 50.8 | 44.8 | 63.6 | 51.9 | 36.4 | 1.6 | -1.4 | 5620.0 | 49.8 | 0.2 |
| Low volatility only | 56.8 | 51.3 | 43.7 | 59.7 | 52.7 | 41.1 | 1.5 | -1.4 | 5620.0 | 49.9 | 0.1 |
| Equal-weight NIFTY 50 (benchmark) | 59.0 | 62.2 | nan | 66.7 | 71.3 | nan | 1.7 | -1.6 | nan | nan | nan |
| NIFTY 50 buy and hold (benchmark) | 57.2 | nan | 37.8 | 56.6 | nan | 28.7 | 1.6 | -1.6 | nan | nan | nan |

## Calendar-year returns %

2026 is a partial year (to 2026-10-23).

| Year | Regime switch (LR) + 12% trigger | Regime switch (LR), no trigger | Stress model only | Equal-weight NIFTY 50 (benchmark) | NIFTY 50 buy and hold (benchmark) |
|---|---|---|---|---|---|
| 2016 | 15.4 | 9.6 | 21.6 | 14.7 | 5.1 |
| 2017 | 30.7 | 43.8 | 29.3 | 42.8 | 28.6 |
| 2018 | -2.1 | 7.4 | 0.9 | 1.2 | 3.2 |
| 2019 | 10.2 | -0.1 | 8.8 | 15.8 | 12.0 |
| 2020 | 33.2 | 49.2 | 42.1 | 29.0 | 14.9 |
| 2021 | 55.6 | 45.9 | 38.2 | 49.5 | 24.1 |
| 2022 | -1.3 | 5.1 | 13.2 | 10.6 | 4.3 |
| 2023 | 36.9 | 36.8 | 27.5 | 40.9 | 20.0 |
| 2024 | 21.4 | 30.3 | 6.5 | 21.4 | 8.8 |
| 2025 | -3.5 | -6.1 | 2.6 | 14.0 | 10.5 |
| 2026 | -9.9 | -15.9 | -11.4 | -7.6 | -13.5 |

## Cost sensitivity (2016–2026)

0.00% = gross, before any cost.

| Approach | cost per side | CAGR % | Sharpe | Max drawdown % | CAGR % 2016-2021 | CAGR % 2022+ |
|---|---|---|---|---|---|---|
| Regime switch (LR) + 12% trigger | 0.00% | 18.64 | 0.72 | -40.24 | 25.93 | 10.03 |
| Regime switch (LR) + 12% trigger | 0.05% | 16.74 | 0.62 | -41.08 | 23.51 | 8.71 |
| Regime switch (LR) + 12% trigger | 0.15% | 15.67 | 0.56 | -38.57 | 22.52 | 7.55 |
| Regime switch (LR) + 12% trigger | 0.30% | 11.33 | 0.35 | -48.83 | 15.63 | 6.09 |
| Regime switch (LR), no trigger | 0.00% | 23.40 | 0.89 | -32.41 | 30.90 | 14.54 |
| Regime switch (LR), no trigger | 0.05% | 21.22 | 0.80 | -32.61 | 28.66 | 12.44 |
| Regime switch (LR), no trigger | 0.15% | 16.98 | 0.60 | -33.59 | 24.29 | 8.36 |
| Regime switch (LR), no trigger | 0.30% | 10.92 | 0.31 | -39.40 | 18.04 | 2.53 |
| Stress model only | 0.00% | 21.49 | 0.94 | -33.15 | 29.49 | 12.19 |
| Stress model only | 0.05% | 19.45 | 0.83 | -33.39 | 27.15 | 10.49 |
| Stress model only | 0.15% | 15.49 | 0.61 | -33.86 | 22.60 | 7.18 |
| Stress model only | 0.30% | 9.80 | 0.27 | -35.66 | 16.10 | 2.41 |
| Equal-weight NIFTY 50 (benchmark) | 0.00% | 20.64 | 0.85 | -38.46 | 24.81 | 15.39 |
| Equal-weight NIFTY 50 (benchmark) | 0.05% | 20.53 | 0.85 | -38.44 | 24.68 | 15.31 |
| Equal-weight NIFTY 50 (benchmark) | 0.15% | 20.32 | 0.84 | -38.40 | 24.43 | 15.13 |
| Equal-weight NIFTY 50 (benchmark) | 0.30% | 20.00 | 0.82 | -38.34 | 24.06 | 14.88 |

## Capacity

- Median stock: avg daily traded value, last year (Rs crore): 407
- Least liquid stock: avg daily traded value (Rs crore): 170
- AUM where a 10% position is 5% of the least liquid stock's daily value (Rs crore): 85
- AUM where a 10% position is 5% of the median stock's daily value (Rs crore): 203

## Volatility forecast accuracy (high = p ≥ 0.5 vs naive 'next 10 days like the last 10')

**Development 2016–2021:** 1476 days, 23% actually high. Hit rate 76.2% (naive 78.3%); precision 47.1%; recall 19.2% (naive 52.5%).

| actual | forecast not high | forecast high |
|---|---|---|
| actual not high | 1059 | 74 |
| actual high | 277 | 66 |

**Hold-out 2022–2026:** 1177 days, 29% actually high. Hit rate 72.9% (naive 67.5%); precision 72.5%; recall 10.8% (naive 42.4%).

| actual | forecast not high | forecast high |
|---|---|---|
| actual not high | 821 | 14 |
| actual high | 305 | 37 |

## Drawdown trigger thresholds

| Trigger | Calmar 2016–2021 | Calmar 2022+ | Triggers |
|---|---|---|---|
| 8% | 0.42 | 0.30 | 18.00 |
| 10% | 0.46 | 0.31 | 13.00 |
| 12% | 0.58 | 0.31 | 10.00 |

## Overfitting checks

Feature information coefficients on high-volatility days:

| Feature | IC 2013–2021 (high-vol days) | IC 2022+ (high-vol days) | Flag |
|---|---|---|---|
| beta | -0.060 | 0.005 | looked useful before 2022, failed after |
| down_beta | -0.043 | 0.010 | looked useful before 2022, failed after |
| hv_excess | -0.016 | -0.014 |  |
| defensive | 0.054 | 0.028 |  |
| rel_strength | -0.010 | -0.030 |  |
| liquidity | -0.041 | -0.029 |  |
| rsi | -0.034 | -0.028 |  |
| macd | -0.017 | -0.017 |  |
| adx | 0.017 | 0.026 |  |
| pct_b | -0.045 | -0.029 |  |
| atr_pct | 0.000 | 0.031 |  |
| obv_trend | -0.007 | -0.007 |  |
| stoch | -0.040 | -0.044 |  |
| ma50_dist | -0.020 | -0.036 |  |
| ma200_dist | -0.001 | -0.030 |  |
| mom_20 | -0.018 | -0.032 |  |
| mom_60 | -0.010 | -0.030 |  |
| mom_120 | -0.015 | -0.015 |  |
| vol_20 | -0.018 | 0.016 |  |

Gradient boosting vs logistic regression (stress model):

| Year | GB in-sample AUC | GB out-of-sample AUC | LR out-of-sample AUC |
|---|---|---|---|
| 2016 | 0.852 | 0.511 | 0.485 |
| 2017 | 0.834 | 0.556 | 0.566 |
| 2018 | 0.836 | 0.558 | 0.556 |
| 2019 | 0.798 | 0.474 | 0.495 |
| 2020 | 0.786 | 0.549 | 0.546 |
| 2021 | 0.759 | 0.499 | 0.477 |
| 2022 | 0.756 | 0.538 | 0.533 |
| 2023 | 0.743 | 0.584 | 0.541 |
| 2024 | 0.740 | 0.498 | 0.512 |
| 2025 | 0.730 | 0.482 | 0.425 |
| 2026 | 0.719 | 0.506 | 0.507 |

**Flags:**

- Gradient boosting fits its training data much better than new data (average AUC gap 0.25): overfitting.
- Feature 'beta' looked useful in high-volatility periods before 2022 but did not hold after.
- Feature 'down_beta' looked useful in high-volatility periods before 2022 but did not hold after.

## Limitations

- Survivorship bias: today's NIFTY 50 list is used for all years; no free point-in-time constituent list exists. This flatters every approach that holds these stocks, including the equal-weight benchmark.
- Dividends: stock prices are dividend-adjusted (total return) but NIFTY 50 (^NSEI) is a price index, so every comparison with NIFTY (and the model target, excess return over NIFTY) favours the stocks by roughly NIFTY's dividend yield, about 1.2-1.5% a year. Equal-weight NIFTY 50 is built from the same adjusted prices, so it is the like-for-like benchmark.
- Yahoo Finance data is unofficial; VIX futures term structure was not available and is not used. Placeholder bars (open = high = low = close, no volume) are dropped on loading.
- Daily data only; the drawdown trigger acts at the next open.
- One market, one decade: 2022 onward is a short hold-out.
- Long-only cash segment; no shorting or derivatives hedges.

## Compliance

Offering stock selections to customers requires SEBI Research Analyst registration, and running the algorithm for clients requires exchange empanelment through a broker and algo registration. This prototype is not offered to anyone.
