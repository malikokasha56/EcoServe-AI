"""Controlled model comparison.

Track A: daily total demand. Every model forecasts one day ahead from the same information:
  the demand history up to the previous day plus A1 = calendar, or A2 = calendar + the day's promotion,
  event and weather mix (assumed known in advance). Prophet is refitted each day for this reason.
  The number of sales records on a day is never used, because it is not known in advance.
Track B: item-level demand (one restaurant, one menu item, one day). Every model receives
  the same feature table, and the historical-average rule is included as a baseline.
Both tracks use the same chronological cut: the first 80% of days train, the last 20% test.
Track A is also checked with rolling-origin evaluation over four later windows.
"""
import time

import numpy as np
import pandas as pd

from ml.forecasting import evaluate, SPLIT_RATIO, SEED

LOOKBACK = 28
CV_FOLDS = 4
COVARIATES = ["promo_share", "event_share", "rainy_share", "cloudy_share"]


# ---------------------------------------------------------------- significance

# Diebold-Mariano test for one step ahead forecasts with absolute-error loss and the Harvey-Leybourne-Newbold
# small-sample correction: p < 0.05 means the two forecasts' errors differ by more than chance would explain.
# With groups (item level), loss differences are first summed per day, because records on the same day are
# correlated, so the test is run on one value per test day.
def diebold_mariano(actual, pred_a, pred_b, groups=None):
    from scipy import stats

    d = np.abs(np.asarray(actual) - np.asarray(pred_a)) - np.abs(np.asarray(actual) - np.asarray(pred_b))
    if groups is not None:
        d = pd.Series(d).groupby(np.asarray(groups)).sum().to_numpy()
    n = len(d)
    var = np.mean((d - d.mean()) ** 2)
    if n < 3 or var == 0:
        return None
    stat = d.mean() / np.sqrt(var / n) * np.sqrt((n - 1) / n)
    return float(2 * stats.t.sf(abs(stat), df=n - 1))


def add_significance(results, actual, preds, baseline, groups=None):
    best = min((r for r in results if r["label"] != baseline), key=lambda r: r["wape"])["label"]
    for r in results:
        r["p_vs_baseline"] = None if r["label"] == baseline else diebold_mariano(
            actual, preds[r["label"]], preds[baseline], groups)
        r["p_vs_best"] = None if r["label"] == best else diebold_mariano(actual, preds[r["label"]], preds[best], groups)
    return best


# ---------------------------------------------------------------- Track A: daily totals

def build_daily(df):
    d = df.copy()
    d["date"] = pd.to_datetime(d["date"])
    d["rainy"] = (d["weather_condition"] == "Rainy").astype(float)
    d["cloudy"] = (d["weather_condition"] == "Cloudy").astype(float)
    daily = d.groupby("date").agg(
        y=("quantity_sold", "sum"),
        promo_share=("has_promotion", "mean"),
        event_share=("special_event", "mean"),
        rainy_share=("rainy", "mean"),
        cloudy_share=("cloudy", "mean"),
    ).reset_index()
    full = pd.DataFrame({"date": pd.date_range(daily["date"].min(), daily["date"].max())})
    daily = full.merge(daily, on="date", how="left")
    daily["y"] = daily["y"].fillna(0.0)
    daily[COVARIATES] = daily[COVARIATES].fillna(0.0).astype(float)
    dow = daily["date"].dt.dayofweek
    daily["dow"] = dow
    daily["is_weekend"] = (dow >= 5).astype(float)
    daily["dow_sin"] = np.sin(2 * np.pi * dow / 7)
    daily["dow_cos"] = np.cos(2 * np.pi * dow / 7)
    for k in range(7):
        daily[f"dow_{k}"] = (dow == k).astype(float)
    return daily


def _calendar(info):
    cols = ["is_weekend"] + [f"dow_{k}" for k in range(7)]
    return cols + COVARIATES if info == "A2" else cols


# Average of all demand up to the previous day, the same history every other model sees.
def mean_baseline(daily, train_end, test_idx):
    y = daily["y"].to_numpy(dtype=float)
    return np.array([y[:i].mean() for i in test_idx])


def seasonal_naive(daily, train_end, test_idx):
    return daily["y"].shift(7).iloc[test_idx].values


def rf_daily(daily, train_end, test_idx, info):
    from sklearn.ensemble import RandomForestRegressor

    d = daily.copy()
    lag_cols = []
    for k in (1, 2, 3, 7, 14):
        d[f"lag_{k}"] = d["y"].shift(k)
        lag_cols.append(f"lag_{k}")
    d["roll_7"] = d["y"].shift(1).rolling(7).mean()
    d["roll_28"] = d["y"].shift(1).rolling(28).mean()
    cols = lag_cols + ["roll_7", "roll_28"] + _calendar(info)
    train = d.iloc[28:train_end]
    model = RandomForestRegressor(n_estimators=300, min_samples_leaf=2, random_state=SEED, n_jobs=2)
    model.fit(train[cols], train["y"])
    return model.predict(d.iloc[test_idx][cols])


