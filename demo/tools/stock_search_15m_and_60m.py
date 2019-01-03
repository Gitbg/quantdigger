import pandas as pd
import tushare as ts
import os
from .download_data_from_ts_to_csv import download_k_data
from .symbols_from_stock_search import get_symbols_from_stock_search_result
from ..stock_search import MACD_MA3


def download_minute_k_data(fqs, periods, strategies, root_path, start, end):
    stocks_basics = ts.get_stock_basics()
    symbols = get_symbols_from_stock_search_result(list(periods), strategies, root_path, start, end)
    sz_symbols = [symbol for symbol in symbols if symbol[0] == '0']
    cyb_symbols = [symbol for symbol in symbols if symbol[0] == '3']
    sh_symbols = [symbol for symbol in symbols if symbol[0] == '6']

    for fq in fqs:
        for k, v in periods.items():
            download_k_data(k, v, fq, 'SZ', sz_symbols, stocks_basics, root_path, end)
            download_k_data(k, v, fq, 'SH', sh_symbols, stocks_basics, root_path, end)
            download_k_data(k, v, fq, 'CYB', cyb_symbols, stocks_basics, root_path, end)









