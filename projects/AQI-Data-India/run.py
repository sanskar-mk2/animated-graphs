import sys, os
import pandas as pd
import numpy as np

root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(root_dir)
from src.racing_bar_chart import AnimatedGraph, PyGamerExt
from src.color import Color

SIZE = 1920, 1080


import pandas as pd
import numpy as np


BREAKPOINTS = {
    "PM10": {
        "Good": (0, 50),
        "Satisfactory": (51, 100),
        "Moderately polluted": (101, 250),
        "Poor": (251, 350),
        "Very poor": (351, 430),
        "Severe": (430, float("inf")),
    },
    "PM2.5": {
        "Good": (0, 30),
        "Satisfactory": (31, 60),
        "Moderately polluted": (61, 90),
        "Poor": (91, 120),
        "Very poor": (121, 250),
        "Severe": (250, float("inf")),
    },
    "NO2": {
        "Good": (0, 40),
        "Satisfactory": (41, 80),
        "Moderately polluted": (81, 180),
        "Poor": (181, 280),
        "Very poor": (281, 400),
        "Severe": (400, float("inf")),
    },
    "O3": {
        "Good": (0, 50),
        "Satisfactory": (51, 100),
        "Moderately polluted": (101, 168),
        "Poor": (169, 208),
        "Very poor": (209, 748),
        "Severe": (748, float("inf")),
    },
    "CO": {
        "Good": (0, 1.0),
        "Satisfactory": (1.1, 2.0),
        "Moderately polluted": (2.1, 10),
        "Poor": (10, 17),
        "Very poor": (17, 34),
        "Severe": (34, float("inf")),
    },
    "SO2": {
        "Good": (0, 40),
        "Satisfactory": (41, 80),
        "Moderately polluted": (81, 380),
        "Poor": (381, 800),
        "Very poor": (801, 1600),
        "Severe": (1600, float("inf")),
    },
    "NH3": {
        "Good": (0, 200),
        "Satisfactory": (201, 400),
        "Moderately polluted": (401, 800),
        "Poor": (801, 1200),
        "Very poor": (1200, 1800),
        "Severe": (1800, float("inf")),
    },
    "Pb": {
        "Good": (0, 0.5),
        "Satisfactory": (0.5, 1.0),
        "Moderately polluted": (1.1, 2.0),
        "Poor": (2.1, 3.0),
        "Very poor": (3.1, 3.5),
        "Severe": (3.5, float("inf")),
    },
}


def calculate_sub_index(
    current_reading,
    prev_category_upper_limit,
    current_category_lower_limit,
    current_category_upper_limit,
    aqi_category_min,
    aqi_category_max,
):
    """
    Calculate Sub Index for a pollutant using AQI formula

    Parameters:
    current_reading: Current pollutant reading
    prev_category_upper_limit: Upper limit of previous category
    current_category_lower_limit: Lower limit of current category
    current_category_upper_limit: Upper limit of current category
    aqi_category_min: Lower AQI value for current category
    aqi_category_max: Upper AQI value for current category

    Returns:
    float: Calculated Sub Index value
    """

    reading_interval = current_category_upper_limit - current_category_lower_limit
    aqi_interval = aqi_category_max - aqi_category_min

    sub_index = prev_category_upper_limit + (
        (current_reading - prev_category_upper_limit)
        * (aqi_interval / reading_interval)
    )

    return round(sub_index, 2)


