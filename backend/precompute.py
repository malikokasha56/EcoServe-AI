"""Offline pipeline: runs the controlled model comparison and stores every result the app serves.

Usage: python precompute.py   (needs requirements-ml.txt; also rewrites data/results.json)

Only the rows loaded from the public dataset are used, never sales typed into the application. Everything is
computed first; the stored results are then replaced in a single transaction and the results file is written
atomically, so a failed run leaves the previous results in place.
"""
import time

import numpy as np
import pandas as pd

from app import create_app
from config import Config
from extensions import db
from models import (
    SalesRecord, ForecastRecord, ExperimentResult, WasteRecord, Recommendation, AnomalyRecord,
    SimulationResult, SimulationSummary,
)
from helpers import default_restaurant_id
from bootstrap import ensure_ready, export_results
from ml import anomaly, experiment, simulation
from ml.forecasting import evaluate

SAFETY = Config.SAFETY_FACTOR
REFERENCE_LABEL = "Item-level RF summed per day (reference)"
RULE = "Historical average rule"


def _dataset_df():
    rows = SalesRecord.query.filter(SalesRecord.source_restaurant_id.isnot(None)).all()
    return pd.DataFrame([{
        "date": r.date,
        "restaurant_id": r.source_restaurant_id,
        "restaurant_type": r.restaurant_type,
        "menu_item_name": r.menu_item_name,
        "meal_type": r.meal_type,
        "typical_ingredient_cost": r.typical_ingredient_cost,
        "observed_market_price": r.observed_market_price,
        "actual_selling_price": r.actual_selling_price,
        "has_promotion": bool(r.has_promotion),
        "special_event": bool(r.special_event),
        "weather_condition": r.weather_condition,
        "quantity_sold": r.quantity_sold,
    } for r in rows])


def _result(row):
    return ExperimentResult(
        track=row["track"], info_set=row["info_set"], model=row["model"], label=row["label"],
        mae=row["mae"], rmse=row["rmse"], mape=row["mape"], wape=row["wape"], r2=row["r2"],
        cv_wape_mean=row.get("cv_wape_mean"), cv_wape_sd=row.get("cv_wape_sd"),
        p_vs_baseline=row.get("p_vs_baseline"), p_vs_best=row.get("p_vs_best"),
        n_test=row["n_test"], seconds=row.get("seconds"),
    )


def _series(rid, label, dates, actual, pred):
    return [ForecastRecord(restaurant_id=rid, model_type=label, forecast_date=pd.Timestamp(d).date(),
                           actual_value=float(a), forecast_value=float(p))
            for d, a, p in zip(dates, actual, pred)]


def comparison(df, rid):
    print("Track A: daily total demand")
    a = experiment.run_daily(df)
    print("Track B: item-level demand")
    b = experiment.run_items(df, a["split_date"])
    rows = []
    for row in a["results"]:
        rows.append(_result(row))
        rows += _series(rid, row["label"], a["dates"], a["actual"], a["series"][row["label"]])
    rows += [_result(row) for row in b["results"]]

    # Reference: the earlier design summed item-level predictions over the records that actually occurred
    # on each test day, which quietly uses how many records a day has. Kept to explain that result.
    test = b["test"].assign(pred=b["preds"]["Random Forest"])
    per_day = test.groupby("date")[["quantity_sold", "pred"]].sum().reindex(pd.to_datetime(a["dates"]), fill_value=0)
    m = evaluate(per_day["quantity_sold"].values, per_day["pred"].values)
    rows.append(_result({"track": "A", "info_set": "reference", "model": "Random Forest", "label": REFERENCE_LABEL,
                         **m, "n_test": len(per_day)}))
    rows += _series(rid, REFERENCE_LABEL, a["dates"], per_day["quantity_sold"].values, per_day["pred"].values)
    print(f"  A {REFERENCE_LABEL:<24} WAPE {m['wape']:5.1f}%  R2 {m['r2']:6.2f}  (not a forecast)")
    return b, rows


def preparation(b, rid):
    best = min((r for r in b["results"] if r["model"] not in ("Mean baseline", RULE)), key=lambda r: r["wape"])["model"]
    test = b["test"]
    policies = {RULE: test["item_mean"].to_numpy(dtype=float), best: np.asarray(b["preds"][best], dtype=float)}
    print("Preparation simulation")
    sim = simulation.run(test, policies, RULE, best, default_margin=SAFETY)
    sim["summary"]["history_feature_wape"] = b["history_only"]["wape"]
    rows = [SimulationResult(**row) for row in sim["grid"]] + [SimulationSummary(data=sim["summary"])]
    rows += simulated_waste(test, policies[best], best, rid)
    rows += recommendations(test, policies, best, rid)
    return rows


