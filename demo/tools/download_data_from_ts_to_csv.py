import tushare as ts
import datetime
import os
import json
import pandas as pd
import numpy as np
import sys
from collections import Counter
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from symbols_from_stock_search import get_symbols_from_stock_search_result

def formatDate(Date, formatType='YYYYMMDD'):
    formatType = formatType.replace('YYYY', Date[0:4])
    formatType = formatType.replace('MM', Date[4:6])
    formatType = formatType.replace('DD', Date[-4:-2])
    return formatType

today = str(datetime.date.today())
yesterday = str(datetime.date.today() - datetime.timedelta(days=3))
testday = str(datetime.date.today() - datetime.timedelta(days=4))


def download_hist_data(period_k, period_v, exchange, symbols, stocks_basics, root_path):
    dir = os.path.join(root_path, 'tushare_csv', 'h_data', period_k, exchange)
    if not os.path.exists(dir):
        os.makedirs(dir)
    for symbol in symbols:
        date = stocks_basics.ix[symbol]['timeToMarket']
        date = formatDate(str(date), "YYYY-MM-DD")
        dhi = ts.get_hist_data(symbol, ktype=period_v, start=date, end=testday, retry_count=10).sort_index()
        if not dhi.empty:
            fname = os.path.join(dir, symbol + '.csv')
            dhi.to_csv(fname)


def download_all_hist_data(periods, root_path):
    stocks_basics = ts.get_stock_basics()
    symbols = stocks_basics.sort_index().index
    sz_symbols = [symbol for symbol in symbols if symbol[0] == '0']
    cyb_symbols = [symbol for symbol in symbols if symbol[0] == '3']
    sh_symbols = [symbol for symbol in symbols if symbol[0] == '6']
    for k, v in periods.items():
        download_hist_data(k, v, 'SZ', stocks_basics, sz_symbols, root_path)
        download_hist_data(k, v, 'SH', stocks_basics, sh_symbols, root_path)
        download_hist_data(k, v, 'CYB', stocks_basics, cyb_symbols, root_path)


def update_hist_data(period_k, period_v, exchange, symbols, root_path):
    dir = os.path.join(root_path, 'tushare_csv', 'h_data', period_k, exchange)
    if not os.path.exists(dir):
        os.makedirs(dir)
    for symbol in symbols:
        dhi = ts.get_hist_data(symbol, ktype=period_v, start=yesterday, end=yesterday, retry_count=10)
        if not dhi.empty:
            fname = os.path.join(dir, symbol + '.csv')
            dhi.to_csv(fname, mode='a', header=False)


def update_all_hist_data(periods, root_path):
    stocks_basics = ts.get_stock_basics()
    symbols = stocks_basics.sort_index().index
    sz_symbols = [symbol for symbol in symbols if symbol[0] == '0']
    cyb_symbols = [symbol for symbol in symbols if symbol[0] == '3']
    sh_symbols = [symbol for symbol in symbols if symbol[0] == '6']
    for k, v in periods.items():
        update_hist_data(k, v, 'SZ', sz_symbols, root_path)
        update_hist_data(k, v, 'SH', sh_symbols, root_path)
        update_hist_data(k, v, 'CYB', cyb_symbols, root_path)


def download_k_data(period_k, period_v, fq, exchange, symbols, stocks_basics, root_path, end, start = None):
    data_dir = os.path.join(root_path, 'tushare_csv', 'k_data', fq, period_k, exchange)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    failed_symbols = {"data_empty" : [],
                      "cannot_get" : [],}

    if fq == 'bfq':
        fq = None

    if period_v == 'W':
        weekend_list, weekend = get_weekend_json(str2datetime(end, '%Y-%m-%d'), root_path)
    elif period_v == 'M':
        monthend_list, monthend = get_monthend_json(str2datetime(end, '%Y-%m-%d'), root_path)

    for symbol in symbols:
        date = start
        if date == None:
            if symbol in stocks_basics.index:
                date = stocks_basics.ix[symbol]['timeToMarket']
                date = formatDate(str(date), "YYYY-MM-DD")

        try:
            dk = ts.get_k_data(symbol, ktype=period_v, autype=fq, start=date, end=end, retry_count=10)
            if not dk.empty:
                fname = os.path.join(data_dir, symbol + '.csv')
                if period_v == 'W':
                    dk.loc[dk.index[-1], 'date'] = weekend
                elif period_v == 'M':
                    dk.loc[dk.index[-1], 'date'] = monthend
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