def _warm_start(model):
    return {k: model.params[k][0][0] if k in ("k", "m", "sigma_obs") else model.params[k][0]
            for k in ("k", "m", "sigma_obs", "delta", "beta")}


# Refitted on all demand up to the previous day before each forecast, so that Prophet forecasts one day ahead
# from the same history as the other models. Each fit starts from the previous fit's parameters to save time.
def prophet_daily(daily, train_end, test_idx, info):
    import logging
    from ml.forecasting import _ensure_prophet_backend
    _ensure_prophet_backend()
    from prophet import Prophet
    logging.getLogger("cmdstanpy").setLevel(logging.WARNING)

    cols = ["ds", "y"] + (COVARIATES if info == "A2" else [])
    pdf = daily.rename(columns={"date": "ds"})
    preds, init = [], None
    for i in test_idx:
        # Under one year of training data, so yearly seasonality cannot be estimated and is left out.
        model = Prophet(weekly_seasonality=True, yearly_seasonality=False, daily_seasonality=False)
        if info == "A2":
            for c in COVARIATES:
                model.add_regressor(c)
        model.fit(pdf.iloc[:i][cols], init=init) if init else model.fit(pdf.iloc[:i][cols])
        init = _warm_start(model)
        preds.append(float(model.predict(pdf.iloc[[i]][cols[:1] + cols[2:]])["yhat"].iloc[0]))
    return np.array(preds)


def lstm_daily(daily, train_end, test_idx, info, epochs=150):
    import tensorflow as tf
    from tensorflow.keras import Model, layers, callbacks

    tf.keras.utils.set_random_seed(SEED)
    y = daily["y"].values.astype("float32")
    mu, sd = y[:train_end].mean(), y[:train_end].std()
    ys = (y - mu) / sd
    feats = daily[_calendar(info)].values.astype("float32")

    # Input 1: the previous LOOKBACK days of demand. Input 2: the target day's known features.
    def windows(idx):
        seq = np.stack([ys[i - LOOKBACK:i] for i in idx])[..., None]
        return seq, feats[idx]

    train_idx = np.arange(LOOKBACK, train_end)
    xs, xf = windows(train_idx)
    tf.keras.backend.clear_session()
    seq_in = layers.Input(shape=(LOOKBACK, 1))
    feat_in = layers.Input(shape=(feats.shape[1],))
    h = layers.LSTM(32)(seq_in)
    h = layers.Dropout(0.2)(h)
    h = layers.Concatenate()([h, feat_in])
    h = layers.Dense(16, activation="relu")(h)
    out = layers.Dense(1)(h)
    model = Model([seq_in, feat_in], out)
    model.compile(optimizer=tf.keras.optimizers.Adam(1e-3), loss="mse")
    model.fit([xs, xf], ys[train_idx], epochs=epochs, batch_size=16, validation_split=0.2, shuffle=False,
              verbose=0, callbacks=[callbacks.EarlyStopping(monitor="val_loss", patience=15, restore_best_weights=True)])
    ts, tfe = windows(np.asarray(test_idx))
    return model.predict([ts, tfe], verbose=0).flatten() * sd + mu


DAILY_MODELS = {
    "Mean baseline": lambda d, e, t, i: mean_baseline(d, e, t),
    "Seasonal naive": lambda d, e, t, i: seasonal_naive(d, e, t),
    "Prophet": prophet_daily,
    "LSTM": lstm_daily,
    "Random Forest": rf_daily,
}
BASELINES = {"Mean baseline", "Seasonal naive"}


def run_daily(df, log=print):
    daily = build_daily(df)
    n = len(daily)
    split = int(n * SPLIT_RATIO)
    test_idx = np.arange(split, n)
    # Rolling origin: four consecutive windows over the last 40% of days, each trained on all earlier days.
    starts = np.linspace(int(n * 0.6), n, CV_FOLDS + 1).astype(int)
    folds = [(starts[k], np.arange(starts[k], starts[k + 1])) for k in range(CV_FOLDS)]

    results, series = [], {}
    for info in ("A1", "A2"):
        for name, fn in DAILY_MODELS.items():
            if name in BASELINES and info == "A2":
                continue
            t0 = time.time()
            pred = fn(daily, split, test_idx, info)
            secs = time.time() - t0
            m = evaluate(daily["y"].values[test_idx], pred)
            cv = []
            for end, idx in folds:
                cv.append(evaluate(daily["y"].values[idx], fn(daily, end, idx, info))["wape"])
            label = name if name in BASELINES else f"{name} ({info})"
            results.append({"track": "A", "info_set": "baseline" if name in BASELINES else info, "model": name,
                            "label": label, **m, "cv_wape_mean": float(np.mean(cv)), "cv_wape_sd": float(np.std(cv)),
                            "n_test": len(test_idx), "seconds": round(secs, 1)})
            series[label] = pred
            log(f"  A {label:<24} WAPE {m['wape']:5.1f}%  R2 {m['r2']:6.2f}  CV WAPE {np.mean(cv):5.1f} +/- {np.std(cv):4.1f}")
    add_significance(results, daily["y"].values[test_idx], series, "Mean baseline")
    return {"results": results, "dates": list(daily["date"].iloc[test_idx]),
            "actual": daily["y"].values[test_idx].tolist(), "series": series, "split_date": daily["date"].iloc[split]}


