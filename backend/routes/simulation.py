from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from models import SimulationResult, SimulationSummary

simulation_bp = Blueprint("simulation", __name__)

ASSUMPTIONS = [
    "Each plan prepares its forecast multiplied by (1 + safety margin) for every restaurant, menu item and day "
    "recorded in the data, as a kitchen would plan for the items on its menu that day.",
    "Promotions, special events and the weather of each day are treated as known in advance.",
    "Portions prepared but not sold are counted as waste: food is perishable and is not carried over to the next day.",
    "Recorded sales are treated as true demand, so sales are assumed not to have been capped by stock running out.",
    "Waste cost uses each record's typical ingredient cost; unserved demand loses the selling price minus that cost.",
    "Only the test period is simulated (days the models never saw), so the result reflects forecasting on new data. "
    "The matched service margin is chosen on these same days, so that comparison is optimistic.",
    "The dataset has no waste measurements. These figures are simulated estimates, not measured waste reduction.",
]


@simulation_bp.route("", methods=["GET"])
@simulation_bp.route("/", methods=["GET"])
@jwt_required()
def get_simulation():
    summary = SimulationSummary.query.first()
    rows = SimulationResult.query.order_by(SimulationResult.policy, SimulationResult.margin).all()
    policies = {}
    for r in rows:
        policies.setdefault(r.policy, []).append(r.to_dict())
    return jsonify(
        summary=summary.data if summary else None,
        policies=policies,
        assumptions=ASSUMPTIONS,
    )
