import tushare as ts
import datetime
import os
import json
import pandas as pd
import numpy as np
from collections import Counter

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
root_path = 'D:\dan\stock'
today = str(datetime.date.today())
yesterday = str(datetime.date.today() - datetime.timedelta(days=3))
testday = str(datetime.date.today() - datetime.timedelta(days=4))

def download_hist_data(period_k, period_v, exchange, symbols):
    dir = os.path.join(root_path, 'tushare_csv', 'h_data', period_k, exchange)
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
    dir = os.path.join(root_path, 'tushare_csv', 'h_data', period_k, exchange)
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

def download_k_data(period_k, period_v, fq, exchange, symbols, end, start = None):
    data_dir = os.path.join(root_path, 'tushare_csv', 'k_data', fq, period_k, exchange)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    failed_symbols = {"data_empty" : [],
                      "cannot_get" : [],}

    if fq == 'bfq':
        fq = None

    for symbol in symbols:
        date = start
        if date == None:
            date = stocks_basics.ix[symbol]['timeToMarket']
            date = formatDate(str(date), "YYYY-MM-DD")

        try:
            dk = ts.get_k_data(symbol, ktype=period_v, autype=fq, start=date, end=end, retry_count=100)
            if not dk.empty:
                fname = os.path.join(data_dir, symbol + '.csv')
                dk.to_csv(fname, index=False)
            else:
                print("dk of symbol %s is empty" % symbol)
                failed_symbols["data_empty"].append(symbol)
        except:
            print("symbol %s can't get" % symbol)
            failed_symbols["cannot_get"].append(symbol)

    if failed_symbols["data_empty"] or failed_symbols["cannot_get"]:
        if fq == None:
            fq = 'bfq'
        failed_file_dir = os.path.join(root_path,'tushare_csv', 'k_data', fq, period_k,
                                       'failed_download', exchange)
        if not os.path.exists(failed_file_dir):
            os.makedirs(failed_file_dir)
        failed_file = os.path.join(failed_file_dir, end + '.json')

        with open(failed_file, 'w') as failed_file:
            json.dump(failed_symbols, failed_file)

def download_all_k_data(symbols):
    sz_symbols = [symbol for symbol in symbols if symbol[0] == '0']
    cyb_symbols = [symbol for symbol in symbols if symbol[0] == '3']
    sh_symbols = [symbol for symbol in symbols if symbol[0] == '6']
    end = get_current_datetime()
    for fq in fqs:
        for k, v in period.items():
            download_k_data(k, v, fq, 'SZ', sz_symbols, str(end))
            download_k_data(k, v, fq, 'SH', sh_symbols, str(end))
            download_k_data(k, v, fq, 'CYB', cyb_symbols, str(end))

def update_day_k_data(fq, exchange, symbols,latest_update, current):
    dir = os.path.join(root_path, 'tushare_csv', 'k_data', fq, '1DAY', exchange)
    if not os.path.exists(dir):
        print("Please download data first.")
        return

    failed_symbols = {"data_empty" : [],
                      "cannot_get" : [],}

    start = str(latest_update + datetime.timedelta(days=1))
    end = str(current)
    for symbol in symbols:
        try:
            dk = ts.get_k_data(symbol, ktype='D', autype=fq, start=start, end=end, retry_count=100)
            if not dk.empty:
                fname = os.path.join(dir, symbol + '.csv')
                #dk_org = pd.read_csv(fname, header=0, names=['date', 'open', 'close', 'high', 'low', 'volume', 'code'])
                #dk_org.to_csv(fname, mode='w', index=False)
                dk.to_csv(fname, mode='a', header=False, index=False)
            else:
                print("dk of symbol %s is empty" % symbol)
                failed_symbols["data_empty"].append(symbol)
        except:
            print("symbol %s can't get" % symbol)
            failed_symbols["cannot_get"].append(symbol)

    if failed_symbols["data_empty"] or failed_symbols["cannot_get"]:
        failed_file_dir = os.path.join(root_path,'tushare_csv', 'k_data', fq, '1DAY',
                                       'failed_update', exchange)
        if not os.path.exists(failed_file_dir):
            os.makedirs(failed_file_dir)
        failed_file = os.path.join(failed_file_dir, end + '.json')

        with open(failed_file, 'w') as failed_file:
            json.dump(failed_symbols, failed_file)

