"""Live record: flat until it starts, append-only ledger, today's bar ignored until final."""
from datetime import datetime

import pandas as pd

from volselect import live
from volselect.data import make_synthetic

P, V, I = make_synthetic(n_symbols=4, n_days=400, seed=2)


def test_ledger_is_append_only(tmp_path):
    rows = pd.DataFrame({"date": [d.date().isoformat() for d in I.index[:60]], "portfolio": "p",
                         "value_rs": (1e6 * I["close"].iloc[:60] / I["close"].iloc[0]).round(2).values})
    path = tmp_path / "ledger.csv"
    assert live.append_ledger(rows.iloc[:30], path)[0] == 30
    changed = rows.copy()
    changed.loc[:29, "value_rs"] += 500  # a later recomputation (e.g. revised prices) disagrees with stored rows
    added, drift = live.append_ledger(changed, path)
    stored = pd.read_csv(path)
    assert added == 30 and len(stored) == 60 and abs(drift - 500) < 1e-6
    assert (stored.value_rs.iloc[:30].round(2) == rows.value_rs.iloc[:30].round(2)).all()  # kept as recorded


def test_todays_bar_is_ignored_until_it_is_final():
    day = V.index[-1]
    morning = datetime(day.year, day.month, day.day, 11, 0, tzinfo=live.IST)
    evening = datetime(day.year, day.month, day.day, 18, 0, tzinfo=live.IST)
    p, v, i = live.drop_unfinished(P, V, I, now=morning)
    assert v.index[-1] < day and i.index[-1] < day and all(df.index[-1] < day for df in p.values())
    assert live.drop_unfinished(P, V, I, now=evening)[1].index[-1] == day


def test_first_rebalance_is_the_morning_after_the_start():
    from volselect import portfolio
    idx = I.index[300:]
    O = pd.DataFrame({s: P[s]["open"].reindex(idx) for s in P})
    C = pd.DataFrame({s: P[s]["close"].reindex(idx) for s in P})
    vol = C.pct_change().rolling(20, min_periods=1).std().fillna(0.2)
    sc = {"equal_weight": vol.notna().astype(float)}
    r = portfolio.run(O, C, vol, sc, None, policy="equal_weight", k=4, rebalance_first=True)
    assert min(r.holdings) == idx[1]
    plain = portfolio.run(O, C, vol, sc, None, policy="equal_weight", k=4)
    assert min(plain.holdings) >= idx[1]
