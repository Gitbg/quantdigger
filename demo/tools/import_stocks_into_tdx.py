# -*- coding: utf-8 -*-

import os
import string
import json
import time
import datetime

period = {'1DAY': '1D', '1WEEK': '1W', '1MONTH': '1M', '1DAY_1WEEK': '1D1W'}

def generate_cfg_string(tdx_board_name):
    cfg_string = ''
    if len(tdx_board_name) > 50:
        print('The length of tdx_board_name %s should not beyond 50 bytes.' % tdx_board_name)
        return cfg_string

    cfg_string = tdx_board_name
    for i in range(50 - len(tdx_board_name)):
        cfg_string += '\x00'
    cfg_string += tdx_board_name
    for i in range(70 - len(tdx_board_name)):
        cfg_string += '\x00'

    return cfg_string


def remove_stocks_from_tdx(tdx_dir,
                           periods,
                           strategies):
    if not os.path.exists(tdx_dir):
        print("The tdx directory, %s, not exist." % tdx_dir)
        exit(1)

    cfg_path = os.path.join(tdx_dir, 'blocknew.cfg')
    if not os.path.exists(cfg_path):
        cfg_file = open(cfg_path, 'wb+')
        cfg = ''
    else:
        cfg_file = open(cfg_path, 'rb')
        cfg = cfg_file.read()
        cfg_file.close()
        cfg_file = open(cfg_path, 'wb')

    file_list = os.listdir(tdx_dir)

    for period_k, period_v in periods.items():
        for strategy in strategies:
            tdx_board_name = period_v + strategy
            for blk in file_list:
                if blk.startswith(tdx_board_name):
                    blk_file = os.path.join(tdx_dir, blk)
                    os.remove(blk_file)
                    cfg_string = generate_cfg_string(blk[:-4])
                    cfg.replace(cfg_string, '')
                    file_list.remove(blk)
    cfg_file.write(cfg)
    cfg_file.close()

def import_stocks_into_tdx(tdx_dir,
                           stock_search_dir,
                           periods,
                           strategies,
                           start_day,
                           end_day,
                           cur_end = None,
                           offset_in_period = None):

    if not os.path.exists(tdx_dir):
        print("The tdx directory, %s, not exist." % tdx_dir)
        exit(1)

    cfg_path = os.path.join(tdx_dir, 'blocknew.cfg')
    if not os.path.exists(cfg_path):
        cfg_file = open(cfg_path, 'wb+')
        cfg = ''
    else:
        cfg_file = open(cfg_path, 'rb')
        cfg = cfg_file.read()
        cfg_file.close()
        cfg_file = open(cfg_path, 'ab+')

    cfg_string = ''
    for period_k, period_v in periods.items():
        p_dir = os.path.join(stock_search_dir, period_k)
        if not os.path.exists(p_dir):
            print("The stock search results directory, %s, not exist." % p_dir)
            continue

        for strategy in strategies:
            p_s_dir = os.path.join(p_dir, strategy)
            if not os.path.exists(p_s_dir):
                print("The stock search results directory, %s, not exist." % p_s_dir)
                continue
            date_list = os.listdir(p_s_dir)
            for date in date_list:
                if start_day <= date <= end_day:
                    p_s_d_dir = os.path.join(p_s_dir, date)
                    csv_list = os.listdir(p_s_d_dir)
                    if len(csv_list):
                        stocks_in_board = []
                        for csv in csv_list:
                            csv_path = os.path.join(p_s_d_dir, csv)
                            with open(csv_path, 'r') as csv_file:
                                stocks = csv_file.readlines()
                                stocks = stocks[1:]
                                for stock in stocks:
                                    stock_exchange = stock.split(',')[1].split('.')
                                    if stock_exchange[1] == 'SH\n':
                                        stocks_in_board.append('1' + stock_exchange[0] + '\n')
                                    elif stock_exchange[1] == 'SZ\n'or stock_exchange[1] == 'CYB\n':
                                        stocks_in_board.append('0' + stock_exchange[0] + '\n')

                        tdx_board_name = period_v + strategy + date.replace('-', '')

                        if cur_end:
                            if date == cur_end and period_k != '1DAY':
                                tdx_board_name += '_' + str(offset_in_period)

                        tdx_board_path = os.path.join(tdx_dir, tdx_board_name + '.blk')
                        with open(tdx_board_path, 'w+') as tdx_board_file:
                            tdx_board_file.writelines(stocks_in_board)
                        if string.find(cfg, tdx_board_name) == -1:
                            cfg_string += generate_cfg_string(tdx_board_name)

    cfg_file.write(cfg_string)
    cfg_file.close()


