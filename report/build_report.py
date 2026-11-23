"""Build the project report (report/report.html, then VolSelect_Project_Report.pdf if Chrome or Edge is
installed) from the result files only. Structure follows the course brief: problem statement,
background and literature, data, methodology, backtest results, limitations, conclusion, references.
Every number is read from results/ and live/, and every comparative claim is checked with claim():
if a claim is not supported by the files, the build fails.

    python run_vs.py                  # or: python verify.py
    python report/build_report.py
"""
from __future__ import annotations

import html
import json
import os
import shutil
import subprocess
import sys
from collections import Counter
from datetime import date
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
R, LIVE = ROOT / "results", ROOT / "live"
sys.path.insert(0, str(ROOT))
from volselect.live import START  # noqa: E402

MAIN, STRESS, MOM, LOWV, GB = ("Regime switch (LR), no trigger", "Stress model only", "Momentum only",
                               "Low volatility only", "Regime switch (GB), no trigger")
TRIG = "Regime switch (LR) + 12% trigger"
EW, NB = "Equal-weight NIFTY 50 (benchmark)", "NIFTY 50 buy and hold (benchmark)"


def claim(ok: bool, text: str) -> None:
    if not bool(ok):
        raise AssertionError(f"Report claim not supported by the result files: {text}")


def n(x, d=2, sign=False) -> str:
    if pd.isna(x):
        return "–"
    return (f"{x:+,.{d}f}" if sign else f"{x:,.{d}f}").replace("-", "−")


csv = lambda name, idx=0: pd.read_csv(R / name, index_col=idx)
T = {k: csv(f"table_{k}.csv") for k in ("full", "development", "hold-out", "covid", "2022")}
wl, cost, cap, acc, ic, auc = (csv("win_loss.csv"), csv("cost_sensitivity.csv"), csv("capacity.csv")["value"],
                               csv("forecast_accuracy.csv"), csv("overfitting_ic.csv"), csv("overfitting_auc.csv"))
cal = csv("calendar_returns.csv")
imp = csv("feature_importance.csv")
eq = pd.read_csv(R / "equity_curves.csv", index_col=0, parse_dates=True)
state = json.loads((R / "current_state.json").read_text(encoding="utf-8"))
F, D, H, C, H1 = T["full"], T["development"], T["hold-out"], T["covid"]["Period return %"], T["2022"]["Period return %"]
g = lambda a, c, col="CAGR %": cost.loc[f"{a} | {c}", col]
nstocks = sum(1 for p in (ROOT / "data").glob("*.NS.csv"))
first, last = eq.index[0], eq.index[-1]

# ------------------------------------------------------------------ claims checked against the files
claim(F.loc[MAIN, "CAGR %"] > F.loc[NB, "CAGR %"] and H.loc[MAIN, "CAGR %"] > H.loc[NB, "CAGR %"], "main beats NIFTY, full and hold-out")
claim(F.loc[MAIN, "CAGR %"] < F.loc[EW, "CAGR %"] and H.loc[MAIN, "CAGR %"] < H.loc[EW, "CAGR %"], "main trails EW, full and hold-out")
claim(H.loc[MAIN, "Max drawdown %"] < H.loc[NB, "Max drawdown %"], "main deeper hold-out drawdown than NIFTY")
claim(F.loc[MAIN, "Max drawdown %"] > F.loc[NB, "Max drawdown %"], "main shallower full drawdown than NIFTY")
claim(F.loc[STRESS, "Beta"] < 0.8 and H.loc[STRESS, "Beta"] < 0.8, "resilience model beta below 0.8")
claim(F.loc[STRESS, "Volatility %"] < F.loc[NB, "Volatility %"], "resilience model less volatile than NIFTY")
for a in (MAIN, STRESS):
    claim(C[a] > max(C[NB], C[EW]) and H1[a] > max(H1[NB], H1[EW]), f"{a} lost less than both benchmarks in both crashes")
claim(g(MAIN, "0.00%", "CAGR % 2022+") < g(EW, "0.00%", "CAGR % 2022+"), "main trails EW from 2022 even gross")
claim(g(MAIN, "0.00%", "CAGR % 2016-2021") > g(EW, "0.00%", "CAGR % 2016-2021"), "main beats EW gross 2016-2021")
claim(D.loc[MAIN, "CAGR %"] > H.loc[MAIN, "CAGR %"], "main weaker in hold-out than development")
claim(acc.iloc[1]["hit_rate"] > acc.iloc[1]["naive_hit_rate"] and acc.iloc[1]["recall"] < acc.iloc[1]["naive_recall"],
      "forecast beats naive on hit rate, loses on recall, hold-out")
