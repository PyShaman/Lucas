import os
import sys
import pandas as pd
from datetime import datetime, date, timedelta


def resource_path(relative_path):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def format_time(time):
    minutes = int(time)
    seconds = int((time * 60) % 60)
    return f"{minutes}\'{seconds}\'\'"

df = pd.read_excel(resource_path("test_data_1.xlsx"))
sterile_hold_min_temp_list = []
sterile_hold_end_temp_list = []
sterile_hold_elapsed_time = {}
for column in range(1, len(df.columns)):
    sterile_hold_min_temp_row = (df[f'Temp_{column}'].values >= 121.0).argmax()
    sterile_hold_min_time = df.at[sterile_hold_min_temp_row, 'TIME']
    sterile_hold_min_temp_list.append(sterile_hold_min_temp_row)
last_termocouple_temp_121_row = max(range(len(sterile_hold_min_temp_list)),
                                    key=sterile_hold_min_temp_list.__getitem__)

for column in range(1, len(df.columns)):
    sterile_hold_end_temp_row = (df[f'Temp_{column}'][sterile_hold_min_temp_list[last_termocouple_temp_121_row]:]
                                 .values < 121.0).argmax()
    sterile_hold_end_time = df.at[sterile_hold_end_temp_row, 'TIME']
    sterile_hold_end_temp_list.append(sterile_hold_end_temp_row)
first_termocouple_temp_121_sterile_hold_row = max(range(len(sterile_hold_end_temp_list)),
                                                  key=sterile_hold_end_temp_list.__getitem__)


new_df = pd.DataFrame(df)[sterile_hold_min_temp_list[last_termocouple_temp_121_row]:
                          sterile_hold_min_temp_list[last_termocouple_temp_121_row] + sterile_hold_end_temp_list[first_termocouple_temp_121_sterile_hold_row]].copy(deep=True)
# print(new_df)
start_time_row = sterile_hold_min_temp_list[last_termocouple_temp_121_row]
end_time_row = sterile_hold_min_temp_list[last_termocouple_temp_121_row] + sterile_hold_end_temp_list[first_termocouple_temp_121_sterile_hold_row]
start_time = df['TIME'][start_time_row]
end_time = df['TIME'][end_time_row]
# print(sterile_hold_min_temp_list)
# print(df['TIME'][0])
# for col in range(1, len(df.columns)):
#     print(abs(datetime.combine(date.today(), df['TIME'][0])-datetime.combine(date.today(), df['TIME'][sterile_hold_min_temp_list[col-1]])))
for col in range(1, len(df.columns)):
    print(df['TIME'][sterile_hold_min_temp_list[col-1]])


# print("abs(A-B): ", abs(datetime.combine(date.today(), start_time)-datetime.combine(date.today(), end_time)))
# print(df["TIME"][0])
# print(df["TIME"][df.shape[0]-1])
# print(f'process time: {abs(datetime.combine(date.today(), df["TIME"][0])-datetime.combine(date.today(), df["TIME"][df.shape[0]-1]))}')
# print(f'process time: {datetime.combine(date.today(), df["TIME"][df.shape[0]-1]) - datetime.combine(date.today(), df["TIME"][0])}')
# for col in range(1, len(new_df.columns)):
#     print(col, 'A:', new_df[f'Temp_{col}'].min(), "B:", new_df[f'Temp_{col}'].max(), "(B-A):", round(new_df[f'Temp_{col}'].max()-new_df[f'Temp_{col}'].min(), 2))


# x_axis = new_df['TIME'].index.tolist()
#
#

#
# f_list = []
# for column in range(1, len(df.columns)):
#     f0 = 0
#     for row in range(1, len(x_axis)):
#         f0 += 0.08333333*(10**((new_df.iloc[row][f'Temp_{column}']-121.0)/6.0))
#     print(f0)
#     f_list.append(format_time(f0))
# print(f_list)
