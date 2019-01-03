import tushare as ts
import pandas as pd
import datetime
import funcat

def formatDate(Date, formatType='YYYYMMDD'):
    formatType = formatType.replace('YYYY', Date[0:4])
    formatType = formatType.replace('MM', Date[4:6])
    formatType = formatType.replace('DD', Date[-4:-2])
    return formatType

stocks_basics = ts.get_stock_basics()
stocks_basics_sort = stocks_basics.sort_values(by = ['timeToMarket',])
symbols = stocks_basics.sort_index().index
sz_symbols = [symbol for symbol in symbols if symbol[0] == '0']
date = stocks_basics.ix['600432']['timeToMarket']
#date = formatDate(str(date), "YYYY-MM-DD")
#dk = ts.get_k_data('600093', start='2017-05-12', end='2018-05-08')
#dk = ts.get_k_data('002044', start=date, end='2017-04-29')
#dk = ts.get_k_data('000017', ktype='M', autype=None, start='2017-04-17', end='2017-04-17')
#dk15 = ts.get_k_data('000017', ktype='15', autype=None, start='2017-07-17', end='2017-08-11')
#dk60 = ts.get_k_data('000017', ktype='60', autype=None, start='2017-07-17', end='2017-08-11')
#dk = ts.get_k_data('000017', ktype='M', autype=None, start='2017-06-07', end='2017-06-08')
dk = ts.get_k_data('600093', ktype='D', autype='fq', start='2017-08-07', end='2018-05-08', retry_count=100)
#dk = ts.get_k_data('603017', ktype='D', autype=None, start='2017-04-20', end='2017-04-20')
#dh = ts.get_h_data('000555', start='2017-04-05', end='2017-04-05')
#dhi = ts.get_hist_data('002051', start='2017-04-06', end='2017-04-06')
#dhi = ts.get_hist_data('600636', start='2017-04-06', end='2017-04-06')
#dh = ts.get_h_data('000555', start=date, end='2017-12-31')
#dhi = ts.get_hist_data('000555', ktype='W',start='2017-03-01', end='2017-04-13')
#dhi = ts.get_hist_data('000555', ktype='60')
dhi = ts.get_hist_data('000555', ktype='60', start='2017-07-31 10:30:00', end='2017-08-18 15:00:00')
code = stocks_basics.index
