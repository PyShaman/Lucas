import os
import pandas as pd
import sys
import time
from colorama import Fore, init
from datetime import datetime, date, timedelta
from model import PandasModel


class App:

    def __init__(self):
        pass

    # @staticmethod
    # def prepare_data_frame(tmcpl):
    #     dtype = {'Time': datetime, }
    #     columns = []
    #     for column in range(1, tmcpl + 1):
    #         dtype[f'Temp_{column}[*C]'] = float
    #         columns.append(f'Temp_{column}[*C]')
    #     return dtype, columns

    # @staticmethod
    # def check_if_temperature_drops(low, high):

    @staticmethod
    def convert(sec):
        return str(timedelta(seconds=sec))

    def read_data(self):
        init()
        ws = pd.read_excel("data.xlsx")
        df = pd.DataFrame(ws)
        # sterile_hold_criteria = df[(df.iloc[:, 1:tmcpl+1] >= 121.0) & (df.iloc[:, 1:tmcpl+1] < 123.0)]
        # sterile_hold_min_temp = (df.Temp_1.values >= 121.0).argmax()
        # sterile_hold_max_temp = (df.Temp_1.values >= 123.0).argmax()
        # print(f"[+] Sterile hold criteria: \n{sterile_hold_criteria}")
        # print(f"[+] Sterile hold min temperature row (>=121.0*C): {sterile_hold_min_temp}")
        # print(f"[+] Sterile hold max temperature row (>=123.0*C): {sterile_hold_max_temp}")
        # sterile_hold_min_time = df.at[sterile_hold_min_temp, 'TIME']
        # sterile_hold_max_time = df.at[sterile_hold_max_temp, 'TIME']
        # print(f"[+] Sterile hold min temperature time (>=121.0*C): {sterile_hold_min_time}")
        # print(f"[+] Sterile hold max temperature time (>=123.0*C): {sterile_hold_max_time}")
        # time_difference = datetime.combine(date.today(), sterile_hold_max_time) - datetime.combine(date.today(),
        #                                                                                            sterile_hold_min_time)
        # print(f"Time span of Sterile Hold: {time_difference}")
        # time_difference_seconds = pd.Timedelta(time_difference).seconds
        # if time_difference_seconds < 930:
        #     print(f"[-] Sterile hold was shorter than 00:15:30 and lasted {time_difference}!")
        # elif time_difference == 930:
        #     print("[+] Sterile hold was equal to 00:15:30!")
        # else:
        #     print(f"[-] Sterile hold was longer than 00:15:30 and lasted {time_difference}!")

        sterile_hold_min_temp_dict = {}
        sterile_hold_min_temp_list = []
        sterile_hold_max_temp_dict = {}
        sterile_hold_min_time_dict = {}
        sterile_hold_max_time_dict = {}
        sterile_hold_elapsed_time = {}
        for column in range(1, len(df.columns)):
            sterile_hold_min_temp_row = (df[f'Temp_{column}'].values >= 121.0).argmax()
            sterile_hold_max_temp_row = (df[f'Temp_{column}'].values >= 123.0).argmax()
            sterile_hold_bad_temp_row = (df[f'Temp_{column}'].values < 121.0).argmax()
            sterile_hold_min_time = df.at[sterile_hold_min_temp_row, 'TIME']
            sterile_hold_max_time = df.at[sterile_hold_max_temp_row, 'TIME']
            time_difference = datetime.combine(date.today(), sterile_hold_max_time) - datetime.combine(date.today(), sterile_hold_min_time)
            sterile_hold_min_temp_dict[f'Temp_{column}'] = sterile_hold_min_temp_row
            sterile_hold_min_temp_list.append(sterile_hold_min_temp_row)
            sterile_hold_max_temp_dict[f'Temp_{column}'] = sterile_hold_max_temp_row
            sterile_hold_min_time_dict[f'Temp_{column}'] = sterile_hold_min_time
            sterile_hold_max_time_dict[f'Temp_{column}'] = sterile_hold_max_time
            sterile_hold_elapsed_time[f'Temp_{column}'] = self.convert(pd.Timedelta(time_difference).seconds)

        last_termocouple_temp_121_row = max(range(len(sterile_hold_min_temp_list)),key=sterile_hold_min_temp_list.__getitem__)
        new_df = pd.DataFrame(ws)[sterile_hold_min_temp_list[last_termocouple_temp_121_row]:sterile_hold_min_temp_list[last_termocouple_temp_121_row] + 186].copy(deep=True).drop(['TIME'], axis=1)
        print(new_df)
        # print((new_df.values < 121.0).any())
        if (new_df.values < 121.0).any():
            print(f"{Fore.RED}Sterile Hold invalid!{Fore.RESET}")
        else:
            print(f"{Fore.GREEN}Sterile Hold is valid!{Fore.RESET}")
        # for column in range(1, tmcpl + 1):
        #     if new_df[f'Temp_{column}'].values.any(axis=1) < 121.0:
        #         print(f"Sterile Hold broken on the Temp_{column}:{(df[f'Temp_{column}'].values < 121.0).argmax()} !!!")
        #     else:
        #         print("Sterile Hold is valid!")./ve
        # print(new_df)
        # print(sterile_hold_min_temp_dict)
        # print(last_termocouple_temp_121_row)
        # print(sterile_hold_max_temp_dict)
        # print(sterile_hold_min_time_dict)
        # print(sterile_hold_max_time_dict)
        # print(sterile_hold_elapsed_time)


def main():
    app = App()
    app.read_data()


if __name__ == '__main__':
    main()
