# import os
# import sys
# import pandas as pd
# from datetime import datetime, date, timedelta
#
#
# def resource_path(relative_path):
#     base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
#     return os.path.join(base_path, relative_path)
#
#
# df = pd.read_excel(resource_path("valid_short_data.xlsx"))
# sterile_hold_min_temp_list = []
# sterile_hold_elapsed_time = {}
# for column in range(1, len(df.columns)):
#     sterile_hold_min_temp_row = (df[f'Temp_{column}'].values >= 121.0).argmax()
#     sterile_hold_max_temp_row = (df[f'Temp_{column}'].values >= 123.0).argmax()
#     sterile_hold_min_time = df.at[sterile_hold_min_temp_row, 'TIME']
#     sterile_hold_max_time = df.at[sterile_hold_max_temp_row, 'TIME']
#     time_difference = datetime.combine(date.today(), sterile_hold_max_time) \
#                       - datetime.combine(date.today(), sterile_hold_min_time)
#     sterile_hold_min_temp_row = (df[f'Temp_{column}'].values >= 121.0).argmax()
#     sterile_hold_min_temp_list.append(sterile_hold_min_temp_row)
#     sterile_hold_elapsed_time[f'Temp_{column}'] = str(timedelta(seconds = pd.Timedelta(time_difference).seconds))
#
# last_termocouple_temp_121_row = max(range(len(sterile_hold_min_temp_list)),
#                                     key = sterile_hold_min_temp_list.__getitem__)
# new_df = pd.DataFrame(df)[sterile_hold_min_temp_list[last_termocouple_temp_121_row]:
#                           sterile_hold_min_temp_list[last_termocouple_temp_121_row] + 187].copy(deep = True)
# x_axis = new_df['TIME'].index.tolist()
# print(x_axis)
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
#



fsdf = 4

l = ['a', 1.0, ]

n = int(input(" how many elements: "))
col = row = 0
for i in range(n):
    print("*", end=" ")
    row += 1
    if row == 4:
        row = 0
        col += 1
        print()

# n = int(input("Enter the start number: "))
#
# if 0 < n < 5:
#     for x in range(n, 38 - (n < -4), 6):
#         for j in range(x,  x + 6):
#             print("*", end=" ")
#         print()