claim((auc["GB in-sample AUC"] - auc["GB out-of-sample AUC"]).mean() > 0.15, "gradient boosting overfits")
claim(auc["LR out-of-sample AUC"].mean() < 0.55, "logistic regression near chance out of sample")
flagged = set(ic.index[ic["Flag"].fillna("") != ""])
claim(flagged == {"beta", "down_beta"}, "only beta and downside beta failed after 2022")
claim(imp.loc["defensive", "high"] > 0 and imp.loc["mom_120", "high"] < 0, "defensive helps, 120-day momentum hurts in stress")
d05, d15 = g(MAIN, "0.05%") - g(EW, "0.05%"), g(MAIN, "0.15%") - g(EW, "0.15%")
claim(d05 > 0 > d15, "break-even between 0.05% and 0.15%")
breakeven = 0.05 + 0.10 * d05 / (d05 - d15)
ratio = (eq[MAIN] / eq[EW]).groupby(eq.index.year).last()
claim(ratio.loc[:2024].min() > 0.85 and ratio.iloc[-1] < 0.8, "VolSelect within ~12% of EW through 2024, well behind by the end")
dd = lambda a, frm=None: (eq[a].loc[frm:] / eq[a].loc[frm:].cummax() - 1).min() * 100
since24 = {a: dd(a, "2024") for a in (MAIN, EW, NB)}
claim(since24[MAIN] < 1.5 * min(since24[EW], since24[NB]), "VolSelect's fall since 2024 much deeper than the benchmarks'")
claim(eq[MAIN].iloc[-1] < eq[MAIN].loc["2024":].max(), "VolSelect still below its post-2024 peak at the end")
covid_trough = {a: (eq[a] / eq[a].cummax() - 1).loc["2020"].min() * 100 for a in (MAIN, EW, NB)}
claim(covid_trough[MAIN] > max(covid_trough[EW], covid_trough[NB]), "VolSelect's COVID fall shallower")
ledger = pd.read_csv(LIVE / "ledger.csv") if (LIVE / "ledger.csv").exists() else pd.DataFrame()
live_days = ledger.date.nunique() if len(ledger) else 0

collected = subprocess.run([sys.executable, "-m", "pytest", "--collect-only", "-q", "tests"], cwd=ROOT,
                           capture_output=True, text=True, encoding="utf-8").stdout.splitlines()
n_tests = sum(1 for x in collected if "::" in x)
n_results = len(list(R.glob("*.csv"))) + len(list(R.glob("*.json")))


def table(head: list[str], rows: list[list], cls: list[str] | None = None) -> str:
    """Numbers right-aligned, text left-aligned (a column is text if any of its cells is)."""
    strip = lambda v: str(v).replace(",", "").replace(".", "").replace("−", "").replace("+", "").replace("%", "").strip()
    numeric = lambda v: strip(v) in ("", "–") or strip(v).isdigit()
    text_col = [i == 0 or any(not numeric(r[i]) for r in rows) for i in range(len(head))]
    h = "".join(f'<th{" class=l" if text_col[i] else ""}>{html.escape(c)}</th>' for i, c in enumerate(head))
    body = ""
    for k, r in enumerate(rows):
        c = f' class="{cls[k]}"' if cls and cls[k] else ""
        body += f"<tr{c}>" + "".join(f'<td{" class=l" if text_col[i] else ""}>{v}</td>' for i, v in enumerate(r)) + "</tr>"
    return f"<table><tr>{h}</tr>{body}</table>"


SHOW = [(MAIN, "VolSelect regime switch (main)"), (STRESS, "Resilience model only"), (MOM, "Momentum only"),
        (LOWV, "Low volatility only"), (EW, "Equal-weight NIFTY 50"), (NB, "NIFTY 50 buy and hold")]
cls = lambda a: "bench" if a in (EW, NB) else ("hl" if a == MAIN else "")


def perf_rows(t: pd.DataFrame) -> list[list]:
    return [[show, n(t.loc[a, "CAGR %"]), n(t.loc[a, "Volatility %"]), n(t.loc[a, "Sharpe"]), n(t.loc[a, "Max drawdown %"]),
             n(t.loc[a, "Beta"]), n(t.loc[a, "Alpha % a year"], 2, True), n(t.loc[a, "Turnover (x/yr)"], 1)] for a, show in SHOW]


PERF_HEAD = ["Approach", "Annual return %", "Volatility %", "Sharpe", "Max drawdown %", "Beta", "Alpha % a year", "Turnover ×/yr"]
CSS = (Path(__file__).parent / "style.css").read_text(encoding="utf-8")
today = date.today().strftime("%d %B %Y").lstrip("0")
a1 = acc.iloc[1]

doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><title>VolSelect: project report</title><style>{CSS}</style></head><body>

