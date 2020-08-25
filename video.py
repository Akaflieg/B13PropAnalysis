from datetime import date, datetime
from functools import partial

from aerofiles.igc import Reader
import pandas as pd
import numpy as np
import cv2


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
data.plot()

FPS = 30
LENGTH = 34 * 60
START_TIME = datetime(hour=8, minute=22, second=0, day=20, month=8, year=2020)
data = data.resample("33.3ms").interpolate("linear")
# start_index = data.index.get_loc(START_TIME)
start_index = data.index.searchsorted(START_TIME)

out = cv2.VideoWriter('project.mp4', cv2.VideoWriter_fourcc(*'MP4V'), 30, (1920, 1080), True)

for i in range(start_index, start_index + FPS * LENGTH):
    print(f"{i + 1} / {FPS * LENGTH + start_index}")
    img = np.ones((1080, 1920, 3), dtype="uint8")
    tas = data.iloc[i].TAS
    alt = data.iloc[i].gps_alt
    img = cv2.rectangle(img, (0, 0), (1920, 60), (255, 255, 255), -1)
    img = cv2.putText(img, f"TAS: {tas:.2f}km/h", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0))
    img = cv2.putText(img, f"ALT: {alt:.2f}m", (400, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0))

    out.write(img)

out.release()
