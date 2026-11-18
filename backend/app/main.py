
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.forecasting import forecast_revenue
from fastapi import HTTPException

from backend.app.database import SessionLocal
from backend.app.models import Sale
from backend.app.schemas import SaleCreate, SaleResponse
from backend.app.analytics import get_sales_analytics
from backend.app.analytics import get_retail_analytics
from fastapi import UploadFile, File
from backend.app.csv_service import import_sales_csv
from backend.app.models import RetailTransaction
app = FastAPI(
    title="FlowMind AI",
    description="Business Intelligence and Automation API",
    version="1.0.0",
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home():
    return {
        "message": "Welcome to FlowMind AI!",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/sales", response_model=SaleResponse, status_code=201)
def create_sale(sale: SaleCreate, db: Session = Depends(get_db)):
    new_sale = Sale(
        product=sale.product,
        quantity=sale.quantity,
        unit_price=sale.unit_price,
        total_amount=sale.quantity * sale.unit_price,
    )

    db.add(new_sale)
    db.commit()
    db.refresh(new_sale)

    return new_sale


@app.get("/sales", response_model=list[SaleResponse])
def get_sales(db: Session = Depends(get_db)):
    return db.query(Sale).order_by(Sale.id.desc()).all()
@app.get("/analytics/sales")
def sales_analytics(db: Session = Depends(get_db)):
    return get_sales_analytics(db)

@app.post("/sales/import-csv")
def import_sales(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a CSV file",
        )

    try:
        result = import_sales_csv(file.file, db)

        return {
            "message": "CSV imported successfully",
            **result,
        }

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Could not import CSV",
        )

    finally:
        file.file.close()


@app.get("/analytics/retail")
def retail_analytics(db: Session = Depends(get_db)):
    return get_retail_analytics(db)


@app.get("/retail/transactions")
def get_retail_transactions(
    limit: int = 1000,
    db: Session = Depends(get_db),
):
    limit = max(1, min(limit, 5000))

    transactions = (
        db.query(RetailTransaction)
        .order_by(RetailTransaction.id.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": transaction.id,
            "invoice_no": transaction.invoice_no,
            "stock_code": transaction.stock_code,
            "description": transaction.description,
            "quantity": transaction.quantity,
            "invoice_date": (
                transaction.invoice_date.isoformat()
                if transaction.invoice_date
                else None
            ),
            "unit_price": float(transaction.unit_price),
            "country": transaction.country,
            "total_amount": float(transaction.total_amount),
        }
        for transaction in transactions
    ]


@app.get("/analytics/forecast")
def get_revenue_forecast(
    days: int = 7,
    db: Session = Depends(get_db),
):
    try:
        return forecast_revenue(db, days=days)
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )
