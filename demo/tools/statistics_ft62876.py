import pandas as pd
import tushare as ts
import os
import json
import matplotlib.pyplot as plt
import stocknum_per_day

ft62876_buy_dir = 'D:\dan\stock\py_stock\quantdigger\candicates\\1DAY\\62876XY'
ft62876_sell_dir = 'D:\dan\stock\py_stock\quantdigger\\to_sell\\1DAY\\62876XY'
stock_num_dir = 'D:\dan\stock\stock_num\stock_num.json'


stocknum_per_day.stocknum_per_day()
with open(stock_num_dir) as json_file:
    stocks_num = json.load(json_file)

x_list = []
y_list = []
dk_sh = ts.get_k_data('sh', start="2008-01-01", end="2017-05-17")
date_list = list(dk_sh.date)
for i in range(len(dk_sh)):
    buy_dir = os.path.join(ft62876_buy_dir, str(date_list[i]), 'SH.csv')
    if os.path.exists(buy_dir):
        x = pd.read_csv(buy_dir)
        x_num = len(x)
        stocks = stocks_num[date_list[i]]['SH']
        x_p = float(x_num) / stocks
    else:
        x_p = 0
        x_num = 0
    x_list.append([x_num, x_p * 2000])

    sell_dir = os.path.join(ft62876_sell_dir, str(date_list[i]), 'SH.csv')
    if os.path.exists(sell_dir):
        y = pd.read_csv(sell_dir)
        y_num = len(y)
        stocks = stocks_num[date_list[i]]['SH']
        y_p = float(y_num) / stocks
    else:
        y_p = 0
        y_num = 0
    y_list.append([y_num, y_p * 2000])

df_x = pd.DataFrame(x_list, columns = ['x_num', 'x_p'], index = dk_sh.date)
df_x['x_p'].plot(figsize=(12,8))
df_y = pd.DataFrame(y_list, columns = ['y_num', 'y_p'], index = dk_sh.date)
df_y['y_p'].plot(figsize=(12,8))
dk_sh = dk_sh.set_index('date')
dk_sh['close'].plot(figsize=(12,8))
plt.show()