def download_k_data_of_stock_search_result(fqs, periods, s_periods, s_strategies, root_path, start, end):
    stocks_basics = ts.get_stock_basics()
    symbols = get_symbols_from_stock_search_result(list(s_periods),
                                                   s_strategies,
                                                   root_path,
                                                   start,
                                                   end)
    sz_symbols = [symbol for symbol in symbols if symbol[0] == '0']
    cyb_symbols = [symbol for symbol in symbols if symbol[0] == '3']
    sh_symbols = [symbol for symbol in symbols if symbol[0] == '6']

    for fq in fqs:
        for k, v in periods.items():
            download_k_data(k, v, fq, 'SZ', sz_symbols, stocks_basics, root_path, end, start)
            download_k_data(k, v, fq, 'SH', sh_symbols, stocks_basics, root_path, end, start)
            download_k_data(k, v, fq, 'CYB', cyb_symbols, stocks_basics, root_path, end, start)

def download_all_k_data(fqs, periods, root_path):
    stocks_basics = ts.get_stock_basics()
    symbols = stocks_basics.sort_index().index
    sz_symbols = [symbol for symbol in symbols if symbol[0] == '0']
    cyb_symbols = [symbol for symbol in symbols if symbol[0] == '3']
    sh_symbols = [symbol for symbol in symbols if symbol[0] == '6']
    end = get_current_datetime()
    #end = get_current_datetime() - datetime.timedelta(days=3)
    for fq in fqs:
        for k, v in periods.items():
            download_k_data(k, v, fq, 'SZ', sz_symbols, stocks_basics, root_path, str(end))
            download_k_data(k, v, fq, 'SH', sh_symbols, stocks_basics, root_path, str(end))
            download_k_data(k, v, fq, 'CYB', cyb_symbols, stocks_basics, root_path, str(end))
    genenrate_contracts(fqs, sh_symbols, sz_symbols, cyb_symbols, root_path)


def update_day_k_data(fq, exchange, symbols, root_path, latest_update, current):
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
            dk = ts.get_k_data(symbol, ktype='D', autype=fq, start=start, end=end, retry_count=10)
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


def update_week_k_data(fq, exchange, symbols, root_path, lastest_update_day, current_day):
    data_dir = os.path.join(root_path, 'tushare_csv', 'k_data', fq, '1WEEK', exchange)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    failed_symbols = {"data_empty" : [],
                      "cannot_get" : [],}

    weekend_list, weekend = get_weekend_json(current_day, root_path)

    lastest_update_day = str(lastest_update_day)
    current_day = str(current_day)
    if lastest_update_day > weekend_list[weekend_list.index(weekend) - 1]:
        for symbol in symbols:
            try:
                dk = ts.get_k_data(symbol, ktype='W', autype=fq, start=current_day, end=current_day, retry_count=10)
                if not dk.empty:
                    dk.loc[dk.index[0], 'date'] = weekend
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
        for lastest_update_weekend in weekend_list:
            if lastest_update_day <= lastest_update_weekend:
                break
        for symbol in symbols:
            try:
                dk = ts.get_k_data(symbol, ktype='W', autype=fq, start=lastest_update_day, end=current_day, retry_count=10)
                if not dk.empty:
                    dk.loc[dk.index[0], 'date'] = lastest_update_weekend
                    dk.loc[dk.index[-1], 'date'] = weekend
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


def update_month_k_data(fq, exchange, symbols, root_path, lastest_update_day, current_day):
    data_dir = os.path.join(root_path, 'tushare_csv', 'k_data', fq, '1MONTH', exchange)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    failed_symbols = {"data_empty" : [],
                      "cannot_get" : [],}

    monthend_list, monthend = get_monthend_json(current_day, root_path)

    lastest_update_day = str(lastest_update_day)
    current_day = str(current_day)
    if lastest_update_day > monthend_list[monthend_list.index(monthend) - 1]:
        for symbol in symbols:
            try:
                dk = ts.get_k_data(symbol, ktype='M', autype=fq, start=current_day, end=current_day, retry_count=10)
                if not dk.empty:
                    dk.loc[dk.index[0], 'date'] = monthend
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
        for lastest_update_monthend in monthend_list:
            if lastest_update_day <= lastest_update_monthend:
                break
        for symbol in symbols:
            try:
                dk = ts.get_k_data(symbol, ktype='M', autype=fq, start=lastest_update_day, end=current_day, retry_count=10)
                if not dk.empty:
                    dk.loc[dk.index[0], 'date'] = lastest_update_monthend
                    dk.loc[dk.index[-1], 'date'] = monthend
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


