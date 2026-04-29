# -*- coding: utf-8 -*-
"""
Created on Tue Sep 30 14:44:11 2025
Fixed on Thu Oct 2 2025
@author: dell
"""

import pandas as pd
import datetime as dt
from sklearn.linear_model import LinearRegression


def predict_next_day(
    eccc_path="../data/eccc_algonquin.csv",
    openmeteo_path="../output/openmeteo_forecast.csv"
):
    # ---------------------------
    # Load ECCC historical data
    # ---------------------------
    eccc_df = pd.read_csv(eccc_path)
    eccc_df = eccc_df.rename(columns={
        "Date/Time": "date",
        "Max Temp (°C)": "t_max",
        "Min Temp (°C)": "t_min",
        "Total Precip (mm)": "precip"
    })

    # Robust date parsing
    eccc_df["date"] = pd.to_datetime(
        eccc_df["date"], format="mixed", dayfirst=True, errors="coerce"
    )

    # Drop invalid rows
    eccc_df = eccc_df.dropna(subset=["date", "t_max", "t_min", "precip"])

    # Create features
    eccc_df["t_avg"] = (eccc_df["t_max"] + eccc_df["t_min"]) / 2
    eccc_df["dayofyear"] = eccc_df["date"].dt.dayofyear

    # ---------------------------
    # Train regression models
    # ---------------------------
    temp_model = LinearRegression()
    precip_model = LinearRegression()

    # Train on historical averages
    temp_model.fit(eccc_df[["dayofyear"]], eccc_df["t_avg"])
    precip_model.fit(eccc_df[["dayofyear"]], eccc_df["precip"])

    # ---------------------------
    # Predict next day
    # ---------------------------
    tomorrow = dt.date.today() + dt.timedelta(days=1)
    future_day = tomorrow.timetuple().tm_yday

    pred_temp_hist = temp_model.predict(pd.DataFrame({"dayofyear": [future_day]}))[0]
    pred_precip_hist = precip_model.predict(pd.DataFrame({"dayofyear": [future_day]}))[0]

    # ---------------------------
    # Load Open-Meteo forecast
    # ---------------------------
    try:
        om_df = pd.read_csv(openmeteo_path)
        om_df["date"] = pd.to_datetime(om_df["date"], errors="coerce")
        om_forecast_row = om_df.loc[om_df["date"].dt.date == tomorrow]
    except Exception:
        om_forecast_row = pd.DataFrame()

    # ---------------------------
    # Blend predictions if forecast available
    # ---------------------------
    if not om_forecast_row.empty:
        t_max = om_forecast_row["t_max"].values[0]
        t_min = om_forecast_row["t_min"].values[0]
        avg_forecast = (t_max + t_min) / 2
        forecast_precip = om_forecast_row["precip"].values[0]

        final_temp = (pred_temp_hist + avg_forecast) / 2
        final_precip = (pred_precip_hist + forecast_precip) / 2

        print(" Using blended prediction (ECCC model + Open-Meteo forecast)")
    else:
        final_temp = pred_temp_hist
        final_precip = pred_precip_hist
        print(" Using only ECCC historical model prediction (Open-Meteo unavailable)")

    # ---------------------------
    # Print results
    # ---------------------------
    print("\n 24-Hour Ahead Weather Prediction")
    print(f"Date: {tomorrow}")
    print(f" - Historical Model Temp: {pred_temp_hist:.2f} °C")
    print(f" - Historical Model Precip: {pred_precip_hist:.2f} mm")

    if not om_forecast_row.empty:
        print(f" - Open-Meteo Forecast Avg Temp: {avg_forecast:.2f} °C")
        print(f" - Open-Meteo Forecast Precip: {forecast_precip:.2f} mm")

    print(f" Final Predicted Avg Temp = {final_temp:.2f} °C")
    print(f" Final Predicted Precip   = {final_precip:.2f} mm\n")

    return {"temp": final_temp, "precip": final_precip}


if __name__ == "__main__":
    predict_next_day()
