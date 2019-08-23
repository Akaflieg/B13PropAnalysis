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
from gui import PropAnalysisWidgetBase
from PySide2 import QtWidgets
import sys

m = 818  # kg
g = 9.81  # m/s^2

# fig, (ax_data_1, ax_zones) = plt.subplots(2, 1, sharex=False)

class PropAnalysisWidget(PropAnalysisWidgetBase):
    """docstring for ClassName"""

    def __init__(self):
        super().__init__()

        self.df = None
        self.zones = []

    def show_data(self, filename):
        self.df = analyse_igc(read_igc(filename))

        self.ax_data_1 = self.fig.add_subplot(111)
        self.ax_data_2 = self.ax_data_1.twinx()

        self.ax_data_2.grid()

        self.df[["vs", "vs_smooth"]].plot(ax=self.ax_data_1)
        self.df[["pressure_alt"]].plot(
            ax=self.ax_data_2, color="green", linewidth=1)

        self.span = mwidgets.SpanSelector(self.ax_data_2, self.onselect, 'horizontal',
                                     span_stays=True, rectprops=dict(facecolor='blue', alpha=0.5), useblit=True)
        # print(df[df.isna().any(axis=1)].head(50))

        # plt.show()
        self.fig_canvas.draw()

    def onselect(self, vmin, vmax):
        if abs(vmax - vmin) < 0.0005:
            return

        self.zones.append([vmin, vmax])
        self.ax_data_2.text((vmax + vmin) / 2, 0, len(self.zones),
                       horizontalalignment="center")
        self.ax_data_2.axvspan(vmin, vmax, alpha=0.5)

        vmin_dt = datetime.utcfromtimestamp(vmin)
        vmax_dt = datetime.utcfromtimestamp(vmax)

        # selections = df.index.to_series()
        # selections = pd.to_numeric(selections)
        # selections[:] = np.nan
        # return
        # selections.loc[vmin_dt:vmax_dt] = df["vs"][vmin_dt:vmax_dt].mean()

        # ax_zones.clear()
        # ax_zones.plot(selections)


def read_igc(filename):
    igc_reader = Reader()
    
    with open(filename, "r") as f:
        return igc_reader.read(f)


def normalise_datetime(df):
    to_datetime = partial(datetime.combine, date(2019, 8, 21))
    df["time"] = df["time"].apply(to_datetime)
    df.set_index("time", inplace=True)
    return df


def resample(df, freq=1):
    return df.resample("1s", base=0).interpolate(method="time").dropna()


def analyse_igc(igc_data):
    df = pd.DataFrame(igc_data["fix_records"][1])
    df = df.drop(["validity"], axis=1)
    df = normalise_datetime(df)
    df = resample(df)
    df["TAS"] = df["TAS"] / 100 / 3.6  # m/s
    df["Ekin"] = 0.5 * m * df["TAS"] ** 2  # J
    df["Epot"] = m * df["gps_alt"] * g  # J
    df["E"] = df["Ekin"] + df["Epot"]  # J

    # print(df.diff()["pressure_alt"] / df.index.to_series().diff())
    # df["alt"] = np.gradient(df["pressure_alt"])
    df["vs"] = df["pressure_alt"].diff()
    df["vs_smooth"] = df["vs"].rolling(5).mean()

    return df


# print(f"Parsing logger file from {parsed_igc_file['header'][1]['glider_registration']}")



# df.to_csv("data.csv")
if __name__ == "__main__":
    print("run")
    app = QtWidgets.QApplication([])

    widget = PropAnalysisWidget()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec_())
