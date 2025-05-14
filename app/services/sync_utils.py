# app/services/sync_utils.py

from .db import SessionLocal, SyncMeta


def get_last_sync(key: str = "binance") -> int:
    """
    Récupère le timestamp (en ms) du dernier sync pour la clé donnée.
    Si aucune entrée n'existe, initialise à 0.
    """
    db = SessionLocal()
    try:
        meta = db.query(SyncMeta).filter_by(key=key).first()
        if meta is None:
            meta = SyncMeta(key=key, value=0)
            db.add(meta)
            db.commit()
        return meta.value
    finally:
        db.close()


def set_last_sync(ts: int, key: str = "binance") -> None:
    """
    Met à jour le timestamp (en ms) du dernier sync pour la clé donnée.
    """
    db = SessionLocal()
    try:
        meta = db.query(SyncMeta).filter_by(key=key).first()
        if meta is None:
            # Au cas où get_last_sync n'aurait pas encore été appelé
            meta = SyncMeta(key=key, value=ts)
            db.add(meta)
        else:
            meta.value = ts
        db.commit()
    finally:
        db.close()