import os
import sys
import pandas as pd
from datetime import datetime, date, timedelta


def resource_path(relative_path):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


df = pd.read_excel(resource_path("valid_short_data.xlsx"))

# print(df['Temp_3'][338:])
sterile_hold_min_temp_list = []
sterile_hold_end_temp_list = []
sterile_hold_elapsed_time = {}
for column in range(1, len(df.columns)):
    sterile_hold_min_temp_row = (df[f'Temp_{column}'].values >= 121.0).argmax()
    sterile_hold_min_time = df.at[sterile_hold_min_temp_row, 'TIME']
    sterile_hold_min_temp_list.append(sterile_hold_min_temp_row)
last_termocouple_temp_121_row = max(range(len(sterile_hold_min_temp_list)), key=sterile_hold_min_temp_list.__getitem__)

for column in range(1, len(df.columns)):
    sterile_hold_end_temp_row = (df[f'Temp_{column}'][sterile_hold_min_temp_list[last_termocouple_temp_121_row]:].values < 121.0).argmax()
    sterile_hold_end_time = df.at[sterile_hold_end_temp_row, 'TIME']
    sterile_hold_end_temp_list.append(sterile_hold_end_temp_row)
first_termocouple_temp_121_sterile_hold_row = min(range(len(sterile_hold_end_temp_list)), key=sterile_hold_end_temp_list.__getitem__)

new_df = pd.DataFrame(df)[sterile_hold_min_temp_list[last_termocouple_temp_121_row]:
                          sterile_hold_min_temp_list[last_termocouple_temp_121_row] + sterile_hold_end_temp_list[first_termocouple_temp_121_sterile_hold_row]].copy(deep=True)
print(new_df)
# x_axis = new_df['TIME'].index.tolist()
#
#
# def format_time(time):
#     minutes = int(time)
#     seconds = int((time * 60) % 60)
#     return f"{minutes}\'{seconds}\'\'"
#
# f_list = []
# for column in range(1, len(df.columns)):
#     f0 = 0
#     for row in range(1, len(x_axis)):
#         f0 += 0.08333333*(10**((new_df.iloc[row][f'Temp_{column}']-121.0)/6.0))
#     print(f0)
#     f_list.append(format_time(f0))
# print(f_list)
