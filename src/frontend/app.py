"""Streamlit frontend for NYC Taxi Fare Prediction."""

import os
from datetime import date, datetime, time

import requests
import streamlit as st

# Set by Terraform on Cloud Run (terraform/cloudrun.tf). Defaults to a local API for development.
API_URL = os.getenv("API_URL", "http://localhost:8080").rstrip("/")

st.set_page_config(page_title="NYC Taxi Fare Predictor", page_icon="🚕")
st.title("NYC Taxi Fare Predictor")

col1, col2 = st.columns(2)

with col1:
    pickup_date = st.date_input("Pickup date", value=date.today())
    pickup_time = st.time_input("Pickup time (NYC local)", value=time(14, 0))
    pickup_dt = datetime.combine(pickup_date, pickup_time)
    is_weekend = pickup_dt.weekday() >= 5

with col2:
    passenger_count = st.number_input("Passengers", min_value=1, max_value=9, value=1)
    trip_distance = st.number_input(
        "Trip distance (miles)", min_value=0.1, max_value=100.0, value=3.0, step=0.5
    )

if is_weekend:
    st.info("Weekend trip")

if st.button("Predict Fare", type="primary", use_container_width=True):
    payload = {
        "pickup_datetime": pickup_dt.isoformat(),
        "passenger_count": passenger_count,
        "trip_distance": trip_distance,
    }
    try:
        resp = requests.post(f"{API_URL}/predict", json=payload, timeout=10)
        resp.raise_for_status()
        fare = resp.json()["predicted_fare"]
        st.metric("Predicted Fare", f"${fare:.2f}")
    except requests.RequestException as e:
        st.error(f"API error: {e}")
