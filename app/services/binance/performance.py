# app/services/binance/performance.py

import pandas as pd
from sqlalchemy.orm import Session
from datetime import datetime
from ..db import Deposit, Withdrawal, Trade
from ...utils.pricing import get_price_at
from ...utils.utils import from_timestamp


def _load_transactions(db: Session):
    """
    Fetch all deposits, withdrawals and trades from the DB.
    Returns a list of (timestamp_ms, asset, net_amount) tuples.
    """
    txs = []

    # deposits add to balance
    for d in db.query(Deposit).all():
        txs.append((d.time, d.asset,  float(d.amount)))

    # withdrawals subtract from balance
    for w in db.query(Withdrawal).all():
        txs.append((w.time, w.asset, -float(w.amount)))

    # trades: assume Trade.qty is positive for buy, negative for sell
    # and Trade.symbol is like 'BTCUSDT'
    for t in db.query(Trade).all():
        base = t.symbol.replace("USDT", "")
        qty  = float(t.qty)
        # buying base spends USDT, selling base adds USDT
        txs.append((t.time, base,           qty))
        txs.append((t.time, "USDT",       -qty * float(t.price)))

    return txs


def build_value_timeseries(db: Session) -> pd.Series:
    """
    Reconstructs the portfolio's total USDT value at each transaction timestamp.
    Returns a pandas Series indexed by datetime, with total_value in USDT.
    """
    txs = _load_transactions(db)
    # sort by time
    txs.sort(key=lambda x: x[0])

    # track running balances per asset
    balances = {}
    records = []

    for ts, asset, amt in txs:
        balances[asset] = balances.get(asset, 0.0) + amt

        # compute total USDT-equivalent value after this tx
        total = 0.0
        for a, bal in balances.items():
            if bal == 0:
                continue
            if a == "USDT" or a == "BUSD":
                total += bal
            else:
                price = get_price_at(f"{a}USDT", ts)
                total += bal * (price or 0.0)
        dt = from_timestamp(ts)
        records.append((dt, total))

    # collapse to one value per timestamp (in case of multiple txs at same ts)
    df = pd.DataFrame(records, columns=["datetime", "value"])
    df = df.groupby("datetime")["value"].last()
    # ensure a monotonic time index
    df = df.sort_index()
    return df


def compute_returns(ts: pd.Series) -> pd.Series:
    """
    Simple periodic returns: r_t = (V_t / V_{t-1}) - 1
    """
    return ts.pct_change().fillna(0.0)


def compute_cumulative_returns(returns: pd.Series) -> pd.Series:
    """
    Cumulative returns series: (1 + r_1) * (1 + r_2) * … - 1
    """
    return (1 + returns).cumprod() - 1


def compute_max_drawdown(cum_rets: pd.Series) -> float:
    """
    Maximum drawdown: max peak-to-trough percentage drop.
    """
    running_max = cum_rets.cummax()
    drawdowns  = (cum_rets - running_max) / running_max
    return float(drawdowns.min())


def compute_cagr(ts: pd.Series) -> float:
    """
    Compound Annual Growth Rate.
    CAGR = (V_end / V_start)^(1/years) - 1
    """
    if len(ts) < 2:
        return 0.0
    start, end = ts.iloc[0], ts.iloc[-1]
    days = (ts.index[-1] - ts.index[0]).days
    if days == 0:
        return 0.0
    years = days / 365.0
    return float((end / start) ** (1.0 / years) - 1.0)


def get_performance(db: Session) -> dict:
    """
    High-level summary of key performance metrics.
    Returns a dict with series and scalars.
    """
    ts       = build_value_timeseries(db)
    rets     = compute_returns(ts)
    cum_rets = compute_cumulative_returns(rets)

    return {
        "value_timeseries":   ts,             # pd.Series[datetime -> USDT value]
        "returns":            rets,           # pd.Series of simple returns
        "cumulative":         cum_rets,       # pd.Series of cum. returns
        "max_drawdown":       compute_max_drawdown(cum_rets),
        "cagr":               compute_cagr(ts),
    }
