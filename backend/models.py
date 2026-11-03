from datetime import datetime

from extensions import db


class Restaurant(db.Model):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    restaurant_type = db.Column(db.String(60))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "restaurant_type": self.restaurant_type}


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="Manager")
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurants.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "restaurant_id": self.restaurant_id,
        }


class SalesRecord(db.Model):
    __tablename__ = "sales_records"

    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurants.id"), index=True)
    # Restaurant number in the public dataset (1 to 50); restaurant_id is this deployment's tenant.
    source_restaurant_id = db.Column(db.Integer)
    date = db.Column(db.Date, nullable=False, index=True)
    menu_item_name = db.Column(db.String(120))
    meal_type = db.Column(db.String(40))
    restaurant_type = db.Column(db.String(60))
    quantity_sold = db.Column(db.Integer, default=0)
    typical_ingredient_cost = db.Column(db.Float)
    observed_market_price = db.Column(db.Float)
    actual_selling_price = db.Column(db.Float)
    has_promotion = db.Column(db.Boolean, default=False)
    special_event = db.Column(db.Boolean, default=False)
    weather_condition = db.Column(db.String(40))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def revenue(self):
        return (self.quantity_sold or 0) * (self.actual_selling_price or 0.0)

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date.isoformat() if self.date else None,
            "menu_item_name": self.menu_item_name,
            "meal_type": self.meal_type,
            "quantity_sold": self.quantity_sold,
            "actual_selling_price": self.actual_selling_price,
            "revenue": round(self.revenue, 2),
            "has_promotion": self.has_promotion,
            "special_event": self.special_event,
            "weather_condition": self.weather_condition,
        }


class WasteRecord(db.Model):
    __tablename__ = "waste_records"

    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurants.id"), index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    waste_category = db.Column(db.String(40))
    menu_item_name = db.Column(db.String(120))
    quantity = db.Column(db.Float, default=0.0)
    unit = db.Column(db.String(20), default="kg")
    cost_estimate = db.Column(db.Float, default=0.0)
    reason = db.Column(db.String(60))
    notes = db.Column(db.Text)
    source = db.Column(db.String(20), default="derived")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date.isoformat() if self.date else None,
            "waste_category": self.waste_category,
            "menu_item_name": self.menu_item_name,
            "quantity": round(self.quantity or 0.0, 2),
            "unit": self.unit,
            "cost_estimate": round(self.cost_estimate or 0.0, 2),
            "reason": self.reason,
            "notes": self.notes,
            "source": self.source,
        }


class ForecastRecord(db.Model):
    __tablename__ = "forecast_records"

    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurants.id"), index=True)
    model_type = db.Column(db.String(80))
    forecast_date = db.Column(db.Date, nullable=False, index=True)
    actual_value = db.Column(db.Float)
    forecast_value = db.Column(db.Float)
    lower_bound = db.Column(db.Float)
    upper_bound = db.Column(db.Float)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "model_type": self.model_type,
            "forecast_date": self.forecast_date.isoformat() if self.forecast_date else None,
            "actual_value": self.actual_value,
            "forecast_value": self.forecast_value,
            "lower_bound": self.lower_bound,
            "upper_bound": self.upper_bound,
        }


# One row per model per comparison track (see ml/experiment.py).
class ExperimentResult(db.Model):
    __tablename__ = "experiment_results"

    id = db.Column(db.Integer, primary_key=True)
    track = db.Column(db.String(4))
    info_set = db.Column(db.String(20))
    model = db.Column(db.String(60))
    label = db.Column(db.String(80))
    mae = db.Column(db.Float)
    rmse = db.Column(db.Float)
    mape = db.Column(db.Float)
    wape = db.Column(db.Float)
    r2 = db.Column(db.Float)
    cv_wape_mean = db.Column(db.Float)
    cv_wape_sd = db.Column(db.Float)
    p_vs_baseline = db.Column(db.Float)
    p_vs_best = db.Column(db.Float)
    n_test = db.Column(db.Integer)
    seconds = db.Column(db.Float)
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        def r(v, d):
            return round(v, d) if v is not None else None

        return {
            "track": self.track,
            "info_set": self.info_set,
            "model": self.model,
            "label": self.label,
            "mae": r(self.mae, 1),
            "rmse": r(self.rmse, 1),
            "mape": r(self.mape, 1),
            "wape": r(self.wape, 1),
            "r2": r(self.r2, 3),
            "cv_wape_mean": r(self.cv_wape_mean, 1),
            "cv_wape_sd": r(self.cv_wape_sd, 1),
            "p_vs_baseline": r(self.p_vs_baseline, 4),
            "p_vs_best": r(self.p_vs_best, 4),
            "n_test": self.n_test,
        }


