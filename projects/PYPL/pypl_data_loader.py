import json
import pandas as pd
import os
import warnings


def json_to_arr(file):
    with open(file, "r") as f:
        return json.load(f)


def arr_to_df(data):
    return pd.DataFrame(
        [i[1:] for i in data[1:]], index=[i[0] for i in data[1:]], columns=data[0][1:]
    )


def load_data(path):
    os.chdir("./projects/PYPL")
    data = json_to_arr(path)
    os.chdir("../../")
    df = arr_to_df(data)
    df = df.transpose()
    df = df * 100

    # Convert column names to dates
    colname = df.columns.to_series()
    dates = pd.to_datetime(colname)

    # Suppress the timezone warning since it's intended behavior
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="Converting to PeriodArray/Index representation will drop timezone information",
        )
        dates = dates.dt.to_period("M").dt.to_timestamp()

    df.columns = dates

    # Sort columns by date and keep only the last occurrence for duplicate months
    df = df.loc[:, ~df.columns.duplicated(keep="last")]

    # Format the dates as "MMM YYYY"
    datesstr = df.columns.strftime("%b %Y")
    df.columns = datesstr

    return df


if __name__ == "__main__":
    pass
