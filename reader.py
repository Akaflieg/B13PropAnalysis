from aerofiles.igc import Reader
from pprint import pprint
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches
import matplotlib.widgets as mwidgets
import matplotlib.dates as mdate
import numpy as np
import datetime
from functools import partial
from datetime import datetime, date

igc_reader = Reader()

date = date(2019, 8, 21)
rects = []
fig, (ax_data_1, ax_zones) = plt.subplots(2, 1, sharex=False)
# fig, ax_data_1 = plt.subplots()
ax_data_2 = ax_data_1.twinx()

zones = []

with open("data.igc", "r") as f:
    parsed_igc_file = igc_reader.read(f)

def normalise_datetime(df):
    to_datetime = partial(datetime.combine, date)
    df["time"] = df["time"].apply(to_datetime)
    df.set_index("time", inplace=True)
    # df.sort_index(inplace=True)
    return df

def resample(df, freq=1):
    return df.resample("1s", base=0).interpolate(method="time").dropna()

def onselect(vmin, vmax):
    global df

    if abs(vmax - vmin) < 0.0005:
        return

    zones.append([vmin, vmax])
    ax_data_2.text((vmax+vmin)/2, 0, len(zones), horizontalalignment="center")
    ax_data_2.axvspan(vmin, vmax, alpha=0.5)
    print(vmin, vmax)

    vmin_dt = datetime.fromtimestamp(vmin)
    vmax_dt = datetime.fromtimestamp(vmax)

    selections = df.index.to_series()
    selections = pd.to_numeric(selections)
    selections[:] = np.nan
    # return
    selections.loc[vmin_dt:vmax_dt] = df["vs"][vmin_dt:vmax_dt].mean()

    print(selections)
    print(selections[selections.notna().any()])

    #ax_zones.clear()
    ax_zones.plot(selections)

m = 818  # kg
g = 9.81  # m/s^2

print(f"Parsing logger file from {parsed_igc_file['header'][1]['glider_registration']}")

df = pd.DataFrame(parsed_igc_file["fix_records"][1])
df = df.drop(["validity"], axis=1)
df = normalise_datetime(df)
df = resample(df)
df["TAS"] = df["TAS"] / 100 / 3.6  # m/s
df["Ekin"] = 0.5 * m * df["TAS"] ** 2  # J
df["Epot"] = m * df["gps_alt"] * g  # J
df["E"] = df["Ekin"] + df["Epot"]  # J

# print(df.diff()["pressure_alt"])
# print(df.index.to_series().diff())
# print(df.diff()["pressure_alt"] / df.index.to_series().diff())
# df["alt"] = np.gradient(df["pressure_alt"])
df["vs"] = df["pressure_alt"].diff()
df["vs_smooth"] = df["vs"].rolling(5).mean()

ax_data_2.grid()

# ani = animation.FuncAnimation(fig, draw, interval=20)

rectprops = dict(facecolor='blue', alpha=0.5)

df[["vs", "vs_smooth"]].plot(ax=ax_data_1)
df[["pressure_alt"]].plot(ax=ax_data_2, color="green", linewidth=1)

span = mwidgets.SpanSelector(ax_data_2, onselect, 'horizontal', span_stays=True, rectprops=rectprops)
print(df[df.isna().any(axis=1)].head(50))

plt.show()
# df.to_csv("data.csv")