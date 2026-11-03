import csv
import json
import os
from collections import Counter
from datetime import date, datetime

from sqlalchemy import Date, DateTime

from config import CSV_PATH, RESULTS_PATH
from extensions import db, bcrypt
from models import (
    Restaurant, User, SalesRecord, Ingredient,
    ForecastRecord, ExperimentResult, AnomalyRecord, WasteRecord, Recommendation,
    SimulationResult, SimulationSummary,
)

DEMO_EMAIL = "manager@restaurant.com"
DEMO_PASSWORD = "password123"

# Tables produced by precompute.py and shipped in data/results.json.
RESULT_TABLES = {
    "forecast_records": ForecastRecord,
    "experiment_results": ExperimentResult,
    "anomaly_records": AnomalyRecord,
    "waste_records": WasteRecord,
    "recommendations": Recommendation,
    "simulation_results": SimulationResult,
    "simulation_summary": SimulationSummary,
}


def _read_csv():
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def seed_restaurant_and_user():
    restaurant = db.session.get(Restaurant, 1)
    if restaurant is None:
        restaurant = Restaurant(id=1, name="EcoServe Restaurant", restaurant_type="Casual Dining")
        db.session.add(restaurant)
        db.session.commit()
    if User.query.filter_by(email=DEMO_EMAIL).first() is None:
        db.session.add(User(
            username="Restaurant Manager",
            email=DEMO_EMAIL,
            password_hash=bcrypt.generate_password_hash(DEMO_PASSWORD).decode("utf-8"),
            role="Manager",
            restaurant_id=restaurant.id,
        ))
        db.session.commit()
    return restaurant


def seed_sales(restaurant_id):
    if SalesRecord.query.first() is not None:
        return 0
    rows = []
    for r in _read_csv():
        rows.append({
            "restaurant_id": restaurant_id,
            "source_restaurant_id": int(r["restaurant_id"]),
            "date": datetime.strptime(r["date"], "%m/%d/%Y").date(),
            "menu_item_name": r["menu_item_name"],
            "meal_type": r["meal_type"],
            "restaurant_type": r["restaurant_type"],
            "quantity_sold": int(r["quantity_sold"]),
            "typical_ingredient_cost": float(r["typical_ingredient_cost"]),
            "observed_market_price": float(r["observed_market_price"]),
            "actual_selling_price": float(r["actual_selling_price"]),
            "has_promotion": r["has_promotion"].strip().upper() == "TRUE",
            "special_event": r["special_event"].strip().upper() == "TRUE",
            "weather_condition": r["weather_condition"],
        })
    db.session.execute(SalesRecord.__table__.insert(), rows)
    db.session.commit()
    return len(rows)


# Inventory is derived from the most common ingredient tags in the dataset.
def seed_ingredients(restaurant_id):
    if Ingredient.query.first() is not None:
        return 0
    data = _read_csv()
    counter = Counter()
    for r in data:
        for tag in r["key_ingredients_tags"].split(","):
            name = tag.strip().title()
            if name:
                counter[name] += 1

    avg_cost = sum(float(r["typical_ingredient_cost"]) for r in data) / len(data)
    for idx, (name, freq) in enumerate(counter.most_common(15)):
        stock = 20 + (freq % 60)
        reorder = 25
        if stock <= reorder * 0.5:
            status = "critical"
        elif stock <= reorder:
            status = "low"
        else:
            status = "good"
        db.session.add(Ingredient(
            restaurant_id=restaurant_id, name=name, unit="kg",
            current_cost=round(avg_cost, 2), stock=float(stock), reorder_point=float(reorder),
            expiry_days=2 + (idx % 8), status=status,
        ))
    db.session.commit()
    return Ingredient.query.count()


def _to_json(obj):
    row = {}
    for col in obj.__table__.columns:
        if col.name == "id":
            continue
        value = getattr(obj, col.name)
        if isinstance(value, (date, datetime)):
            value = value.isoformat()
        row[col.name] = value
    return row


def _from_json(model, row):
    values = {}
    for col in model.__table__.columns:
        if col.name not in row:
            continue
        value = row[col.name]
        if value is not None and isinstance(col.type, DateTime):
            value = datetime.fromisoformat(value)
        elif value is not None and isinstance(col.type, Date):
            value = date.fromisoformat(value[:10])
        values[col.name] = value
    return values


def export_results(path=RESULTS_PATH):
    bundle = {
        "generated_at": datetime.utcnow().isoformat(timespec="seconds"),
        "tables": {name: [_to_json(o) for o in model.query.all()] for name, model in RESULT_TABLES.items()},
    }
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(bundle, f)
    os.replace(tmp, path)
    return {name: len(rows) for name, rows in bundle["tables"].items()}


def load_results(path=RESULTS_PATH):
    if ExperimentResult.query.first() is not None or not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        bundle = json.load(f)
    counts = {}
    for name, model in RESULT_TABLES.items():
        rows = [_from_json(model, r) for r in bundle["tables"].get(name, [])]
        if rows:
            db.session.execute(model.__table__.insert(), rows)
        counts[name] = len(rows)
    db.session.commit()
    return counts


# Idempotent: safe to call on every start, only fills what is missing.
def ensure_ready(log=print):
    db.create_all()
    restaurant = seed_restaurant_and_user()
    n = seed_sales(restaurant.id)
    if n:
        log(f"  Loaded {n} sales records from restaurant_sales_data.csv")
    n = seed_ingredients(restaurant.id)
    if n:
        log(f"  Created {n} inventory items")
    counts = load_results()
    if counts:
        log(f"  Loaded pre-computed model results ({counts['experiment_results']} comparison results)")


if __name__ == "__main__":
    from app import create_app

    with create_app().app_context():
        ensure_ready()
        print(f"Ready. Demo login: {DEMO_EMAIL} / {DEMO_PASSWORD}")
