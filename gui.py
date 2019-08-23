import sys
from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtWidgets import *
from matplotlib.backends.backend_qt5agg import (
    FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure


class PropAnalysisWidgetBase(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # self.setTitle("B13 Prop Analysis")

        self.fig = Figure()
        self.fig_canvas = FigureCanvas(self.fig)
        self.value_table = None
        self.select_button = QPushButton("Load")
        self.remove_button = QPushButton("Remove selected")

        self.layout = QGridLayout()
        self.layout.addWidget(self.fig_canvas, 0, 0, 2, 1)
        # self.layout.addWidget(self.value_table, 0, 1)
        self.layout.addWidget(self.remove_button, 0, 1)
        self.layout.addWidget(self.select_button, 1, 1)
        self.setLayout(self.layout)

        self.select_button.pressed.connect(self.select_log)


        self.igc_selector = QFileDialog(self)
        self.igc_selector.setFileMode(QFileDialog.ExistingFile)
        self.igc_selector.setNameFilter("IGC Files (*.igc)")

    def select_log(self):
        if self.igc_selector.exec_():
            print(self.igc_selector.selectedFiles())
            self.show_data(self.igc_selector.selectedFiles()[0])

    def show_data(self):
        pass

if __name__ == "__main__":
    print("run")
    app = QtWidgets.QApplication([])

    widget = PropAnalysisWidgetBase()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec_())