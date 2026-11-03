from datetime import datetime

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import func

from extensions import db
from models import WasteRecord, SalesRecord, AnomalyRecord
from helpers import default_restaurant_id, to_number, ValidationError, json_object

waste_bp = Blueprint("waste", __name__)


@waste_bp.route("", methods=["GET"])
@waste_bp.route("/", methods=["GET"])
@jwt_required()
def list_waste():
    query = WasteRecord.query
    date_str = request.args.get("date")
    if date_str:
        try:
            day = datetime.strptime(date_str, "%Y-%m-%d").date()
            query = query.filter(WasteRecord.date == day)
        except ValueError:
            return jsonify(message="date must be YYYY-MM-DD"), 400
    records = query.order_by(WasteRecord.date.desc(), WasteRecord.id.desc()).limit(100).all()
    return jsonify(waste=[r.to_dict() for r in records])


@waste_bp.route("", methods=["POST"])
@waste_bp.route("/", methods=["POST"])
@jwt_required()
def create_waste():
    data = json_object()
    date_str = data.get("date")
    try:
        day = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else datetime.utcnow().date()
    except ValueError:
        return jsonify(message="date must be YYYY-MM-DD"), 400

    food_item = (data.get("foodItem") or "").strip()
    if not food_item:
        raise ValidationError("Please select a food item")
    quantity = to_number(data.get("quantity"), "Quantity", float, minimum=0)
    if quantity <= 0:
        raise ValidationError("Quantity must be greater than 0")

    record = WasteRecord(
        restaurant_id=default_restaurant_id(),
        date=day,
        waste_category=data.get("reason") or "Preparation",
        menu_item_name=food_item,
        quantity=quantity,
        unit=data.get("unit") or "kg",
        cost_estimate=to_number(data.get("costImpact"), "Cost impact", float, minimum=0, default=0.0),
        reason=data.get("reason"),
        notes=data.get("notes"),
        source="manual",
    )
    db.session.add(record)
    db.session.commit()
    return jsonify(waste=record.to_dict()), 201


# Two separate sources that are never added together: "estimated" overproduction from the preparation
# simulation (in portions, not measured) and "logged" entries typed in by users (kg, g, L or units).
@waste_bp.route("/overview", methods=["GET"])
@jwt_required()
def overview():
    est = WasteRecord.query.filter_by(source="derived")
    est_portions = float(est.with_entities(func.coalesce(func.sum(WasteRecord.quantity), 0)).scalar() or 0)
    est_cost = float(est.with_entities(func.coalesce(func.sum(WasteRecord.cost_estimate), 0)).scalar() or 0)
    est_days = est.with_entities(func.count(func.distinct(WasteRecord.date))).scalar() or 0
    est_note = est.with_entities(WasteRecord.notes).first()

    daily_rows = (
        est.with_entities(WasteRecord.date, func.sum(WasteRecord.quantity))
        .group_by(WasteRecord.date)
        .order_by(WasteRecord.date.desc())
        .limit(14)
        .all()
    )
    est_items = [
        {"name": n, "portions": round(float(q or 0)), "cost": round(float(c or 0))}
        for n, q, c in est.with_entities(
            WasteRecord.menu_item_name, func.sum(WasteRecord.quantity), func.sum(WasteRecord.cost_estimate)
        ).group_by(WasteRecord.menu_item_name).order_by(func.sum(WasteRecord.quantity).desc()).all()
    ]

    logged = WasteRecord.query.filter_by(source="manual")
    by_reason = [
        {"name": (r or "unspecified").replace("-", " ").capitalize(), "entries": int(n), "cost": round(float(c or 0), 2)}
        for r, n, c in logged.with_entities(
            WasteRecord.reason, func.count(WasteRecord.id), func.sum(WasteRecord.cost_estimate)
        ).group_by(WasteRecord.reason).all()
    ]
    by_item = [
        {"name": n, "entries": int(k), "cost": round(float(c or 0), 2)}
        for n, k, c in logged.with_entities(
            WasteRecord.menu_item_name, func.count(WasteRecord.id), func.sum(WasteRecord.cost_estimate)
        ).group_by(WasteRecord.menu_item_name).order_by(func.sum(WasteRecord.cost_estimate).desc()).limit(5).all()
    ]

    return jsonify(
        estimated={
            "portions": round(est_portions, 1),
            "cost": round(est_cost, 2),
            "days": int(est_days),
            "method": est_note[0] if est_note else None,
            "daily": [{"day": d.strftime("%b %d"), "portions": round(float(w or 0), 1)} for d, w in reversed(daily_rows)],
            "byItem": est_items,
        },
        logged={
            "entries": logged.count(),
            "cost": round(float(logged.with_entities(func.coalesce(func.sum(WasteRecord.cost_estimate), 0)).scalar() or 0), 2),
            "byReason": by_reason,
            "byItem": by_item,
        },
        salesAnomalies=AnomalyRecord.query.filter_by(is_anomaly=True).count(),
    )


@waste_bp.route("/food-items", methods=["GET"])
@jwt_required()
def food_items():
    rows = db.session.query(SalesRecord.menu_item_name).distinct().all()
    return jsonify(foodItems=[r[0] for r in rows])
