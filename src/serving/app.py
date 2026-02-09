"""FastAPI application for taxi fare prediction."""

import pandas as pd
from fastapi import FastAPI

from .model import get_model
from .schemas import PredictionOutput, TripInput

app = FastAPI(title="NYC Taxi Fare Prediction API")


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/predict", response_model=PredictionOutput)
def predict(trip: TripInput):
    model = get_model()
    features = pd.DataFrame([trip.model_dump()])
    prediction = model.predict(features)[0]
    return PredictionOutput(predicted_fare=round(float(prediction), 2))