def calculate_aqi(df):
    # Check which columns are actually present in the dataframe
    available_columns = df.columns.tolist()

    df["custom_date"] = df["From Date"].apply(
        lambda x: x.date() if x.hour >= 6 else (x - pd.Timedelta(days=1)).date()
    )

    # Create mapping of pollutant names to their column names
    column_mapping = {
        "PM10": "PM10 (ug/m3)",
        "PM2.5": "PM2.5 (ug/m3)",
        "NO2": "NO2 (ug/m3)",
        "O3": "Ozone (ug/m3)",
        "CO": "CO (mg/m3)",
        "SO2": "SO2 (ug/m3)",
        "NH3": "NH3 (ug/m3)",
    }

    # Filter to only include columns that are present in the data
    agg_dict = {}
    for col in column_mapping.values():
        if col in available_columns:
            agg_dict[col] = "mean"

    # Get daily means
    daily_averages = df.groupby("custom_date").agg(agg_dict).round(2)
    daily_averages = daily_averages.reset_index()

    # Get daily counts
    count_dict = {col: "count" for col in agg_dict.keys()}
    daily_counts = df.groupby("custom_date").agg(count_dict)

    # Filter for days with at least 16 hours of data for each pollutant
    valid_days = daily_counts[daily_counts >= 16].dropna().index

    # Filter averages to only include valid days
    daily_averages = daily_averages[daily_averages["custom_date"].isin(valid_days)]

    # Calculate sub-indices for each available pollutant
    for pollutant, column_name in column_mapping.items():
        if column_name not in available_columns:
            continue

        # Create sub-index column name
        sub_index_col = f"{pollutant}_SubIndex"
        daily_averages[sub_index_col] = np.nan

        # Calculate sub-index for each reading
        for idx, row in daily_averages.iterrows():
            reading = row[column_name]
            if pd.isna(reading):
                continue

            # Find appropriate category based on reading
            prev_upper = 0
            for category, (lower, upper) in BREAKPOINTS[pollutant].items():
                if lower <= reading <= upper:
                    # Map AQI categories to ranges
                    aqi_ranges = {
                        "Good": (0, 50),
                        "Satisfactory": (51, 100),
                        "Moderately polluted": (101, 200),
                        "Poor": (201, 300),
                        "Very poor": (301, 400),
                        "Severe": (401, 500),
                    }

                    daily_averages.at[idx, sub_index_col] = calculate_sub_index(
                        reading,
                        prev_upper,
                        lower,
                        upper,
                        aqi_ranges[category][0],
                        aqi_ranges[category][1],
                    )
                    break
                prev_upper = upper

    # Calculate overall AQI (worst sub-index) only if requirements are met
    sub_index_columns = [
        col for col in daily_averages.columns if col.endswith("_SubIndex")
    ]
    daily_averages["AQI"] = np.nan

    for idx in daily_averages.index:
        # Get non-null sub-indices for this row
        valid_indices = [
            col for col in sub_index_columns if not pd.isna(daily_averages.at[idx, col])
        ]

        # Check if either PM2.5 or PM10 is present (if they exist in the data)
        has_pm = (
            any(idx in valid_indices for idx in ["PM2.5_SubIndex", "PM10_SubIndex"])
            if any(
                pm in sub_index_columns for pm in ["PM2.5_SubIndex", "PM10_SubIndex"]
            )
            else False
        )

        # Calculate AQI only if we have at least 3 pollutants and one is PM (when PM data exists)
        if len(valid_indices) >= 3 and (
            has_pm
            or not any(
                pm in sub_index_columns for pm in ["PM2.5_SubIndex", "PM10_SubIndex"]
            )
        ):
            daily_averages.at[idx, "AQI"] = daily_averages.loc[idx, valid_indices].max()

    return daily_averages


def average_and_transpose(df):
    """
    Calculate monthly averages and transpose dates to columns
    """
    # Convert index to datetime if not already
    df.index = pd.to_datetime(df.index)

    # Calculate monthly average
    monthly_df = df.resample("M").mean()

    # Format the date index to YYYY-MM format
    monthly_df.index = monthly_df.index.strftime("%Y-%m")

    # Transpose so dates become columns
    monthly_df = monthly_df.T

    return monthly_df


def process_data():
    index = pd.read_csv("projects/AQI-Data-India/data/stations_info.csv")
    # file_name,state,city,agency,station_location,start_month,start_month_num,start_year
    df_list = []
    station_names = {}  # Dictionary to store station name mappings

    for idx, row in index.iterrows():
        file_name = row["file_name"]
        # if filename dont begin with UP, continue
        if not file_name.startswith("UP"):
            continue

        # Create station name with city, state and location
        station_name = f"{row['city']}, {row['state']} ({row['station_location']})"
        station_names[file_name] = station_name

        print(f"Processing {file_name} ({station_name})")
        df = pd.read_csv(
            f"projects/AQI-Data-India/data/{file_name}.csv",
            parse_dates=["From Date", "To Date"],
        )
        df = calculate_aqi(df)
        df_list.append(df)

    # Extract AQI columns from each dataframe and combine
    aqi_dfs = []
    for i, df in enumerate(df_list):
        file_name = list(station_names.keys())[i]
        station_name = station_names[file_name]
        aqi_df = df[["custom_date", "AQI"]].copy()
        aqi_df = aqi_df.rename(columns={"AQI": f"AQI_{station_name}"})
        aqi_dfs.append(aqi_df)

    # Combine all AQI data
    df = aqi_dfs[0]
    for aqi_df in aqi_dfs[1:]:
        df = pd.merge(df, aqi_df, on="custom_date", how="outer")

    # Set date as index
    df = df.set_index("custom_date")

    df.to_csv("UP.csv")

    # Handle missing values by forward filling then backward filling
    # df = df.fillna(method="ffill").fillna(method="bfill")

    df = average_and_transpose(df)

    # interpolate forward
    df = df.interpolate(method="linear", limit_direction="forward", axis=1)

    # Handle any missing values after averaging by filling horizontally
    # df = df.fillna(method="ffill", axis=1).fillna(method="bfill", axis=1)

    # save to UP.csv
    df.to_csv("UP2.csv")
    return df


FONT: str = "./assets/fonts/Kelvinch-Bold.otf"
if __name__ == "__main__":
    data = pd.read_csv("UP2.csv", index_col=0)
    app = PyGamerExt(SIZE)
    graph = AnimatedGraph(
        pgapp=app,
        data=data,
        header=100,
        header_text="AQI for UP",
        header_font_size=40,
        header_font=FONT,
        bar_height=40,
        width_multiplier=2,
        colors=[Color.random_rgb() for _ in range(500)],
        left_gap=400,
        text_bar_distance=30,
        small_text_size=30,
        to_show=10,
        # debug=True
    )
    graph.run()
