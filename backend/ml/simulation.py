"""Preparation simulation on the item-level test records.

The dataset records sales only, so waste cannot be measured. Instead each preparation plan is replayed on
days the models never saw: prepared = forecast x (1 + safety margin). Assumptions:
  - unsold portions are wasted (perishable food, no carry-over to the next day),
  - recorded sales equal true demand (sales were not capped by stock running out),
  - ingredient cost per portion is the record's typical_ingredient_cost, and a portion that could not be
    served loses its margin (selling price minus ingredient cost).
"""
import numpy as np

MARGINS = [round(m, 2) for m in np.arange(0, 0.21, 0.01)]
# Margins used only to match service levels; a negative value means preparing below the forecast.
FINE_MARGINS = np.round(np.arange(-0.5, 1.0001, 0.0025), 4)
DEFAULT_MARGIN = 0.10
BOOTSTRAP = 1000
SEED = 42


def outcomes(actual, forecast, margin, cost, price):
    prepared = forecast * (1 + margin)
    over = np.maximum(prepared - actual, 0)
    short = np.maximum(actual - prepared, 0)
    served = np.minimum(prepared, actual)
    return {
        "prepared": float(prepared.sum()),
        "overproduction": float(over.sum()),
        "shortfall": float(short.sum()),
        "fill_rate": float(served.sum() / actual.sum() * 100),
        "short_days_pct": float((short > 0).mean() * 100),
        "waste_cost": float((over * cost).sum()),
        "lost_margin": float((short * np.maximum(price - cost, 0)).sum()),
    }


# Smallest margin at which a plan serves at least the target share of demand (fill rate rises with margin).
def margin_for_fill_rate(actual, forecast, target, cost, price):
    for m in FINE_MARGINS:
        if outcomes(actual, forecast, m, cost, price)["fill_rate"] >= target:
            return float(m)
    return float(FINE_MARGINS[-1])


def run(test, policies, baseline, model, default_margin=DEFAULT_MARGIN, log=print):
    """test: item-level test rows; policies: {name: forecast array}; baseline/model: policy names."""
    actual = test["quantity_sold"].to_numpy(dtype=float)
    cost = test["typical_ingredient_cost"].to_numpy(dtype=float)
    price = test["actual_selling_price"].to_numpy(dtype=float)

    grid = []
    for name, forecast in policies.items():
        for m in MARGINS:
            grid.append({"policy": name, "margin": m, **outcomes(actual, forecast, m, cost, price)})

    base = outcomes(actual, policies[baseline], default_margin, cost, price)
    same = outcomes(actual, policies[model], default_margin, cost, price)
    # Like-for-like on service: the margin at which the model serves the same share of demand as the baseline.
    m_star = margin_for_fill_rate(actual, policies[model], base["fill_rate"], cost, price)
    matched = outcomes(actual, policies[model], m_star, cost, price)

    # Uncertainty: resample whole test days with replacement and recompute each comparison.
    rng = np.random.default_rng(SEED)
    days = test["date"].to_numpy()
    unique_days = np.unique(days)
    day_index = {d: np.where(days == d)[0] for d in unique_days}

    def per_record(forecast, m):
        prepared = forecast * (1 + m)
        return np.maximum(prepared - actual, 0), np.minimum(prepared, actual)

    b_over, b_served = per_record(policies[baseline], default_margin)
    s_over, s_served = per_record(policies[model], default_margin)
    m_over, _ = per_record(policies[model], m_star)
    boot = {"same": [], "fill": [], "matched": []}
    for _ in range(BOOTSTRAP):
        idx = np.concatenate([day_index[d] for d in rng.choice(unique_days, len(unique_days), replace=True)])
        b, demand = b_over[idx].sum(), actual[idx].sum()
        boot["same"].append((b - s_over[idx].sum()) / b * 100)
        boot["fill"].append((s_served[idx].sum() - b_served[idx].sum()) / demand * 100)
        boot["matched"].append((b - m_over[idx].sum()) / b * 100)
    ci = {k: [float(x) for x in np.percentile(v, [2.5, 97.5])] for k, v in boot.items()}

    def pct_less(x):
        return (base["overproduction"] - x) / base["overproduction"] * 100

    summary = {
        "baseline": baseline,
        "model": model,
        "default_margin": default_margin,
        "baseline_overproduction": base["overproduction"],
        "baseline_fill_rate": base["fill_rate"],
        "baseline_waste_cost": base["waste_cost"],
        "same_margin_overproduction": same["overproduction"],
        "same_margin_fill_rate": same["fill_rate"],
        "same_margin_waste_cost": same["waste_cost"],
        "same_margin_reduction_pct": pct_less(same["overproduction"]),
        "same_margin_reduction_ci": ci["same"],
        "same_margin_fill_gain": same["fill_rate"] - base["fill_rate"],
        "same_margin_fill_gain_ci": ci["fill"],
        "matched_margin": m_star,
        "matched_overproduction": matched["overproduction"],
        "matched_fill_rate": matched["fill_rate"],
        "matched_waste_cost": matched["waste_cost"],
        "matched_reduction_pct": pct_less(matched["overproduction"]),
        "matched_reduction_ci": ci["matched"],
        "test_records": len(test),
        "test_days": len(unique_days),
        "actual_demand": float(actual.sum()),
    }
    log(f"  Same {default_margin:.0%} margin: {baseline} wastes {base['overproduction']:,.0f} portions at "
        f"{base['fill_rate']:.1f}% fill; {model} wastes {same['overproduction']:,.0f} at {same['fill_rate']:.1f}% "
        f"({summary['same_margin_reduction_pct']:.1f}% less, CI {ci['same'][0]:.1f} to {ci['same'][1]:.1f}; "
        f"fill +{summary['same_margin_fill_gain']:.1f} pts, CI {ci['fill'][0]:.1f} to {ci['fill'][1]:.1f})")
    log(f"  Same {base['fill_rate']:.1f}% fill: {model} at {m_star:+.1%} margin wastes {matched['overproduction']:,.0f} "
        f"({summary['matched_reduction_pct']:.1f}% less, CI {ci['matched'][0]:.1f} to {ci['matched'][1]:.1f})")
    return {"grid": grid, "summary": summary}
