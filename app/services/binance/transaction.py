from services.db import Deposit, Withdrawal, SessionLocal
from sqlalchemy.exc import SQLAlchemyError


def sync_deposits(deposits: list, session=None) -> None:
    """
    Upsert deposit records into the database.

    :param deposits: List of deposit dicts from Binance API.
    :param session: Optional SQLAlchemy session. If not provided, a new session is created and closed internally.
    """
    own_session = False
    if session is None:
        session = SessionLocal()
        own_session = True
    try:
        for dep in deposits:
            tx_id = dep.get("txId")
            if not tx_id:
                continue
            # Check for existing record
            record = session.query(Deposit).filter_by(txId=tx_id).first()
            data = {
                "txId": tx_id,
                "asset": dep.get("asset"),
                "amount": float(dep.get("amount", 0)),
                "time": int(dep.get("time", 0)),
            }
            if record:
                # Update existing
                for key, value in data.items():
                    setattr(record, key, value)
            else:
                # Insert new
                session.add(Deposit(**data))
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        raise
    finally:
        if own_session:
            session.close()


def sync_withdrawals(withdrawals: list, session=None) -> None:
    """
    Upsert withdrawal records into the database.

    :param withdrawals: List of withdrawal dicts from Binance API.
    :param session: Optional SQLAlchemy session. If not provided, a new session is created and closed internally.
    """
    own_session = False
    if session is None:
        session = SessionLocal()
        own_session = True
    try:
        for wd in withdrawals:
            tx_id = wd.get("txId")
            if not tx_id:
                continue
            record = session.query(Withdrawal).filter_by(txId=tx_id).first()
            data = {
                "txId": tx_id,
                "asset": wd.get("asset"),
                "amount": float(wd.get("amount", 0)),
                "time": int(wd.get("applyTime", wd.get("time", 0))),
            }
            if record:
                for key, value in data.items():
                    setattr(record, key, value)
            else:
                session.add(Withdrawal(**data))
        session.commit()
    except SQLAlchemyError:
        session.rollback()
        raise
    finally:
        if own_session:
            session.close()


__all__ = ["sync_deposits", "sync_withdrawals"]
