"""Data provenance and consistency of the shipped results."""
import csv
import json
import os

import pytest

from config import CSV_PATH, DATASET, RESULTS_PATH

req = pytest.mark.req

EXPECTED_COLUMNS = [
    "date", "restaurant_id", "restaurant_type", "menu_item_name", "meal_type", "key_ingredients_tags",
    "typical_ingredient_cost", "observed_market_price", "actual_selling_price", "quantity_sold", "has_promotion",
    "special_event", "weather_condition",
]
PERSONAL_HINTS = ["name", "email", "phone", "customer", "address", "staff", "employee", "age", "gender"]


def _results():
    with open(RESULTS_PATH, encoding="utf-8") as f:
        return json.load(f)["tables"]


@req("NFR-05")
def test_dataset_is_the_published_file(evidence):
    """The CSV is the unmodified public Kaggle file"""
    size = os.path.getsize(CSV_PATH)
    evidence.check("Size of restaurant_sales_data.csv", "1,304,756 bytes (size of the file published on Kaggle)",
                   f"{size:,} bytes", size == 1304756)


@req("NFR-05")
def test_dataset_has_no_personal_data(evidence):
    """The dataset contains only sales, price, calendar and context fields"""
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        header = next(csv.reader(f))
    personal = [c for c in header if any(h in c.lower() for h in PERSONAL_HINTS) and c != "menu_item_name"]
    evidence.check("Read the CSV header", "13 known columns, none describing a person",
                   f"{len(header)} columns; personal fields: {personal or 'none'}",
                   header == EXPECTED_COLUMNS and not personal)


@req("NFR-05")
def test_dataset_attribution(client, evidence):
    """The dataset source and licence are attributed in the application"""
    d = client.get("/api/public/overview").get_json()["dataset"]
    evidence.check("GET /api/public/overview (no sign-in)", "title, author, Kaggle URL and CC BY-SA 4.0 licence",
                   f"{d['title']} by {d['author']}, {d['licence']}, {d['url']}",
                   d["licence"] == "CC BY-SA 4.0" and "kaggle.com" in d["url"] and d["author"] == DATASET["author"])


@req("FR-08", "FR-09")
def test_track_b_models_beat_current_rule(evidence):
    """Stored item-level results: every learned model beats the historical-average rule"""
    rows = [r for r in _results()["experiment_results"] if r["track"] == "B"]
    rule = next(r for r in rows if r["model"].startswith("Historical average"))
    learned = [r for r in rows if r["model"] not in ("Mean baseline", rule["model"])]
    worse = [r["model"] for r in learned if r["wape"] >= rule["wape"] or (r["p_vs_baseline"] or 1) >= 0.05]
    evidence.check("Read Track B results from data/results.json",
                   f"all learned models below {rule['wape']:.1f}% WAPE with p < 0.05",
                   ", ".join(f"{r['model']} {r['wape']:.1f}%" for r in learned), not worse)


@req("FR-08", "NFR-07")
def test_reference_result_is_flagged(evidence):
    """The result that used the realised record count is stored only as a flagged reference"""
    rows = [r for r in _results()["experiment_results"] if r["info_set"] == "reference"]
    evidence.check("Read reference rows from data/results.json", "one row, info set 'reference', label says reference",
                   [f"{r['label']} ({r['wape']:.1f}% WAPE)" for r in rows],
                   len(rows) == 1 and "reference" in rows[0]["label"].lower())


@req("FR-10", "NFR-07")
def test_simulated_waste_is_labelled(evidence):
    """Every stored overproduction record is labelled as simulated"""
    derived = [w for w in _results()["waste_records"] if w["source"] == "derived"]
    unlabeled = [w for w in derived if "Simulated" not in (w["notes"] or "") or "Simulated" not in w["waste_category"]]
    evidence.check("Read derived waste records from data/results.json", "all labelled 'Simulated'",
                   f"{len(derived)} records, {len(unlabeled)} without the label", derived and not unlabeled)
