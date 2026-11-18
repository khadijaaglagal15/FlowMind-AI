
from pathlib import Path

import pandas as pd
from sqlalchemy import insert

from backend.app.database import engine
from backend.app.models import RetailTransaction

CSV_PATH = Path("data/sales_real.csv")
CHUNK_SIZE = 10_000


def main():
    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"Fichier introuvable : {CSV_PATH.resolve()}"
        )

    total_imported = 0

    for chunk in pd.read_csv(CSV_PATH, chunksize=CHUNK_SIZE):
        chunk = chunk.rename(
            columns={
                "InvoiceNo": "invoice_no",
                "StockCode": "stock_code",
                "Description": "description",
                "Quantity": "quantity",
                "InvoiceDate": "invoice_date",
                "UnitPrice": "unit_price",
                "Country": "country",
                "TotalAmount": "total_amount",
            }
        )

        chunk["invoice_date"] = pd.to_datetime(
            chunk["invoice_date"], errors="raise"
        )

        records = chunk.to_dict(orient="records")

        with engine.begin() as connection:
            connection.execute(
                insert(RetailTransaction),
                records,
            )

        total_imported += len(records)
        print(f"Transactions importées : {total_imported:,}")

    print(f"\nImport terminé : {total_imported:,} transactions.")


if __name__ == "__main__":
    main()