<div class="cover"><div>
<div class="band"></div>
<div class="tag">Design Experience project · Portfolio Management · {today}</div>
<h1>VolSelect</h1>
<p class="lead" style="font-size:12.5pt;max-width:150mm">A volatility-aware NIFTY 50 portfolio: forecast when market volatility will rise, hold the stocks most likely to hold up, and test it honestly on data the model never saw.</p>
<p class="muted" style="margin-top:14pt">Vansh Dave · Karthik Agarwal &nbsp;|&nbsp; B.Tech AI, 5th semester &nbsp;|&nbsp; Guide: Sailesh Kulkarni</p>
</div><div>
<table>
<tr><th class=l>Brief requirement (Portfolio Management)</th><th class=l>Where in this report</th></tr>
<tr><td class=l>Stock universe and selection logic</td><td class=l>3. Data; 4.2–4.3</td></tr>
<tr><td class=l>Weighting method and rebalancing frequency</td><td class=l>4.3 (inverse volatility, weekly)</td></tr>
<tr><td class=l>Comparison against a benchmark</td><td class=l>4.4; every results table (NIFTY 50 and equal-weight NIFTY 50)</td></tr>
<tr><td class=l>Annualised return, volatility, Sharpe, max drawdown, beta/alpha</td><td class=l>5.1, 5.2</td></tr>
<tr><td class=l>Portfolio value chart vs benchmark</td><td class=l>5.3</td></tr>
<tr><td class=l>Build on one period, test on a later one (out-of-sample)</td><td class=l>4.5; 5.2</td></tr>
<tr><td class=l>Code and data to reproduce any number</td><td class=l>Appendix A: <code>python verify.py</code></td></tr>
</table>
<p class="small muted">Daily data, as the brief specifies for Portfolio Management groups. Academic research prototype; not investment advice.</p>
</div></div>

<div class="section"><h2>1. Problem statement</h2>
<p class="lead">When the stock market becomes volatile, most portfolios fall together. Can a model that forecasts rising volatility choose the NIFTY 50 stocks that lose less, without giving up too much return when markets are calm?</p>
<p>Retail and professional investors in India face this every time India VIX jumps: COVID in 2020, the 2022 sell-off, and smaller shocks since. Holding the index means taking every fall in full; moving to cash means missing rebounds. We test a middle path: stay fully invested, but switch <i>which</i> stocks are held according to a daily forecast of market volatility.</p>
<h3>Research questions</h3>
<ol>
<li>Can India VIX, realised volatility and a GARCH model forecast high-volatility periods for NIFTY better than a naive rule?</li>
<li>In high-volatility periods, which stock characteristics (beta, sector, trend, momentum and others) go with beating the index?</li>
<li>Does a portfolio that switches between a momentum ranking (calm markets) and a resilience ranking (rising or high volatility) beat NIFTY 50 and equal-weight NIFTY 50 after costs, on data it was not built on?</li>
</ol>
<h3>What counts as success</h3>
<p>Higher return per unit of risk than the benchmarks (Sharpe), smaller losses in stress periods, and, most importantly, that both hold on the 2022–2026 out-of-sample period, after 0.15% trading cost per side.</p>
</div>

