# fetch_openmeteo.py
import openmeteo_requests
import requests_cache
from retry_requests import retry
import pandas as pd
import os

def fetch_openmeteo(save=False, out_path="../output/openmeteo_forecast.csv"):
    # Setup session with retry + cache
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    client = openmeteo_requests.Client(session=retry_session)

    params = {
        "latitude": 45.53,
        "longitude": -78.27,
        "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
        "forecast_days": 16,
        "timezone": "auto"
    }

    responses = client.weather_api("https://api.open-meteo.com/v1/forecast", params=params)
    response = responses[0]

    # Build DataFrame
    daily = response.Daily()
    df = pd.DataFrame({
        "date": pd.date_range(
            start=pd.to_datetime(daily.Time(), unit="s"),
            end=pd.to_datetime(daily.TimeEnd(), unit="s"),
            freq=pd.Timedelta(seconds=daily.Interval()),
            inclusive="left"
        ),
        "t_max": daily.Variables(0).ValuesAsNumpy(),
        "t_min": daily.Variables(1).ValuesAsNumpy(),
        "precip": daily.Variables(2).ValuesAsNumpy()
    })

    # Optionally save
    if save:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        df.to_csv(out_path, index=False)
        print(f"✅ Saved forecast data to {out_path}")

    return df


# Example usage
if __name__ == "__main__":
    forecast_df = fetch_openmeteo(save=True)
    print(forecast_df.head())
