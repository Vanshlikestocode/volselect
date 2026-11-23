"""Collect every number the slide deck uses from results/ into slides/deck_data.json, so the deck is
built from the same files that verify.py checks.   python slides/deck_data.py && node slides/build_deck.js"""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
R = ROOT / "results"
MAIN, STRESS, MOM = "Regime switch (LR), no trigger", "Stress model only", "Momentum only"
EW, NB = "Equal-weight NIFTY 50 (benchmark)", "NIFTY 50 buy and hold (benchmark)"
KEYS = {"volselect": MAIN, "resilience": STRESS, "momentum": MOM, "equal_weight": EW, "nifty": NB}

T = {k: pd.read_csv(R / f"table_{k}.csv", index_col=0) for k in ("full", "development", "hold-out", "covid", "2022")}
cost = pd.read_csv(R / "cost_sensitivity.csv", index_col=0)
acc = pd.read_csv(R / "forecast_accuracy.csv", index_col=0)
ic = pd.read_csv(R / "overfitting_ic.csv", index_col=0)
wl = pd.read_csv(R / "win_loss.csv", index_col=0)
eq = pd.read_csv(R / "equity_curves.csv", index_col=0, parse_dates=True)
weekly = eq[[MAIN, EW, NB]].resample("W-FRI").last().dropna() / 1e5

r = lambda x, d=2: None if pd.isna(x) else round(float(x), d)
data = {
    "period": {"start": eq.index[0].strftime("%b %Y"), "end": eq.index[-1].strftime("%d %b %Y"), "stocks": sum(1 for _ in (ROOT / "data").glob("*.NS.csv"))},
    "perf": {per: {k: {c: r(T[per].loc[a, c]) for c in ("CAGR %", "Volatility %", "Sharpe", "Max drawdown %", "Beta", "Alpha % a year", "Turnover (x/yr)")}
                   for k, a in KEYS.items()} for per in ("full", "development", "hold-out")},
    "crash": {per: {k: r(T[per].loc[a, "Period return %"], 1) for k, a in KEYS.items()} for per in ("covid", "2022")},
    "gross": {k: {p: r(cost.loc[f"{a} | 0.00%", c], 1) for p, c in (("full", "CAGR %"), ("dev", "CAGR % 2016-2021"), ("test", "CAGR % 2022+"))}
              for k, a in (("volselect", MAIN), ("equal_weight", EW))},
    "forecast": {k: r(acc.iloc[1][k] * 100, 1) for k in ("hit_rate", "naive_hit_rate", "precision", "recall", "naive_recall")},
    "ic": {k: [r(ic.loc[k].iloc[0], 3), r(ic.loc[k].iloc[1], 3), str(ic.loc[k, "Flag"]) if pd.notna(ic.loc[k, "Flag"]) else ""]
           for k in ("defensive", "rsi", "stoch", "beta", "down_beta")},
    "weeks_up": r(wl.loc[MAIN, "Weeks up %"], 1), "picks_beat": r(wl.loc[MAIN, "Picks beating NIFTY %"], 1),
    "chart": {"labels": [d.strftime("%b %Y") for d in weekly.index],
              "volselect": [round(x, 3) for x in weekly[MAIN]], "equal_weight": [round(x, 3) for x in weekly[EW]],
              "nifty": [round(x, 3) for x in weekly[NB]]},
}
(Path(__file__).parent / "deck_data.json").write_text(json.dumps(data, indent=1), encoding="utf-8")
print("wrote slides/deck_data.json")
