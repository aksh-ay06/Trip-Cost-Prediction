"""Pydantic request/response schemas for the prediction API."""

from pydantic import BaseModel, Field


class TripInput(BaseModel):
    pickup_hour: int = Field(..., ge=0, le=23, description="Hour of pickup (0-23)")
    pickup_dayofweek: int = Field(..., ge=1, le=7, description="Day of week (1=Sunday, 7=Saturday)")
    is_weekend: int = Field(..., ge=0, le=1, description="1 if Saturday or Sunday, 0 otherwise")
    passenger_count: int = Field(..., ge=1, le=9)
    trip_distance: float = Field(..., gt=0)


class PredictionOutput(BaseModel):
    predicted_fare: float
