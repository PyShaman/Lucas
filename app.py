import os
import pandas as pd
import sys
from datetime import datetime, date, timedelta
from model import PandasModel
from os import path
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


FORM_CLASS, _ = loadUiType(path.join(resource_path("main.ui")))


class Main(QMainWindow, FORM_CLASS):
    def __init__(self, parent=None):
        super(Main, self).__init__(parent)
        QMainWindow.__init__(self)
        QMainWindow.setFixedSize(self, 641, 463)
        self.setupUi(self)
        self.buttons()

    def buttons(self):
        self.load_btn.clicked.connect(self.open_file)
        self.validation_btn.clicked.connect(self.validate_data)

    def open_file(self):
        global df
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open File", "", "Excel (*.xlsx)")
        df = pd.read_excel(file_name)
        model = PandasModel(df)
        self.table.setModel(model)
        self.termocouple_number.setText(str(len(df.columns)-1))

    def validate_data(self):
        sterile_hold_min_temp_list = []
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
        delta_time = datetime.combine(date.today(), new_df.iloc[186]['TIME']) - datetime.combine(date.today(), new_df.iloc[0]['TIME'])
        if delta_time == timedelta(minutes=15, seconds=30):
            self.time_delta.setStyleSheet('font: 75 16pt "Century Gothic";color: rgb(20, 125, 0);')
        else:
            self.time_delta.setStyleSheet('font: 75 16pt "Century Gothic";color: rgb(255, 0, 0);')
        self.time_delta.setText(str(delta_time))


def main():
    app = QApplication(sys.argv)
    window = Main()
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