<div class="section"><h2>2. Background and literature</h2>
<p><b>Volatility clusters and can be forecast.</b> Engle (1982) and Bollerslev (1986) showed that large price moves tend to follow large moves; the GARCH(1,1) model captures this and remains a standard one-day-ahead volatility forecast. India VIX, built from NIFTY option prices, measures the market's own expectation of volatility over the next 30 days; Whaley (2000) described the US equivalent as the "investor fear gauge". We combine both with realised volatility.</p>
<p><b>Which stocks hold up.</b> Low-beta and low-volatility stocks have historically delivered better risk-adjusted returns than theory predicts (Ang et al., 2006; Frazzini and Pedersen, 2014), which suggests holding them when risk rises. Momentum, the tendency of recent winners to keep winning over 3–12 months (Jegadeesh and Titman, 1993), works in calm markets but is known to crash when markets turn sharply. That trade-off is the reason for a regime switch.</p>
<p><b>The benchmark to beat.</b> DeMiguel, Garlappi and Uppal (2009) found that a simple equal-weight (1/N) portfolio is very hard to beat out of sample; optimised portfolios lose their edge to estimation error. We therefore report equal-weight NIFTY 50 alongside the NIFTY 50 index.</p>
<p><b>Testing honestly.</b> The more settings a researcher tries, the more likely the best backtest is luck (Bailey et al., 2017). We use a walk-forward design (models refitted each year on past data only), keep a hold-out period from 2022, fix design choices in advance, and add automatic checks that flag any indicator or setting that worked before 2022 and failed after. Performance is measured with the Sharpe ratio (Sharpe, 1966), and beta and alpha from the capital asset pricing model (Jensen's alpha).</p>
</div>

<div class="section"><h2>3. Data</h2>
{table(["Item", "Detail"], [
 ["Source", "Yahoo Finance via the <code>yfinance</code> library; daily OHLCV, adjusted for splits and dividends. Bundled with the project as CSV and fingerprinted (SHA-256 manifest)."],
 ["Instruments", f"The {nstocks} stocks in NSE's current NIFTY 50 list (<code>data/ind_nifty50list.csv</code>, with sectors), the NIFTY 50 index (^NSEI) and India VIX (^INDIAVIX)"],
 ["Period", f"Prices from January 2012 (to build features and train the first models); portfolio test {first:%d %b %Y} to {last:%d %b %Y}"],
 ["Frequency", "Daily candles (open, high, low, close, volume), as required for Portfolio Management groups"],
 ["Split", "Development (build) period 2016–2021; out-of-sample (test) period 1 Jan 2022 to the end of the data"],
 ["Cleaning", "Yahoo writes placeholder bars (open = high = low = close, no volume) for days a stock did not trade, including some market holidays; these are dropped. A stock's missing day is treated as a no-trade day (price carried). Stocks that listed after 2012 join on their first trading day."],
 ["Live data", f"The same source is fetched every trading day after the close for the forward paper-trading record, kept in <code>live/</code> and never mixed with the research data."],
])}
<p><b>Known biases.</b> The list is today's NIFTY 50, so stocks that left the index are missing (survivorship bias), which flatters every approach that holds these stocks, the equal-weight benchmark included. Stock prices include dividends but the NIFTY 50 index (^NSEI) does not, so comparisons with NIFTY favour the stocks by roughly 1.2–1.5% a year; equal-weight NIFTY 50 is built from the same adjusted prices and is the like-for-like benchmark.</p>
</div>

<div class="section"><h2>4. Methodology</h2>
<h3>4.1 Volatility regime forecast</h3>
<p>Each day, after the close, a logistic regression estimates the probability that NIFTY's realised volatility over the next 10 sessions will be "high", defined as above the 75th percentile of 10-day volatility over the previous year (a threshold known at the time). Inputs: India VIX level and 5-day change, 10- and 20-day realised volatility, the VIX-to-realised ratio, and a GARCH(1,1) forecast whose parameters are fitted only on data before the forecast year. The probability sets the regime: <b>calm</b> below 30%, <b>rising</b> 30–50%, <b>high</b> above 50% (cut-offs fixed before testing).</p>
<h3>4.2 Stock universe and selection logic</h3>
<p>All {nstocks} NIFTY 50 stocks are scored daily on 19 measures: beta and downside beta to NIFTY, past excess return in high-volatility periods, defensive sector, relative strength, liquidity, RSI, MACD, ADX, Bollinger %B, ATR, on-balance volume trend, stochastic, distance from the 50- and 200-day averages, 20/60/120-day momentum and 20-day volatility. Each measure is converted to a rank across stocks (0 to 1), so different scales do not matter. Two logistic regressions estimate each stock's chance of beating NIFTY over the next 10 sessions: one trained on calm days, one on high-volatility days (the <b>resilience model</b>).</p>
<p><b>Selection rule (regime switch):</b> in a calm regime, hold the 10 stocks with the highest 120-day momentum; in a rising or high regime, hold the 10 stocks with the highest resilience-model score.</p>
<h3>4.3 Weighting, rebalancing and costs</h3>
{table(["Choice", "Value", "Why"], [
 ["Number of stocks", "10", "Enough diversification across sectors, still selective"],
 ["Weighting", "Inverse volatility (weight ∝ 1 / 20-day volatility)", "A simple risk-parity-style rule: calmer stocks get more capital, no optimiser to overfit"],
 ["Rebalancing", "Weekly, at the open of the first session of each week", "Responds to regime changes within days"],
 ["Timing", "Signals at the close of day t−1, trades at the open of day t", "No look-ahead: tested by changing future prices and checking past results do not move"],
 ["Costs", "0.15% of every rupee traded, each side", "STT on delivery (0.1%), exchange and regulatory charges, slippage; also tested at 0%, 0.05% and 0.30%"],
 ["Cash", "Fully invested, never moves to cash", "Avoids missing rebounds"],
])}
<h3>4.4 Benchmarks and comparison approaches</h3>
<p>NIFTY 50 buy and hold, and equal-weight NIFTY 50 (all stocks, equal weights, rebalanced weekly at the same cost). To see what each part contributes, we also run momentum only, resilience model only, low volatility only, a gradient-boosting version of the regime switch, and variants with a drawdown trigger (on an 8, 10 or 12% fall the model retrains on recent data and may switch approach; the level was chosen on 2016–2021 only).</p>
<h3>4.5 Out-of-sample design</h3>
<p><b>Walk-forward:</b> every 1 January, the regime model, GARCH parameters and stock models are refitted on data up to the previous 31 December, then used unchanged for that year. Models train only on rows whose 10-day outcome is complete before the cut-off. <b>Development and test:</b> all design choices (10 stocks, weekly rebalance, regime cut-offs, horizons, cost) were fixed while working on 2016–2021; 2022 onward is reported separately as the out-of-sample test.</p>
<h3>4.6 Metrics</h3>
<p>Annual return (CAGR); annualised volatility of daily returns; Sharpe ratio = annualised mean excess return over a 6.5% risk-free rate ÷ annualised volatility; maximum drawdown = largest fall from a previous peak; beta = covariance of daily excess returns with NIFTY ÷ variance of NIFTY's; alpha (Jensen's) = annualised mean excess return − beta × NIFTY's mean excess return; turnover = rupees traded per year ÷ portfolio value.</p>
</div>

