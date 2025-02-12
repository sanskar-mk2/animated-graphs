import json
import pandas as pd


def json_to_arr(file):
    with open(file, "r") as f:
        return json.load(f)


def arr_to_df(data):
    return pd.DataFrame(
        [i[1:] for i in data[1:]], index=[i[0] for i in data[1:]], columns=data[0][1:]
    )


def load_data(path):
    data = json_to_arr(path)
    df = arr_to_df(data)
    df = df.transpose()
    colname = df.columns.to_series()
    dates = pd.to_datetime(colname)
    datesstr = dates.strftime("%b %Y")
    df.columns = datesstr
    return df


if __name__ == "__main__":
    df = load_data("./PYPL/All.json")
    print(df)
