"""Pydantic request/response schemas for the prediction API."""

from datetime import datetime

from pydantic import BaseModel, Field


class TripInput(BaseModel):
    pickup_datetime: datetime = Field(
        ...,
        description=(
            "Pickup time in ISO 8601, e.g. 2026-03-04T14:30:00. Treated as NYC local "
            "time unless it includes a UTC offset. Hour, day of week, and the weekend "
            "flag are derived from it on the server."
        ),
        examples=["2026-03-04T14:30:00"],
    )
    passenger_count: int = Field(..., ge=1, le=9)
    trip_distance: float = Field(..., gt=0, le=100, description="Trip distance in miles")


class PredictionOutput(BaseModel):
    predicted_fare: float
