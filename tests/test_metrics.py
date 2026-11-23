import numpy as np
import pandas as pd

from volselect.metrics import RF, beta_alpha, calendar_returns, summarize

IDX = pd.bdate_range("2020-01-01", periods=600)
RNG = np.random.default_rng(0)
M = pd.Series(RNG.normal(0.0004, 0.01, len(IDX)), index=IDX)


def test_beta_and_alpha_recover_a_known_portfolio():
    """Portfolio excess return = 1.5 x market excess return + 0.02% a day: beta 1.5, alpha 0.02% x 252."""
    rf = RF / 252
    p = rf + 1.5 * (M - rf) + 0.0002
    out = beta_alpha((1 + p).cumprod(), (1 + M).cumprod())
    assert abs(out["Beta"] - 1.5) < 1e-9
    assert abs(out["Alpha % a year"] - 0.0002 * 252 * 100) < 1e-6


def test_benchmark_against_itself():
    e = (1 + M).cumprod()
    out = beta_alpha(e, e)
    assert abs(out["Beta"] - 1) < 1e-12 and abs(out["Alpha % a year"]) < 1e-9


def test_summary_and_calendar_returns():
    e = pd.Series([100.0, 110.0, 121.0], index=pd.to_datetime(["2020-01-02", "2020-12-31", "2021-12-31"]))
    r = calendar_returns(e)
    assert abs(r[2020] - 10) < 1e-9 and abs(r[2021] - 10) < 1e-9
    s = summarize((1 + M).cumprod())
    assert abs(s["Volatility %"] - M.iloc[1:].std() * np.sqrt(252) * 100) < 1e-9  # the first return is undefined
    assert s["Max drawdown %"] <= 0
