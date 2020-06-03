import os
import pandas as pd
import pyqtgraph as pg
import sys
from datetime import datetime, date, timedelta
from model import PandasModel
from pyqtgraph import PlotWidget, plot
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUiType


def resource_path(relative_path):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


FORM_CLASS, _ = loadUiType(resource_path("main_3.ui"))


class Main(QMainWindow, FORM_CLASS):
    def __init__(self, parent=None):
        super(Main, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.buttons()
        self.labels = dict()

    def buttons(self):
        self.load_btn.clicked.connect(self.open_file)
        self.validation_btn.setEnabled(False)
        self.validation_btn.clicked.connect(self.validate_data)
        self.calculate_btn.setEnabled(False)
        self.calculate_btn.clicked.connect(self.calculate_data)
        self.clear_btn.setEnabled(False)
        self.clear_btn.clicked.connect(self.clear_data)

    def open_file(self):
        global df
        try:
            file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open File", "", "Excel (*.xlsx)")
            df = pd.read_excel(resource_path(file_name))
            model = PandasModel(df)
            self.table.setModel(model)
            self.termocouple_number.setText(str(len(df.columns) - 1))
            self.validation_btn.setEnabled(True)
            self.calculate_btn.setEnabled(False)
        except FileNotFoundError:
            pass

    @staticmethod
    def format_time(time):
        minutes = int(time)
        seconds = int((time * 60) % 60)
        return f"{minutes}\'{seconds}\'\'"

    def validate_data(self):
        global new_df
        self.clear_btn.setEnabled(False)
        sterile_hold_min_temp_list = []
        sterile_hold_break_temp_list = []
        sterile_hold_elapsed_time = {}
        for column in range(1, len(df.columns)):
            sterile_hold_min_temp_row = (df[f'Temp_{column}'].values >= 121.0).argmax()
            sterile_hold_max_temp_row = (df[f'Temp_{column}'].values >= 123.0).argmax()
            sterile_hold_min_time = df.at[sterile_hold_min_temp_row, 'TIME']
            sterile_hold_max_time = df.at[sterile_hold_max_temp_row, 'TIME']
            time_difference = datetime.combine(date.today(), sterile_hold_max_time) \
                              - datetime.combine(date.today(), sterile_hold_min_time)
            sterile_hold_min_temp_row = (df[f'Temp_{column}'].values >= 121.0).argmax()
            sterile_hold_min_temp_list.append(sterile_hold_min_temp_row)
            sterile_hold_elapsed_time[f'Temp_{column}'] = str(timedelta(seconds=pd.Timedelta(time_difference).seconds))

        last_termocouple_temp_121_row = max(range(len(sterile_hold_min_temp_list)),
                                            key=sterile_hold_min_temp_list.__getitem__)
        new_df = pd.DataFrame(df)[sterile_hold_min_temp_list[last_termocouple_temp_121_row]:
                                  sterile_hold_min_temp_list[last_termocouple_temp_121_row] + 187].copy(deep=True)
        model = PandasModel(new_df)
        self.table.setModel(model)
        temp_df = new_df.drop(['TIME'], axis=1)
        if (temp_df.values >= 121.0).all() and (temp_df.values <= 123.0).all():
            self.validation_label.setStyleSheet(
                'background-color: rgb(75, 225, 0);color: rgb(20, 125, 0);font: 75 16pt "Century Gothic";')
            self.validation_label.setText('Sterile Hold valid!')
        if (temp_df.values < 121.0).any():
            self.validation_label.setStyleSheet(
                'background-color: rgb(255, 0, 0);color: rgb(255, 255, 255);font: 75 16pt "Century Gothic";')
            self.validation_label.setText('Sterile Hold invalid!')
        self.start_time.setText(str(new_df.iloc[0]['TIME']))
        self.stop_time.setText(str(new_df.iloc[186]['TIME']))
        delta_time = datetime.combine(date.today(), new_df.iloc[186]['TIME']) - datetime.combine(date.today(),
                                                                                                 new_df.iloc[0]['TIME'])
        if delta_time == timedelta(minutes=15, seconds=30):
            self.time_delta.setStyleSheet('font: 75 16pt "Century Gothic";color: rgb(20, 125, 0);')
        else:
            self.time_delta.setStyleSheet('font: 75 16pt "Century Gothic";color: rgb(255, 0, 0);')
        self.time_delta.setText(str(delta_time))
        self.calculate_btn.setEnabled(True)

    def calculate_data(self):
        self.graphics_view.clear()
        self.clear_btn.setEnabled(True)
        colors = ['#FF0000', '#FF8000', '#FFFF00', '#80FF00', '#00FF00', '#00FF80', '#00FFFF', '#0080FF', '#0000FF',
                  '#7F00FF', '#FF00FF', '#FF007F']
        x_axis = new_df['TIME'].index.tolist()
        self.graphics_view.getPlotItem().setLabel('bottom', "Time index")
        self.graphics_view.getPlotItem().setLabel('left', "Temperature")
        self.graphics_view.getPlotItem().addLegend()
        self.graphics_view.getPlotItem().addLine(y=121.0, pen=pg.mkPen(style=QtCore.Qt.DotLine, color='#FFFFFF'))
        self.graphics_view.getPlotItem().addLine(y=123.0, pen=pg.mkPen(style=QtCore.Qt.DotLine, color='#FFFFFF'))
        for column in range(1, len(df.columns)):
            y_axis = new_df[f'Temp_{column}'].values.tolist()
            self.graphics_view.plot(x_axis, y_axis, pen=pg.mkPen(color=colors[column-1]), name=f'T{column}')
        f_list = []
        for column in range(1, len(df.columns)):
            f0 = 0
            for row in range(1, len(x_axis)):
                f0 += 0.08333333 * (10 ** ((new_df.iloc[row][f'Temp_{column}'] - 121.0) / 6.0))
            f_list.append(f0)
        col = row = 0
        for n in range(1, len(f_list)+1):
            self.labels[f"label_{n}"] = QtWidgets.QLabel(self.partial_f0_box)
            self.labels[f"label_{n}"].setStyleSheet(f'background-color: {colors[n - 1]};color : black;')
            self.labels[f"label_{n}"].setText(f'[T{n}] F0={self.format_time(f_list[n - 1])}')
            self.labels[f"label_{n}"].setAlignment(QtCore
                              .Qt
                              .AlignCenter)
            self.labels[f"label_{n}"].setObjectName(f'label_{n}')
            self.gridLayout.addWidget(self.labels[f"label_{n}"], col, row, 1, 1)
            row += 1
            if row == 4:
                row = 0
                col += 1
        self.T_total.setText(f'F_average = {self.format_time(sum(f_list)/len(f_list))}')

    def clear_data(self):
        self.termocouple_number.setText("")
        self.validation_label.setStyleSheet("")
        self.validation_label.setText("")
        self.start_time.setText("")
        self.stop_time.setText("")
        self.time_delta.setText("")
        self.table.setModel(None)
        self.T_total.setText("")
        self.graphics_view.clear()
        index = self.gridLayout.count()
        while index > 0:
            self.gridLayout.itemAt(index - 1).widget().setParent(None)
            index -= 1
        self.validation_btn.setEnabled(False)
        self.calculate_btn.setEnabled(False)
        self.clear_btn.setEnabled(False)


def main():
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
