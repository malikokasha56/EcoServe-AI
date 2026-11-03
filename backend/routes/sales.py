from datetime import datetime

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import func

from extensions import db
from models import SalesRecord
from helpers import default_restaurant_id, to_number, ValidationError, json_object

sales_bp = Blueprint("sales", __name__)


@sales_bp.route("", methods=["GET"])
@sales_bp.route("/", methods=["GET"])
@jwt_required()
def list_sales():
    query = SalesRecord.query
    date_str = request.args.get("date")
    if date_str:
        try:
            day = datetime.strptime(date_str, "%Y-%m-%d").date()
            query = query.filter(SalesRecord.date == day)
        except ValueError:
            return jsonify(message="date must be YYYY-MM-DD"), 400

    search = request.args.get("search")
    if search:
        query = query.filter(SalesRecord.menu_item_name.ilike(f"%{search}%"))

    limit = min(to_number(request.args.get("limit"), "limit", int, minimum=1, default=100), 500)
    records = query.order_by(SalesRecord.date.desc(), SalesRecord.id.desc()).limit(limit).all()
    return jsonify(sales=[r.to_dict() for r in records])


@sales_bp.route("", methods=["POST"])
@sales_bp.route("/", methods=["POST"])
@jwt_required()
def create_sale():
    data = json_object()
    date_str = data.get("date")
    try:
        day = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else datetime.utcnow().date()
    except ValueError:
        return jsonify(message="date must be YYYY-MM-DD"), 400

    items = data.get("items") or []
    if not isinstance(items, list) or not items:
        return jsonify(message="At least one item is required"), 400
    if not all(isinstance(item, dict) for item in items):
        raise ValidationError("Each item must be an object with a name and a quantity")

    created = []
    for item in items:
        name = (item.get("name") or "").strip()
        if not name:
            raise ValidationError("Each item needs a name")
        record = SalesRecord(
            restaurant_id=default_restaurant_id(),
            date=day,
            menu_item_name=name,
            meal_type=item.get("mealType"),
            quantity_sold=to_number(item.get("quantity"), "quantity", int, minimum=1),
            actual_selling_price=to_number(item.get("price"), "price", float, minimum=0, default=0.0),
        )
        db.session.add(record)
        created.append(record)
    db.session.commit()
    return jsonify(sales=[r.to_dict() for r in created]), 201


@sales_bp.route("/history", methods=["GET"])
@jwt_required()
def history():
    records = SalesRecord.query.order_by(SalesRecord.date.desc(), SalesRecord.id.desc()).limit(200).all()
    return jsonify(history=[
        {
            "id": r.id,
            "date": r.date.isoformat(),
            "item": r.menu_item_name,
            "mealType": r.meal_type,
            "quantity": r.quantity_sold,
            "revenue": round(r.revenue, 2),
        }
        for r in records
    ])


@sales_bp.route("/overview", methods=["GET"])
@jwt_required()
def overview():
    last_day = db.session.query(func.max(SalesRecord.date)).scalar()
    if last_day is None:
        return jsonify(message="No data"), 200

    day_rows = SalesRecord.query.filter(SalesRecord.date == last_day).all()
    units_sold = sum(r.quantity_sold or 0 for r in day_rows)
    total_revenue = round(sum(r.revenue for r in day_rows), 2)
    avg_price = round(total_revenue / units_sold, 2) if units_sold else 0

    product = (
        db.session.query(
            SalesRecord.menu_item_name,
            func.sum(SalesRecord.quantity_sold),
            func.sum(SalesRecord.quantity_sold * SalesRecord.actual_selling_price),
        )
        .filter(SalesRecord.date == last_day)
        .group_by(SalesRecord.menu_item_name)
        .order_by(func.sum(SalesRecord.quantity_sold).desc())
        .limit(5)
        .all()
    )

    return jsonify(
        stats={
            "unitsSold": int(units_sold),
            "records": len(day_rows),
            "totalRevenue": total_revenue,
            "avgPricePerUnit": avg_price,
            "date": last_day.isoformat(),
        },
        productPerformance=[
            {"product": p[0], "sold": int(p[1] or 0), "revenue": round(float(p[2] or 0), 2)}
            for p in product
        ],
    )


@sales_bp.route("/menu-items", methods=["GET"])
@jwt_required()
def menu_items():
    rows = (
        db.session.query(
            SalesRecord.menu_item_name,
            func.avg(SalesRecord.actual_selling_price),
        )
        .group_by(SalesRecord.menu_item_name)
        .all()
    )
    latest = db.session.query(func.max(SalesRecord.date)).scalar()
    return jsonify(
        menuItems=[
            {"id": idx + 1, "name": name, "price": round(float(price or 0), 2)}
            for idx, (name, price) in enumerate(rows)
        ],
        latestDate=latest.isoformat() if latest else None,
    )
