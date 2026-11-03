"""API tests: run against a fresh SQLite database built exactly as on first start (CSV + shipped results)."""
import time
import uuid
from datetime import timedelta

import pytest

req = pytest.mark.req


def unique_email():
    return f"user-{uuid.uuid4().hex[:8]}@example.com"


# ---------------------------------------------------------------- start-up

@req("NFR-01")
def test_health_reports_ready_system(client, evidence):
    """Health check reports a ready system on SQLite with the shipped results"""
    body = client.get("/api/health").get_json()
    c = body["checks"]
    evidence.check("GET /api/health on a new database", "status ok, engine sqlite, 10,000 sales records, results loaded",
                   f"status {body['status']}, engine {c['database']['engine']}, {c['sales_data']['records']} records, "
                   f"{c['model_results']['results']} results", body["status"] in ("ok", "degraded")
                   and c["database"]["engine"] == "sqlite" and c["sales_data"]["records"] == 10000
                   and c["model_results"]["results"] > 0)


@req("NFR-01")
def test_runs_without_ml_libraries(evidence):
    """The web application code imports no machine learning library"""
    import ast
    import pathlib

    ml_libs = {"tensorflow", "prophet", "sklearn", "pandas", "numpy", "scipy"}
    found = set()
    files = ["app.py", "bootstrap.py", "config.py", "helpers.py", "models.py", "run.py", "extensions.py"]
    root = pathlib.Path(__file__).resolve().parents[1]
    paths = [root / f for f in files] + list((root / "routes").glob("*.py"))
    for p in paths:
        for node in ast.walk(ast.parse(p.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Import):
                found |= {a.name.split(".")[0] for a in node.names} & ml_libs
            elif isinstance(node, ast.ImportFrom) and node.module:
                found |= {node.module.split(".")[0]} & ml_libs
    evidence.check(f"Scan imports of {len(paths)} runtime modules", "no ML library imported",
                   ", ".join(sorted(found)) or "none imported", not found)


# ---------------------------------------------------------------- authentication

@req("FR-01")
def test_register_new_account(client, evidence):
    """A new account can be registered"""
    email = unique_email()
    r = client.post("/api/auth/register", json={"firstName": "Test", "lastName": "User", "email": email,
                                                "password": "longenough1"})
    evidence.check(f"POST /api/auth/register {email}, 11-character password", "201 with a session token",
                   f"{r.status_code}, token {'present' if r.get_json().get('token') else 'missing'}",
                   r.status_code == 201 and r.get_json().get("token"))


@req("FR-01", "NFR-04")
@pytest.mark.parametrize("payload,expected", [
    ({"email": "", "password": "longenough1"}, 400),
    ({"email": "short@example.com", "password": "short"}, 400),
    ({"email": "manager@restaurant.com", "password": "longenough1"}, 409),
])
def test_register_rejects_invalid(client, evidence, payload, expected):
    """Invalid or duplicate registrations are rejected"""
    r = client.post("/api/auth/register", json=payload)
    evidence.check(f"POST /api/auth/register {payload}", f"{expected} with a message",
                   f"{r.status_code}: {r.get_json().get('message')}", r.status_code == expected)


@req("FR-01", "NFR-04")
def test_same_name_can_register_twice(client, evidence):
    """Two people with the same name can both register (only the email must be unique)"""
    codes = [client.post("/api/auth/register", json={"firstName": "Sam", "lastName": "Lee", "email": unique_email(),
                                                     "password": "longenough1"}).status_code for _ in range(2)]
    evidence.check("Register two accounts named Sam Lee with different emails", "201 and 201", codes, codes == [201, 201])


@req("FR-02")
def test_login_with_demo_account(client, evidence):
    """The demo account can sign in"""
    r = client.post("/api/auth/login", json={"email": "manager@restaurant.com", "password": "password123"})
    evidence.check("POST /api/auth/login with the demo credentials", "200 with token and user",
                   f"{r.status_code}, user {r.get_json().get('user', {}).get('email')}",
                   r.status_code == 200 and r.get_json().get("token"))


@req("FR-02")
def test_login_rejects_wrong_password(client, evidence):
    """A wrong password is rejected"""
    r = client.post("/api/auth/login", json={"email": "manager@restaurant.com", "password": "wrong-password"})
    evidence.check("POST /api/auth/login with a wrong password", "401 'Invalid email or password'",
                   f"{r.status_code}: {r.get_json().get('message')}", r.status_code == 401)


@req("FR-03")
@pytest.mark.parametrize("path", ["/api/dashboard/summary", "/api/sales", "/api/forecast", "/api/simulation",
                                  "/api/recommendations", "/api/waste/overview", "/api/reports"])
def test_data_requires_sign_in(client, evidence, path):
    """Application data requires a signed-in user"""
    r = client.get(path)
    evidence.check(f"GET {path} without a token", "401", r.status_code, r.status_code == 401)


@req("NFR-03")
def test_passwords_are_hashed(app, evidence):
    """Passwords are stored only as bcrypt hashes"""
    from models import User

    with app.app_context():
        user = User.query.filter_by(email="manager@restaurant.com").first()
        stored = user.password_hash
    evidence.check("Read the stored password of the demo account", "bcrypt hash ($2b$...), not the plain password",
                   stored[:7] + "...", stored.startswith("$2") and "password123" not in stored)


@req("NFR-03")
def test_expired_session_rejected(app, client, evidence):
    """An expired session token is rejected"""
    from flask_jwt_extended import create_access_token

    with app.app_context():
        expired = create_access_token(identity="1", expires_delta=timedelta(seconds=-5))
    r = client.get("/api/dashboard/summary", headers={"Authorization": f"Bearer {expired}"})
    evidence.check("GET /api/dashboard/summary with a token that expired 5 s ago", "401 'Session expired'",
                   f"{r.status_code}: {r.get_json().get('message')}", r.status_code == 401)


@req("NFR-03")
def test_active_session_is_extended(app, client, evidence):
    """A token close to expiry is renewed while the user is active"""
    from flask_jwt_extended import create_access_token

    with app.app_context():
        soon = create_access_token(identity="1", expires_delta=timedelta(minutes=5))
        fresh = create_access_token(identity="1")
    r1 = client.get("/api/auth/me", headers={"Authorization": f"Bearer {soon}"})
    r2 = client.get("/api/auth/me", headers={"Authorization": f"Bearer {fresh}"})
    has1, has2 = "X-Refreshed-Token" in r1.headers, "X-Refreshed-Token" in r2.headers
    evidence.check("GET /api/auth/me with a token expiring in 5 min, then a new 30 min token",
                   "renewed token only for the expiring one", f"expiring: {has1}, fresh: {has2}", has1 and not has2)


@req("NFR-03")
def test_session_lifetime_is_30_minutes(app, evidence):
    """Sessions are configured to expire after 30 minutes"""
    value = app.config["JWT_ACCESS_TOKEN_EXPIRES"]
    evidence.check("Read JWT_ACCESS_TOKEN_EXPIRES", "30 minutes", value, value == timedelta(minutes=30))


# ---------------------------------------------------------------- sales

@req("FR-04")
def test_record_sale(client, auth, evidence):
    """A sale can be recorded on the latest trading day"""
    latest = client.get("/api/sales/menu-items", headers=auth).get_json()["latestDate"]
    r = client.post("/api/sales", headers=auth, json={"date": latest, "items": [{"name": "Laksa", "quantity": 3, "price": 12.5}]})
    sale = r.get_json()["sales"][0]
    evidence.check(f"POST /api/sales 3 x Laksa at $12.50 on {latest}", "201, revenue 37.50",
                   f"{r.status_code}, revenue {sale['revenue']}", r.status_code == 201 and sale["revenue"] == 37.5)


@req("FR-04", "NFR-04")
@pytest.mark.parametrize("payload", [
    [{"name": "Laksa", "quantity": 1}],
    {"items": ["Laksa"]},
    {"items": []},
    {"items": [{"name": "Laksa", "quantity": "two"}]},
    {"items": [{"name": "Laksa", "quantity": -1}]},
    {"items": [{"name": "", "quantity": 1}]},
    {"date": "2024-13-40", "items": [{"name": "Laksa", "quantity": 1}]},
])
def test_invalid_sale_rejected(client, auth, evidence, payload):
    """Invalid sales entries are rejected with a message"""
    r = client.post("/api/sales", headers=auth, json=payload)
    evidence.check(f"POST /api/sales {payload}", "400 with a message", f"{r.status_code}: {r.get_json().get('message')}",
                   r.status_code == 400)


@req("FR-05")
def test_sales_history_and_search(client, auth, evidence):
    """Sales history lists records and search filters them"""
    history = client.get("/api/sales/history", headers=auth).get_json()["history"]
    found = client.get("/api/sales?search=Laksa", headers=auth).get_json()["sales"]
    only_laksa = all("Laksa" in s["menu_item_name"] for s in found)
    evidence.check("GET /api/sales/history; GET /api/sales?search=Laksa", "history rows; search returns only Laksa",
                   f"{len(history)} history rows; {len(found)} results, all Laksa: {only_laksa}",
                   len(history) > 0 and len(found) > 0 and only_laksa)


@req("FR-05")
def test_sales_overview(client, auth, evidence):
    """The overview reports the latest day's sales"""
    s = client.get("/api/sales/overview", headers=auth).get_json()["stats"]
    evidence.check("GET /api/sales/overview", "latest date 2025-01-01, portions and revenue > 0",
                   f"{s['date']}, {s['unitsSold']} portions, ${s['totalRevenue']}",
                   s["date"] == "2025-01-01" and s["unitsSold"] > 0 and s["totalRevenue"] > 0)


# ---------------------------------------------------------------- waste

@req("FR-06")
def test_log_waste(client, auth, evidence):
    """A waste entry can be logged"""
    r = client.post("/api/waste", headers=auth, json={"foodItem": "Laksa", "quantity": 1.5, "unit": "kg",
                                                      "reason": "expired", "costImpact": 6})
    w = r.get_json()["waste"]
    evidence.check("POST /api/waste 1.5 kg Laksa, expired, $6", "201, source manual",
                   f"{r.status_code}, source {w['source']}, {w['quantity']} {w['unit']}",
                   r.status_code == 201 and w["source"] == "manual")


@req("FR-06", "NFR-04")
@pytest.mark.parametrize("payload", [{"foodItem": "", "quantity": 1}, {"foodItem": "Laksa", "quantity": "x"},
                                     {"foodItem": "Laksa", "quantity": 0}, {"foodItem": "Laksa", "quantity": "nan"},
                                     {"foodItem": "Laksa", "quantity": "inf"}, ["Laksa", 1]])
def test_invalid_waste_rejected(client, auth, evidence, payload):
    """Invalid waste entries are rejected with a message"""
    r = client.post("/api/waste", headers=auth, json=payload)
    evidence.check(f"POST /api/waste {payload}", "400 with a message", f"{r.status_code}: {r.get_json().get('message')}",
                   r.status_code == 400)


@req("FR-07", "NFR-07")
def test_waste_sources_kept_separate(client, auth, evidence):
    """Simulated overproduction and logged waste are reported separately"""
    body = client.get("/api/waste/overview", headers=auth).get_json()
    est, logged = body["estimated"], body["logged"]
    evidence.check("GET /api/waste/overview after logging one entry",
                   "separate 'estimated' (portions, labelled simulated) and 'logged' sections",
                   f"estimated {est['portions']:,.0f} portions ({est['method']}); logged {logged['entries']} entries",
                   est["portions"] > 0 and "Simulated" in (est["method"] or "") and logged["entries"] >= 1)


# ---------------------------------------------------------------- models and simulation

@req("FR-08")
def test_comparison_results_available(client, auth, evidence):
    """Both comparison tracks are served with metrics and significance tests"""
    body = client.get("/api/forecast", headers=auth).get_json()
    a, b = body["trackA"], body["trackB"]
    complete = all(r["wape"] is not None and r["r2"] is not None for r in a + b)
    has_cv = all(r["cv_wape_mean"] is not None for r in a if r["info_set"] != "reference")
    has_p = any(r["p_vs_baseline"] is not None for r in a) and any(r["p_vs_baseline"] is not None for r in b)
    evidence.check("GET /api/forecast", "Track A and B results with WAPE, R2, rolling WAPE and p-values",
                   f"{len(a)} Track A rows, {len(b)} Track B rows; metrics {complete}, rolling {has_cv}, p-values {has_p}",
                   len(a) >= 8 and len(b) >= 6 and complete and has_cv and has_p)


@req("FR-09")
def test_same_test_period_for_all_models(client, auth, evidence):
    """Every daily model is evaluated on the same test days, after the training days"""
    body = client.get("/api/forecast", headers=auth).get_json()
    d = body["design"]
    n_tests = {r["n_test"] for r in body["trackA"]}
    evidence.check("GET /api/forecast design", "one test size for every model; train + test = 367 days",
                   f"split {d['splitDate']}, train {d['trainDays']}, test {d['testDays']}, n_test values {n_tests}",
                   len(n_tests) == 1 and d["trainDays"] + d["testDays"] == 367)


@req("FR-08", "FR-09")
def test_reference_row_is_not_ranked(client, auth, evidence):
    """The leaked reference result is shown but never chosen as the best model"""
    body = client.get("/api/forecast", headers=auth).get_json()
    ref = [r for r in body["trackA"] if r["info_set"] == "reference"]
    evidence.check("GET /api/forecast", "one reference row, best Track A model is a real forecast",
                   f"{len(ref)} reference row(s), best = {body['best']['A']}",
                   len(ref) == 1 and body["best"]["A"] != ref[0]["label"])


@req("FR-10")
def test_simulation_grid(client, auth, evidence):
    """The simulation covers both plans for margins 0% to 20%"""
    body = client.get("/api/simulation", headers=auth).get_json()
    margins = {p: sorted(round(r["margin"] * 100) for r in rows) for p, rows in body["policies"].items()}
    ok = len(margins) == 2 and all(m == list(range(21)) for m in margins.values())
    evidence.check("GET /api/simulation", "2 plans x 21 margins (0-20%), with assumptions",
                   f"{ {p: len(m) for p, m in margins.items()} }, {len(body['assumptions'])} assumptions",
                   ok and len(body["assumptions"]) >= 5)


@req("FR-10")
def test_simulation_headline_consistent(client, auth, evidence):
    """The headline comparison matches the 10% rows of the grid"""
    body = client.get("/api/simulation", headers=auth).get_json()
    s = body["summary"]
    rule10 = next(r for r in body["policies"][s["baseline"]] if round(r["margin"] * 100) == 10)
    model10 = next(r for r in body["policies"][s["model"]] if round(r["margin"] * 100) == 10)
    expected = (rule10["overproduction"] - model10["overproduction"]) / rule10["overproduction"] * 100
    evidence.check("GET /api/simulation, recompute the 10% reduction from the grid",
                   f"{expected:.1f}% (from grid)", f"{s['same_margin_reduction_pct']:.1f}% (summary), "
                   f"CI {s['same_margin_reduction_ci'][0]:.1f} to {s['same_margin_reduction_ci'][1]:.1f}",
                   abs(expected - s["same_margin_reduction_pct"]) < 0.1)


@req("FR-11")
def test_preparation_plan_per_day(client, auth, evidence):
    """A preparation plan exists for each test day and can be selected by date"""
    body = client.get("/api/recommendations", headers=auth).get_json()
    day = client.get("/api/recommendations?date=2024-12-01", headers=auth).get_json()
    evidence.check("GET /api/recommendations; then ?date=2024-12-01", "74 test days; plan for the chosen day",
                   f"{len(body['dates'])} days; {len(day['recommendations'])} items on {day['summary']['date']}",
                   len(body["dates"]) == 74 and day["summary"]["date"] == "2024-12-01" and day["recommendations"])


@req("FR-11", "NFR-04")
def test_plan_rejects_date_outside_test_period(client, auth, evidence):
    """A date outside the test period is rejected"""
    r = client.get("/api/recommendations?date=2023-01-01", headers=auth)
    evidence.check("GET /api/recommendations?date=2023-01-01", "400 with a message",
                   f"{r.status_code}: {r.get_json().get('message')}", r.status_code == 400)


@req("FR-11")
def test_mark_suggestion_applied(client, auth, evidence):
    """A suggestion can be marked as applied"""
    rec = client.get("/api/recommendations", headers=auth).get_json()["recommendations"][0]
    r = client.post(f"/api/recommendations/{rec['id']}/apply", headers=auth)
    missing = client.post("/api/recommendations/999999/apply", headers=auth)
    evidence.check(f"POST /api/recommendations/{rec['id']}/apply; then id 999999", "200 status applied; then 404",
                   f"{r.status_code} {r.get_json()['recommendation']['status']}; {missing.status_code}",
                   r.status_code == 200 and r.get_json()["recommendation"]["status"] == "applied"
                   and missing.status_code == 404)


@req("FR-12")
def test_anomaly_endpoint(client, auth, evidence):
    """Unusual sales days are listed with the IQR bounds"""
    body = client.get("/api/anomalies", headers=auth).get_json()
    s = body["summary"]
    evidence.check("GET /api/anomalies", "367 days analysed, flagged days with method, IQR bounds",
                   f"{s['days']} days, {s['flagged']} flagged, bounds {s['iqrLower']} to {s['iqrUpper']}",
                   s["days"] == 367 and s["flagged"] == len(body["anomalies"]) and s["iqrLower"] < s["iqrUpper"])


# ---------------------------------------------------------------- reports, dashboard, inventory

@req("FR-13")
@pytest.mark.parametrize("report", ["sales", "waste", "forecast", "comparison", "simulation"])
def test_csv_downloads(client, auth, evidence, report):
    """Each report downloads as a CSV file"""
    r = client.get(f"/api/reports/{report}/download", headers=auth)
    lines = r.data.decode().splitlines()
    evidence.check(f"GET /api/reports/{report}/download", "200 text/csv with a header and rows",
                   f"{r.status_code} {r.mimetype}, {len(lines) - 1} rows",
                   r.status_code == 200 and r.mimetype == "text/csv" and len(lines) > 1)


@req("FR-14")
def test_dashboard_summary(client, auth, evidence):
    """The dashboard reports latest-day sales, best model error and simulated overproduction"""
    body = client.get("/api/dashboard/summary", headers=auth).get_json()
    titles = [k["title"] for k in body["kpis"]]
    needed = ["Sales (latest day)", "Best model error (WAPE)", "Simulated overproduction"]
    evidence.check("GET /api/dashboard/summary", f"KPIs include {needed}; 7-day trend", f"{titles}; {len(body['salesTrend'])} days",
                   all(t in titles for t in needed) and len(body["salesTrend"]) == 7)


@req("FR-15", "NFR-07")
def test_inventory_marked_illustrative(client, auth, evidence):
    """Inventory is returned and flagged as illustrative"""
    body = client.get("/api/inventory", headers=auth).get_json()
    evidence.check("GET /api/inventory", "items listed, illustrative = true with an explanation",
                   f"{len(body['items'])} items, illustrative = {body['illustrative']}",
                   len(body["items"]) > 0 and body["illustrative"] is True and "Illustrative" in body["note"])


@req("FR-16")
def test_retrain_refused_without_ml_libraries(client, auth, evidence, monkeypatch):
    """Retraining is refused when the ML libraries are missing"""
    import importlib.util

    real = importlib.util.find_spec
    monkeypatch.setattr(importlib.util, "find_spec", lambda name, *a: None if name == "tensorflow" else real(name, *a))
    r = client.post("/api/forecast/train", headers=auth)
    evidence.check("POST /api/forecast/train with TensorFlow not installed", "409 explaining the missing library",
                   f"{r.status_code}: {r.get_json().get('message')[:70]}...", r.status_code == 409)


@req("FR-16")
def test_retrain_runs_one_at_a_time(client, auth, evidence, monkeypatch):
    """A second retraining request is refused while one is running"""
    import importlib.util
    import routes.forecast as forecast

    class Running:
        def poll(self):
            return None

    started = []
    monkeypatch.setattr(importlib.util, "find_spec", lambda name, *a: object())
    monkeypatch.setattr(forecast.subprocess, "Popen", lambda *a, **k: started.append(1) or Running())
    monkeypatch.setitem(forecast._training, "process", None)
    first = client.post("/api/forecast/train", headers=auth)
    second = client.post("/api/forecast/train", headers=auth)
    evidence.check("POST /api/forecast/train twice (training process simulated)", "first 200 starts one run; second 409",
                   f"{first.status_code}, {second.status_code}, runs started {len(started)}",
                   first.status_code == 200 and second.status_code == 409 and len(started) == 1)


# ---------------------------------------------------------------- robustness and performance

@req("NFR-04")
@pytest.mark.parametrize("method,path", [("GET", "/api/does-not-exist"), ("POST", "/api/forecast/generate"),
                                         ("GET", "/api/sales?limit=abc")])
def test_bad_requests_get_clear_errors(client, auth, evidence, method, path):
    """Unknown endpoints and malformed parameters return 4xx JSON, not a server error"""
    r = client.open(path, method=method, headers=auth)
    evidence.check(f"{method} {path}", "404 or 400 JSON message", f"{r.status_code}: {r.get_json().get('message')}",
                   r.status_code in (400, 404) and r.is_json)


@req("NFR-02")
@pytest.mark.parametrize("path", ["/api/dashboard/summary", "/api/forecast", "/api/simulation", "/api/recommendations",
                                  "/api/waste/overview", "/api/anomalies", "/api/sales/history"])
def test_response_time(client, auth, evidence, path):
    """Main requests respond within one second"""
    client.get(path, headers=auth)
    start = time.perf_counter()
    r = client.get(path, headers=auth)
    ms = (time.perf_counter() - start) * 1000
    evidence.check(f"GET {path} (second request)", "200 in under 1000 ms", f"{r.status_code} in {ms:.0f} ms",
                   r.status_code == 200 and ms < 1000)


# ---------------------------------------------------------------- honest reporting

@req("NFR-07")
def test_no_accuracy_figure_anywhere(client, auth, evidence):
    """No API response contains an 'accuracy' figure"""
    paths = ["/api/dashboard/summary", "/api/forecast", "/api/forecast/compare", "/api/public/overview",
             "/api/simulation", "/api/recommendations", "/api/waste/overview"]
    hits = [p for p in paths if "accuracy" in client.get(p, headers=auth).data.decode().lower()]
    evidence.check(f"GET {len(paths)} endpoints and search for 'accuracy'", "not found in any response",
                   ", ".join(hits) or "not found", not hits)
