import json
import pandas as pd  # type:ignore
import os


def json_to_arr(file):
    with open(file, "r") as f:
        return json.load(f)


def arr_to_df(data):
    return pd.DataFrame(
        [i[1:] for i in data[1:]], index=[i[0] for i in data[1:]], columns=data[0][1:]
    )


if __name__ == "__main__":
    os.chdir("./projects/PYPL/")
    data = json_to_arr("All.json")
