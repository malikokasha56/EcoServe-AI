"""Unit tests of the machine learning layer on small hand-checked examples (needs requirements-ml.txt)."""
import pytest

np = pytest.importorskip("numpy")
pd = pytest.importorskip("pandas")
pytest.importorskip("sklearn")
pytest.importorskip("scipy")

from ml import anomaly, experiment, simulation  # noqa: E402
from ml.forecasting import evaluate  # noqa: E402

req = pytest.mark.req


# ---------------------------------------------------------------- metrics

@req("NFR-06")
def test_error_metrics_hand_calculation(evidence):
    """MAE, RMSE, WAPE, MAPE and R2 match a hand calculation"""
    m = evaluate(np.array([100, 200, 300]), np.array([110, 190, 330]))
    expected = {"mae": 16.667, "rmse": 19.149, "wape": 8.333, "mape": 8.333, "r2": 0.945}
    got = {k: round(m[k], 3) for k in expected}
    evidence.check("actual [100, 200, 300], forecast [110, 190, 330]", expected, got,
                   all(abs(got[k] - v) < 0.001 for k, v in expected.items()))


@req("NFR-06")
def test_wape_and_mape_with_zero_demand(evidence):
    """MAPE skips zero-demand days; WAPE is undefined when all demand is zero"""
    m = evaluate(np.array([0, 100]), np.array([10, 90]))
    all_zero = evaluate(np.array([0, 0]), np.array([1, 1]))
    evidence.check("actual [0, 100] vs [10, 90]; actual [0, 0] vs [1, 1]", "MAPE 10.0 (zero day skipped); WAPE NaN",
                   f"MAPE {m['mape']:.1f}; WAPE {all_zero['wape']}", abs(m["mape"] - 10) < 1e-9 and np.isnan(all_zero["wape"]))


# ---------------------------------------------------------------- significance test

@req("NFR-06", "FR-08")
def test_diebold_mariano_behaviour(evidence):
    """The Diebold-Mariano test separates a clearly better forecast and is symmetric"""
    rng = np.random.default_rng(0)
    actual = rng.normal(100, 10, 74)
    good = actual + rng.normal(0, 2, 74)
    bad = actual + rng.normal(0, 15, 74)
    p = experiment.diebold_mariano(actual, good, bad)
    p_rev = experiment.diebold_mariano(actual, bad, good)
    same = experiment.diebold_mariano(actual, good, good)
    evidence.check("74 days; errors sd 2 vs sd 15; then identical forecasts",
                   "p < 0.05, same p either way round, no test for identical forecasts",
                   f"p = {p:.2e}, reversed {p_rev:.2e}, identical -> {same}", p < 0.05 and abs(p - p_rev) < 1e-12 and same is None)


@req("NFR-06", "FR-08")
def test_diebold_mariano_no_false_alarm(evidence):
    """Two equally good forecasts are usually not called different"""
    rng = np.random.default_rng(1)
    rejections = 0
    for _ in range(200):
        actual = rng.normal(100, 10, 74)
        a, b = actual + rng.normal(0, 5, 74), actual + rng.normal(0, 5, 74)
        rejections += experiment.diebold_mariano(actual, a, b) < 0.05
    rate = rejections / 200 * 100
    evidence.check("200 trials of two equally accurate forecasts", "about 5% called significant (below 10%)",
                   f"{rate:.1f}%", rate < 10)


# ---------------------------------------------------------------- equal information and no leakage

def _toy_sales():
    rows = [
        ("2024-01-01", 1, "A", 10, False), ("2024-01-02", 1, "A", 20, True), ("2024-01-02", 1, "A", 40, False),
        ("2024-01-03", 1, "A", 30, False), ("2024-01-05", 1, "A", 50, False),
    ]
    return pd.DataFrame([{
        "date": d, "restaurant_id": r, "menu_item_name": i, "quantity_sold": q, "has_promotion": p,
        "special_event": False, "weather_condition": "Sunny", "restaurant_type": "Cafe", "meal_type": "Lunch",
        "typical_ingredient_cost": 2.0, "observed_market_price": 5.0, "actual_selling_price": 6.0,
    } for d, r, i, q, p in rows])


@req("FR-09")
def test_daily_inputs_exclude_record_count(evidence):
    """Daily models never receive the number of records per day"""
    daily = experiment.build_daily(_toy_sales())
    features = set(experiment._calendar("A2"))
    leaked = [c for c in features if "count" in c or c in ("n", "records", "n_records")]
    evidence.check("Build Track A inputs (A2) from toy sales", "no record-count input; calendar + 4 covariates",
                   f"{len(features)} inputs, record-count inputs: {leaked or 'none'}",
                   not leaked and set(experiment.COVARIATES) <= features)


