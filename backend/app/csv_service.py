
import pandas as pd
from sqlalchemy.orm import Session

from backend.app.models import Sale


def import_sales_csv(file, db: Session):
    df = pd.read_csv(file)

    required_columns = {"product", "quantity", "unit_price"}

    if not required_columns.issubset(df.columns):
        missing = required_columns - set(df.columns)
        raise ValueError(
            f"Missing required columns: {', '.join(sorted(missing))}"
        )

    if df.empty:
        raise ValueError("CSV file is empty")

    df = df[["product", "quantity", "unit_price"]].copy()

    df["product"] = df["product"].astype("string").str.strip()
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["unit_price"] = pd.to_numeric(
        df["unit_price"], errors="coerce"
    )

    if (
        df["product"].isna().any()
        or df["product"].eq("").any()
        or df["quantity"].isna().any()
        or df["unit_price"].isna().any()
    ):
        raise ValueError("CSV contains missing or invalid values")

    if (
        (df["quantity"] <= 0).any()
        or (df["unit_price"] <= 0).any()
        or (df["quantity"] % 1 != 0).any()
    ):
        raise ValueError("Quantity and price must be positive")

    sales = [
        Sale(
            product=row.product,
            quantity=int(row.quantity),
            unit_price=float(row.unit_price),
            total_amount=int(row.quantity) * float(row.unit_price),
        )
        for row in df.itertuples(index=False)
    ]

    try:
        db.add_all(sales)
        db.commit()
    except Exception:
        db.rollback()
        raise

    return {"imported_rows": len(sales)}
