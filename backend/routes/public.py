from flask import Blueprint, jsonify
from sqlalchemy import func

from config import DATASET
from extensions import db
from models import ExperimentResult, SalesRecord

public_bp = Blueprint("public", __name__)


# Unauthenticated summary for the landing page: dataset provenance and the measured model errors.
@public_bp.route("/overview", methods=["GET"])
def overview():
    first, last, records = db.session.query(
        func.min(SalesRecord.date), func.max(SalesRecord.date), func.count(SalesRecord.id)
    ).one()
    rows = ExperimentResult.query.filter(ExperimentResult.info_set != "reference").order_by(ExperimentResult.wape).all()
    return jsonify(
        dataset={**DATASET, "records": records,
                 "from": first.isoformat() if first else None, "to": last.isoformat() if last else None},
        trackA=[r.to_dict() for r in rows if r.track == "A"],
        trackB=[r.to_dict() for r in rows if r.track == "B"],
    )