@req("FR-09")
def test_daily_series_has_no_gaps(evidence):
    """Missing days become zero-demand days so the daily series is continuous"""
    daily = experiment.build_daily(_toy_sales())
    jan4 = daily.loc[daily["date"] == "2024-01-04", "y"].iloc[0]
    evidence.check("Toy sales on 1, 2, 3 and 5 January", "5 consecutive days, 4 January = 0",
                   f"{len(daily)} days, 4 January = {jan4}", len(daily) == 5 and jan4 == 0)


@req("FR-09")
def test_history_feature_uses_earlier_days_only(evidence):
    """The item-level history feature only uses days before the record (no leakage)"""
    d, _ = experiment.build_items(_toy_sales(), pd.Timestamp("2024-01-05"))
    by_day = d.groupby(d["date"].dt.strftime("%m-%d"))[["prior_mean", "prior_count"]].first()
    got = {k: (round(v.prior_mean, 2), int(v.prior_count)) for k, v in by_day.iterrows()}
    expected = {"01-02": (10.0, 1), "01-03": (23.33, 3), "01-05": (25.0, 4)}
    evidence.check("Sales of A on 1 Jan (10), 2 Jan (20, 40), 3 Jan (30), 5 Jan (50)",
                   "2 Jan sees only 10; 3 Jan sees 10, 20, 40; 5 Jan sees all four earlier sales",
                   {k: got[k] for k in expected}, all(got[k] == v for k, v in expected.items()))


@req("FR-09")
def test_item_split_is_chronological(evidence):
    """Item-level training records all come before the test records"""
    df = pd.read_csv(experiment_csv())
    d, train = experiment.build_items(df, pd.Timestamp("2024-10-20"))
    last_train, first_test = d.loc[train, "date"].max(), d.loc[~train, "date"].min()
    evidence.check("Split the real dataset at 2024-10-20", "last training day before first test day; 2,031 test records",
                   f"train to {last_train:%Y-%m-%d}, test from {first_test:%Y-%m-%d}, {int((~train).sum())} test records",
                   last_train < first_test and int((~train).sum()) == 2031)


@req("FR-09")
def test_mean_baseline_uses_history_to_previous_day(evidence):
    """The mean baseline uses all demand up to the day before each forecast, like the other models"""
    daily = pd.DataFrame({"y": [10.0, 20.0, 30.0, 40.0, 50.0]})
    pred = experiment.mean_baseline(daily, 3, np.array([3, 4]))
    evidence.check("Demand 10, 20, 30, 40, 50, forecast days 4 and 5", "20.0 (mean of 3 days) and 25.0 (mean of 4 days)",
                   list(pred), list(pred) == [20.0, 25.0])


@req("FR-09", "NFR-06")
def test_item_level_significance_uses_daily_totals(evidence):
    """At item level the significance test treats each test day as one observation"""
    rng = np.random.default_rng(5)
    days = np.repeat(np.arange(30), 20)
    actual = rng.gamma(3, 100, len(days))
    a, b = actual + rng.normal(0, 20, len(days)), actual + rng.normal(0, 22, len(days))
    p_rows = experiment.diebold_mariano(actual, a, b)
    p_days = experiment.diebold_mariano(actual, a, b, groups=days)
    evidence.check("600 records on 30 days, two similar forecasts", "per day p value computed on 30 values",
                   f"per record p = {p_rows:.3g}, per day p = {p_days:.3g}", p_days is not None and 0 <= p_days <= 1)


@req("FR-09", "NFR-05")
def test_pipeline_reads_only_dataset_rows(app, evidence):
    """Retraining uses only the public dataset, never sales typed into the application"""
    from datetime import date
    from extensions import db
    from models import SalesRecord
    from precompute import _dataset_df

    with app.app_context():
        db.session.add(SalesRecord(restaurant_id=1, date=date(2026, 10, 1), menu_item_name="Laksa", quantity_sold=5))
        db.session.commit()
        df = _dataset_df()
    evidence.check("Add a sale dated 1 October 2026 in the app, then load the pipeline input",
                   "10,000 rows, all dated within the dataset period",
                   f"{len(df):,} rows, last date {max(df['date'])}", len(df) == 10000 and str(max(df["date"])) == "2025-01-01")


@req("FR-09")
def test_seasonal_naive_is_last_week(evidence):
    """The seasonal naive baseline repeats the value from seven days earlier"""
    daily = pd.DataFrame({"y": np.arange(20, dtype=float)})
    pred = experiment.seasonal_naive(daily, 14, np.arange(14, 20))
    evidence.check("Daily demand 0..19, forecast days 14-19", "7, 8, 9, 10, 11, 12", list(pred.astype(int)),
                   list(pred) == [7, 8, 9, 10, 11, 12])


def experiment_csv():
    import os
    return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                        "restaurant_sales_data.csv")


# ---------------------------------------------------------------- simulation

