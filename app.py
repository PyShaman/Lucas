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

from timeit import default_timer as timer


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
        self.protocol_labels = dict()

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
        stat_open = timer()
        try:
            file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open File", "", "Excel (*.xlsx)")
            df = pd.read_excel(resource_path(file_name))
            model = PandasModel(df)
            self.table.setModel(model)
            self.termocouple_number.setText(str(len(df.columns) - 1))
            self.process_time.setText(str(abs(
                datetime.combine(date.today(), df["TIME"][0])
                - datetime.combine(date.today(), df["TIME"][df.shape[0] - 1]))))
            self.validation_btn.setEnabled(True)
            self.calculate_btn.setEnabled(False)
        except FileNotFoundError:
            pass
        end_open = timer()
        print(f'Opening file: {end_open-stat_open}')

    @staticmethod
    def format_time(time):
        minutes = int(time)
        seconds = int((time * 60) % 60)
        return f"{minutes}\'{seconds}\'\'"

    def validate_data(self):
        global new_df
        global sterile_hold_min_temp_list
        start_validate = timer()
        self.clear_btn.setEnabled(False)
        sterile_hold_min_temp_list = []
        sterile_hold_end_temp_list = []
        for column in range(1, len(df.columns)):
            sterile_hold_min_temp_row = (df[f'Temp_{column}'].values >= 121.0).argmax()
            sterile_hold_min_temp_list.append(sterile_hold_min_temp_row)
        last_termocouple_temp_121_row = max(range(len(sterile_hold_min_temp_list)),
                                            key=sterile_hold_min_temp_list.__getitem__)

        for column in range(1, len(df.columns)):
            sterile_hold_end_temp_row = (df[f'Temp_{column}'][sterile_hold_min_temp_list[
                                                                  last_termocouple_temp_121_row]:].values < 121.0).argmax()
            sterile_hold_end_temp_list.append(sterile_hold_end_temp_row)
        first_termocouple_temp_121_sterile_hold_row = min(range(len(sterile_hold_end_temp_list)),
                                                          key=sterile_hold_end_temp_list.__getitem__)
        start_time_row = sterile_hold_min_temp_list[last_termocouple_temp_121_row]
        end_time_row = sterile_hold_min_temp_list[last_termocouple_temp_121_row] + sterile_hold_end_temp_list[
            first_termocouple_temp_121_sterile_hold_row]
        start_time = df['TIME'][start_time_row]
        end_time = df['TIME'][end_time_row]
        new_df = pd.DataFrame(df)[sterile_hold_min_temp_list[last_termocouple_temp_121_row]:
                                  sterile_hold_min_temp_list[last_termocouple_temp_121_row] +
                                  sterile_hold_end_temp_list[first_termocouple_temp_121_sterile_hold_row]].copy(deep=True)
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
        if (temp_df.values > 123.0).any():
            self.validation_label.setStyleSheet(
                'background-color: rgb(255, 0, 0);color: rgb(255, 255, 255);font: 75 16pt "Century Gothic";')
            self.validation_label.setText('Sterile Hold invalid!')
        self.start_time.setText(str(start_time))
        self.stop_time.setText(str(end_time))
        delta_time = abs(datetime.combine(date.today(), start_time) - datetime.combine(date.today(), end_time))
        if timedelta(minutes=15, seconds=0) <= delta_time <= timedelta(minutes=15, seconds=30):
            self.time_delta.setStyleSheet('font: 75 16pt "Century Gothic";color: rgb(0, 255, 0);')
        else:
            self.time_delta.setStyleSheet('font: 75 16pt "Century Gothic";color: rgb(255, 0, 0);')

        self.time_delta.setText(str(delta_time))
        self.calculate_btn.setEnabled(True)
        end_validate = timer()
        print(f'Validate data: {end_validate - start_validate}')

    def calculate_data(self):
        start_calculate = timer()
        self.graphics_view.clear()
        self.clear_btn.setEnabled(True)
        colors = ['#FF0000', '#FF8000', '#FFFF00', '#80FF00', '#00FF00', '#00FF80', '#00FFFF', '#0080FF', '#0000FF',
                  '#7F00FF', '#FF00FF', '#FF007F', '#FF0000', '#FF8000', '#FFFF00', '#80FF00', '#00FF00', '#00FF80',
                  '#00FFFF', '#0080FF', '#0000FF', '#7F00FF', '#FF00FF', '#FF007F', '#FF0000', '#FF8000', '#FFFF00',
                  '#80FF00', '#00FF00', '#00FF80', '#00FFFF', '#0080FF', '#0000FF', '#7F00FF', '#FF00FF', '#FF007F',
                  '#FF0000', '#FF8000', '#FFFF00', '#80FF00', '#00FF00', '#00FF80', '#00FFFF', '#0080FF', '#0000FF',
                  '#7F00FF', '#FF00FF', '#FF007F']
        x_axis = new_df['TIME'].index.tolist()
        self.graphics_view.getPlotItem().setLabel('bottom', "Time index")
        self.graphics_view.getPlotItem().setLabel('left', "Temperature")
        self.graphics_view.getPlotItem().addLegend()
        self.graphics_view.getPlotItem().addLine(y=121.0, pen=pg.mkPen(style=QtCore.Qt.DotLine, color='#FFFFFF'))
        self.graphics_view.getPlotItem().addLine(y=123.0, pen=pg.mkPen(style=QtCore.Qt.DotLine, color='#FFFFFF'))
        for column in range(1, len(df.columns)):
            y_axis = new_df[f'Temp_{column}'].values.tolist()
            self.graphics_view.plot(x_axis, y_axis, pen=pg.mkPen(color=colors[column - 1]), name=f'T{column}')
        f_list = []
        for column in range(1, len(df.columns)):
            f0 = 0
            for row in range(1, len(x_axis)):
                f0 += 0.08333333 * (10 ** ((new_df.iloc[row][f'Temp_{column}'] - 121.0) / 6.0))
            f_list.append(f0)
        # col = row = 0
        # for n in range(1, len(f_list) + 1):
        #     self.labels[f'label_{n}'] = QtWidgets.QLabel(self.partial_f0_box)
        #     self.labels[f'label_{n}'].setStyleSheet(f'background-color: {colors[n - 1]};color : black;')
        #     self.labels[f'label_{n}'].setText(f'[T{n}] F0={self.format_time(f_list[n - 1])}')
        #     self.labels[f'label_{n}'].setAlignment(QtCore.Qt.AlignCenter)
        #     self.labels[f'label_{n}'].setObjectName(f'label_{n}')
        #     self.gridLayout.addWidget(self.labels[f"label_{n}"], col, row, 1, 1)
        #     row += 1
        #     if row == 4:
        #         row = 0
        #         col += 1
        self.T_total.setText(f'F_average = {self.format_time(sum(f_list) / len(f_list))}')
        for m in range(1, len(f_list) + 1):
            self.protocol_labels[f'lc_{m}'] = QtWidgets.QLabel(self.validation_protocol_box)
            self.protocol_labels[f'lc_{m}'].setStyleSheet(f'background-color: {colors[m - 1]};color : black;')
            self.protocol_labels[f'lc_{m}'].setText(f'{m}')
            self.protocol_labels[f'lc_{m}'].setAlignment(QtCore.Qt.AlignCenter)
            self.protocol_labels[f'lc_{m}'].setObjectName(f'lc_{m}')
            self.gridLayout_5.addWidget(self.protocol_labels[f"lc_{m}"], m, 0, 1, 1)

            self.protocol_labels[f'tfs_{m}'] = QtWidgets.QLabel(self.validation_protocol_box)
            self.protocol_labels[f'tfs_{m}'].setStyleSheet(f'background-color: {colors[m - 1]};color : black;')
            self.protocol_labels[f'tfs_{m}'].setText(f'{abs(datetime.combine(date.today(), df["TIME"][0])-datetime.combine(date.today(), df["TIME"][sterile_hold_min_temp_list[m-1]]))}')
            self.protocol_labels[f'tfs_{m}'].setAlignment(QtCore.Qt.AlignCenter)
            self.protocol_labels[f'tfs_{m}'].setObjectName(f'tfs_{m}')
            self.gridLayout_5.addWidget(self.protocol_labels[f"tfs_{m}"], m, 1, 1, 1)

            self.protocol_labels[f'tas_{m}'] = QtWidgets.QLabel(self.validation_protocol_box)
            self.protocol_labels[f'tas_{m}'].setStyleSheet(f'background-color: {colors[m - 1]};color : black;')
            self.protocol_labels[f'tas_{m}'].setText(f'{df["TIME"][sterile_hold_min_temp_list[m-1]]}')
            self.protocol_labels[f'tas_{m}'].setAlignment(QtCore.Qt.AlignCenter)
            self.protocol_labels[f'tas_{m}'].setObjectName(f'tas_{m}')
            self.gridLayout_5.addWidget(self.protocol_labels[f"tas_{m}"], m, 2, 1, 1)

            self.protocol_labels[f't_min_{m}'] = QtWidgets.QLabel(self.validation_protocol_box)
            self.protocol_labels[f't_min_{m}'].setStyleSheet(f'background-color: {colors[m - 1]};color : black;')
            self.protocol_labels[f't_min_{m}'].setText(f'{round(new_df[f"Temp_{m}"].min(),2)}')
            self.protocol_labels[f't_min_{m}'].setAlignment(QtCore.Qt.AlignCenter)
            self.protocol_labels[f't_min_{m}'].setObjectName(f't_min_{m}')
            self.gridLayout_5.addWidget(self.protocol_labels[f"t_min_{m}"], m, 3, 1, 1)

            self.protocol_labels[f't_max_{m}'] = QtWidgets.QLabel(self.validation_protocol_box)
            self.protocol_labels[f't_max_{m}'].setStyleSheet(f'background-color: {colors[m - 1]};color : black;')
            self.protocol_labels[f't_max_{m}'].setText(f'{round(new_df[f"Temp_{m}"].max(),2)}')
            self.protocol_labels[f't_max_{m}'].setAlignment(QtCore.Qt.AlignCenter)
            self.protocol_labels[f't_max_{m}'].setObjectName(f't_max_{m}')
            self.gridLayout_5.addWidget(self.protocol_labels[f"t_max_{m}"], m, 4, 1, 1)

            self.protocol_labels[f'ttf_{m}'] = QtWidgets.QLabel(self.validation_protocol_box)
            self.protocol_labels[f'ttf_{m}'].setStyleSheet(f'background-color: {colors[m - 1]};color : black;')
            self.protocol_labels[f'ttf_{m}'].setText(f'{round(new_df[f"Temp_{m}"].max()-new_df[f"Temp_{m}"].min(), 2)}')
            self.protocol_labels[f'ttf_{m}'].setAlignment(QtCore.Qt.AlignCenter)
            self.protocol_labels[f'ttf_{m}'].setObjectName(f'ttf_{m}')
            self.gridLayout_5.addWidget(self.protocol_labels[f"ttf_{m}"], m, 5, 1, 1)

            self.protocol_labels[f'f0v_{m}'] = QtWidgets.QLabel(self.validation_protocol_box)
            self.protocol_labels[f'f0v_{m}'].setStyleSheet(f'background-color: {colors[m - 1]};color : black;')
            self.protocol_labels[f'f0v_{m}'].setText(f'{round(f_list[m - 1], 4)}')
            self.protocol_labels[f'f0v_{m}'].setAlignment(QtCore.Qt.AlignCenter)
            self.protocol_labels[f'f0v_{m}'].setObjectName(f'f0v_{m}')
            self.gridLayout_5.addWidget(self.protocol_labels[f"f0v_{m}"], m, 6, 1, 1)

            self.protocol_labels[f'f0vr_{m}'] = QtWidgets.QLabel(self.validation_protocol_box)
            self.protocol_labels[f'f0vr_{m}'].setStyleSheet(f'background-color: {colors[m - 1]};color : black;')
            self.protocol_labels[f'f0vr_{m}'].setText(f'{self.format_time(f_list[m - 1])}')
            self.protocol_labels[f'f0vr_{m}'].setAlignment(QtCore.Qt.AlignCenter)
            self.protocol_labels[f'f0vr_{m}'].setObjectName(f'f0vr_{m}')
            self.gridLayout_5.addWidget(self.protocol_labels[f"f0vr_{m}"], m, 7, 1, 1)
        end_calculate = timer()
        print(f'Calculate data: {end_calculate - start_calculate}')

    def clear_data(self):
        start_clear = timer()
        self.termocouple_number.setText("")
        self.process_time.setText("")
        self.validation_label.setStyleSheet("")
        self.validation_label.setText("")
        self.start_time.setText("")
        self.stop_time.setText("")
        self.time_delta.setText("")
        self.table.setModel(None)
        self.T_total.setText("")
        self.graphics_view.clear()
        # index = self.gridLayout.count()
        # while index > 0:
        #     self.gridLayout.itemAt(index - 1).widget().setParent(None)
        #     index -= 1
        index_2 = self.gridLayout_5.count()
        while index_2 > 8:
            self.gridLayout_5.itemAt(index_2 - 1).widget().setParent(None)
            index_2 -= 1
        self.validation_btn.setEnabled(False)
        self.calculate_btn.setEnabled(False)
        self.clear_btn.setEnabled(False)
        end_clear = timer()
        print(f'Clear data: {end_clear - start_clear}')


def main():
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