def generate_contracts_of_total_symbols(fqs, root_path):
    total_symbols = ts.get_stock_basics().sort_index().index
    t_sz_symbols = [symbol for symbol in total_symbols if symbol[0] == '0']
    t_cyb_symbols = [symbol for symbol in total_symbols if symbol[0] == '3']
    t_sh_symbols = [symbol for symbol in total_symbols if symbol[0] == '6']

    genenrate_contracts(fqs, t_sh_symbols, t_sz_symbols, t_cyb_symbols, root_path)


def update_last_day_k_data(fqs, periods, root_path):
    stocks_basics = ts.get_stock_basics()
    total_symbols = stocks_basics.sort_index().index
    t_sz_symbols = [symbol for symbol in total_symbols if symbol[0] == '0']
    t_cyb_symbols = [symbol for symbol in total_symbols if symbol[0] == '3']
    t_sh_symbols = [symbol for symbol in total_symbols if symbol[0] == '6']

    genenrate_contracts(fqs, t_sh_symbols, t_sz_symbols, t_cyb_symbols, root_path)
    for fq in fqs:
        lastest_update_day = get_latest_update_datetime('1DAY', fq, 'SZ', root_path)
        current_day = get_current_datetime()
        last_day = current_day - datetime.timedelta(days=1)
        special_symbols = get_special_symbols(lastest_update_day, last_day, root_path)

        s_sz_symbols = [symbol for symbol in special_symbols if symbol[0:2] == u'00']
        s_cyb_symbols = [symbol for symbol in special_symbols if symbol[0:2] == u'30']
        s_sh_symbols = [symbol for symbol in special_symbols if symbol[0:2] == u'60']
        for k, v in periods.items():
            download_k_data(k, v, fq, 'SH', s_sh_symbols, stocks_basics, root_path, str(last_day))
            download_k_data(k, v, fq, 'SZ', s_sz_symbols, stocks_basics, root_path, str(last_day))
            download_k_data(k, v, fq, 'CYB', s_cyb_symbols, stocks_basics, root_path, str(last_day))

        u_sz_symbols = set(t_sz_symbols) - set(s_sz_symbols)
        u_cyb_symbols = set(t_cyb_symbols) - set(s_cyb_symbols)
        u_sh_symbols = set(t_sh_symbols) - set(s_sh_symbols)

        if periods.has_key('1DAY'):
            update_day_k_data(fq, 'SH', u_sh_symbols, root_path, lastest_update_day, last_day)
            update_day_k_data(fq, 'SZ', u_sz_symbols, root_path, lastest_update_day, last_day)
            update_day_k_data(fq, 'CYB', u_cyb_symbols, root_path, lastest_update_day, last_day)
        if periods.has_key('1WEEK'):
            update_week_k_data(fq, 'SZ', u_sz_symbols, root_path, lastest_update_day, last_day)
            update_week_k_data(fq, 'SH', u_sh_symbols, root_path, lastest_update_day, last_day)
            update_week_k_data(fq, 'CYB', u_cyb_symbols, root_path, lastest_update_day, last_day)
        if periods.has_key('1MONTH'):
            update_month_k_data(fq, 'SZ', u_sz_symbols, root_path, lastest_update_day, last_day)
            update_month_k_data(fq, 'SH', u_sh_symbols, root_path, lastest_update_day, last_day)
            update_month_k_data(fq, 'CYB', u_cyb_symbols, root_path, lastest_update_day, last_day)


def genenrate_contracts(fqs, t_sh_symbols, t_sz_symbols, t_cyb_symbols, root_path):
    for fq in fqs:
        dir = os.path.join(root_path, 'tushare_csv', 'k_data', fq)
        if not os.path.exists(dir):
            os.makedirs(dir)
        fname = os.path.join(dir, "CONTRACTS.csv")
        exchange_sh = ['SH' for item in t_sh_symbols]
        exchange_sz = ['SZ' for item in t_sz_symbols]
        exchange_cyb = ['CYB' for item in t_cyb_symbols]
        exchanges = exchange_sh + exchange_sz + exchange_cyb
        symbols = map(str, t_sh_symbols) + map(str, t_sz_symbols) + map(str, t_cyb_symbols)
        long_margin_ratio = [1 for item in symbols]
        volume_multiple = [1 for item in symbols]
        pd.DataFrame({'code' : symbols,
                      'exchange': exchanges,
                      'long_margin_ratio': long_margin_ratio,
                      'volume_multiple': volume_multiple}).to_csv(fname, index=False)


