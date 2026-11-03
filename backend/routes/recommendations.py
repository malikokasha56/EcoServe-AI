from collections import defaultdict
from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy import func

from config import Config
from extensions import db
from helpers import ValidationError
from models import Recommendation, SimulationSummary

recommendations_bp = Blueprint("recommendations", __name__)


def _period_stats():
    # Per test day, which plan's total was closer to what was actually sold.
    rows = db.session.query(
        Recommendation.date,
        func.sum(Recommendation.recommended_quantity),
        func.sum(Recommendation.rule_quantity),
        func.sum(Recommendation.actual_quantity),
    ).group_by(Recommendation.date).all()
    model_closer = sum(1 for _, m, r, a in rows if abs((m or 0) - (a or 0)) < abs((r or 0) - (a or 0)))
    item_err = defaultdict(float)
    for rec in Recommendation.query.all():
        item_err["model"] += abs((rec.recommended_quantity or 0) - (rec.actual_quantity or 0))
        item_err["rule"] += abs((rec.rule_quantity or 0) - (rec.actual_quantity or 0))
    return {
        "days": len(rows),
        "modelCloserDays": model_closer,
        "modelItemError": round(item_err["model"]),
        "ruleItemError": round(item_err["rule"]),
    }


@recommendations_bp.route("", methods=["GET"])
@recommendations_bp.route("/", methods=["GET"])
@jwt_required()
def list_recommendations():
    dates = [d for (d,) in db.session.query(Recommendation.date).distinct().order_by(Recommendation.date).all()]
    if not dates:
        return jsonify(recommendations=[], dates=[], summary=None, period=None)

    date_str = request.args.get("date")
    if date_str:
        try:
            day = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            raise ValidationError("date must be YYYY-MM-DD")
        if day not in dates:
            raise ValidationError("No preparation plan for that date (choose a test-period day)")
    else:
        day = dates[-1]

    recs = (Recommendation.query.filter_by(date=day)
            .order_by(Recommendation.recommended_quantity.desc()).all())
    sim = SimulationSummary.query.first()
    return jsonify(
        recommendations=[r.to_dict() for r in recs],
        dates=[d.isoformat() for d in dates],
        summary={
            "date": day.isoformat(),
            "model": sim.data.get("model") if sim and sim.data else None,
            "planned": round(sum(r.recommended_quantity or 0 for r in recs)),
            "rule": round(sum(r.rule_quantity or 0 for r in recs)),
            "actual": round(sum(r.actual_quantity or 0 for r in recs)),
            "pending": sum(1 for r in recs if r.status == "pending"),
            "applied": sum(1 for r in recs if r.status == "applied"),
            "safetyMarginPct": round(Config.SAFETY_FACTOR * 100),
        },
        period=_period_stats(),
    )


@recommendations_bp.route("/<int:rec_id>/apply", methods=["POST"])
@jwt_required()
def apply(rec_id):
    rec = db.session.get(Recommendation, rec_id)
    if rec is None:
        return jsonify(message="Recommendation not found"), 404
    rec.status = "applied"
    db.session.commit()
    return jsonify(recommendation=rec.to_dict())
