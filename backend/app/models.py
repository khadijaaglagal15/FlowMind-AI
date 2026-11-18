
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func

from backend.app.database import engine
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    product = Column(String(100), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    sale_date = Column(DateTime(timezone=True), server_default=func.now())

class RetailTransaction(Base):
    __tablename__ = "retail_transactions"

    id = Column(Integer, primary_key=True, index=True)
    invoice_no = Column(String(20), nullable=False, index=True)
    stock_code = Column(String(20), nullable=False)
    description = Column(String(255), nullable=False)
    quantity = Column(Integer, nullable=False)
    invoice_date = Column(DateTime, nullable=False, index=True)
    unit_price = Column(Float, nullable=False)
    country = Column(String(100), nullable=False)
    total_amount = Column(Float, nullable=False)
