"""Generates the report figures from the dataset and backend/data/results.json.

Run with the machine learning environment:  python report/make_figures.py
"""
import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "report", "figures")
os.makedirs(OUT, exist_ok=True)

GREEN, RED, PURPLE, BLUE, AMBER, GREY = "#10b981", "#ef4444", "#8b5cf6", "#3b82f6", "#f59e0b", "#6b7280"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.spines.top": False,
                     "axes.spines.right": False, "figure.dpi": 100, "savefig.dpi": 220, "savefig.bbox": "tight"})

df = pd.read_csv(os.path.join(ROOT, "restaurant_sales_data.csv"))
df["date"] = pd.to_datetime(df["date"])
daily = df.groupby("date").agg(total=("quantity_sold", "sum"), records=("quantity_sold", "size")).reset_index()
results = json.load(open(os.path.join(ROOT, "backend", "data", "results.json")))["tables"]
exp = pd.DataFrame(results["experiment_results"])
facts = json.load(open(os.path.join(ROOT, "report", "facts.json")))
SPLIT = pd.Timestamp("2024-10-20")


def save(fig, name):
    fig.savefig(os.path.join(OUT, name))
    plt.close(fig)
    print("wrote", name)


# ---------------------------------------------------------------- data understanding
fig, ax = plt.subplots(figsize=(9, 3.4))
ax.plot(daily["date"], daily["total"], color=GREY, lw=0.9)
ax.plot(daily["date"], daily["total"].rolling(7, center=True).mean(), color=PURPLE, lw=2, label="7 day average")
ax.axvline(SPLIT, color=RED, ls="--", lw=1.2)
ax.axvspan(SPLIT, daily["date"].max(), color=RED, alpha=0.06)
ax.text(SPLIT, ax.get_ylim()[1] * 0.97, "  test period", color=RED, va="top")
ax.set_ylabel("Portions sold per day")
ax.legend(frameon=False, loc="upper left")
save(fig, "fig_daily_demand.png")

fig, ax = plt.subplots(figsize=(5.2, 3.8))
ax.scatter(daily["records"], daily["total"], s=12, color=BLUE, alpha=0.6)
b, a = np.polyfit(daily["records"], daily["total"], 1)
xs = np.linspace(daily["records"].min(), daily["records"].max(), 10)
ax.plot(xs, a + b * xs, color=RED, lw=1.5)
ax.set_xlabel("Sales records on the day")
ax.set_ylabel("Total portions sold")
ax.text(0.03, 0.95, f"R² = {facts['r2_total_on_records']:.2f}", transform=ax.transAxes, va="top")
save(fig, "fig_records_vs_total.png")

fig, ax = plt.subplots(figsize=(6, 3.2))
lags = range(1, 15)
ac = [daily["total"].autocorr(k) for k in lags]
ax.bar(lags, ac, color=[PURPLE if k in (7, 14) else GREY for k in lags])
ax.axhline(0, color="black", lw=0.8)
ax.axhline(1.96 / np.sqrt(len(daily)), color=RED, ls="--", lw=0.8)
ax.axhline(-1.96 / np.sqrt(len(daily)), color=RED, ls="--", lw=0.8)
ax.set_xlabel("Lag (days)")
ax.set_ylabel("Autocorrelation")
ax.set_xticks(list(lags))
save(fig, "fig_autocorrelation.png")

fig, axes = plt.subplots(1, 4, figsize=(11, 3.2), sharey=True)
groups = [
    ("Promotion", df.groupby("has_promotion").quantity_sold.mean().rename({False: "No", True: "Yes"})),
    ("Weekend", df.groupby(df.date.dt.dayofweek >= 5).quantity_sold.mean().rename({False: "Weekday", True: "Weekend"})),
    ("Special event", df.groupby("special_event").quantity_sold.mean().rename({False: "No", True: "Yes"})),
    ("Meal", df.groupby("meal_type").quantity_sold.mean()),
]
for ax, (title, s) in zip(axes, groups):
    ax.bar(s.index.astype(str), s.values, color=[GREY, GREEN, BLUE][: len(s)])
    ax.set_title(title)
    ax.tick_params(axis="x", labelsize=8.5, rotation=20 if len(s) > 2 else 0)
axes[0].set_ylabel("Mean portions per record")
save(fig, "fig_demand_drivers.png")

# ---------------------------------------------------------------- architecture and data model
def box(ax, x, y, w, h, title, lines, color):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.03", fc=color, ec="#374151", alpha=0.18))
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.03", fc="none", ec="#374151"))
    ax.text(x + w / 2, y + h - 0.06, title, ha="center", va="top", weight="bold")
    for i, line in enumerate(lines):
        ax.text(x + w / 2, y + h - 0.2 - i * 0.11, line, ha="center", va="top", fontsize=8.5)