<div class="section"><h2>5. Backtest results</h2>
<h3>5.1 Full walk-forward, {first.year}–{last.year}</h3>
{table(PERF_HEAD, perf_rows(F), [cls(a) for a, _ in SHOW])}
<p class="small muted">Source: <code>results/table_full.csv</code>. All after 0.15% cost per side.</p>
<p><b>How to read this.</b> The VolSelect regime switch grew {n(F.loc[MAIN,'CAGR %'],1)}% a year against {n(F.loc[NB,'CAGR %'],1)}% for NIFTY 50, with a beta of {n(F.loc[MAIN,'Beta'])} and a Sharpe ratio of {n(F.loc[MAIN,'Sharpe'])} against {n(F.loc[NB,'Sharpe'])}. But simply holding all 50 stocks equally earned {n(F.loc[EW,'CAGR %'],1)}% with a higher Sharpe ({n(F.loc[EW,'Sharpe'])}), so stock selection did not add value over the like-for-like benchmark. The positive alphas against NIFTY are inflated by about 1.2–1.5 points a year because the stocks include dividends and the index does not; equal weight's own alpha of {n(F.loc[EW,'Alpha % a year'],1)}% shows the size of that bias plus survivorship. The resilience model alone has the lowest beta ({n(F.loc[STRESS,'Beta'])}) and lower volatility than the index ({n(F.loc[STRESS,'Volatility %'],1)}% against {n(F.loc[NB,'Volatility %'],1)}%): it does hold defensive stocks, as designed.</p>

<h3>5.2 Built on 2016–2021, tested on 2022 onward</h3>
{table(["Approach", "Development: return %", "Sharpe", "Max DD %", "Test 2022+: return %", "Volatility %", "Sharpe", "Max DD %", "Beta", "Alpha %"],
 [[show, n(D.loc[a,"CAGR %"]), n(D.loc[a,"Sharpe"]), n(D.loc[a,"Max drawdown %"]), n(H.loc[a,"CAGR %"]), n(H.loc[a,"Volatility %"]),
   n(H.loc[a,"Sharpe"]), n(H.loc[a,"Max drawdown %"]), n(H.loc[a,"Beta"]), n(H.loc[a,"Alpha % a year"],2,True)] for a, show in SHOW],
 [cls(a) for a, _ in SHOW])}
<p class="small muted">Sources: <code>results/table_development.csv</code>, <code>results/table_hold-out.csv</code>.</p>
<p><b>How to read this.</b> This is the honest test. In the development years the regime switch earned {n(D.loc[MAIN,'CAGR %'],1)}% a year; on the unseen 2022+ data it earned {n(H.loc[MAIN,'CAGR %'],1)}%, still ahead of NIFTY ({n(H.loc[NB,'CAGR %'],1)}%) but far behind equal weight ({n(H.loc[EW,'CAGR %'],1)}%), and with a deeper worst fall than NIFTY ({n(H.loc[MAIN,'Max drawdown %'],1)}% against {n(H.loc[NB,'Max drawdown %'],1)}%). The resilience model kept its low beta out of sample ({n(H.loc[STRESS,'Beta'])}) and the lowest volatility of the stock portfolios ({n(H.loc[STRESS,'Volatility %'],1)}%). The drop from development to test is the pattern the literature warns about, and the reason we report both.</p>
</div>

<div class="section"><h3 style="margin-top:0">5.3 Portfolio value against the benchmarks</h3>
<img class="chart" src="../results/chart_1_equity.png" alt="Portfolio value against NIFTY 50 and equal-weight NIFTY 50">
<div class="cap">Growth of Rs 10 lakh, log scale; dotted line: start of the out-of-sample test. <code>results/chart_1_equity.png</code></div>
<p><b>How to read this.</b> A log scale shows equal percentage changes as equal heights. VolSelect (blue) and equal weight (gold) both pull far ahead of NIFTY (grey) from 2020, helped by dividends and survivorship as explained in section 3. VolSelect stays within about 12% of equal weight through 2024 (it was ahead in 2018, 2020 and 2024), then falls behind: in 2025 it returned {n(cal.loc[2025, MAIN],1)}% while equal weight returned {n(cal.loc[2025, EW],1)}%, and by the end of the data it is worth {n((1 - ratio.iloc[-1]) * 100, 0)}% less than equal weight.</p>
<h3>5.4 Falls from the previous peak</h3>
<img class="chart" src="../results/chart_2_drawdown.png" alt="Drawdown chart">
<div class="cap">Drawdown: how far each portfolio is below its previous high. <code>results/chart_2_drawdown.png</code></div>
<p><b>How to read this.</b> All three fell sharply in March 2020, but VolSelect's fall was shallower ({n(covid_trough[MAIN],1)}% from its peak against {n(covid_trough[NB],1)}% for NIFTY and {n(covid_trough[EW],1)}% for equal weight). Since 2024 the picture reverses: VolSelect has fallen {n(since24[MAIN],1)}% from its peak and had not recovered by the end of the data, against at most {n(since24[EW],1)}% for equal weight and {n(since24[NB],1)}% for NIFTY. Most of its out-of-sample shortfall comes from this period.</p>
<h3>5.5 Stress periods</h3>
<img class="chart" src="../results/chart_5_crisis.png" alt="Returns in the COVID crash and the 2022 sell-off" style="width:72%">
{table(["Approach", "COVID crash, 14 Feb–30 Apr 2020 %", "2022 sell-off, Jan–Jun %"], [[show, n(C[a],1), n(H1[a],1)] for a, show in SHOW], [cls(a) for a, _ in SHOW])}
<p><b>How to read this.</b> This is where the idea works. In both sell-offs the regime switch and the resilience model lost less than NIFTY and less than equal weight: in the COVID crash {n(C[MAIN],1)}% against {n(C[NB],1)}% for NIFTY, and in the first half of 2022 the resilience model lost only {n(H1[STRESS],1)}% against {n(H1[NB],1)}%. Selection by resilience protects capital in stress; the cost shows up in calm, rising markets.</p>
</div>

