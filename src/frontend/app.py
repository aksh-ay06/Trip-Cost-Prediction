"""Streamlit frontend for NYC Taxi Fare Prediction."""

import os

import requests
import streamlit as st

API_URL = os.getenv(
    "API_URL", "https://taxi-prediction-api-6b5db6zo2q-uc.a.run.app"
)

st.set_page_config(page_title="NYC Taxi Fare Predictor", page_icon="🚕")
st.title("NYC Taxi Fare Predictor")

DAYS = {
    "Sunday": 1,
    "Monday": 2,
    "Tuesday": 3,
    "Wednesday": 4,
    "Thursday": 5,
    "Friday": 6,
    "Saturday": 7,
}

col1, col2 = st.columns(2)

with col1:
    pickup_hour = st.slider("Pickup hour", 0, 23, 14)
    day_name = st.selectbox("Day of week", list(DAYS.keys()), index=3)
    pickup_dayofweek = DAYS[day_name]
    is_weekend = 1 if day_name in ("Sunday", "Saturday") else 0

with col2:
    passenger_count = st.number_input("Passengers", min_value=1, max_value=9, value=1)
    trip_distance = st.number_input(
        "Trip distance (miles)", min_value=0.1, max_value=100.0, value=3.0, step=0.5
    )

if is_weekend:
    st.info("Weekend trip")

if st.button("Predict Fare", type="primary", use_container_width=True):
    payload = {
        "pickup_hour": pickup_hour,
        "pickup_dayofweek": pickup_dayofweek,
        "is_weekend": is_weekend,
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