def import_stocks_into_ths(ths_dir,
                           stock_search_dir,
                           periods,
                           strategies,
                           start_day,
                           end_day,
                           cur_end = None,
                           offset_in_period = None):

    stocks_in_board = ''
    for period_k, period_v in periods.items():
        p_dir = os.path.join(stock_search_dir, period_k)
        if not os.path.exists(p_dir):
            print("The stock search results directory, %s, not exist." % p_dir)
            continue

        for strategy in strategies:
            p_s_dir = os.path.join(p_dir, strategy)
            if not os.path.exists(p_s_dir):
                print("The stock search results directory, %s, not exist." % p_s_dir)
                continue
            date_list = os.listdir(p_s_dir)
            for date in date_list:
                if start_day <= date <= end_day:
                    p_s_d_dir = os.path.join(p_s_dir, date)
                    csv_list = os.listdir(p_s_d_dir)
                    if len(csv_list):
                        for csv in csv_list:
                            csv_path = os.path.join(p_s_d_dir, csv)
                            with open(csv_path, 'r') as csv_file:
                                stocks = csv_file.readlines()
                                stocks = stocks[1:]
                                for stock in stocks:
                                    stock_exchange = stock.split(',')[1].split('.')
                                    if stock_exchange[1] == 'SH\n':
                                        stocks_in_board += '17:' + stock_exchange[0] + ','
                                    elif stock_exchange[1] == 'SZ\n' or stock_exchange[1] == 'CYB\n':
                                        stocks_in_board += '33:' + stock_exchange[0] + ','

    stocks_in_board += '\n'
    if not os.path.exists(ths_dir):
        print("The tdx directory, %s, not exist." % ths_dir)
        exit(1)

    cfg_path = os.path.join(ths_dir, 'StockBlock.ini')
    if not os.path.exists(cfg_path):
        return
    else:
        cfg_file = open(cfg_path, 'r')
        cfglines = cfg_file.readlines()
        cfg_file.close()

        board_num = len(cfglines) - cfglines.index('[BLOCK_NAME_MAP_TABLE]\n') - 1
        if board_num < 7:
            cfglines.insert(cfglines.index('[BLOCK_NAME_MAP_TABLE]\n') + 1 + board_num,
                            str(23 + board_num) + "=" + start_day.replace('-', ''))
            cfglines.insert(cfglines.index('[BLOCK_STOCK_CONTEXT]\n') + 2 + board_num,
                            str(23 + board_num) + "=" + stocks_in_board)
        else:
            board_id_list = [item[0:2] for item in
                            cfglines[cfglines.index('[BLOCK_NAME_MAP_TABLE]\n') + 1:]]
            board_id_list = filter(lambda x:x, board_id_list)
            board_name_list = [item[-9: -1] for item in
                              cfglines[cfglines.index('[BLOCK_NAME_MAP_TABLE]\n') + 1:]]
            board_name_list = filter(lambda x: x, board_name_list)
            replace_index = cfglines.index('[BLOCK_NAME_MAP_TABLE]\n') + board_name_list.index(min(board_name_list)) + 1
            cfglines.remove(cfglines[replace_index])
            cfglines.insert(replace_index,
                            board_id_list[board_name_list.index(min(board_name_list))] + "=" + start_day.replace('-', '') + '\n')
            replace_index = cfglines.index('[BLOCK_STOCK_CONTEXT]\n') + board_name_list.index(min(board_name_list)) + 2
            cfglines.remove(cfglines[replace_index])
            cfglines.insert(replace_index,
                            board_id_list[board_name_list.index(min(board_name_list))] + "=" + stocks_in_board)

        cfg_file = open(cfg_path, 'w')
        cfg_file.writelines(cfglines)
        cfg_file.close()

def import_stocks_into_ths_v2(ths_dir,
                           stock_search_dir,
                           periods,
                           strategies,
                           start_day,
                           end_day,
                           cur_end = None,
                           offset_in_period = None):

    stocks_in_board = ''
    for period_k, period_v in periods.items():
        p_dir = os.path.join(stock_search_dir, period_k)
        if not os.path.exists(p_dir):
            print("The stock search results directory, %s, not exist." % p_dir)
            continue

        for strategy in strategies:
            p_s_dir = os.path.join(p_dir, strategy)
            if not os.path.exists(p_s_dir):
                print("The stock search results directory, %s, not exist." % p_s_dir)
                continue
            date_list = os.listdir(p_s_dir)
            for date in date_list:
                if start_day <= date <= end_day:
                    p_s_d_dir = os.path.join(p_s_dir, date)
                    csv_list = os.listdir(p_s_d_dir)
                    if len(csv_list):
                        for csv in csv_list:
                            csv_path = os.path.join(p_s_d_dir, csv)
                            with open(csv_path, 'r') as csv_file:
                                stocks = csv_file.readlines()
                                stocks = stocks[1:]
                                for stock in stocks:
                                    stock_exchange = stock.split(',')[1].split('.')
                                    if stock_exchange[1] == 'SH\n':
                                        stocks_in_board += '' + stock_exchange[0]
                                    elif stock_exchange[1] == 'SZ\n' or stock_exchange[1] == 'CYB\n':
                                        stocks_in_board += '!' + stock_exchange[0]

    if not os.path.exists(ths_dir):
        print("The tdx directory, %s, not exist." % ths_dir)
        exit(1)

    input_path = os.path.join(ths_dir, 'input.sel')
    if not os.path.exists(input_path):
        return
    else:
        input_file = open(input_path, 'r+')
        input_file.truncate(2)
        input_file.seek(2)
        input_file.write(stocks_in_board)
        input_file.close()

