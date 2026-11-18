
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.models import Sale


def get_sales_analytics(db: Session):
    summary = db.query(
        func.count(Sale.id),
        func.coalesce(func.sum(Sale.total_amount), 0),
        func.coalesce(func.avg(Sale.total_amount), 0),
    ).one()

    best_product = (
        db.query(
            Sale.product,
            func.sum(Sale.quantity).label("total_quantity"),
        )
        .group_by(Sale.product)
        .order_by(func.sum(Sale.quantity).desc())
        .first()
    )

    return {
        "total_sales": summary[0],
        "total_revenue": float(summary[1]),
        "average_sale": round(float(summary[2]), 2),
        "best_selling_product": (
            {
                "product": best_product[0],
                "quantity_sold": int(best_product[1]),
            }
            if best_product
            else None
        ),
    }

def get_retail_analytics(db: Session):
    from backend.app.models import RetailTransaction

    # 1. Calcul des indicateurs principaux
    summary = db.query(
        func.count(RetailTransaction.id),
        func.coalesce(func.sum(RetailTransaction.total_amount), 0),
        func.coalesce(func.avg(RetailTransaction.total_amount), 0),
    ).one()

    # 2. Recherche du produit le plus vendu en quantité
    best_product = (
        db.query(
            RetailTransaction.description,
            func.sum(RetailTransaction.quantity).label("total_quantity"),
        )
        .group_by(RetailTransaction.description)
        .order_by(func.sum(RetailTransaction.quantity).desc())
        .first()
    )

    # 3. Pays avec le chiffre d'affaires le plus élevé
    best_country = (
        db.query(
            RetailTransaction.country,
            func.sum(RetailTransaction.total_amount).label("revenue"),
        )
        .group_by(RetailTransaction.country)
        .order_by(func.sum(RetailTransaction.total_amount).desc())
        .first()
    )

    return {
        "total_transactions": int(summary[0]),
        "total_revenue": round(float(summary[1]), 2),
        "average_transaction": round(float(summary[2]), 2),
        "best_selling_product": (
            {
                "product": best_product[0],
                "quantity_sold": int(best_product[1]),
            }
            if best_product
            else None
        ),
        "top_country": (
            {
                "country": best_country[0],
                "revenue": round(float(best_country[1]), 2),
            }
            if best_country
            else None
        ),
    }