def update_week_k_data(fq, exchange, symbols, lastest_update_day, current_day):
    data_dir = os.path.join(root_path, 'tushare_csv', 'k_data', fq, '1WEEK', exchange)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    failed_symbols = {"data_empty" : [],
                      "cannot_get" : [],}

    year = current_day.year
    calendar_week = os.path.join(root_path, 'py_stock', 'calendar', str(year) + '_week.txt')
    if not os.path.exists(calendar_week):
        print('calendar_week file is not exist')
        exit(1)
    with open(calendar_week, 'r') as c_week:
        week_end = c_week.readline().split(',')

    lastest_update_day = str(lastest_update_day)
    current_day = str(current_day)
    for weekend in week_end:
        if current_day <= weekend:
            break
    if lastest_update_day > week_end[week_end.index(weekend) - 1]:
        for symbol in symbols:
            try:
                dk = ts.get_k_data(symbol, ktype='W', autype=fq, start=current_day, end=current_day, retry_count=100)
                if not dk.empty:
                    dk['date'] = weekend
                    fname = os.path.join(data_dir, symbol + '.csv')
                    org_dk = pd.read_csv(fname)
                    if weekend == list(org_dk['date'])[-1]:
                        org_dk.drop(org_dk.index[-1], inplace=True)
                    org_dk.append(dk).to_csv(fname, mode='w', index=False)
                else:
                    print("dk of symbol %s is empty" % symbol)
                    failed_symbols["data_empty"].append(symbol)
            except:
                print("symbol %s can't get" % symbol)
                failed_symbols["cannot_get"].append(symbol)
    else:
        for lastest_update_weekend in week_end:
            if lastest_update_day <= lastest_update_weekend:
                break
        for symbol in symbols:
            try:
                dk = ts.get_k_data(symbol, ktype='W', autype=fq, start=lastest_update_day, end=current_day, retry_count=100)
                if not dk.empty:
                    list(dk['date'])[0] = lastest_update_weekend
                    fname = os.path.join(data_dir, symbol + '.csv')
                    org_dk = pd.read_csv(fname)
                    if lastest_update_weekend == list(org_dk['date'])[-1]:
                        org_dk.drop(org_dk.index[-1], inplace=True)
                    org_dk.append(dk).to_csv(fname, mode='w', index=False)
                else:
                    print("dk of symbol %s is empty" % symbol)
                    failed_symbols["data_empty"].append(symbol)
            except:
                print("symbol %s can't get" % symbol)
                failed_symbols["cannot_get"].append(symbol)

    if failed_symbols["data_empty"] or failed_symbols["cannot_get"]:
        failed_file_dir = os.path.join(root_path,'tushare_csv', 'k_data', fq, '1WEEK',
                                       'failed_update', exchange)
        if not os.path.exists(failed_file_dir):
            os.makedirs(failed_file_dir)
        failed_file = os.path.join(failed_file_dir, current_day + '.json')

        with open(failed_file, 'w') as failed_file:
            json.dump(failed_symbols, failed_file)

def update_month_k_data(fq, exchange, symbols, lastest_update_day, current_day):
    data_dir = os.path.join(root_path, 'tushare_csv', 'k_data', fq, '1MONTH', exchange)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    failed_symbols = {"data_empty" : [],
                      "cannot_get" : [],}

    year = current_day.year
    calendar_month = os.path.join(root_path, 'py_stock', 'calendar', str(year) + '_month.txt')
    if not os.path.exists(calendar_month):
        print('calendar_month file is not exist')
        exit(1)
    with open(calendar_month, 'r') as c_month:
        month_end = c_month.readline().split(',')

    lastest_update_day = str(lastest_update_day)
    current_day = str(current_day)
    for monthend in month_end:
        if current_day <= monthend:
            break
    if lastest_update_day > month_end[month_end.index(monthend) - 1]:
        for symbol in symbols:
            try:
                dk = ts.get_k_data(symbol, ktype='M', autype=fq, start=current_day, end=current_day, retry_count=100)
                if not dk.empty:
                    dk['date'] = monthend
                    fname = os.path.join(data_dir, symbol + '.csv')
                    org_dk = pd.read_csv(fname)
                    if monthend == list(org_dk['date'])[-1]:
                        org_dk.drop(org_dk.index[-1], inplace=True)
                    org_dk.append(dk).to_csv(fname, mode='w', index=False)
                else:
                    print("dk of symbol %s is empty" % symbol)
                    failed_symbols["data_empty"].append(symbol)
            except:
                print("symbol %s can't get" % symbol)
                failed_symbols["cannot_get"].append(symbol)
    else:
        for lastest_update_monthend in month_end:
            if lastest_update_day <= lastest_update_monthend:
                break
        for symbol in symbols:
            try:
                dk = ts.get_k_data(symbol, ktype='M', autype=fq, start=lastest_update_day, end=current_day, retry_count=100)
                if not dk.empty:
                    list(dk['date'])[0] = lastest_update_monthend
                    fname = os.path.join(data_dir, symbol + '.csv')
                    org_dk = pd.read_csv(fname)
                    if lastest_update_monthend == list(org_dk['date'])[-1]:
                        org_dk.drop(org_dk.index[-1], inplace=True)
                    org_dk.append(dk).to_csv(fname, mode='w', index=False)
                else:
                    print("dk of symbol %s is empty" % symbol)
                    failed_symbols["data_empty"].append(symbol)
            except:
                print("symbol %s can't get" % symbol)
                failed_symbols["cannot_get"].append(symbol)

    if failed_symbols["data_empty"] or failed_symbols["cannot_get"]:
        failed_file_dir = os.path.join(root_path,'tushare_csv', 'k_data', fq, '1MONTH',
                                       'failed_update', exchange)
        if not os.path.exists(failed_file_dir):
            os.makedirs(failed_file_dir)
        failed_file = os.path.join(failed_file_dir, current_day + '.json')

        with open(failed_file, 'w') as failed_file:
            json.dump(failed_symbols, failed_file)

