"""Shared settings, error metrics and Prophet setup used by the model comparison (ml/experiment.py)."""
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

SPLIT_RATIO = 0.80
SEED = 42


def _mape(y_true, y_pred):
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    mask = y_true != 0
    if mask.sum() == 0:
        return float("nan")
    return float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100)


# WAPE (weighted absolute percentage error) avoids MAPE's small-denominator blow-up.
def _wape(y_true, y_pred):
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    denom = np.sum(np.abs(y_true))
    if denom == 0:
        return float("nan")
    return float(np.sum(np.abs(y_true - y_pred)) / denom * 100)


def evaluate(y_true, y_pred):
    mae = float(mean_absolute_error(y_true, y_pred))
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    mape = _mape(y_true, y_pred)
    wape = _wape(y_true, y_pred)
    r2 = float(r2_score(y_true, y_pred))
    return {"mae": mae, "rmse": rmse, "mape": mape, "wape": wape, "r2": r2}


# Prophet ships a precompiled model but cmdstanpy rejects the bundled path when its
# makefile is absent; create an empty stub so the precompiled model can be used.
def _ensure_prophet_backend():
    import os
    import prophet

    stan_dir = os.path.join(os.path.dirname(prophet.__file__), "stan_model")
    if not os.path.isdir(stan_dir):
        return
    for name in os.listdir(stan_dir):
        cmdstan_path = os.path.join(stan_dir, name)
        if name.startswith("cmdstan-") and os.path.isdir(cmdstan_path):
            makefile = os.path.join(cmdstan_path, "makefile")
            if not os.path.exists(makefile):
                open(makefile, "a").close()