# The dataset records sales only, so waste is never measured. Stored here is the simulated overproduction
# of the model plan (forecast x (1 + margin) minus actual sales), per day and menu item.
def simulated_waste(test, forecast, model, rid):
    t = test.assign(over=np.maximum(forecast * (1 + SAFETY) - test["quantity_sold"].to_numpy(dtype=float), 0))
    t["cost"] = t["over"] * t["typical_ingredient_cost"]
    grouped = t.groupby(["date", "menu_item_name"])[["over", "cost"]].sum().reset_index()
    print(f"Simulated overproduction: {t['over'].sum():,.0f} portions over the test period")
    return [WasteRecord(
        restaurant_id=rid, date=pd.Timestamp(row.date).date(), waste_category="Simulated overproduction",
        menu_item_name=row.menu_item_name, quantity=round(float(row.over), 1), unit="portions",
        cost_estimate=round(float(row.cost), 2), reason="overproduction", source="derived",
        notes=f"Simulated: {model} forecast x {1 + SAFETY:.2f} minus actual sales",
    ) for row in grouped.itertuples(index=False)]


# Preparation plan for every test day: model forecast plus the safety margin per menu item, stored next to
# what the historical-average rule would have prepared and what was actually sold.
def recommendations(test, policies, model, rid):
    t = test.assign(model=policies[model] * (1 + SAFETY), rule=policies[RULE] * (1 + SAFETY))
    per_item = t.groupby(["date", "menu_item_name"]).agg(
        model=("model", "sum"), rule=("rule", "sum"), actual=("quantity_sold", "sum"),
        restaurants=("restaurant_id", "nunique"),
    ).reset_index()
    print(f"Preparation plans: {len(per_item)} item-days over {per_item['date'].nunique()} test days")
    rows = []
    for r in per_item.itertuples(index=False):
        prep = round(float(r.model))
        rows.append(Recommendation(
            restaurant_id=rid, date=pd.Timestamp(r.date).date(), menu_item_name=r.menu_item_name,
            recommended_quantity=prep, rule_quantity=round(float(r.rule)), actual_quantity=round(float(r.actual)),
            restaurants=int(r.restaurants), safety_factor_applied=SAFETY,
            title=f"Prepare about {prep} portions of {r.menu_item_name}",
            description=(f"{model} forecast for the {int(r.restaurants)} restaurant(s) with {r.menu_item_name} "
                         f"on the menu on {pd.Timestamp(r.date):%d %b %Y}, plus a {int(SAFETY * 100)}% safety margin."),
            category="preparation", action="Set the preparation quantity", status="pending",
        ))
    return rows


def anomalies(df, rid):
    daily = df.assign(date=pd.to_datetime(df["date"])).groupby("date")["quantity_sold"].sum().sort_index()
    results = anomaly.detect(daily.to_numpy(dtype=float))
    print(f"Anomalies: {sum(r['is_anomaly'] for r in results)} flagged of {len(results)} days")
    return [AnomalyRecord(
        restaurant_id=rid, date=d.date(), metric="sales",
        value=res["value"], expected=res["expected"], lower_bound=res["lower"], upper_bound=res["upper"],
        method=res["method"], severity=res["severity"], is_anomaly=res["is_anomaly"],
    ) for d, res in zip(daily.index, results)]


def replace_results(rows):
    try:
        for model in (ForecastRecord, ExperimentResult, AnomalyRecord, Recommendation, SimulationResult,
                      SimulationSummary):
            model.query.delete()
        WasteRecord.query.filter_by(source="derived").delete()
        db.session.add_all(rows)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise


def run():
    app = create_app()
    with app.app_context():
        ensure_ready()
        rid = default_restaurant_id()
        df = _dataset_df()
        if df.empty:
            print("No sales data.")
            return
        t0 = time.time()
        b, rows = comparison(df, rid)
        rows += preparation(b, rid)
        rows += anomalies(df, rid)
        replace_results(rows)
        counts = export_results()
        print(f"Results bundle written: {counts}")
        print(f"\nPre-compute complete in {time.time() - t0:.0f}s.")


if __name__ == "__main__":
    run()
