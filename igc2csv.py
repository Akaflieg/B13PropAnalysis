import pandas as pd
from functools import partial
from aerofiles.igc import Reader
from datetime import date, datetime


def read_igc(filename):
    igc_reader = Reader()

    with open(filename, "r") as f:
        return igc_reader.read(f)


def normalise_datetime(df):
    to_datetime = partial(datetime.combine, date(2020, 8, 20))
    df["time"] = df["time"].apply(to_datetime)
    df.set_index("time", inplace=True)
    return df


def analyse_igc(igc_data):
    df = pd.DataFrame(igc_data["fix_records"][1])
    df = df.drop(["validity"], axis=1)
    df = normalise_datetime(df)
    # df = resample(df)
    df["TAS"] = df["TAS"] / 100  # m/s

    # print(df.diff()["pressure_alt"] / df.index.to_series().diff())
    # df["alt"] = np.gradient(df["pressure_alt"])
    df["vs"] = df["pressure_alt"].diff()
    df["vs_smooth"] = df["vs"].rolling(5).mean()

    return df


igc = read_igc(
    r"C:\Users\Oisin\Akaflieg Berlin e.V\Akaflieg Berlin - Documents\B13 Sommertreffen\Überziehen\IGC Logs\2020-08-21 Überziehen Kurvenflug.igc")
data = analyse_igc(igc)
data.to_csv("data.csv")