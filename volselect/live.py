"""Live mode: a forward paper-trading record of the VolSelect portfolio against equal-weight NIFTY 50,
today's volatility regime and stock ranking, and the target portfolio for the next rebalance. Runs on
fresh prices kept apart from the frozen research data (data/ and results/ are never touched, so
verify.py stays exact).

The record starts at the close of START. Each trading day after the NSE close (GitHub Actions runs
`python live_update.py` at 18:00 IST), the same pipeline as run_vs.py is re-run on the latest prices:
regime forecast and stock model refitted on data up to the previous 31 December, weekly top-10
inverse-volatility portfolio, 0.15% cost per side. Every new day is appended to live/ledger.csv; rows
already written are never changed, and each day is a git commit, so the record cannot be edited later.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, time, timedelta, timezone
from pathlib import Path

import pandas as pd

from . import features, portfolio, regime, selection, universe

ROOT = Path(__file__).resolve().parent.parent
LIVE = Path(os.environ.get("VOLSELECT_LIVE", ROOT / "live"))
LIVE_DATA = LIVE / "data"  # downloaded prices; not committed
START = pd.Timestamp(os.environ.get("VOLSELECT_LIVE_START", "2026-11-23"))  # fixed when the record began
IST = timezone(timedelta(hours=5, minutes=30))
BAR_FINAL = time(16, 30)  # NSE closes 15:30 IST; today's daily bar is treated as final an hour later
K = 10
PORTFOLIOS = {"VolSelect (regime switch)": "regime_switch", "Equal-weight NIFTY 50": "equal_weight"}


def drop_unfinished(prices: dict, vix: pd.Series | None, nifty: pd.DataFrame | None, now: datetime | None = None):
    """Before 16:30 IST today's bar is still moving: decisions use completed days only."""
    now = now or datetime.now(IST)
    if now.time() >= BAR_FINAL:
        return prices, vix, nifty
    today = pd.Timestamp(now.date())
    cut = lambda x: None if x is None else x[x.index < today]
    return {k: cut(v) for k, v in prices.items()}, cut(vix), cut(nifty)


def compute(prices: dict, nifty: pd.DataFrame, vix: pd.Series, sectors: pd.DataFrame) -> dict:
    """Everything the live page needs, from one pass of the research pipeline."""
    nc = nifty["close"]
    last = nc.index[-1]
    first_year = min(START.year, last.year)
    f = regime.walk_forward(nc, vix, first_year)
    P = features.panel(prices, nc, f["rv10"] > f["thr"], sectors)
    wide = lambda col: P[col].unstack("ticker")
    tick = sorted(prices)
    stress = []
    for year in range(first_year, last.year + 1):  # stock model refitted each January on past data only
        models = selection.fit(P, f["y"], pd.Timestamp(f"{year - 1}-12-31"))
        stress.append(selection.score(models, P, "high", f"{year}-01-01", f"{year}-12-31"))
    idx = nc.index[nc.index >= START]
    out = {"last": last, "f": f, "P": P, "models": models, "idx": idx}
    if len(idx) >= 1:
        O = pd.DataFrame({t: prices[t]["open"].reindex(idx) for t in tick})
        C = pd.DataFrame({t: prices[t]["close"].reindex(idx) for t in tick})
        vol = wide("vol_20").reindex(index=idx, columns=tick)
        scores = {"momentum": wide("mom_120").reindex(index=idx, columns=tick),
                  "stress": pd.concat(stress).reindex(index=idx, columns=tick),
                  "equal_weight": vol.notna().astype(float).where(vol.notna())}
        reg = f["regime"].reindex(idx)
        out |= {"vol": vol, "scores": scores, "reg": reg,
                "runs": {name: portfolio.run(O, C, vol, scores, reg, policy=pol, k=K, rebalance_first=True)
                         for name, pol in PORTFOLIOS.items()}}
    return out


def _weights_on(res, d) -> dict:
    """Target weights of the most recent rebalance at or before day d."""
    days = [x for x in sorted(res.holdings) if x <= d]
    return res.holdings[days[-1]]["weights"] if days else {}


def day_rows(c: dict, nifty: pd.DataFrame, vix: pd.Series) -> pd.DataFrame:
    rows = []
    for name, res in c.get("runs", {}).items():
        eq = res.equity
        for i, d in enumerate(eq.index):
            w = _weights_on(res, d)
            rows.append({
                "date": d.date().isoformat(), "portfolio": name, "value_rs": round(float(eq.iloc[i]), 2),
                "day_return_pct": round(float(eq.iloc[i] / eq.iloc[i - 1] - 1) * 100, 4) if i else 0.0,
                "invested_pct": round(float(res.exposure.iloc[i]) * 100, 2),
                "rebalanced_at_open": "yes" if d in res.holdings else "",
                "regime_used": res.holdings[d]["scores"] if d in res.holdings else "",
                "holdings": "; ".join(f"{t.replace('.NS', '')} {x:.1%}" for t, x in sorted(w.items(), key=lambda kv: -kv[1]))
                            if name.startswith("VolSelect") else f"all {len(w)} stocks equally" if w else "",
                "nifty_close": round(float(nifty["close"].get(d, float("nan"))), 2),
                "india_vix": round(float(vix.get(d, float("nan"))), 2),
            })
    return pd.DataFrame(rows)


