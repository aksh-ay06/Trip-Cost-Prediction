"""FastAPI application for taxi fare prediction."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from .features import build_features
from .model import get_model
from .schemas import PredictionOutput, TripInput


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the model from GCS before accepting traffic, so the first request
    # doesn't pay the download cost and a missing or broken model fails the
    # deploy (Cloud Run startup check) instead of failing user requests.
    get_model()
    yield


app = FastAPI(title="NYC Taxi Fare Prediction API", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/predict", response_model=PredictionOutput)
def predict(trip: TripInput):
    model = get_model()
    features = build_features(trip.pickup_datetime, trip.passenger_count, trip.trip_distance)
    prediction = model.predict(features)[0]
    return PredictionOutput(predicted_fare=round(float(prediction), 2))
