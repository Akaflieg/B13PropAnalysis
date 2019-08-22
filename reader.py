from aerofiles.igc import Reader
from pprint import pprint
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches
import numpy as np
import datetime
from functools import partial

igc_reader = Reader()

date = datetime.date(2019, 8, 21)
rects = []
fig, ax1 = plt.subplots()
ax2 = ax1.twinx()

editing_rect = None

with open("data.igc", "r") as f:
    parsed_igc_file = igc_reader.read(f)

def normalise_datetime(df):
    to_datetime = partial(datetime.datetime.combine, date)
    df["time"] = df["time"].apply(to_datetime)
    df.set_index("time", inplace=True)
    return df

def resample(df, freq=1):
    return df.resample("1s", base=0).mean().dropna()

m = 818  # kg
g = 9.81  # m/s^2

print(f"Parsing logger file from {parsed_igc_file['header'][1]['glider_registration']}")

df = pd.DataFrame(parsed_igc_file["fix_records"][1])
df = normalise_datetime(df)
df = resample(df)
df["TAS"] = df["TAS"] / 100 / 3.6  # m/s
df["Ekin"] = 0.5 * m * df["TAS"] ** 2  # J
df["Epot"] = m * df["gps_alt"] * g  # J
df["E"] = df["Ekin"] + df["Epot"]  # J
df["alt"] = np.gradient(df["pressure_alt"], edge_order=2)
df["alt_rol"] = df["alt"].rolling(5).mean()

ax1.grid()

def draw(_):
    global ax1

    ax1.clear()
    ax2.clear()

    df[["alt", "alt_rol"]].plot(ax=ax1)
    df[["pressure_alt"]].plot(ax=ax2, color="green", linewidth=1)

    for rect in rects:
        rect.draw(ax1)

ani = animation.FuncAnimation(fig, draw, interval=20)

plt.show()
# df.to_csv("data.csv")