def arrow(ax, x1, y1, x2, y2, label=""):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="->", color="#374151", lw=1.3))
    if label:
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.04, label, ha="center", fontsize=8, color="#374151")


fig, ax = plt.subplots(figsize=(10, 5.2))
ax.set_xlim(0, 3.2)
ax.set_ylim(0, 1.75)
ax.axis("off")
box(ax, 0.05, 1.05, 0.9, 0.62, "Browser", ["React and TypeScript pages", "Recharts visualisations", "JWT kept in local storage"], BLUE)
box(ax, 1.15, 1.05, 0.9, 0.62, "Flask application", ["REST API (11 blueprints)", "JWT authentication", "Serves the built frontend"], GREEN)
box(ax, 2.25, 1.05, 0.9, 0.62, "Database", ["SQLite by default", "PostgreSQL optional", "SQLAlchemy models"], AMBER)
box(ax, 1.15, 0.08, 0.9, 0.7, "Offline pipeline", ["precompute.py", "experiment.py (Tracks A, B)", "simulation.py, anomaly.py", "TensorFlow, Prophet, scikit learn"], PURPLE)
box(ax, 2.25, 0.08, 0.9, 0.7, "Shipped inputs", ["restaurant_sales_data.csv", "(public Kaggle dataset)", "data/results.json", "(stored model results)"], GREY)
box(ax, 0.05, 0.08, 0.9, 0.7, "Launchers", ["START.bat / start.sh", "EcoServe.exe (portable)", "run.py: checks, free port", "Waitress server"], GREY)
arrow(ax, 0.95, 1.36, 1.15, 1.36, "HTTP / JSON")
arrow(ax, 2.05, 1.36, 2.25, 1.36, "ORM")
arrow(ax, 2.7, 0.78, 2.7, 1.05, "")
ax.text(2.74, 0.9, "loaded on start", fontsize=8, color="#374151")
arrow(ax, 2.05, 0.43, 2.25, 0.43, "writes")
arrow(ax, 0.95, 0.43, 1.6, 1.05, "")
ax.text(1.22, 0.85, "starts", fontsize=8, color="#374151")
save(fig, "fig_architecture.png")

fig, ax = plt.subplots(figsize=(10, 6.2))
ax.set_xlim(0, 3.35)
ax.set_ylim(0, 2.45)
ax.axis("off")


def entity(x, top, name, cols, color):
    h = 0.27 + 0.11 * len(cols)
    box(ax, x, top - h, 0.75, h, name, cols, color)
    return top - h, h


core, result = AMBER, PURPLE
ry, rh = entity(0.05, 2.35, "restaurants", ["id (PK)", "name", "restaurant_type"], core)
uy, uh = entity(0.05, 1.45, "users", ["id (PK)", "email (unique)", "password_hash", "role", "restaurant_id (FK)"], core)
sy, sh = entity(0.92, 2.35, "sales_records", ["id (PK)", "restaurant_id (FK)", "source_restaurant_id", "date, menu_item_name",
                                             "meal_type, prices", "has_promotion, special_event", "weather_condition", "quantity_sold"], core)
wy, wh = entity(0.92, 1.05, "waste_records", ["id (PK)", "restaurant_id (FK)", "date, menu_item_name", "quantity, unit, cost",
                                             "source (derived / manual)"], core)
entity(1.8, 2.35, "experiment_results", ["track, info_set, model", "mae, rmse, mape, wape, r2", "cv_wape_mean, cv_wape_sd",
                                         "p_vs_baseline, p_vs_best"], result)
entity(2.6, 2.35, "simulation_results", ["policy, margin", "overproduction, shortfall", "fill_rate",
                                          "waste_cost, lost_margin"], result)
entity(1.8, 1.45, "forecast_records", ["model_type (label)", "forecast_date", "actual_value", "forecast_value"], result)
entity(2.6, 1.45, "recommendations", ["date, menu_item_name", "recommended_quantity", "rule_quantity",
                                       "actual_quantity, status"], result)
arrow(ax, 0.42, ry, 0.42, 1.45)
arrow(ax, 0.8, ry + rh * 0.6, 0.92, ry + rh * 0.6)
arrow(ax, 0.8, ry + rh * 0.3, 0.92, wy + wh * 0.5)
ax.text(1.8, 0.45, "Orange: operational data. Purple: stored results of the offline pipeline.", fontsize=8.5, color="#374151")
ax.text(1.8, 0.33, "Also stored: anomaly_records, simulation_summary, ingredients (illustrative).", fontsize=8.5, color="#374151")
save(fig, "fig_data_model.png")

