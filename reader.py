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
fig, (ax_data_1, ax_zones) = plt.subplots(2, 1)
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
    return df.resample("1s", base=0).mean().dropna()

def onselect(vmin, vmax):
    global df

    if abs(vmax - vmin) < 0.0005:
        return

    zones.append([vmin, vmax])
    ax_data_2.text((vmax+vmin)/2, 0, len(zones), horizontalalignment="center")
    ax_data_2.axvspan(vmin, vmax, alpha=0.5)
    print(vmin, vmax)

    df = df.dropna()

    vmin_dt = mdate.num2date(vmin).replace(tzinfo=None)
    vmax_dt = mdate.num2date(vmax).replace(tzinfo=None)

    selections = df.index.to_series()
    selections = pd.to_numeric(selections)
    selections[:] = np.nan
    # return
    print(mdate.num2date(vmin))
    print(selections.index[0])
    print(selections[vmin_dt:vmax_dt])
    selections.loc[vmin_dt:vmax_dt] = df["alt_rol"][vmin_dt:vmax_dt].mean()

    print(selections)

    #ax_zones.clear()
    ax_zones.plot(selections)

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

ax_data_1.grid()

# ani = animation.FuncAnimation(fig, draw, interval=20)

rectprops = dict(facecolor='blue', alpha=0.5)

df[["alt", "alt_rol"]].plot(ax=ax_data_1)
df[["pressure_alt"]].plot(ax=ax_data_2, color="green", linewidth=1)

span = mwidgets.SpanSelector(ax_data_2, onselect, 'horizontal', span_stays=True, rectprops=rectprops)

plt.show()
# df.to_csv("data.csv")