import tushare as ts
from collections import Counter
import datetime
import os
import json

def stocknum_per_day():
    total_stocks_basics = ts.get_stock_basics()
    sz_stocks_basics = total_stocks_basics[(total_stocks_basics.index > '000000')
                                           & (total_stocks_basics.index < '300000')]
    cyb_stocks_basics = total_stocks_basics[(total_stocks_basics.index > '300000')
                                           & (total_stocks_basics.index < '600000')]
    sh_stocks_basics = total_stocks_basics[total_stocks_basics.index > '600000']

    sz_counter = Counter(list(sz_stocks_basics['timeToMarket']))
    sh_counter = Counter(list(sh_stocks_basics['timeToMarket']))
    cyb_counter = Counter(list(cyb_stocks_basics['timeToMarket']))

    setup_date = datetime.date(1990,12,10)
    today = datetime.date.today()
    stock_num = {}
    sz_stock_num = 0
    sh_stock_num = 0
    cyb_stock_num = 0
    total_stock_num = 0
    while setup_date <= today:
        k = int(setup_date.strftime('%Y%m%d'))
        if sz_counter.has_key(k):
            sz_stock_num += sz_counter[k]
        if sh_counter.has_key(k):
            sh_stock_num += sh_counter[k]
        if cyb_counter.has_key(k):
            cyb_stock_num += cyb_counter[k]
        total_stock_num = sz_stock_num + sh_stock_num + cyb_stock_num
        stock_num[setup_date.strftime('%Y-%m-%d')] = {'SZ': sz_stock_num,
                                                       'SH': sh_stock_num,
                                                       'CYB': cyb_stock_num,
                                                       'TOT': total_stock_num}
        setup_date += datetime.timedelta(days=1)
    root_path = 'D:\dan\stock'
    file_dir = os.path.join(root_path, 'stock_num')
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    stock_num_file = os.path.join(file_dir, 'stock_num' + '.json')

    with open(stock_num_file, 'w') as stock_num_file:
        json.dump(stock_num, stock_num_file)

'''
stocknum_per_day()
with open('D:\dan\stock\stock_num\stock_num.json') as json_file:
    stocks_num = json.load(json_file)
print('Ok')'''