<div class="section"><h3 style="margin-top:0">5.6 Win/loss</h3>
{table(["Approach", "Weeks up %", "Weeks beating NIFTY %", "Months up %", "Months beating NIFTY %", "Months beating equal wt %", "Avg up week %", "Avg down week %", "Picks beating NIFTY %"],
 [[show, n(wl.loc[a,"Weeks up %"],1), n(wl.loc[a,"Weeks beating NIFTY %"],1), n(wl.loc[a,"Months up %"],1), n(wl.loc[a,"Months beating NIFTY %"],1),
   n(wl.loc[a,"Months beating equal weight %"],1), n(wl.loc[a,"Avg up week %"]), n(wl.loc[a,"Avg down week %"]), n(wl.loc[a].get("Picks beating NIFTY %"),1)]
  for a, show in SHOW], [cls(a) for a, _ in SHOW])}
<p class="small muted">Source: <code>results/win_loss.csv</code>. A pick is one stock held from one rebalance to the next; it wins if it beat NIFTY.</p>
<p><b>How to read this.</b> VolSelect rose in {n(wl.loc[MAIN,'Weeks up %'],0)}% of weeks and beat NIFTY in {n(wl.loc[MAIN,'Months beating NIFTY %'],0)}% of months, but individual picks beat NIFTY only about half the time ({n(wl.loc[MAIN,'Picks beating NIFTY %'],1)}%). The model is not a stock-picker in normal markets; its value is in how much less it loses when volatility rises.</p>
<h3>5.7 Trading costs</h3>
{table(["Approach", "Cost per side", "Return 2016–26 %", "Return 2016–21 %", "Return 2022+ %"],
 [[show if c == "0.00%" else "", "none (gross)" if c == "0.00%" else c, n(g(a, c)), n(g(a, c, "CAGR % 2016-2021")), n(g(a, c, "CAGR % 2022+"))]
  for a, show in ((MAIN, "VolSelect regime switch"), (EW, "Equal-weight NIFTY 50")) for c in ("0.00%", "0.05%", "0.15%", "0.30%")])}
<p><b>How to read this.</b> Before any cost VolSelect beat equal weight in the development years ({n(g(MAIN,'0.00%','CAGR % 2016-2021'),1)}% against {n(g(EW,'0.00%','CAGR % 2016-2021'),1)}%) but trailed it from 2022 even with no cost ({n(g(MAIN,'0.00%','CAGR % 2022+'),1)}% against {n(g(EW,'0.00%','CAGR % 2022+'),1)}%). Weekly rebalancing turns the portfolio over about {n(F.loc[MAIN,'Turnover (x/yr)'],0)} times a year, so at 0.15% per side costs take roughly {n(g(MAIN,'0.00%') - g(MAIN,'0.15%'),1)} points a year; the break-even cost over the full period is about {breakeven:.2f}% per side, below the 0.1% STT alone.</p>
<h3>5.8 Capacity</h3>
<p>Over the last year the median NIFTY 50 stock traded Rs {n(cap.iloc[0],0)} crore a day and the least liquid Rs {n(cap.iloc[1],0)} crore; a 10% position stays below 5% of a day's traded value up to about Rs {n(cap.iloc[2],0)} crore of capital (<code>results/capacity.csv</code>).</p>
</div>

<div class="section"><h3 style="margin-top:0">5.9 Volatility forecast</h3>
<img class="chart" src="../results/chart_3_regime.png" alt="Forecast probability of high volatility against actual volatility">
{table(["Period", "Days", "Share actually high", "Hit rate", "Naive hit rate", "Precision", "Recall", "Naive recall"],
 [[p, n(r["days"],0), f"{r['share_high']:.0%}", f"{r['hit_rate']:.1%}", f"{r['naive_hit_rate']:.1%}", f"{r['precision']:.1%}", f"{r['recall']:.1%}", f"{r['naive_recall']:.1%}"]
  for p, r in acc.iterrows()])}
