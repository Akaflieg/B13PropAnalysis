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

class Rectangle:
    def __init__(self):
        self.x0 = 0
        self.x1 = 0
        self.mousex = 0

    def start(self, event):
        self.x0 = event.xdata

    def on_motion(self, event):
        'on motion we will move the rect if the mouse is over us'
        if event.xdata:
            self.mousex = event.xdata

    def on_release(self, event):
        'on release we reset the press data'
        self.press = None
        self.rect.figure.canvas.draw()

    def disconnect(self):
        'disconnect all the stored connection ids'
        self.rect.figure.canvas.mpl_disconnect(self.cidpress)
        self.rect.figure.canvas.mpl_disconnect(self.cidrelease)
        self.rect.figure.canvas.mpl_disconnect(self.cidmotion)

    def draw(self, ax):
        ax.bar(self.x0, 500, self.mousex - self.x0, color=(1, 0, 0, 0.5), align='edge')

    def finish(self):
        pass

def normalise_datetime(df):
    to_datetime = partial(datetime.datetime.combine, date)
    df["time"] = df["time"].apply(to_datetime)
    df.set_index("time", inplace=True)
    return df

def resample(df, freq=1):
    return df.resample("1s", base=0).mean().dropna()

def onclick(event):
    global editing_rect

    if editing_rect:
        editing_rect.finish()
        editing_rect = None
    else:
        rect = Rectangle()
        rect.start(event)
        rects.append(rect)
        editing_rect = rect

def onmotion(event):
    global editing_rect

    if editing_rect:
        editing_rect.on_motion(event)

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

fig.canvas.mpl_connect('button_press_event', onclick)
fig.canvas.mpl_connect('motion_notify_event', onmotion)

plt.show()
# df.to_csv("data.csv")