def next_rebalance(c: dict) -> dict:
    """Target top 10 if the portfolio were rebalanced on the latest close, against what it holds now.
    The portfolio rebalances at the open of the first session of each week."""
    f, P, last = c["f"], c["P"], c["last"]
    reg = f["regime"].iloc[-1]
    cur = P.xs(last, level="date").dropna(subset=selection.COLS)
    if reg in (None, "calm"):
        score, by = cur["mom_120"], "120-day momentum (calm market)"
    else:
        score = pd.Series(c["models"]["high"].predict_proba(cur[selection.COLS])[:, 1], index=cur.index)
        by = "resilience model (rising/high volatility)"
    target = portfolio.pick(score, cur["vol_20"], K)
    held = _weights_on(c["runs"]["VolSelect (regime switch)"], last) if c.get("runs") else {}
    rows = []
    for t in sorted(set(target.index) | set(held), key=lambda t: -target.get(t, 0)):
        a, b = held.get(t, 0.0), float(target.get(t, 0.0))
        rows.append({"stock": t.replace(".NS", ""), "now_pct": round(a * 100, 2), "target_pct": round(b * 100, 2),
                     "action": "BUY" if b and not a else "SELL" if a and not b else "HOLD"})
    friday = last.weekday() == 4
    return {"after_close_of": last.date().isoformat(), "ranked_by": by, "regime": reg,
            "executes": "at the next session's open (first session of the new week)" if friday or not held
            else "at the open of the first session of next week, if the ranking is still the same then",
            "orders": rows}


def ranking(c: dict, sectors: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Today's ranking of all 50 stocks and the regime state."""
    f, P, last = c["f"], c["P"], c["last"]
    cur = P.xs(last, level="date").dropna(subset=selection.COLS)
    sec = sectors.set_index("ticker")["Industry"]
    rank = pd.DataFrame({"stock": [t.replace(".NS", "") for t in cur.index], "sector": sec.reindex(cur.index).values,
                         "stress_score": c["models"]["high"].predict_proba(cur[selection.COLS])[:, 1],
                         "momentum_120d_pct": cur["mom_120"].values * 100, "volatility_20d_pct": cur["vol_20"].values * 100,
                         "beta": cur["beta"].values})
    reg = f["regime"].iloc[-1]
    by = "momentum_120d_pct" if reg in (None, "calm") else "stress_score"
    rank = rank.sort_values(by, ascending=False).reset_index(drop=True)
    rank.insert(0, "rank", range(1, len(rank) + 1))
    rank["in_top_10"] = rank["rank"] <= K
    state = {"date": last.date().isoformat(), "p_high": round(float(f["p_high"].iloc[-1]), 4), "regime": reg,
             "ranked_by": "120-day momentum (calm market)" if by == "momentum_120d_pct" else "resilience model (rising/high volatility)",
             "india_vix": round(float(f["vix"].iloc[-1]), 2), "nifty_realised_vol_20d": round(float(f["rv20"].iloc[-1]), 2)}
    return rank, state


def append_ledger(new: pd.DataFrame, path: Path | None = None) -> tuple[int, float]:
    """Add only (date, portfolio) rows that are not in the ledger yet; never rewrite old rows.
    Returns (rows added, largest difference between a stored value and today's recomputation)."""
    path = Path(path or LIVE / "ledger.csv")
    if path.exists():
        old = pd.read_csv(path, dtype=str, keep_default_na=False)
        have = set(zip(old.date, old.portfolio))
        mask = [(d, p) not in have for d, p in zip(new.date, new.portfolio)]
        both = new[[not x for x in mask]].merge(old[["date", "portfolio", "value_rs"]], on=["date", "portfolio"], suffixes=("", "_old"))
        drift = float((both.value_rs.astype(float) - both.value_rs_old.astype(float)).abs().max()) if len(both) else 0.0
        add = new[mask]
        out = pd.concat([old, add.astype(str)], ignore_index=True)
    else:
        add, drift, out = new, 0.0, new
    path.parent.mkdir(parents=True, exist_ok=True)
    out.sort_values(["date", "portfolio"], kind="stable").to_csv(path, index=False)
    return len(add), drift


def write_json(obj, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, default=str), encoding="utf-8")
