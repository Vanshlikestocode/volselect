import numpy as np
import pandas as pd

RF = 0.065  # annual risk-free rate (approx. Indian 91-day T-bill), used for Sharpe, Sortino and alpha


def drawdown(equity: pd.Series) -> pd.Series:
    return equity / equity.cummax() - 1


def summarize(equity: pd.Series, rf: float = RF) -> dict:
    """Headline statistics of a daily equity curve."""
    equity = equity.dropna()
    if len(equity) < 3:
        return {}
    r = equity.pct_change().dropna()
    years = max((equity.index[-1] - equity.index[0]).days / 365.25, 1e-9)
    cagr = (equity.iloc[-1] / equity.iloc[0]) ** (1 / years) - 1
    ex = r - rf / 252
    sharpe = ex.mean() / r.std() * np.sqrt(252) if r.std() > 0 else np.nan
    down = np.sqrt((np.minimum(ex, 0) ** 2).mean()) * np.sqrt(252)  # downside deviation below the risk-free rate
    mdd = drawdown(equity).min()
    return {
        "CAGR %": cagr * 100,
        "Volatility %": r.std() * np.sqrt(252) * 100,
        "Sharpe": sharpe,
        "Sortino": (ex.mean() * 252) / down if down > 0 else np.nan,
        "Max drawdown %": mdd * 100,
        "Calmar": cagr / abs(mdd) if mdd < 0 else np.nan,
        "Worst day %": r.min() * 100,
        "Days below -2% (count)": int((r <= -0.02).sum()),
        "95% daily VaR %": np.percentile(r, 5) * 100,
    }


def beta_alpha(equity: pd.Series, benchmark: pd.Series, rf: float = RF) -> dict:
    """CAPM beta and Jensen's alpha against a benchmark, from daily returns on common dates.
    Alpha is annualised: (mean excess return - beta x mean benchmark excess return) x 252."""
    r = pd.concat([equity.pct_change(), benchmark.pct_change()], axis=1, join="inner").dropna()
    if len(r) < 20:
        return {"Beta": np.nan, "Alpha % a year": np.nan}
    p, m = r.iloc[:, 0] - rf / 252, r.iloc[:, 1] - rf / 252
    beta = np.cov(p, m, ddof=1)[0, 1] / m.var(ddof=1)
    return {"Beta": beta, "Alpha % a year": (p.mean() - beta * m.mean()) * 252 * 100}


def calendar_returns(equity: pd.Series) -> pd.Series:
    """Return % for each calendar year (first year from the first available value)."""
    e = equity.dropna()
    year_end = e.groupby(e.index.year).last()
    start = pd.concat([pd.Series([e.iloc[0]], index=[year_end.index[0]]), year_end.shift(1).iloc[1:]])
    return (year_end / start - 1) * 100
