import pandas as pd
import tushare as ts
import os

day_dir = 'D:\dan\stock\py_stock\quantdigger\candicates\\1DAY\ZT62808DKLINE_MACD7'
#week_dir = 'D:\dan\stock\py_stock\quantdigger\candicates\\1WEEK\ZT62808DKLINE_MACD6'
week_dir = 'D:\dan\stock\py_stock\quantdigger\candicates\\1WEEK\ZT62808DKLINE_MA3'
save_dir = 'D:\dan\stock\py_stock\quantdigger\candicates'

day_list = os.listdir(day_dir)
week_list = os.listdir(week_dir)

wk_sh = ts.get_k_data('sh', ktype = 'W', start = '2015-01-01', end = '2017-06-02')
weekend_list = list(wk_sh.date)
#TODO: check the last item of weekend_list

weekend = ''
for day in day_list:
    for weekend in weekend_list:
        if day <= weekend:
            last_weekend = weekend_list[weekend_list.index(weekend) - 1]
            week_csv_dir = os.path.join(week_dir, last_weekend, 'SH.csv')
            if not os.path.exists(week_csv_dir):
                print('Last weekend csv not exists, date is %s' % last_weekend)
                break
            week_stocks = pd.read_csv(week_csv_dir, names = ['id', 'code'])
            day_csv_dir = os.path.join(day_dir, day, 'SH.csv')
            day_stocks = pd.read_csv(day_csv_dir, names = ['id', 'code'])
            stocks = set(day_stocks['code'][1:]) & set(week_stocks['code'][1:])
            if len(stocks) != 0:
                save_path = os.path.join(save_dir, '1DAY_1WEEK', 'DKLINE_MACD7_MA0', day)
                if os.path.exists(save_path) != True:
                    os.makedirs(save_path)
                save_path = os.path.join(save_path, 'SH.csv')
                pd.DataFrame(list(stocks)).to_csv(save_path)
            break


