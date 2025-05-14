from sqlalchemy import create_engine, Column, Integer, String, BigInteger, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///portfolio.db")

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

class SyncMeta(Base):
    __tablename__ = "sync_meta"
    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, index=True)
    value = Column(BigInteger, default=0)

class Deposit(Base):
    __tablename__ = "deposits"
    txId = Column(String, primary_key=True, index=True)
    asset = Column(String)
    amount = Column(Float)
    time = Column(BigInteger)

class Withdrawal(Base):
    __tablename__ = "withdrawals"
    txId = Column(String, primary_key=True, index=True)
    asset = Column(String)
    amount = Column(Float)
    time = Column(BigInteger)

class Trade(Base):
    __tablename__ = "trades"
    id = Column(Integer, primary_key=True, autoincrement=True)
    orderId = Column(Integer, index=True)
    symbol = Column(String)
    price = Column(Float)
    qty = Column(Float)
    time = Column(BigInteger)

# Au démarrage de l’app
def init_db():
    Base.metadata.create_all(bind=engine)