def update_k_data(fqs):
    total_symbols = stocks_basics.sort_index().index
    t_sz_symbols = [symbol for symbol in total_symbols if symbol[0] == '0']
    t_cyb_symbols = [symbol for symbol in total_symbols if symbol[0] == '3']
    t_sh_symbols = [symbol for symbol in total_symbols if symbol[0] == '6']

    for fq in fqs:
        lastest_update_day = get_latest_update_datetime('1DAY', fq, 'SZ')
        current_day = get_current_datetime()
        special_symbols = get_special_symbols(lastest_update_day, current_day)

        s_sz_symbols = [symbol for symbol in special_symbols if symbol[0:2] == u'00']
        s_cyb_symbols = [symbol for symbol in special_symbols if symbol[0] == '3']
        s_sh_symbols = [symbol for symbol in special_symbols if symbol[0] == '6']
        for k, v in period.items():
            download_k_data(k, v, fq, 'SZ', s_sz_symbols, str(current_day))
            download_k_data(k, v, fq, 'SH', s_sh_symbols, str(current_day))
            download_k_data(k, v, fq, 'CYB', s_cyb_symbols, str(current_day))

        u_sz_symbols = set(t_sz_symbols) - set(s_sz_symbols)
        u_cyb_symbols = set(t_cyb_symbols) - set(s_cyb_symbols)
        u_sh_symbols = set(t_sh_symbols) - set(s_sh_symbols)
        update_day_k_data(fq, 'SZ', u_sz_symbols, lastest_update_day, current_day)
        update_day_k_data(fq, 'SH', u_sh_symbols, lastest_update_day, current_day)
        update_day_k_data(fq, 'CYB', u_cyb_symbols, lastest_update_day, current_day)
        update_week_k_data(fq, 'SZ', u_sz_symbols, lastest_update_day, current_day)
        update_week_k_data(fq, 'SH', u_sh_symbols, lastest_update_day, current_day)
        update_week_k_data(fq, 'CYB', u_cyb_symbols, lastest_update_day, current_day)
        update_month_k_data(fq, 'SZ', u_sz_symbols, lastest_update_day, current_day)
        update_month_k_data(fq, 'SH', u_sh_symbols, lastest_update_day, current_day)
        update_month_k_data(fq, 'CYB', u_cyb_symbols, lastest_update_day, current_day)

def get_latest_update_datetime(period_k, fq, exchange):
    datetimes = []
    symbols = []
    randoms = np.random.randint(11, 99, size=10)
    if exchange == 'SZ':
        symbols = ['0000' + str(item) for item in randoms]
    elif exchange == 'SH':
        symbols = ['6000' + str(item) for item in randoms]
    elif exchange == 'CYB':
        symbols = ['3000' + str(item) for item in randoms]

    for symbol in symbols:
        fname = os.path.join(root_path, 'tushare_csv', 'k_data', fq, period_k, exchange, symbol + '.csv')
        if os.path.exists(fname):
            dk = pd.read_csv(fname)
            if not dk.empty:
                datetimes.append(list(dk['date'])[-1])

    return datetime.datetime.strptime(Counter(datetimes).most_common(1)[0][0], '%Y-%m-%d').date()

def get_current_datetime():
    return datetime.date.today()

def get_special_symbols(latest_update, current):
    xd_stocks_path = os.path.join(root_path, 'tushare_csv', 'xd_stocks')
    if not os.path.exists(xd_stocks_path):
        os.makedirs(xd_stocks_path)

    # Get the XD stocks' symbol
    os.chdir(xd_stocks_path)
    update_day = latest_update + datetime.timedelta(days=1)
    while update_day <= current:
        if os.path.exists(str(update_day) + '.json'):
            update_day = update_day + datetime.timedelta(days=1)
            continue
        os.system('scrapy runspider ' + os.path.join(xd_stocks_path, 'xd_stocks_spider.py') + ' -o '
                + str(update_day) + '.json' + ' -a xd_date=' + str(update_day))
        update_day = update_day + datetime.timedelta(days=1)

    # Download all history data of XD stocks
    specail_symbols = set()
    update_day = latest_update + datetime.timedelta(days=1)
    while update_day <= current:
        with open(str(update_day) + '.json') as json_file:
            specail_stocks = json.load(json_file)
            specail_symbols |= (set(specail_stocks[0]['xd_stocks'])
                                | set(specail_stocks[0]['fp_stocks'])
                                | set(specail_stocks[0]['new_stocks']))
        update_day = update_day + datetime.timedelta(days=1)
    return specail_symbols

update_k_data(fqs)

#update_all_hist_data(symbols)
#download_all_hist_data(symbols)
#download_all_k_data(symbols)
#update_all_k_data(symbols)