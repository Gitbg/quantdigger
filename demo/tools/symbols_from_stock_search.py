import pandas as pd
import os


def get_symbols_from_stock_search_result(periods, strategies, root_path, start, end):
    total_symbols = []
    for period in periods:
        for strategy in strategies:
            candicates_path = os.path.join(root_path, 'py_stock', 'quantdigger', 'candicates', period, strategy)
            date_list = os.listdir(candicates_path)
            date_list = filter(lambda n: start <= n <= end, date_list)
            for date in date_list:
                date_csv_dir = os.path.join(candicates_path, date, 'SH.csv')
                date_symbols = pd.read_csv(date_csv_dir, names=['id', 'code'])
                total_symbols = list(set(total_symbols) | set(date_symbols['code'][1:]))

    total_symbols = [symbol[0:6] for symbol in total_symbols]
    return total_symbols