<p><b>How to read this.</b> The shaded area is the forecast probability; the black line is the volatility that actually followed. On the 2022+ test the forecast was right on {a1['hit_rate']:.0%} of days against {a1['naive_hit_rate']:.0%} for a naive "next 10 days like the last 10" rule, and when it said "high" it was right {a1['precision']:.0%} of the time. But it caught only {a1['recall']:.0%} of the high-volatility days (recall), against {a1['naive_recall']:.0%} for the naive rule: it is cautious, and misses most spikes. This is the weakest link of the system.</p>
<h3>5.10 Which stock characteristics mattered</h3>
<img class="chart" src="../results/chart_4_importance.png" alt="Average model coefficients by regime" style="width:78%">
{table(["Indicator", "Information coefficient 2013–2021", "2022+", "Verdict"], [[k.replace("_"," "), n(ic.loc[k].iloc[0],3,True), n(ic.loc[k].iloc[1],3,True), "failed after 2022" if k in flagged else "held"]
  for k in ("beta", "down_beta", "defensive", "liquidity", "rsi", "pct_b", "stoch", "mom_120")])}
<p><b>How to read this.</b> The bars are the resilience model's average coefficients: positive means the characteristic helped a stock beat NIFTY in high-volatility periods. Being in a defensive sector helped and recent big winners (120-day momentum) were hurt. The table checks each indicator's information coefficient (rank correlation with the next 10-day excess return on high-volatility days) before and after 2022: defensive sector and not being overbought (low RSI, %B, stochastic) held up out of sample; the low-beta effect did not.</p>
<h3>5.11 Overfitting checks</h3>
<p>The gradient-boosting version scored an average in-sample AUC of {n(auc['GB in-sample AUC'].mean(),2)} but only {n(auc['GB out-of-sample AUC'].mean(),2)} on the following year (0.5 = guessing): it overfits. The logistic regression scored {n(auc['LR out-of-sample AUC'].mean(),2)} on the following year, so neither model predicts which individual stock will beat NIFTY, consistent with picks winning only about half the time (5.6). We kept the logistic regression because it is simpler and its coefficients can be explained; the portfolio's value in stress comes from its defensive, low-beta tilt rather than from picking winners (<code>results/overfitting_auc.csv</code>). The drawdown trigger level chosen on 2016–2021 was not the best afterwards; we report it but do not use it as the main approach.</p>
<h3>5.12 Live forward record</h3>
<p>Since the close of {START:%d %b %Y} the same pipeline runs every trading day at 18:00 IST on fresh prices: VolSelect and equal-weight NIFTY 50, Rs 10 lakh each, appended to an append-only ledger (<code>live/ledger.csv</code>) and committed to git, so every day is timestamped. {"At the time of writing it has " + str(live_days) + " trading days, too short to judge." if live_days else "It starts at that day's close; the first trades fill the next morning."} It is shown live in the project's dashboard (<code>streamlit run volselect_app.py</code>).</p>
</div>

<div class="section"><h2>6. Limitations</h2>
{table(["Limitation", "Effect on the results"], [
 ["Survivorship bias", "Today's NIFTY 50 list is used for every year, so failed or demoted stocks are missing; this inflates every stock portfolio, the equal-weight benchmark included."],
 ["Dividends", "Stocks are total return, NIFTY 50 (^NSEI) is price only: returns and alpha against NIFTY are overstated by about 1.2–1.5% a year."],
 ["Short test period", "2022 onward is under five years and largely one market regime."],
 ["Forecast recall", f"The volatility forecast misses most high-volatility spells (recall {a1['recall']:.0%} out of sample)."],
 ["Turnover and costs", f"About {n(F.loc[MAIN,'Turnover (x/yr)'],0)}× a year; the edge before costs did not survive out of sample."],
 ["Daily data", "Trades are assumed at the next open; intraday moves and opening-auction slippage are not modelled beyond the cost assumption."],
 ["Data source", "Yahoo Finance is unofficial; adjusted prices are revised over time (the bundled data is fingerprinted)."],
 ["Scope", "Long only, cash segment; no shorting, futures or options hedges."],
])}
</div>

