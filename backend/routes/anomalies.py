from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from models import AnomalyRecord

anomalies_bp = Blueprint("anomalies", __name__)


@anomalies_bp.route("", methods=["GET"])
@anomalies_bp.route("/", methods=["GET"])
@jwt_required()
def list_anomalies():
    records = AnomalyRecord.query.order_by(AnomalyRecord.date).all()

    detected = [r for r in records if r.is_anomaly]
    high = [r for r in detected if r.severity == "high"]

    anomaly_list = [
        {
            "id": r.id,
            "value": round(r.value, 1) if r.value is not None else None,
            "expected": round(r.expected, 1) if r.expected is not None else None,
            "method": r.method,
            "severity": r.severity,
            "date": r.date.isoformat() if r.date else None,
        }
        for r in detected
    ]

    series = [
        {"date": r.date.isoformat(), "value": round(r.value, 1) if r.value is not None else 0, "anomaly": r.is_anomaly}
        for r in records
    ]
    first = records[0] if records else None

    return jsonify(
        anomalies=anomaly_list,
        series=series,
        summary={
            "flagged": len(detected),
            "highSeverity": len(high),
            "days": len(records),
            "flaggedPct": round(len(detected) / len(records) * 100, 1) if records else 0,
            "mean": round(first.expected, 1) if first else None,
            "iqrLower": round(first.lower_bound, 1) if first and first.lower_bound is not None else None,
            "iqrUpper": round(first.upper_bound, 1) if first and first.upper_bound is not None else None,
        },
    )
