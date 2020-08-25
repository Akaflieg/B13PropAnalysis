import sys
from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtWidgets import *
from matplotlib.backends.backend_qt5agg import (
    FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure


class PropAnalysisWidgetBase(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.main_widget = QWidget()

        self.logfile = ""

        # self.setTitle("B13 Prop Analysis")

        self.fig = Figure()
        self.fig_canvas = FigureCanvas(self.fig)
        self.value_table = None
        self.select_button = QPushButton("Load")
        self.remove_button = QPushButton("Remove selected")
        self.save_button = QPushButton("Save")
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(1)
        self.data_table.setHorizontalHeaderLabels(["avg vs"])
        self.data_table.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.addToolBar(QtCore.Qt.BottomToolBarArea,
                        NavigationToolbar(self.fig_canvas, self))

        self.layout = QGridLayout()
        self.layout.addWidget(self.fig_canvas, 0, 0, 2, 1)
        self.layout.addWidget(self.data_table, 1, 1, 1, 3)
        self.layout.addWidget(self.select_button, 0, 1)
        self.layout.addWidget(self.remove_button, 0, 2)
        self.layout.addWidget(self.save_button, 0, 3)
        self.main_widget.setLayout(self.layout)
        self.setCentralWidget(self.main_widget)

        self.select_button.pressed.connect(self.select_log)
        self.remove_button.pressed.connect(self.remove_selected)
        self.save_button.pressed.connect(self.save)

        self.igc_selector = QFileDialog(self)
        self.igc_selector.setFileMode(QFileDialog.ExistingFile)
        self.igc_selector.setNameFilter("IGC Files (*.igc)")

    def select_log(self):
        if self.igc_selector.exec_():
            self.logfile = self.igc_selector.selectedFiles()[0]
            self.show_data(self.logfile)

    def show_data(self, filename):
        pass

    def remove_selected(self):
        pass

    def save(self):
        pass


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = PropAnalysisWidgetBase()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec_())
