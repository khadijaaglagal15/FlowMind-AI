
from datetime import timedelta
from sklearn.ensemble import HistGradientBoostingRegressor
import numpy as np
import pandas as pd
from sqlalchemy import func
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

from backend.app.models import RetailTransaction


FEATURES = [
    "lag_1",
    "lag_7",
    "rolling_7",
    "day_of_week",
    "month",
    "day_of_month",
]


def get_daily_revenue(db):
    """Récupérer le chiffre d'affaires agrégé par jour depuis PostgreSQL."""

    rows = (
        db.query(
            func.date(RetailTransaction.invoice_date).label("day"),
            func.sum(RetailTransaction.total_amount).label("revenue"),
        )
        .filter(RetailTransaction.invoice_date.isnot(None))
        .group_by(func.date(RetailTransaction.invoice_date))
        .order_by(func.date(RetailTransaction.invoice_date))
        .all()
    )

    if not rows:
        raise ValueError("Aucune donnée de vente disponible.")

    df = pd.DataFrame(
        [(row.day, float(row.revenue)) for row in rows],
        columns=["date", "revenue"],
    )

    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").sort_index()

    # Créer une ligne pour chaque jour, y compris les jours sans vente.
    full_dates = pd.date_range(df.index.min(), df.index.max(), freq="D")
    df = df.reindex(full_dates, fill_value=0)
    df.index.name = "date"

    return df


def create_features(df):
    """Construire les variables explicatives à partir des jours précédents."""

    data = df.copy()

    data["lag_1"] = data["revenue"].shift(1)
    data["lag_7"] = data["revenue"].shift(7)

    # Moyenne des 7 jours précédents, sans inclure le jour à prédire.
    data["rolling_7"] = (
        data["revenue"].shift(1).rolling(window=7).mean()
    )

    data["day_of_week"] = data.index.dayofweek
    data["month"] = data.index.month
    data["day_of_month"] = data.index.day

    return data.dropna()


def forecast_revenue(db, days=7):
    """Évaluer le modèle puis prévoir les prochains jours."""

    if not 1 <= days <= 30:
        raise ValueError("L'horizon doit être compris entre 1 et 30 jours.")

    daily = get_daily_revenue(db)

    if len(daily) < 45:
        raise ValueError(
            "Il faut au moins 45 jours de données pour entraîner le modèle."
        )

    supervised = create_features(daily)

    X = supervised[FEATURES]
    y = supervised["revenue"]

    # Évaluation chronologique : les 30 derniers jours servent au test.
    test_size = min(30, max(7, len(supervised) // 5))
    split_index = len(supervised) - test_size

    X_train, X_test = X.iloc[:split_index], X.iloc[split_index:]
    y_train, y_test = y.iloc[:split_index], y.iloc[split_index:]

    evaluation_model = RandomForestRegressor(
        n_estimators=200,
        random_state=42,
        n_jobs=-1,
    )
    evaluation_model.fit(X_train, y_train)

    test_predictions = np.maximum(
        0, evaluation_model.predict(X_test)
    )

    model_mae = mean_absolute_error(y_test, test_predictions)

    # Baseline : prévoir le chiffre d'affaires du même jour de la semaine
    # précédente. Cela donne un point de comparaison simple.
    baseline_predictions = X_test["lag_7"].to_numpy()
    baseline_mae = mean_absolute_error(y_test, baseline_predictions)
        

    gradient_model = HistGradientBoostingRegressor(
        max_iter=200,
        learning_rate=0.05,
        max_leaf_nodes=15,
        random_state=42,
    )

    gradient_model.fit(X_train, y_train)

    gradient_predictions = np.maximum(
        0, gradient_model.predict(X_test)
    )

    gradient_mae = mean_absolute_error(
        y_test, gradient_predictions
    )

    # Entraîner le modèle final sur toutes les données disponibles.
    model = RandomForestRegressor(
        n_estimators=200,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X, y)

    history = daily["revenue"].astype(float).tolist()
    last_date = daily.index.max()
    forecasts = []

    # Prévision récursive : chaque prédiction alimente la suivante.
    for step in range(1, days + 1):
        forecast_date = last_date + timedelta(days=step)

        features = pd.DataFrame(
            [{
                "lag_1": history[-1],
                "lag_7": history[-7],
                "rolling_7": float(np.mean(history[-7:])),
                "day_of_week": forecast_date.dayofweek,
                "month": forecast_date.month,
                "day_of_month": forecast_date.day,
            }],
            columns=FEATURES,
        )

        prediction = max(0.0, float(model.predict(features)[0]))
        history.append(prediction)

        forecasts.append({
            "date": forecast_date.date().isoformat(),
            "predicted_revenue": round(prediction, 2),
        })

    return {
        "data_from": daily.index.min().date().isoformat(),
        "data_through": last_date.date().isoformat(),
        "forecast_days": days,
                "evaluation": {
            "test_days": int(test_size),
            "random_forest_mae": round(float(model_mae), 2),
            "baseline_mae": round(float(baseline_mae), 2),
            "gradient_boosting_mae": round(float(gradient_mae), 2),
        },
        "forecast": forecasts,
    }
