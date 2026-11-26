"""Turn an API request into the model's feature row.

The time features must match how training computes them in BigQuery
(src/processing/features.py):

    EXTRACT(HOUR FROM pickup_datetime)       -> pickup_hour (0-23)
    EXTRACT(DAYOFWEEK FROM pickup_datetime)  -> pickup_dayofweek (1=Sunday ... 7=Saturday)
    DAYOFWEEK IN (1, 7)                      -> is_weekend

The TLC tables store NYC local wall-clock time, so naive datetimes are
treated as NYC local time and timezone-aware ones are converted to it.
"""

from datetime import datetime
from zoneinfo import ZoneInfo

import pandas as pd

NYC_TZ = ZoneInfo("America/New_York")

# Column order the model was trained with. Must match FEATURES in src/config.py.
FEATURE_ORDER = [
    "pickup_hour",
    "pickup_dayofweek",
    "is_weekend",
    "passenger_count",
    "trip_distance",
]


def to_nyc_local(pickup_datetime: datetime) -> datetime:
    """Return the pickup time as NYC local wall-clock time (naive)."""
    if pickup_datetime.tzinfo is not None:
        pickup_datetime = pickup_datetime.astimezone(NYC_TZ)
    return pickup_datetime.replace(tzinfo=None)


def bigquery_dayofweek(ts: datetime) -> int:
    """Day of week in BigQuery's convention: 1 = Sunday ... 7 = Saturday."""
    # Python: Monday=0 ... Sunday=6
    return (ts.weekday() + 1) % 7 + 1


def build_features(pickup_datetime: datetime, passenger_count: int, trip_distance: float) -> pd.DataFrame:
    """Build a single-row DataFrame in the column order the model expects."""
    local = to_nyc_local(pickup_datetime)
    dayofweek = bigquery_dayofweek(local)
    row = {
        "pickup_hour": local.hour,
        "pickup_dayofweek": dayofweek,
        "is_weekend": int(dayofweek in (1, 7)),
        "passenger_count": passenger_count,
        "trip_distance": trip_distance,
    }
    return pd.DataFrame([row], columns=FEATURE_ORDER)
