from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from models import Ingredient

inventory_bp = Blueprint("inventory", __name__)


@inventory_bp.route("", methods=["GET"])
@inventory_bp.route("/", methods=["GET"])
@jwt_required()
def list_inventory():
    items = Ingredient.query.order_by(Ingredient.name).all()
    total = len(items)
    critical = sum(1 for i in items if i.status == "critical")
    expiring = sum(1 for i in items if (i.expiry_days or 99) <= 3)
    healthy = sum(1 for i in items if i.status == "good")
    health_score = round(healthy / total * 100) if total else 100

    return jsonify(
        items=[i.to_dict() for i in items],
        stats={
            "totalItems": total,
            "criticalStock": critical,
            "expiringSoon": expiring,
            "healthScore": health_score,
        },
        illustrative=True,
        note=("Illustrative demo data. The public dataset has no stock records, so these items are the 15 most "
              "common ingredient tags in the dataset with generated stock and expiry values."),
    )
