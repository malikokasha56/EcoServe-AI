from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import func

from extensions import db
from models import SalesRecord, WasteRecord, ExperimentResult, Recommendation, AnomalyRecord, Ingredient, ForecastRecord
from helpers import daily_sales_rows, best_model

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/summary", methods=["GET"])
@jwt_required()
def summary():
    # Restricted to the dataset period, so a sale entered with a later date does not hide the test period.
    last_dataset_day = (db.session.query(func.max(SalesRecord.date))
                        .filter(SalesRecord.source_restaurant_id.isnot(None)).scalar())
    rows = [r for r in daily_sales_rows() if last_dataset_day is None or r.date <= last_dataset_day]
    if not rows:
        return jsonify(message="No data. Seed the database first."), 200

    # Last seven trading days that have data, so a gap in the calendar never empties the charts.
    recent = rows[-7:]
    latest = rows[-1]
    recent_dates = [r.date for r in recent]

    best = best_model()
    forecast_map = {}
    if best is not None:
        forecast_map = {
            f.forecast_date: f.forecast_value
            for f in ForecastRecord.query.filter(
                ForecastRecord.model_type == best.label,
                ForecastRecord.forecast_date.in_(recent_dates),
            ).all()
        }
    waste_map = dict(
        db.session.query(WasteRecord.date, func.sum(WasteRecord.quantity))
        .filter(WasteRecord.source == "derived", WasteRecord.date.in_(recent_dates))
        .group_by(WasteRecord.date)
        .all()
    )

    latest_forecast = forecast_map.get(latest.date)
    overproduction_7d = sum(float(v or 0) for v in waste_map.values())
    kpis = [
        {"title": "Sales (latest day)", "value": f"{int(latest.quantity_sold or 0):,} portions",
         "note": latest.date.isoformat()},
        {"title": "Forecast (latest day)",
         "value": f"{round(latest_forecast):,} portions" if latest_forecast is not None else "n/a",
         "note": best.label if best else "no model results"},
        {"title": "Revenue (latest day)", "value": f"${float(latest.revenue or 0):,.0f}",
         "note": latest.date.isoformat()},
        {"title": "Best model error (WAPE)", "value": f"{best.wape:.1f}%" if best else "n/a",
         "note": f"{best.label}, lower is better" if best else ""},
        {"title": "Simulated overproduction", "value": f"{overproduction_7d:,.0f} portions",
         "note": "last 7 days of the test period, simulated (not measured)"},
        {"title": "Inventory health", "value": f"{_inventory_health()}/100", "note": "illustrative demo data"},
    ]

    sales_trend = [
        {
            "day": r.date.strftime("%a %d"),
            "sales": int(r.quantity_sold or 0),
            "predicted": round(forecast_map[r.date]) if forecast_map.get(r.date) is not None else None,
            "waste": round(float(waste_map.get(r.date, 0) or 0), 1),
        }
        for r in recent
    ]

    model_errors = [
        {"model": m.label, "wape": round(m.wape, 1)}
        for m in ExperimentResult.query.filter(ExperimentResult.track == "A", ExperimentResult.info_set != "reference")
        .order_by(ExperimentResult.wape).all()
    ]

    revenue = [{"day": r.date.strftime("%a %d"), "revenue": round(float(r.revenue or 0))} for r in recent]

    plan_day = db.session.query(func.max(Recommendation.date)).scalar()
    recs = [r.to_dict() for r in Recommendation.query.filter_by(date=plan_day)
            .order_by(Recommendation.recommended_quantity.desc()).limit(4).all()]

    low_stock = [
        {"name": i.name, "quantity": f"{i.stock} {i.unit}", "status": i.status}
        for i in Ingredient.query.filter(Ingredient.status.in_(["low", "critical"])).limit(3).all()
    ]
    expiring = [
        {"name": i.name, "quantity": f"{i.stock} {i.unit}", "days": i.expiry_days}
        for i in Ingredient.query.filter(Ingredient.expiry_days <= 3).limit(3).all()
    ]

    return jsonify(
        kpis=kpis,
        forecastModel=best.label if best else None,
        salesTrend=sales_trend,
        modelErrors=model_errors,
        revenue=revenue,
        recommendations=recs,
        lowStock=low_stock,
        expiring=expiring,
    )


def _inventory_health():
    total = Ingredient.query.count()
    if total == 0:
        return 100
    healthy = Ingredient.query.filter(Ingredient.status == "good").count()
    return round(healthy / total * 100)


@dashboard_bp.route("/anomaly-count", methods=["GET"])
@jwt_required()
def anomaly_count():
    count = AnomalyRecord.query.filter_by(is_anomaly=True).count()
    return jsonify(count=count)
