"""Market data: NSE daily OHLCV from Yahoo Finance cached as CSV (data/), and a synthetic set
for offline tests. Never present synthetic results as market results."""
from __future__ import annotations

import os
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

INDEX_TICKER = "^NSEI"
VIX_TICKER = "^INDIAVIX"

DATA_DIR = Path(os.environ.get("VOLSELECT_DATA", Path(__file__).resolve().parent.parent / "data"))


def _clean(df: pd.DataFrame) -> pd.DataFrame:
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.rename(columns=str.lower)[["open", "high", "low", "close", "volume"]]
    df.index = pd.to_datetime(df.index).tz_localize(None).normalize()
    df = df[~df.index.duplicated()].sort_index()
    df = df.replace(0, np.nan).dropna(subset=["open", "high", "low", "close"])
    return df



def read_csv(path: Path) -> pd.DataFrame | None:
    """Read a cached CSV defensively: tolerate extra header rows (older yfinance
    exports), coerce dates and numbers, drop anything unparseable."""
    try:
        df = pd.read_csv(path, index_col=0)
    except Exception:
        return None
    df.columns = [str(c).lower() for c in df.columns]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        df.index = pd.to_datetime(df.index, errors="coerce", utc=True).tz_localize(None).normalize()
    df = df[df.index.notna()]
    df = df.apply(pd.to_numeric, errors="coerce")
    if "close" not in df:
        return None
    df = df.dropna(subset=["close"])
    df = df[~df.index.duplicated()].sort_index()
    if {"open", "high", "low", "volume"} <= set(df.columns) and (df["volume"] > 0).any():
        # Yahoo writes a placeholder bar (open = high = low = close, no volume) for days a stock did not
        # trade: market holidays (e.g. 2014-04-24) and gaps in its feed (e.g. 2025-03-18). No trade was
        # possible at that price, so the row is dropped rather than traded on.
        flat = (df["open"] == df["high"]) & (df["high"] == df["low"]) & (df["low"] == df["close"])
        df = df[~(flat & ~(df["volume"] > 0))]
    return df if len(df) > 50 else None



def make_synthetic(n_symbols=12, n_days=3400, seed=7):
    """Regime-switching GBM with volatility clustering and occasional crash days.

    Produces OHLC per symbol, a synthetic 'VIX' derived from market volatility and an
    equal-weight index. For pipeline testing only.
    """
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2012-01-02", periods=n_days)
    # market regime: 0 calm, 1 stressed
    regime = np.zeros(n_days, dtype=int)
    for t in range(1, n_days):
        p_switch = 0.01 if regime[t - 1] == 0 else 0.04
        regime[t] = 1 - regime[t - 1] if rng.random() < p_switch else regime[t - 1]
    mkt_vol = np.where(regime == 1, 0.024, 0.009)
    mkt_drift = np.where(regime == 1, -0.0012, 0.0006)
    mkt = mkt_drift + mkt_vol * rng.standard_t(4, n_days) / np.sqrt(2)
    crash = rng.random(n_days) < 0.003
    mkt[crash] -= rng.uniform(0.03, 0.08, crash.sum())

    prices = {}
    for i in range(n_symbols):
        beta = rng.uniform(0.7, 1.3)
        idio = rng.normal(0.0002, rng.uniform(0.008, 0.015), n_days)
        # mild trend persistence so trend strategies have something to find
        trend = np.convolve(rng.normal(0, 0.0015, n_days), np.ones(60) / 60, mode="same")
        r = beta * mkt + idio + trend
        close = 100 * rng.uniform(0.5, 5) * np.exp(np.cumsum(r))
        gap = rng.normal(0, 0.004, n_days) + 0.5 * mkt
        open_ = close * np.exp(-r + gap)  # open sits between previous close and today
        rng_hl = np.abs(rng.normal(0, mkt_vol * 0.8 + 0.004, n_days))
        high = np.maximum(open_, close) * (1 + rng_hl)
        low = np.minimum(open_, close) * (1 - rng_hl)
        prices[f"SYN{i:02d}"] = pd.DataFrame(
            {"open": open_, "high": high, "low": low, "close": close,
             "volume": rng.integers(1e5, 1e6, n_days)}, index=dates)

    realized = pd.Series(mkt, index=dates).rolling(20, min_periods=5).std() * np.sqrt(252) * 100
    vix = (realized * 1.15 + 3).bfill().clip(lower=9)
    index_close = pd.DataFrame({k: v["close"] for k, v in prices.items()}).pct_change().mean(axis=1)
    index = pd.DataFrame({"close": 10000 * (1 + index_close.fillna(0)).cumprod()})
    return prices, vix, index
