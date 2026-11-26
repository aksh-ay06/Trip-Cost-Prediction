"""FastAPI application for taxi fare prediction."""

from fastapi import FastAPI

from .features import build_features
from .model import get_model
from .schemas import PredictionOutput, TripInput

app = FastAPI(title="NYC Taxi Fare Prediction API")


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/predict", response_model=PredictionOutput)
def predict(trip: TripInput):
    model = get_model()
    features = build_features(trip.pickup_datetime, trip.passenger_count, trip.trip_distance)
    prediction = model.predict(features)[0]
    return PredictionOutput(predicted_fare=round(float(prediction), 2))