# ---------------------------------------------------------------- results
a = exp[(exp.track == "A") & (exp.info_set != "reference")].copy()
a = a.sort_values("cv_wape_mean")
fig, ax = plt.subplots(figsize=(8, 4))
y = np.arange(len(a))
colors = [GREY if s == "baseline" else (BLUE if s == "A1" else PURPLE) for s in a.info_set]
ax.barh(y, a.cv_wape_mean, xerr=a.cv_wape_sd, color=colors, alpha=0.85, capsize=3)
ax.scatter(a.wape, y, color="black", zorder=3, s=18, label="80/20 holdout WAPE")
ax.set_yticks(y)
ax.set_yticklabels(a.label)
ax.invert_yaxis()
ax.set_xlabel("WAPE (%), bars: rolling origin mean ± 1 sd")
ax.legend(frameon=False, loc="lower center", bbox_to_anchor=(0.5, 1.0))
save(fig, "fig_trackA_wape.png")

fr = pd.DataFrame(results["forecast_records"])
fr["forecast_date"] = pd.to_datetime(fr["forecast_date"])
piv = fr.pivot_table(index="forecast_date", columns="model_type", values="forecast_value")
act = fr.groupby("forecast_date").actual_value.first()
fig, ax = plt.subplots(figsize=(10, 3.8))
ax.plot(act.index, act.values, color=GREEN, lw=2.2, label="Actual")
for label, color in [("Prophet (A2)", BLUE), ("LSTM (A2)", PURPLE), ("Random Forest (A2)", AMBER), ("Mean baseline", GREY)]:
    ax.plot(piv.index, piv[label], color=color, lw=1.2, ls="--" if label == "Mean baseline" else "-", label=label)
ax.set_ylabel("Portions per day")
ax.legend(frameon=False, ncol=5, loc="upper left", fontsize=8.5)
save(fig, "fig_trackA_series.png")

b = exp[exp.track == "B"].sort_values("wape")
fig, ax = plt.subplots(figsize=(8, 3.4))
ax.barh(b.model, b.wape, color=[GREEN if i == 0 else (GREY if m.startswith(("Mean", "Historical")) else PURPLE) for i, m in enumerate(b.model)])
for i, v in enumerate(b.wape):
    ax.text(v + 0.5, i, f"{v:.1f}%", va="center", fontsize=9)
ax.invert_yaxis()
ax.set_xlabel("WAPE on 2,031 item level test records (%)")
save(fig, "fig_trackB_wape.png")

imp = pd.DataFrame(facts["gb_permutation_importance_mae"], columns=["feature", "mae"]).head(10)
fig, ax = plt.subplots(figsize=(7, 3.6))
ax.barh(imp.feature, imp.mae, color=PURPLE)
ax.invert_yaxis()
ax.set_xlabel("Increase in MAE when the feature is shuffled (portions)")
save(fig, "fig_importance.png")

sim = pd.DataFrame(results["simulation_results"])
s = results["simulation_summary"][0]["data"]
fig, ax1 = plt.subplots(figsize=(8, 3.8))
for policy, color in [(s["baseline"], RED), (s["model"], GREEN)]:
    p = sim[sim.policy == policy]
    ax1.plot(p.margin * 100, p.overproduction / 1000, color=color, lw=2, label=f"{policy}")
ax1.set_xlabel("Safety margin (%)")
ax1.set_ylabel("Overproduction (thousand portions)")
ax1.legend(frameon=False, loc="upper left")
save(fig, "fig_sim_margin.png")

fig, ax = plt.subplots(figsize=(6.4, 4.2))
for policy, color in [(s["baseline"], RED), (s["model"], GREEN)]:
    p = sim[sim.policy == policy]
    ax.plot(p.fill_rate, p.overproduction / 1000, marker="o", ms=3, color=color, label=policy)
ax.axvline(s["baseline_fill_rate"], color=GREY, ls=":", lw=1)
ax.set_xlabel("Share of demand served (%)")
ax.set_ylabel("Overproduction (thousand portions)")
ax.legend(frameon=False)
save(fig, "fig_sim_tradeoff.png")

an = pd.DataFrame(results["anomaly_records"])
an["date"] = pd.to_datetime(an["date"])
fig, ax = plt.subplots(figsize=(9, 3.2))
ax.scatter(an.date, an.value, s=8, color=[RED if f else GREY for f in an.is_anomaly])
ax.axhline(an.upper_bound.iloc[0], color=RED, ls="--", lw=1)
ax.axhline(an.expected.iloc[0], color=GREY, ls=":", lw=1)
ax.set_ylabel("Portions sold per day")
save(fig, "fig_anomalies.png")
