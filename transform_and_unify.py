# -*- coding: utf-8 -*-
"""
Created on Tue Sep 30 14:43:14 2025

@author: dell
"""

# transform_and_unify.py
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 30 14:43:14 2025

@author: dell
"""

# transform_and_unify.py
import pandas as pd
from fetch_openmeteo import fetch_openmeteo

def transform_and_unify(
    eccc_path="../data/eccc_algonquin.csv",
    out_path="../output/joe_unified_data.csv"
):
    # Load ECCC data
    eccc_df = pd.read_csv(eccc_path)

    # Fetch Open-Meteo forecast
    openmeteo_df = fetch_openmeteo(save=False)

    # Clean ECCC: rename columns to standard schema
    eccc_df = eccc_df.rename(columns={
        "Date/Time": "date",
        "Max Temp (°C)": "t_max",
        "Min Temp (°C)": "t_min",
        "Total Precip (mm)": "precip"
    })
    eccc_df["date"] = pd.to_datetime(eccc_df["date"], errors="coerce")

    # Add source column
    eccc_df["source"] = "eccc"
    openmeteo_df["source"] = "openmeteo"

    # Keep consistent fields
    joe_df = pd.concat([
        eccc_df[["date", "t_max", "t_min", "precip", "source"]],
        openmeteo_df[["date", "t_max", "t_min", "precip", "source"]]
    ])

    # Sort by date
    joe_df = joe_df.sort_values("date").reset_index(drop=True)

    # Save unified dataset
    joe_df.to_csv(out_path, index=False)
    print(f"✅ Unified data saved to {out_path}")

    return joe_df


if __name__ == "__main__":
    df = transform_and_unify()
    print(df.head())