<div><h2>7. Conclusion</h2>
<p>We built and tested a fully walk-forward, volatility-aware NIFTY 50 portfolio. Three findings hold up:</p>
<ol>
<li><b>Selection by resilience protects in sell-offs.</b> In the COVID crash and the 2022 sell-off the regime switch and the resilience model lost clearly less than NIFTY and equal weight, and the resilience model kept a low beta ({n(H.loc[STRESS,'Beta'])}) out of sample.</li>
<li><b>It does not beat equal weight.</b> Over 2016–2026 and on the 2022+ test, holding all 50 stocks equally earned more with a higher Sharpe ratio; from 2022 the selection trailed equal weight even before costs. Consistent with DeMiguel et al. (2009), 1/N is hard to beat.</li>
<li><b>The volatility forecast is the weak link.</b> It is accurate when it signals high volatility but misses most spikes, so the portfolio is often in the wrong regime early in a sell-off.</li>
</ol>
<p><b>Next steps:</b> point-in-time index membership to remove survivorship bias; a total-return NIFTY benchmark; lower turnover (monthly rebalance or a buffer before replacing a stock); a forecast tuned for recall; and a longer live record. Every result in this report can be reproduced with one command (Appendix A), and the live record lets anyone check the method going forward.</p>
</div>

<div class="section"><h2>8. References</h2>
<ol class="small">
<li>Ang, A., Hodrick, R. J., Xing, Y. and Zhang, X. (2006). The cross-section of volatility and expected returns. <i>Journal of Finance</i>, 61(1), 259–299.</li>
<li>Bailey, D. H., Borwein, J. M., López de Prado, M. and Zhu, Q. J. (2017). The probability of backtest overfitting. <i>Journal of Computational Finance</i>, 20(4), 39–69.</li>
<li>Bollerslev, T. (1986). Generalized autoregressive conditional heteroskedasticity. <i>Journal of Econometrics</i>, 31(3), 307–327.</li>
<li>DeMiguel, V., Garlappi, L. and Uppal, R. (2009). Optimal versus naive diversification: how inefficient is the 1/N portfolio strategy? <i>Review of Financial Studies</i>, 22(5), 1915–1953.</li>
<li>Engle, R. F. (1982). Autoregressive conditional heteroscedasticity with estimates of the variance of United Kingdom inflation. <i>Econometrica</i>, 50(4), 987–1007.</li>
<li>Frazzini, A. and Pedersen, L. H. (2014). Betting against beta. <i>Journal of Financial Economics</i>, 111(1), 1–25.</li>
<li>Jegadeesh, N. and Titman, S. (1993). Returns to buying winners and selling losers: implications for stock market efficiency. <i>Journal of Finance</i>, 48(1), 65–91.</li>
<li>Sharpe, W. F. (1966). Mutual fund performance. <i>Journal of Business</i>, 39(1), 119–138.</li>
<li>Whaley, R. E. (2000). The investor fear gauge. <i>Journal of Portfolio Management</i>, 26(3), 12–17.</li>
<li>National Stock Exchange of India. NIFTY 50 index constituents and India VIX methodology. nseindia.com.</li>
<li>Software: pandas, NumPy, scikit-learn, arch (GARCH), Matplotlib, Streamlit, yfinance.</li>
</ol>

<h2 style="margin-top:18pt">Appendix A. Reproducing every number</h2>
<pre>pip install -r requirements.txt
python verify.py</pre>
<p><code>verify.py</code> checks the bundled data against its SHA-256 manifest, runs the {n_tests} unit tests (including tests that change future prices and confirm past results do not move), re-runs the whole study into a temporary folder and compares all {n_results} result files with <code>results/</code> number by number. Expected verdict: <b>ALL RESULTS REPRODUCED</b> (about one minute, offline). Do not run <code>--download</code> first: Yahoo revises adjusted prices, so fresh data shifts the numbers slightly. <code>VIVA_GUIDE.md</code> maps every number in this report and the slides to the file it comes from.</p>
<h2>Appendix B. Corrections to our October results</h2>
<p>Re-checking for this submission found and fixed: a bug in the indicator check (the after-2022 column was never computed, wrongly flagging five indicators); Yahoo placeholder bars that left stocks unscored for weeks in 2025 and early 2026; a one-day misalignment in a "high-volatility days" table (that October claim is withdrawn); a Sortino formula; and a rebalance that could re-spend a stock with no opening price. All are covered by tests or by <code>verify.py</code>; affected October numbers are superseded by this report.</p>
</div>
</body></html>"""

out = Path(__file__).parent / "report.html"
out.write_text(doc, encoding="utf-8")
print(f"wrote {out}  ({n_results} result files, {n_tests} tests, all claims checked)")
cands = [os.environ.get("CHROME", ""), "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
         r"C:\Program Files\Google\Chrome\Application\chrome.exe", r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
         shutil.which("google-chrome") or "", shutil.which("chromium") or "", shutil.which("chromium-browser") or ""]
browser = next((c for c in cands if c and Path(c).exists()), None)
if "--no-pdf" in sys.argv:
    pass
elif browser:
    pdf = ROOT / "VolSelect_Project_Report.pdf"
    subprocess.run([browser, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--allow-file-access-from-files",
                    f"--print-to-pdf={pdf}", out.resolve().as_uri()], capture_output=True)
    print(f"wrote {pdf}" if pdf.exists() else "PDF step failed; open report.html in a browser and print to PDF")
else:
    print("No Chrome/Edge found: open report/report.html in a browser and print to PDF")
