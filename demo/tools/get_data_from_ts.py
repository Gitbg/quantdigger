import tushare as ts
import pandas as pd
import datetime

def formatDate(Date, formatType='YYYYMMDD'):
    formatType = formatType.replace('YYYY', Date[0:4])
    formatType = formatType.replace('MM', Date[4:6])
    formatType = formatType.replace('DD', Date[-4:-2])
    return formatType

stocks_basics = ts.get_stock_basics()
code = stocks_basics.sort_index().index
date = stocks_basics.ix['000017']['timeToMarket']
date = formatDate(str(date), "YYYY-MM-DD")
#dk = ts.get_k_data('000566', start='2017-04-05', end='2017-04-05')
#dk = ts.get_k_data('000017', ktype='M', autype=None, start='2017-04-17', end='2017-04-17')
#dk = ts.get_k_data('000017', ktype='M', autype=None, start='2017-04-13', end='2017-04-13')
#dk = ts.get_k_data('000017', ktype='W', autype=None, start='2017-04-12', end='2017-04-12')
#dk = ts.get_k_data('000017', ktype='D', autype=None, start='2017-04-18', end='2017-04-18')
#dh = ts.get_h_data('000555', start='2017-04-05', end='2017-04-05')
#dhi = ts.get_hist_data('002051', start='2017-04-06', end='2017-04-06')
#dhi = ts.get_hist_data('600636', start='2017-04-06', end='2017-04-06')
#dh = ts.get_h_data('000555', start=date, end='2017-12-31')
#dhi = ts.get_hist_data('000555', ktype='W',start='2017-03-01', end='2017-04-13')


dt = datetime.date.today()
dir(dt)
print (dt.strftime('%w'))

code = stocks_basics.index