# ---------------------------------------------------------------- Track B: item level

B_CATEGORICAL = ["restaurant_id", "restaurant_type", "menu_item_name", "meal_type", "weather_condition"]
B_NUMERIC = ["typical_ingredient_cost", "observed_market_price", "actual_selling_price",
             "has_promotion", "special_event", "is_weekend", "dow", "month", "prior_mean", "prior_count"]


def build_items(df, split_date):
    d = df.copy()
    d["date"] = pd.to_datetime(d["date"])
    d = d.sort_values("date").reset_index(drop=True)
    d["has_promotion"] = d["has_promotion"].astype(float)
    d["special_event"] = d["special_event"].astype(float)
    d["dow"] = d["date"].dt.dayofweek
    d["is_weekend"] = (d["dow"] >= 5).astype(float)
    d["month"] = d["date"].dt.month

    # History feature: mean quantity of the same restaurant and item on strictly earlier days only.
    key = ["restaurant_id", "menu_item_name"]
    per_day = d.groupby(key + ["date"])["quantity_sold"].agg(["sum", "count"]).reset_index()
    per_day[["cum_sum", "cum_n"]] = per_day.groupby(key)[["sum", "count"]].cumsum().values
    per_day["prior_count"] = per_day["cum_n"] - per_day["count"]
    per_day["prior_mean"] = (per_day["cum_sum"] - per_day["sum"]) / per_day["prior_count"].replace(0, np.nan)
    d = d.merge(per_day[key + ["date", "prior_mean", "prior_count"]], on=key + ["date"], how="left")

    train = d["date"] < split_date
    item_mean = d[train].groupby("menu_item_name")["quantity_sold"].mean()
    d["item_mean"] = d["menu_item_name"].map(item_mean).fillna(d.loc[train, "quantity_sold"].mean())
    d["prior_mean"] = d["prior_mean"].fillna(d["item_mean"])
    return d, train.values


def run_items(df, split_date, log=print):
    from sklearn.compose import ColumnTransformer
    from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
    from sklearn.linear_model import Ridge
    from sklearn.neural_network import MLPRegressor
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import OneHotEncoder, StandardScaler, OrdinalEncoder

    d, train = build_items(df, split_date)
    tr, te = d[train], d[~train]
    y_tr, y_te = tr["quantity_sold"].values, te["quantity_sold"].values

    onehot = ColumnTransformer([("cat", OneHotEncoder(handle_unknown="ignore"), B_CATEGORICAL),
                                ("num", StandardScaler(), B_NUMERIC)])
    ordinal = ColumnTransformer([("cat", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1), B_CATEGORICAL),
                                 ("num", "passthrough", B_NUMERIC)])
    models = {
        "Mean baseline": None,
        "Historical average rule": None,
        "Linear regression": make_pipeline(onehot, Ridge(alpha=1.0)),
        "Neural network (MLP)": make_pipeline(onehot, MLPRegressor((64, 32), max_iter=500, early_stopping=True,
                                                                    random_state=SEED)),
        "Random Forest": make_pipeline(ordinal, RandomForestRegressor(n_estimators=300, min_samples_leaf=2,
                                                                      random_state=SEED, n_jobs=2)),
        "Gradient boosting": make_pipeline(ordinal, HistGradientBoostingRegressor(random_state=SEED)),
    }
    cols = B_CATEGORICAL + B_NUMERIC
    results, preds = [], {}
    for name, model in models.items():
        t0 = time.time()
        if name == "Mean baseline":
            pred = np.full(len(te), y_tr.mean())
        elif name == "Historical average rule":
            pred = te["item_mean"].values
        else:
            model.fit(tr[cols], y_tr)
            pred = np.clip(model.predict(te[cols]), 0, None)
        m = evaluate(y_te, pred)
        results.append({"track": "B", "info_set": "B", "model": name, "label": name, **m,
                        "n_test": len(te), "seconds": round(time.time() - t0, 1)})
        preds[name] = pred
        log(f"  B {name:<34} WAPE {m['wape']:5.1f}%  R2 {m['r2']:6.2f}  MAE {m['mae']:6.1f}")
    add_significance(results, y_te, preds, "Historical average rule", groups=te["date"].to_numpy())
    # Check reported in the evaluation: the history feature used directly as a forecast.
    history_only = evaluate(y_te, te["prior_mean"].to_numpy())
    log(f"  B {'History feature alone (check)':<34} WAPE {history_only['wape']:5.1f}%  R2 {history_only['r2']:6.2f}")
    return {"results": results, "test": te.reset_index(drop=True), "preds": preds, "history_only": history_only}