# Preparation simulation (ml/simulation.py): one row per plan and safety margin.
class SimulationResult(db.Model):
    __tablename__ = "simulation_results"

    id = db.Column(db.Integer, primary_key=True)
    policy = db.Column(db.String(60))
    margin = db.Column(db.Float)
    prepared = db.Column(db.Float)
    overproduction = db.Column(db.Float)
    shortfall = db.Column(db.Float)
    fill_rate = db.Column(db.Float)
    short_days_pct = db.Column(db.Float)
    waste_cost = db.Column(db.Float)
    lost_margin = db.Column(db.Float)

    def to_dict(self):
        return {
            "policy": self.policy,
            "margin": self.margin,
            "prepared": round(self.prepared),
            "overproduction": round(self.overproduction),
            "shortfall": round(self.shortfall),
            "fill_rate": round(self.fill_rate, 1),
            "short_days_pct": round(self.short_days_pct, 1),
            "waste_cost": round(self.waste_cost),
            "lost_margin": round(self.lost_margin),
        }


class SimulationSummary(db.Model):
    __tablename__ = "simulation_summary"

    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.JSON)


class Recommendation(db.Model):
    __tablename__ = "recommendations"

    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurants.id"), index=True)
    date = db.Column(db.Date, index=True)
    menu_item_name = db.Column(db.String(120))
    recommended_quantity = db.Column(db.Float)
    rule_quantity = db.Column(db.Float)
    actual_quantity = db.Column(db.Float)
    restaurants = db.Column(db.Integer)
    safety_factor_applied = db.Column(db.Float)
    title = db.Column(db.String(160))
    description = db.Column(db.Text)
    category = db.Column(db.String(40))
    action = db.Column(db.String(120))
    status = db.Column(db.String(20), default="pending")
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date.isoformat() if self.date else None,
            "menu_item_name": self.menu_item_name,
            "recommended_quantity": self.recommended_quantity,
            "rule_quantity": self.rule_quantity,
            "actual_quantity": self.actual_quantity,
            "restaurants": self.restaurants,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "action": self.action,
            "status": self.status,
        }


class AnomalyRecord(db.Model):
    __tablename__ = "anomaly_records"

    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurants.id"), index=True)
    date = db.Column(db.Date, index=True)
    metric = db.Column(db.String(20))
    value = db.Column(db.Float)
    expected = db.Column(db.Float)
    lower_bound = db.Column(db.Float)
    upper_bound = db.Column(db.Float)
    method = db.Column(db.String(20))
    severity = db.Column(db.String(20))
    is_anomaly = db.Column(db.Boolean, default=False)
    detected_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date.isoformat() if self.date else None,
            "metric": self.metric,
            "value": round(self.value, 2) if self.value is not None else None,
            "expected": round(self.expected, 2) if self.expected is not None else None,
            "method": self.method,
            "severity": self.severity,
            "is_anomaly": self.is_anomaly,
        }


class Ingredient(db.Model):
    __tablename__ = "ingredients"

    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurants.id"), index=True)
    name = db.Column(db.String(120))
    unit = db.Column(db.String(20))
    current_cost = db.Column(db.Float)
    stock = db.Column(db.Float)
    reorder_point = db.Column(db.Float)
    expiry_days = db.Column(db.Integer)
    status = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "unit": self.unit,
            "current_cost": self.current_cost,
            "stock": self.stock,
            "reorder_point": self.reorder_point,
            "expiry_days": self.expiry_days,
            "status": self.status,
        }
