import importlib.util
import os
import subprocess
import sys

from flask import Blueprint, current_app, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import func

from extensions import db
from models import ForecastRecord, ExperimentResult, SalesRecord
from helpers import best_model

forecast_bp = Blueprint("forecast", __name__)


def _series():
    rows = ForecastRecord.query.filter(ForecastRecord.model_type.isnot(None)).order_by(ForecastRecord.forecast_date).all()
    by_day = {}
    for r in rows:
        day = by_day.setdefault(r.forecast_date, {"date": r.forecast_date.isoformat(), "day": r.forecast_date.strftime("%b %d")})
        if r.actual_value is not None:
            day["actual"] = round(r.actual_value)
        day[r.model_type] = round(r.forecast_value)
    return [by_day[d] for d in sorted(by_day)]


def _design():
    first_test = db.session.query(func.min(ForecastRecord.forecast_date)).scalar()
    test_days = db.session.query(func.count(func.distinct(ForecastRecord.forecast_date))).scalar() or 0
    total_days = (db.session.query(func.count(func.distinct(SalesRecord.date)))
                  .filter(SalesRecord.source_restaurant_id.isnot(None)).scalar() or 0)
    b = ExperimentResult.query.filter_by(track="B").first()
    return {
        "splitDate": first_test.isoformat() if first_test else None,
        "trainDays": max(total_days - test_days, 0),
        "testDays": test_days,
        "testRecords": b.n_test if b else None,
        "cvFolds": 4,
    }


@forecast_bp.route("", methods=["GET"])
@forecast_bp.route("/", methods=["GET"])
@jwt_required()
def get_forecast():
    rows = ExperimentResult.query.order_by(ExperimentResult.wape).all()
    best_a, best_b = best_model("A"), best_model("B")
    return jsonify(
        design=_design(),
        trackA=[r.to_dict() for r in rows if r.track == "A"],
        trackB=[r.to_dict() for r in rows if r.track == "B"],
        best={"A": best_a.label if best_a else None, "B": best_b.label if best_b else None},
        series=_series(),
        itemAverages=_item_averages(),
    )


# Descriptive statistic, not a forecast: average quantity per restaurant-day for each menu item.
def _item_averages():
    rows = (
        db.session.query(SalesRecord.menu_item_name, func.avg(SalesRecord.quantity_sold), func.count(SalesRecord.id))
        .group_by(SalesRecord.menu_item_name)
        .order_by(func.avg(SalesRecord.quantity_sold).desc())
        .all()
    )
    return [{"item": name, "avgQty": round(float(avg or 0), 1), "records": int(n)} for name, avg, n in rows]


@forecast_bp.route("/compare", methods=["GET"])
@jwt_required()
def compare():
    rows = ExperimentResult.query.filter(ExperimentResult.info_set != "reference").order_by(ExperimentResult.wape).all()
    best_a, best_b = best_model("A"), best_model("B")
    return jsonify(results=[r.to_dict() for r in rows],
                   best={"A": best_a.label if best_a else None, "B": best_b.label if best_b else None})


_training = {"process": None}
ML_PACKAGES = ("tensorflow", "prophet", "sklearn", "pandas")


# Reruns the whole comparison (precompute.py) in a separate process, so the request returns immediately
# and the web server is not blocked while the models train (about 20 minutes).
# Retraining needs the optional ML libraries (requirements-ml.txt); the app itself runs on the
# shipped pre-computed results without them.
@forecast_bp.route("/train", methods=["POST"])
@jwt_required()
def train():
    missing = [p for p in ML_PACKAGES if importlib.util.find_spec(p) is None]
    if missing:
        return jsonify(message="Retraining needs the machine learning libraries "
                               f"({', '.join(missing)} not installed). The results shown are the "
                               "pre-computed ones. See README section 'Retraining the models'."), 409

    proc = _training["process"]
    if proc is not None and proc.poll() is None:
        return jsonify(message="Retraining is already running. Reload the page in a few minutes."), 409

    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_path = os.path.join(current_app.config["INSTANCE_DIR"], "precompute_last.log")
    with open(log_path, "w") as log_file:
        _training["process"] = subprocess.Popen(
            [sys.executable, "precompute.py"], cwd=backend_dir, stdout=log_file, stderr=subprocess.STDOUT,
        )
    return jsonify(message="Retraining started in the background. The full comparison takes about 20 minutes; "
                           "reload the page afterwards to see the updated results.")
