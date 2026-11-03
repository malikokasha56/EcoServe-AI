import csv
import io

from flask import Blueprint, jsonify, request, Response
from flask_jwt_extended import jwt_required
from sqlalchemy import func

from extensions import db
from models import SalesRecord, WasteRecord, ForecastRecord, ExperimentResult, SimulationResult

reports_bp = Blueprint("reports", __name__)

# Report definitions are derived from live data rather than stored files.
_REPORTS = [
    {"id": "sales", "name": "Sales records", "type": "Sales", "source": SalesRecord},
    {"id": "waste", "name": "Simulated overproduction and logged waste", "type": "Waste", "source": WasteRecord},
    {"id": "forecast", "name": "Model forecasts vs actual demand (test period)", "type": "Forecast", "source": ForecastRecord},
    {"id": "comparison", "name": "Model comparison results (both tracks)", "type": "Models", "source": ExperimentResult},
    {"id": "simulation", "name": "Preparation simulation by safety margin", "type": "Simulation", "source": SimulationResult},
]


@reports_bp.route("", methods=["GET"])
@reports_bp.route("/", methods=["GET"])
@jwt_required()
def list_reports():
    reports = []
    for r in _REPORTS:
        count = db.session.query(func.count(r["source"].id)).scalar() or 0
        reports.append({
            "id": r["id"],
            "name": r["name"],
            "type": r["type"],
            "records": int(count),
        })
    return jsonify(
        reports=reports,
        summary={"available": len(reports), "totalRecords": sum(r["records"] for r in reports)},
    )


@reports_bp.route("/<report_id>/download", methods=["GET"])
@jwt_required()
def download(report_id):
    definition = next((r for r in _REPORTS if r["id"] == report_id), None)
    if definition is None:
        return jsonify(message="Report not found"), 404

    rows = definition["source"].query.all()
    if not rows:
        return jsonify(message="No data for this report"), 404

    data = [row.to_dict() for row in rows]
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=list(data[0].keys()))
    writer.writeheader()
    writer.writerows(data)

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={report_id}_report.csv"},
    )
