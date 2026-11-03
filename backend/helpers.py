import math

from flask import current_app, request
from sqlalchemy import func

from extensions import db
from models import SalesRecord, ExperimentResult


class ValidationError(ValueError):
    pass


def default_restaurant_id():
    return current_app.config.get("DEFAULT_RESTAURANT_ID", 1)


def to_number(value, field, cast=float, minimum=None, default=None):
    if value in (None, ""):
        if default is not None:
            return default
        raise ValidationError(f"{field} is required")
    try:
        number = cast(value)
    except (TypeError, ValueError):
        raise ValidationError(f"{field} must be a number")
    if isinstance(number, float) and not math.isfinite(number):
        raise ValidationError(f"{field} must be a finite number")
    if minimum is not None and number < minimum:
        raise ValidationError(f"{field} must be at least {minimum}")
    return number


def json_object():
    data = request.get_json(silent=True)
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValidationError("Request body must be a JSON object")
    return data


# Daily aggregated demand (total quantity sold and revenue per day), ordered by date.
def daily_sales_rows():
    rows = (
        db.session.query(
            SalesRecord.date.label("date"),
            func.sum(SalesRecord.quantity_sold).label("quantity_sold"),
            func.sum(SalesRecord.quantity_sold * SalesRecord.actual_selling_price).label("revenue"),
        )
        .group_by(SalesRecord.date)
        .order_by(SalesRecord.date)
        .all()
    )
    return rows


# Lowest test-period WAPE within a comparison track (the reference row is not a forecast and is excluded).
def best_model(track="A"):
    rows = ExperimentResult.query.filter(ExperimentResult.track == track,
                                         ExperimentResult.info_set != "reference").all()
    rows = [r for r in rows if r.wape is not None]
    return min(rows, key=lambda r: r.wape) if rows else None