def get_latest_update_datetime(period_k, fq, exchange, root_path):
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


def str2datetime(datestr, format):
    return datetime.datetime.strptime(datestr, format)


def datetime2str(date, format):
    return datetime.datetime.strftime(date, format)


def get_special_symbols(latest_update, current, root_path):
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


def get_weekend_txt(current_day, root_path):
    year = current_day.year
    calendar_week = os.path.join(root_path, 'py_stock', 'calendar', str(year) + '_week.txt')
    if not os.path.exists(calendar_week):
        print('calendar_week file is not exist')
        exit(1)
    with open(calendar_week, 'r') as c_week:
        weekend_list = c_week.readline().split(',')

    current_day = str(current_day)
    for weekend in weekend_list:
        if current_day <= weekend:
            break

    return weekend_list, weekend


def get_monthend_txt(current_day, root_path):
    year = current_day.year
    calendar_month = os.path.join(root_path, 'py_stock', 'calendar', str(year) + '_month.txt')
    if not os.path.exists(calendar_month):
        print('calendar_month file is not exist')
        exit(1)
    with open(calendar_month, 'r') as c_month:
        monthend_list = c_month.readline().split(',')

    current_day = str(current_day)
    for monthend in monthend_list:
        if current_day <= monthend:
            break

    return monthend_list, monthend


def get_weekend_json(current_day, root_path):
    year = current_day.year
    week_path = os.path.join(root_path, 'py_stock', 'calendar', str(year) + '_week.json')
    if not os.path.exists(week_path):
        print('calendar_week file is not exist')
        exit(1)
    with open(week_path, 'r') as json_file:
        calendar_week = json.load(json_file)
        weekstart_list = calendar_week[0][str(year) + '_weekstart']
        weekend_list = calendar_week[0][str(year) + '_weekend']

    current_day = str(current_day)
    for weekend in weekend_list:
        if current_day <= weekend:
            break

    weekend_index = weekend_list.index(weekend)
    if current_day < weekstart_list[weekend_index]:
        if weekend_index == 0:
            print "The first trading day of this year is not begin"
            return None, None
        else:
            weekend = weekend_list[weekend_index - 1]

    return weekend_list, weekend


def get_monthend_json(current_day, root_path):
    year = current_day.year
    month_path = os.path.join(root_path, 'py_stock', 'calendar', str(year) + '_month.json')
    if not os.path.exists(month_path):
        print('calendar_month file is not exist')
        exit(1)
    with open(month_path, 'r') as json_file:
        calendar_month = json.load(json_file)
        monthstart_list = calendar_month[0][str(year) + '_monthstart']
        monthend_list = calendar_month[0][str(year) + '_monthend']

    current_day = str(current_day)
    for monthend in monthend_list:
        if current_day <= monthend:
            break

    monthend_index = monthend_list.index(monthend)
    if current_day < monthstart_list[monthend_index]:
        if monthend_index == 0:
            print "The first trading day of this year is not begin"
            return None, None
        else:
            monthend = monthend_list[monthend_index - 1]

    return monthend_list, monthend


def main():
    root_path = 'D:\dan\stock'

    #periods = {'1DAY': 'D', '1WEEK': 'W', '1MONTH': 'M'}
    #fqs = ('bfq', 'qfq', 'hfq')
    periods = {'1DAY': 'D', }
    fqs = ('qfq',)
    download_all_k_data(fqs, periods, root_path)

    #periods = {'1DAY': 'D',}
    #fqs = ('qfq',)
    #update_last_day_k_data(fqs, periods, root_path)

    #periods = {'15MINUTE': '15',}
    #s_periods = {'1DAY': 'D',}
    #s_strategies = ['MACD_MA9']
    #start = '2017-08-07'
    #end = '2017-08-11'
    # download_k_data_of_stock_search_result(fqs, periods, s_periods, s_strategies, root_path, start, end)



    #update_all_hist_data(periods, root_path)
    #download_all_hist_data(periods, root_path)
    #generate_contracts_of_total_symbols(fqs, root_path)



if __name__ == "__main__":
    main()

#update_last_day_k_data(fqs)

#update_all_hist_data(symbols)
#download_all_hist_data(symbols)
#download_all_k_data(symbols)
#generate_contracts_of_total_symbols(fqs)
#update_last_day_k_data(('qfq',))
#update_last_day_k_data(fqs)
#update_all_k_data(symbols)