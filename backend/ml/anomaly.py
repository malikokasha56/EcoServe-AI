import numpy as np


def zscore_flags(values, threshold=3.0):
    values = np.asarray(values, dtype=float)
    mean = float(np.mean(values))
    std = float(np.std(values))
    flags = [abs((v - mean) / std) > threshold if std > 0 else False for v in values]
    return flags, mean, std


def iqr_flags(values, k=1.5):
    values = np.asarray(values, dtype=float)
    q1 = float(np.percentile(values, 25))
    q3 = float(np.percentile(values, 75))
    iqr = q3 - q1
    lower = q1 - k * iqr
    upper = q3 + k * iqr
    flags = [(v < lower or v > upper) for v in values]
    return flags, lower, upper


# Combines Z-score (threshold 3) with the 1.5x IQR rule; a point is flagged by either.
def detect(values, zthreshold=3.0):
    values = np.asarray(values, dtype=float)
    z, mean, std = zscore_flags(values, zthreshold)
    iqr, lower, upper = iqr_flags(values)

    results = []
    for i, v in enumerate(values):
        is_anom = bool(z[i] or iqr[i])
        if z[i] and iqr[i]:
            method = "zscore+iqr"
        elif z[i]:
            method = "zscore"
        elif iqr[i]:
            method = "iqr"
        else:
            method = None

        severity = None
        if is_anom and std > 0:
            dist = abs((v - mean) / std)
            severity = "high" if dist > 4 else "medium"

        results.append({
            "value": float(v),
            "expected": mean,
            "lower": lower,
            "upper": upper,
            "is_anomaly": is_anom,
            "method": method,
            "severity": severity,
        })
    return results
