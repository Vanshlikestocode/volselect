"""Daily live update: fetch the latest NSE prices, extend the forward paper-trading record (VolSelect
against equal-weight NIFTY 50), and write today's regime, ranking and target portfolio. Run after the
market closes; GitHub Actions does it every weekday at 18:00 IST (.github/workflows/live-update.yml)
and commits the result, so each day is timestamped.

    python live_update.py               # download fresh prices, then update live/
    python live_update.py --no-download # reuse the prices already in live/data/

Writes to live/ only. The research data (data/) and results (results/) are never touched.
Paper trading only: no orders are sent anywhere.
"""
from __future__ import annotations

import argparse
from datetime import datetime

from volselect import live, universe


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-download", action="store_true")
    a = ap.parse_args()
    if not a.no_download:
        print("Downloading latest prices ...")
        universe.download(start="2012-01-01", force=True, folder=live.LIVE_DATA)  # the models train on the full history

    now = datetime.now(live.IST)
    prices, nifty, vix = universe.load(live.LIVE_DATA)
    prices, vix, nifty = live.drop_unfinished(prices, vix, nifty, now=now)
    sectors = universe.constituents()
    c = live.compute(prices, nifty, vix, sectors)

    rows = live.day_rows(c, nifty, vix)
    added, drift = live.append_ledger(rows) if len(rows) else (0, 0.0)
    rank, state = live.ranking(c, sectors)
    rank.round(4).to_csv(live.LIVE / "ranking.csv", index=False)
    live.write_json(state, live.LIVE / "regime.json")
    live.write_json(live.next_rebalance(c), live.LIVE / "plan.json")
    live.write_json({"updated_at_ist": now.strftime("%Y-%m-%d %H:%M"), "last_completed_session": c["last"].date().isoformat(),
                     "record_starts": live.START.date().isoformat(), "rows_added": added,
                     "largest_restatement_rs": round(drift, 2)}, live.LIVE / "status.json")
    print(f"Last completed session {c['last'].date()}. Ledger rows added: {added}. "
          f"Regime: {state['regime']} (chance of high volatility {state['p_high']:.0%}).")
    if drift > 1:
        print(f"Note: Yahoo revised past prices; recomputed values differ from the stored record by up to Rs {drift:,.0f}. "
              "Stored rows are kept as recorded.")


if __name__ == "__main__":
    main()
