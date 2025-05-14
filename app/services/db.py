import os
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    BigInteger,
    Float,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Retrieve database URL from environment or default to SQLite file
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./portfolio.db")

# Create engine and session factory
engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True,
)
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)

# Base declarative class
Base = declarative_base()

class SyncMeta(Base):
    """
    Stores metadata about last synchronization timestamps per source.
    """
    __tablename__ = "sync_meta"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, nullable=False)
    value = Column(BigInteger, default=0, nullable=False)

class Deposit(Base):
    """
    Represents a Binance deposit transaction.
    """
    __tablename__ = "deposits"

    txId = Column(String, primary_key=True, index=True)
    asset = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    time = Column(BigInteger, nullable=False)

class Withdrawal(Base):
    """
    Represents a Binance withdrawal transaction.
    """
    __tablename__ = "withdrawals"

    txId = Column(String, primary_key=True, index=True)
    asset = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    time = Column(BigInteger, nullable=False)

class Trade(Base):
    """
    Represents a Binance trade (order fill).
    """
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, autoincrement=True)
    orderId = Column(Integer, index=True, nullable=False)
    symbol = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    qty = Column(Float, nullable=False)
    time = Column(BigInteger, nullable=False)


def init_db():
    """
    Initialize database by creating all tables.
    Call this once at application startup.
    """
    Base.metadata.create_all(bind=engine)