def get_cur_weekend_and_offset(current_day, week_dir):
    year = current_day.year
    if not os.path.exists(week_dir):
        print('calendar_week file is not exist')
        exit(1)
    with open(week_dir, 'r') as json_file:
        calendar_week = json.load(json_file)
        weekstart_list = calendar_week[0][str(year) + '_weekstart']
        weekend_list = calendar_week[0][str(year) + '_weekend']

        current_day = str(current_day)
        for weekend in weekend_list:
            if current_day <= weekend:
                break

        weekend_index = weekend_list.index(weekend)
        weekstart = weekstart_list[weekend_index]
        if current_day < weekstart:
            print('current_day is in a holiday')
            return None, -1
        else:
            t = time.strptime(current_day, "%Y-%m-%d")
            cur_datetime = datetime.datetime(*t[:6])
            t = time.strptime(weekstart, "%Y-%m-%d")
            ws_datetime = datetime.datetime(*t[:6])
            return weekend, (cur_datetime - ws_datetime).days + 1

def daily_import_stocks_into_tdx(week_dir,
                                 tdx_dir,
                                 stock_search_dir,
                                 periods,
                                 strategies):
    current_day = datetime.date.today()
    last_day = current_day - datetime.timedelta(days=1)
    weekend, offset = get_cur_weekend_and_offset(last_day, week_dir)
    import_stocks_into_tdx(tdx_dir,
                           stock_search_dir,
                           periods,
                           strategies,
                           str(last_day),
                           str(weekend),
                           str(weekend),
                           offset)

def daily_import_stocks_into_ths(week_dir,
                                 ths_dir,
                                 stock_search_dir,
                                 periods,
                                 strategies):
    current_day = datetime.date.today()
    last_day = current_day - datetime.timedelta(days=1)
    weekend, offset = get_cur_weekend_and_offset(last_day, week_dir)
    uipath = unicode(ths_dir, "utf8")
    import_stocks_into_ths(uipath,
                           stock_search_dir,
                           periods,
                           strategies,
                           str(last_day),
                           str(weekend),
                           str(weekend),
                           offset)

def daily_import_stocks_into_ths_v2(week_dir,
                                 ths_dir,
                                 stock_search_dir,
                                 periods,
                                 strategies):
    current_day = datetime.date.today()
    last_day = current_day - datetime.timedelta(days=1)
    weekend, offset = get_cur_weekend_and_offset(last_day, week_dir)
    uipath = unicode(ths_dir, "utf8")
    import_stocks_into_ths_v2(uipath,
                           stock_search_dir,
                           periods,
                           strategies,
                           str(last_day),
                           str(weekend),
                           str(weekend),
                           offset)

'''
import_stocks_into_tdx('D:\\new_qlzq_v6\T0002\\blocknew',
                       'D:\dan\stock\py_stock\quantdigger\candicates',
                       {'1DAY': '1D',},
                       ['ZT62808DKLINE_MACD1_MA60', ],#['ZT62808DKLINE_MACD4', 'ZT62808DKLINE_MACD7'],#['MACD_MA7', 'MACD_MA8', 'MACD_MA9'],
                       '2018-01-26',
                       '2018-01-26'
                       )


remove_stocks_from_tdx('D:\\new_qlzq_v6\T0002\\blocknew',
                       {'1DAY': '1D',},
                       ['ZT62808DKLINE_MACD4',])


'''
daily_import_stocks_into_tdx('D:\dan\stock\py_stock\calendar\\2018_week.json',
                             'D:\\new_qlzq_v6\T0002\\blocknew',
                             'D:\dan\stock\py_stock\quantdigger\candicates',
                             {'1DAY': '1D',},
                             ['MA60_MA20',
                              'ZT62808DKLINE_MACD1_MA60',
                              'ZT62808DKLINE_MACD7_MA60',
                              'MACD_MA7',
                              'MACD_MA8',
                              'MACD_MA9',
                              'MACD_MA7A',
                              'MACD_MA8A',
                              'MACD_MA9A']#['ZT62808DKLINE_MACD4','ZT62808DKLINE_MACD7'] #['MACD_MA7', 'MACD_MA8'],
                             )

'''
daily_import_stocks_into_ths('D:\dan\stock\py_stock\calendar\\2018_week.json',
                             'C:\\同花顺软件\\同花顺\\mx_297788656',
                             'D:\dan\stock\py_stock\quantdigger\candicates',
                             {'1DAY': '1D',},
                             ['MA60_MA20',
                              'ZT62808DKLINE_MACD1_MA60',
                              'ZT62808DKLINE_MACD7_MA60',
                              'MACD_MA7',
                              'MACD_MA7A',
                              'MACD_MA8',
                              'MACD_MA8A',
                              'MACD_MA9',
                              'MACD_MA9A']#['ZT62808DKLINE_MACD4','ZT62808DKLINE_MACD7'] #['MACD_MA7', 'MACD_MA8'],
                             )
'''