@req("FR-10", "NFR-06")
def test_simulation_hand_calculation(evidence):
    """Overproduction, shortfall, fill rate and costs match a hand calculation"""
    out = simulation.outcomes(np.array([10.0, 20.0]), np.array([10.0, 10.0]), 0.10,
                              cost=np.array([2.0, 2.0]), price=np.array([5.0, 5.0]))
    expected = {"prepared": 22, "overproduction": 1, "shortfall": 9, "fill_rate": 70, "waste_cost": 2, "lost_margin": 27}
    got = {k: round(out[k], 6) for k in expected}
    evidence.check("demand [10, 20], forecast [10, 10], margin 10%, cost 2, price 5", expected, got,
                   all(abs(got[k] - v) < 1e-6 for k, v in expected.items()))


@req("FR-10", "NFR-06")
def test_simulation_margin_trade_off(evidence):
    """A larger margin never reduces overproduction or the share of demand served"""
    rng = np.random.default_rng(3)
    actual = rng.gamma(3, 100, 500)
    forecast = actual * rng.normal(1, 0.3, 500).clip(0.1)
    cost, price = np.full(500, 3.0), np.full(500, 8.0)
    rows = [simulation.outcomes(actual, forecast, m, cost, price) for m in simulation.MARGINS]
    over_ok = all(b["overproduction"] >= a["overproduction"] for a, b in zip(rows, rows[1:]))
    fill_ok = all(b["fill_rate"] >= a["fill_rate"] for a, b in zip(rows, rows[1:]))
    evidence.check("500 random records, margins 0% to 20%", "overproduction and fill rate never decrease",
                   f"overproduction {rows[0]['overproduction']:,.0f} -> {rows[-1]['overproduction']:,.0f}, "
                   f"fill {rows[0]['fill_rate']:.1f}% -> {rows[-1]['fill_rate']:.1f}%", over_ok and fill_ok)


@req("FR-10", "NFR-06")
def test_simulation_is_reproducible(evidence):
    """Running the simulation twice gives identical results, including confidence intervals"""
    rng = np.random.default_rng(4)
    n = 300
    test = pd.DataFrame({
        "date": np.repeat(pd.date_range("2024-01-01", periods=30), 10),
        "quantity_sold": rng.gamma(3, 100, n), "typical_ingredient_cost": 3.0, "actual_selling_price": 8.0,
    })
    policies = {"rule": test["quantity_sold"].mean() * np.ones(n), "model": test["quantity_sold"] * rng.normal(1, 0.2, n)}
    a = simulation.run(test, policies, "rule", "model", log=lambda *_: None)["summary"]
    b = simulation.run(test, policies, "rule", "model", log=lambda *_: None)["summary"]
    evidence.check("Run the same simulation twice", "identical summaries",
                   f"reduction {a['same_margin_reduction_pct']:.2f}% vs {b['same_margin_reduction_pct']:.2f}%, "
                   f"CI {a['same_margin_reduction_ci']} vs {b['same_margin_reduction_ci']}", a == b)


@req("FR-10")
def test_matched_service_margin(evidence):
    """The matched margin is the smallest that reaches the target share of demand served"""
    actual, forecast = np.full(10, 100.0), np.full(10, 80.0)
    cost = price = np.ones(10)
    m = simulation.margin_for_fill_rate(actual, forecast, 90.0, cost, price)
    reached = simulation.outcomes(actual, forecast, m, cost, price)["fill_rate"]
    below = simulation.outcomes(actual, forecast, m - 0.0025, cost, price)["fill_rate"]
    evidence.check("demand 100, forecast 80, target 90% served", "margin 12.5% (80 x 1.125 = 90)",
                   f"margin {m:.4f}, served {reached:.2f}%, one step lower {below:.2f}%",
                   abs(m - 0.125) < 1e-9 and reached >= 90 > below)


# ---------------------------------------------------------------- anomaly detection

@req("FR-12")
def test_anomaly_rule(evidence):
    """A clear outlier is flagged and the IQR bounds sit around Q1 and Q3"""
    values = np.append(np.arange(90.0, 111.0), 500.0)
    res = anomaly.detect(values)
    q1, q3 = np.percentile(values, [25, 75])
    flagged = [int(v["value"]) for v in res if v["is_anomaly"]]
    lower, upper = res[0]["lower"], res[0]["upper"]
    evidence.check("21 values from 90 to 110 and one value of 500", "only 500 flagged; bounds Q1 - 1.5 IQR and Q3 + 1.5 IQR",
                   f"flagged {flagged}; bounds {lower:.2f} to {upper:.2f} (Q1 {q1}, Q3 {q3})",
                   flagged == [500] and abs(lower - (q1 - 1.5 * (q3 - q1))) < 1e-9 and abs(upper - (q3 + 1.5 * (q3 - q1))) < 1e-9)
