import tushare as ts
import datetime
import os
import json
import pandas as pd

def formatDate(Date, formatType='YYYYMMDD'):
    formatType = formatType.replace('YYYY', Date[0:4])
    formatType = formatType.replace('MM', Date[4:6])
    formatType = formatType.replace('DD', Date[-4:-2])
    return formatType

stocks_basics = ts.get_stock_basics()
symbols = stocks_basics.sort_index().index
period = {'1DAY': 'D', '1WEEK': 'W', '1MONTH': 'M'}
fqs = ('bfq', 'qfq', 'hfq')
exchanges = ('SZ', 'SH', 'CYB')
root_path = 'D:\dan\stock\\tushare_csv'
today = str(datetime.date.today())
yesterday = str(datetime.date.today() - datetime.timedelta(days=3))
testday = str(datetime.date.today() - datetime.timedelta(days=4))

def download_hist_data(period_k, period_v, exchange, symbols):
    dir = os.path.join(root_path, 'h_data', period_k, exchange)
    if not os.path.exists(dir):
        os.makedirs(dir)
    for symbol in symbols:
        date = stocks_basics.ix[symbol]['timeToMarket']
        date = formatDate(str(date), "YYYY-MM-DD")
        dhi = ts.get_hist_data(symbol, ktype=period_v, start=date, end=testday, retry_count=100).sort_index()
        if not dhi.empty:
            fname = os.path.join(dir, symbol + '.csv')
            dhi.to_csv(fname)

def download_all_hist_data(symbols):
    sz_symbols = [symbol for symbol in symbols if symbol[0] == '0']
    cyb_symbols = [symbol for symbol in symbols if symbol[0] == '3']
    sh_symbols = [symbol for symbol in symbols if symbol[0] == '6']
    for k, v in period.items():
        download_hist_data(k, v, 'SZ', sz_symbols)
        download_hist_data(k, v, 'SH', sh_symbols)
        download_hist_data(k, v, 'CYB', cyb_symbols)

def update_hist_data(period_k, period_v, exchange, symbols):
    dir = os.path.join(root_path, 'h_data', period_k, exchange)
    if not os.path.exists(dir):
        os.makedirs(dir)
    for symbol in symbols:
        dhi = ts.get_hist_data(symbol, ktype=period_v, start=yesterday, end=yesterday, retry_count=100)
        if not dhi.empty:
            fname = os.path.join(dir, symbol + '.csv')
            dhi.to_csv(fname, mode='a', header=False)

def update_all_hist_data(symbols):
    sz_symbols = [symbol for symbol in symbols if symbol[0] == '0']
    cyb_symbols = [symbol for symbol in symbols if symbol[0] == '3']
    sh_symbols = [symbol for symbol in symbols if symbol[0] == '6']
    for k, v in period.items():
        update_hist_data(k, v, 'SZ', sz_symbols)
        update_hist_data(k, v, 'SH', sh_symbols)
        update_hist_data(k, v, 'CYB', cyb_symbols)

def download_k_data(period_k, period_v, fq, exchange, symbols):
    dir = os.path.join(root_path, 'k_data', fq, period_k, exchange)
    if not os.path.exists(dir):
        os.makedirs(dir)

    if fq == 'bfq':
        fq = None

    for symbol in symbols:
        date = stocks_basics.ix[symbol]['timeToMarket']
        date = formatDate(str(date), "YYYY-MM-DD")
        try:
            dk = ts.get_k_data(symbol, ktype=period_v, autype=fq, start=date, end=yesterday, retry_count=100)
            if not dk.empty:
                fname = os.path.join(dir, symbol + '.csv')
                dk.to_csv(fname, index=False)
            else:
                print("dk of symbol %s is empty" % symbol)
        except:
            print("symbol %s can't get" % symbol)

def download_all_k_data(symbols):
    sz_symbols = [symbol for symbol in symbols if symbol[0] == '0']
    cyb_symbols = [symbol for symbol in symbols if symbol[0] == '3']
    sh_symbols = [symbol for symbol in symbols if symbol[0] == '6']
    for fq in fqs:
        for k, v in period.items():
            download_k_data(k, v, fq, 'SZ', sz_symbols)
            download_k_data(k, v, fq, 'SH', sh_symbols)
            download_k_data(k, v, fq, 'CYB', cyb_symbols)

def update_k_data(period_k, period_v, fq, exchange, symbols):
    dir = os.path.join(root_path, 'k_data', fq, period_k, exchange)
    if not os.path.exists(dir):
        os.makedirs(dir)
    for symbol in symbols:
        try:
            dk = ts.get_k_data(symbol, ktype=period_v, autype=fq, start=yesterday, end=yesterday, retry_count=100)
            if not dk.empty:
                fname = os.path.join(dir, symbol + '.csv')
                #dk_org = pd.read_csv(fname, header=0, names=['date', 'open', 'close', 'high', 'low', 'volume', 'code'])
                #dk_org.to_csv(fname, mode='w', index=False)
                dk.to_csv(fname, mode='a', header=False, index=False)
            else:
                print("dk of symbol %s is empty" % symbol)
        except:
            print("symbol %s can't get" % symbol)

def update_all_k_data(symbols):
    xd_stocks_path = os.path.join(root_path, 'xd_stocks')
    if not os.path.exists(xd_stocks_path):
        os.makedirs(xd_stocks_path)

    os.chdir(xd_stocks_path)
    if os.path.exists(yesterday + '.json'):
        os.remove(yesterday + '.json')
    os.system('scrapy runspider ' + os.path.join(xd_stocks_path, 'xd_stocks_spider.py') + ' -o '
                + yesterday + '.json' + ' -a xd_date=' + yesterday)

    with open(yesterday + '.json') as json_file:
        xd_stocks = json.load(json_file)
    xd_symbols = set(xd_stocks[0]['xd_stocks'])
    download_all_k_data(xd_symbols)

    noraml_symbols = set(symbols) -xd_symbols
    sz_symbols = [symbol for symbol in noraml_symbols if symbol[0] == '0']
    cyb_symbols = [symbol for symbol in noraml_symbols if symbol[0] == '3']
    sh_symbols = [symbol for symbol in noraml_symbols if symbol[0] == '6']
    for fq in fqs:
        for k, v in period.items():
            update_k_data(k, v, fq, 'SZ', sz_symbols)
            update_k_data(k, v, fq, 'SH', sh_symbols)
            update_k_data(k, v, fq, 'CYB', cyb_symbols)

#update_all_hist_data(symbols)
#download_all_hist_data(symbols)
#download_all_k_data(symbols)
update_all_k_data(symbols)