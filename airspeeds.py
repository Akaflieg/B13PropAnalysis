from datetime import date, datetime
from functools import partial

from aerofiles.igc import Reader
import pandas as pd
import numpy as np
import cv2
import matplotlib.pyplot as plt


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
    df["TAS"] = df["TAS"] / 100  # km/h

    df["rlat"] = np.radians(df["lat"])
    df["rlon"] = np.radians(df["lon"])
    shifted = df.shift(-1)
    df["a"] = np.sin((df["rlat"] - shifted["rlat"])/2)**2 + np.cos(df["rlat"]) * np.cos(shifted["rlat"]) * np.sin((df["rlon"] - shifted["rlon"])/2)**2

    df["vGPS"] = 2 * 6371 * np.arcsin(np.sqrt(df["a"])
    df["vGPS"] *= 1000 * 3.6
    df["vGPS"] /= 3
    df["diff"] = df["TAS"] - df["vGPS"]

    df["vs"] = df["pressure_alt"].diff()
    df["vs_smooth"] = df["vs"].rolling(5).mean()

    return df


START = datetime(year=2020, month=8, day=20, hour=10, minute=48, second=0)
END = datetime(year=2020, month=8, day=20, hour=10, minute=49, second=0)

igc = read_igc(
    r"C:\Users\Oisin\Akaflieg Berlin e.V\Akaflieg Berlin - Documents\B13 Sommertreffen\Überziehen\IGC Logs\2020-08-20 Überzeihversuche.igc")
data = analyse_igc(igc)
data = data[(data.index >= START) & (data.index <= END)]
ax = data[["TAS", "vGPS", "diff"]].plot(grid=True)
plt.show()