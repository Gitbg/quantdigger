# -*- coding: utf-8 -*-

# @file stock_search.py
# @brief 选股的例子
# @author wondereamer
# @version 0.2
# @date 2015-12-09

from quantdigger import *
from quantdigger.interaction.save import save_candicates
from quantdigger.technicals import qMA, qFT62876XY, qZT62808, qMACD,qZT62808_VAR19, qVR, qMTM

class StockSearch(Strategy):
    def __init__(self, name):
        super(StockSearch, self).__init__(name)
        self.candicates = []
        self.to_sell = []

    def on_bar(self, ctx):
        if(len(self.candicates) != 0):
            save_candicates('D:\dan\stock\py_stock\quantdigger\candicates',
                            ctx.strategy,
                            ctx.ctx_datetime,
                            ctx.pcontract,
                            self.candicates)

        if(len(self.to_sell) != 0):
            save_candicates('D:\dan\stock\py_stock\quantdigger\\to_sell',
                            ctx.strategy,
                            ctx.ctx_datetime,
                            ctx.pcontract,
                            self.to_sell)

        for symbol in self.to_sell:
            if ctx.pos('long', symbol) > 0:
                ctx.sell(ctx[symbol].close, 1, symbol)
                #print "sell:", symbol

        for symbol in self.candicates:
            if ctx.pos('long', symbol) == 0:
                ctx.buy(ctx[symbol].close, 1, symbol)
                #print "buy:", symbol


        self.candicates = []
        self.to_sell = []
        return

    def on_exit(self, ctx):
        print("策略运行结束．")
        return

class MA10MA20(StockSearch):
    """ 策略A1 """
    def __init__(self, name):
        super(MA10MA20, self).__init__(name)

    def on_init(self, ctx):
        """初始化数据""" 
        ctx.ma10 = qMA(ctx._cur_data_context.raw_data.close, 10, 'ma10', 'y', 2)
        ctx.ma20 = qMA(ctx._cur_data_context.raw_data.close, 20, 'ma20', 'b', 2)

    def on_symbol(self, ctx):
        if ctx.curbar > 20:
            if ctx.ma10[1] < ctx.ma20[1] and ctx.ma10 > ctx.ma20:
                self.candicates.append(ctx.symbol)
            elif ctx.ma10[1] < ctx.ma20[1]:
                self.to_sell.append(ctx.symbol)

class FT62876XY(StockSearch):
    def __init__(self, name):
        super(FT62876XY, self).__init__(name)

    def on_init(self, ctx):
        ctx.ft62876 = qFT62876XY(ctx._cur_data_context.raw_data)

    def on_symbol(self, ctx):
        if ctx.ft62876['x'] == True:
            self.candicates.append(ctx.symbol)

        if ctx.ft62876['y'] == True:
            self.to_sell.append(ctx.symbol)

class MACD_ONLY0(StockSearch):
    def __init__(self, name):
        super(MACD_ONLY0, self).__init__(name)

    def on_init(self,ctx):
        ctx.ma5 = qMA(ctx._cur_data_context.raw_data.close, 5, 'ma5', 'y', 2)
        ctx.ma10 = qMA(ctx._cur_data_context.raw_data.close, 10, 'ma10', 'y', 2)
        ctx.ma20 = qMA(ctx._cur_data_context.raw_data.close, 20, 'ma20', 'y', 2)

    def on_symbol(self, ctx):
        if (ctx.ma20[2] <= ctx.ma20[1] <= ctx.ma20
            and ctx.ma10[1] <= ctx.ma10
            and ctx.ma5[1] <= ctx.ma5
            and ctx.ma5[1] <= ctx.ma10[1]
            and ctx.ma10 <= ctx.ma5):
            self.candicates.append(ctx.symbol)

class MACD_MA0(StockSearch):
    def __init__(self, name):
        super(MACD_MA0, self).__init__(name)

    def on_init(self, ctx):
        ctx.macd = qMACD(ctx._cur_data_context.raw_data.close, 12, 26, 9)
        ctx.ma5 = qMA(ctx._cur_data_context.raw_data.close, 5, 'ma5', 'y', 2)
        ctx.ma10 = qMA(ctx._cur_data_context.raw_data.close, 10, 'ma10', 'y', 2)
        ctx.ma20 = qMA(ctx._cur_data_context.raw_data.close, 20, 'ma20', 'y', 2)

    def on_symbol(self, ctx):
        if (ctx.macd['diff'] > 0
            and ctx.macd['dea'] > 0
            and ctx.macd['macd'] > 0
            and (ctx.macd['diff'] - ctx.macd['dea'] < 0.01)
            and ctx.ma10 > ctx.ma20
            and ctx.ma10[1] > ctx.ma20[1]
            and ctx.ma10[2] > ctx.ma20[2]
            and ctx.ma10[2] <= ctx.ma10[1] <= ctx.ma10
            and ctx.ma20[2] <= ctx.ma20[1] <= ctx.ma20
            and ctx.ma20 <= ctx.low <= ctx.ma10
            and ctx.close >= ctx.ma5):
                self.candicates.append(ctx.symbol)

class MACD_MA1(MACD_MA0):
    def __init__(self, name):
        super(MACD_MA1, self).__init__(name)

    def on_symbol(self, ctx):
        if (ctx.macd['diff'] > 0
            and ctx.macd['dea'] > 0
            and (abs(ctx.macd['diff'] - ctx.macd['dea']) <= 0.03)
            and ctx.ma10 > ctx.ma20
            and ctx.ma10[1] > ctx.ma20[1]
            and ctx.ma10[2] > ctx.ma20[2]
            and ctx.ma10[2] <= ctx.ma10[1] <= ctx.ma10
            and ctx.ma20[2] <= ctx.ma20[1] <= ctx.ma20
            and ctx.ma20 <= ctx.low <= ctx.ma10
            and (not (ctx.ma5 < ctx.ma10 and ctx.ma5 < ctx.ma5[1]))
            and ctx.close >= ctx.ma5):
                self.candicates.append(ctx.symbol)

class MACD_MA2(MACD_MA0):
    def __init__(self, name):
        super(MACD_MA2, self).__init__(name)

    def on_symbol(self, ctx):
        if (abs(ctx.macd['diff'] - ctx.macd['dea']) <= 0.03
            and ctx.ma10 > ctx.ma20
            and ctx.ma10[1] > ctx.ma20[1]
            and ctx.ma10[2] > ctx.ma20[2]
            and ctx.ma10[2] <= ctx.ma10[1] <= ctx.ma10
            and ctx.ma20[2] <= ctx.ma20[1] <= ctx.ma20
            and ctx.ma20 <= ctx.low <= ctx.ma10
            and (not (ctx.ma5 < ctx.ma10 and ctx.ma5 < ctx.ma5[1]))
            and ctx.close >= ctx.ma5):
                self.candicates.append(ctx.symbol)

class MACD_MA3(MACD_MA0):
    def __init__(self, name):
        super(MACD_MA3, self).__init__(name)

    def on_symbol(self, ctx):
        if (abs(ctx.macd['diff'] - ctx.macd['dea']) <= 0.03
            and ctx.ma10 > ctx.ma20
            and ctx.ma10[1] > ctx.ma20[1]
            and ctx.ma10[2] > ctx.ma20[2]
            and ctx.ma10[2] <= ctx.ma10[1] <= ctx.ma10
            and ctx.ma20[2] <= ctx.ma20[1] <= ctx.ma20
            and ctx.ma20 <= ctx.low <= ctx.ma10
            and (not (ctx.ma5 < ctx.ma10 and ctx.ma5 < ctx.ma5[1]))
            and ctx.ma20 < ctx.close[1] < ctx.ma10
            and ctx.ma10 < ctx.close < ctx.ma5):
                self.candicates.append(ctx.symbol)

class MACD_MA4(MACD_MA0):
    def __init__(self, name):
        super(MACD_MA4, self).__init__(name)

    def on_symbol(self, ctx):
        if (ctx.ma5 < ctx.ma10 < ctx.ma20
            and ctx.ma5[1] < ctx.ma10[1] < ctx.ma20[1]
            and ctx.ma5[2] < ctx.ma10[2] < ctx.ma20[2]
            and ctx.ma5[2] <= ctx.ma5[1] <= ctx.ma5
            and ctx.ma10[2] <= ctx.ma10[1] <= ctx.ma10
            and ctx.ma20[2] <= ctx.ma20[1] <= ctx.ma20
            and ctx.close < ctx.close[1]
            and ctx.ma10 < ctx.close < ctx.ma5):
                self.candicates.append(ctx.symbol)

class MACD_MA5(MACD_MA0):
    def __init__(self, name):
        super(MACD_MA5, self).__init__(name)

    def on_symbol(self, ctx):
        if (abs(ctx.macd['diff'] - ctx.macd['dea']) >= 0.1
            and ctx.macd['macd'] > ctx.macd['macd'][1]
            and ctx.macd['macd'][2] > ctx.macd['macd'][1]
            and ctx.ma10 > ctx.ma20
            and ctx.ma10[1] > ctx.ma20[1]
            and ctx.ma10[2] > ctx.ma20[2]
            and ctx.ma10[2] <= ctx.ma10[1] <= ctx.ma10
            and ctx.ma20[2] <= ctx.ma20[1] <= ctx.ma20
            and ctx.ma20 <= ctx.low <= ctx.ma10
            and (not (ctx.ma5 < ctx.ma10 and ctx.ma5 < ctx.ma5[1]))
            and ctx.close >= ctx.ma5):
                self.candicates.append(ctx.symbol)

class MACD_MA6(MACD_MA0):
    def __init__(self, name):
        super(MACD_MA6, self).__init__(name)

    def on_symbol(self, ctx):
        if (abs(ctx.macd['diff'] - ctx.macd['dea']) >= 0.1
            and ctx.ma10 > ctx.ma20
            and ctx.ma10[1] > ctx.ma20[1]
            and ctx.ma10[2] > ctx.ma20[2]
            and ctx.ma20[2] <= ctx.ma20[1] <= ctx.ma20
            and ctx.ma20 <= ctx.low <= ctx.ma10
            and (not (ctx.ma5 < ctx.ma10 and ctx.ma5 < ctx.ma5[1]))
            and ctx.ma20 < ctx.close[1] < ctx.ma10
            and ctx.ma10 < ctx.close < ctx.ma5):
                self.candicates.append(ctx.symbol)

class MACD_MA7(MACD_MA0):
    def __init__(self, name):
        super(MACD_MA7, self).__init__(name)

    def on_symbol(self, ctx):
        if (abs(ctx.macd['diff'] - ctx.macd['dea']) >= 0.1
            and ctx.ma10 > ctx.ma20
            and ctx.ma10[1] > ctx.ma20[1]
            and ctx.ma10[2] > ctx.ma20[2]
            and ctx.ma10[2] <= ctx.ma10[1] <= ctx.ma10
            and ctx.ma20[2] <= ctx.ma20[1] <= ctx.ma20
            and (not (ctx.ma5 < ctx.ma10 and ctx.ma5 < ctx.ma5[1]))
            and ctx.low <= ctx.ma20
            and ctx.ma10 >= ctx.close >= ctx.ma20):
                self.candicates.append(ctx.symbol)

class MACD_MA8(MACD_MA0):
    def __init__(self, name):
        super(MACD_MA8, self).__init__(name)

    def on_symbol(self, ctx):
        if (0.05 <= abs(ctx.macd['diff'] - ctx.macd['dea']) <= 0.09
            and ctx.ma10 > ctx.ma20
            and ctx.ma10[1] > ctx.ma20[1]
            and ctx.ma10[2] > ctx.ma20[2]
            and ctx.ma10[2] <= ctx.ma10[1] <= ctx.ma10
            and ctx.ma20[2] <= ctx.ma20[1] <= ctx.ma20
            and (not (ctx.ma5 < ctx.ma10 and ctx.ma5 < ctx.ma5[1]))
            and ctx.low <= ctx.ma20
            and ctx.ma10 >= ctx.close >= ctx.ma20):
                self.candicates.append(ctx.symbol)

class MACD_MA9(MACD_MA0):
    def __init__(self, name):
        super(MACD_MA9, self).__init__(name)

    def on_symbol(self, ctx):
        if (abs(ctx.macd['diff'] - ctx.macd['dea']) <= 0.04
            and ctx.ma10 > ctx.ma20
            and ctx.ma10[1] > ctx.ma20[1]
            and ctx.ma10[2] > ctx.ma20[2]
            and ctx.ma10[2] <= ctx.ma10[1] <= ctx.ma10
            and ctx.ma20[2] <= ctx.ma20[1] <= ctx.ma20
            and (not (ctx.ma5 < ctx.ma10 and ctx.ma5 < ctx.ma5[1]))
            and ctx.low <= ctx.ma20
            and ctx.close >= ctx.ma5):
                self.candicates.append(ctx.symbol)

class MACD_MA10(MACD_MA0):
    def __init__(self, name):
        super(MACD_MA10, self).__init__(name)

    def on_symbol(self, ctx):
        if (abs(ctx.macd['diff'] - ctx.macd['dea']) <= 0.04
            and ctx.ma10 > ctx.ma20
            and ctx.ma10[1] > ctx.ma20[1]
            and ctx.ma10[2] > ctx.ma20[2]
            and ctx.ma10[2] <= ctx.ma10[1] <= ctx.ma10
            and ctx.ma20[2] <= ctx.ma20[1] <= ctx.ma20
            and ctx.low <= ctx.ma20
            and ctx.close >= ctx.ma5):
                self.candicates.append(ctx.symbol)

class ZT62808DKLINE_MACD(StockSearch):
    def __init__(self, name):
        super(ZT62808DKLINE_MACD, self).__init__(name)

    def on_init(self, ctx):
        ctx.zt62808dkline = qZT62808(ctx._cur_data_context.raw_data)
        ctx.macd = qMACD(ctx._cur_data_context.raw_data.close, 12, 26, 9)

    def on_symbol(self, ctx):
        if (ctx.macd['diff'] > 0
            and ctx.macd['dea'] > 0
            and ctx.macd['macd'] > 0
            and (ctx.macd['diff'] - ctx.macd['dea'] < 0.01)
            and ctx.low <= ctx.zt62808dkline
            and ctx.high >= ctx.zt62808dkline
            and (ctx.close <= ctx.open and ctx.volume < ctx.volume[1]
                 or ctx.close > ctx.open and ctx.volume > ctx.volume[1])):
                self.candicates.append(ctx.symbol)

# MACD三项大于0，点水0.01，上穿多空线，收盘价大于开盘价，量增
class ZT62808DKLINE_MACD0(ZT62808DKLINE_MACD):
    def __init__(self, name):
        super(ZT62808DKLINE_MACD0, self).__init__(name)

    def on_symbol(self, ctx):
        if (ctx.macd['diff'] > 0
            and ctx.macd['dea'] > 0
            and ctx.macd['macd'] > 0
            and (ctx.macd['diff'] - ctx.macd['dea'] < 0.01)
            and ctx.low <= ctx.zt62808dkline
            and ctx.high >= ctx.zt62808dkline
            and ctx.close > ctx.open and ctx.volume > ctx.volume[1]):
                self.candicates.append(ctx.symbol)

# MACD两项大于0，点水0.01，上穿多空线，收盘价小于等于开盘价，量减
class ZT62808DKLINE_MACD1(ZT62808DKLINE_MACD):
    def __init__(self, name):
        super(ZT62808DKLINE_MACD1, self).__init__(name)

    def on_symbol(self, ctx):
        if (ctx.macd['diff'] > 0
            and ctx.macd['dea'] > 0
            and (abs(ctx.macd['diff'] - ctx.macd['dea']) < 0.01)
            and ctx.low <= ctx.zt62808dkline
            and ctx.high >= ctx.zt62808dkline
            and ctx.close <= ctx.open and ctx.volume < ctx.volume[1]):
                self.candicates.append(ctx.symbol)

# MACD两项大于0，点水0.01，上穿多空线，收盘价大于开盘价，量增
class ZT62808DKLINE_MACD2(ZT62808DKLINE_MACD):
    def __init__(self, name):
        super(ZT62808DKLINE_MACD2, self).__init__(name)

    def on_symbol(self, ctx):
        if (ctx.macd['diff'] > 0
            and ctx.macd['dea'] > 0
            and (abs(ctx.macd['diff'] - ctx.macd['dea']) < 0.01)
            and ctx.low <= ctx.zt62808dkline
            and ctx.high >= ctx.zt62808dkline
            and ctx.close > ctx.open and ctx.volume > ctx.volume[1]):
                self.candicates.append(ctx.symbol)

# MACD两项大于0，点水0.03，上穿多空线，收盘价小于等于开盘价，量减
class ZT62808DKLINE_MACD3(ZT62808DKLINE_MACD):
    def __init__(self, name):
        super(ZT62808DKLINE_MACD3, self).__init__(name)

    def on_symbol(self, ctx):
        if (ctx.macd['diff'] > 0
            and ctx.macd['dea'] > 0
            and (abs(ctx.macd['diff'] - ctx.macd['dea']) < 0.03)
            and ctx.low <= ctx.zt62808dkline
            and ctx.high >= ctx.zt62808dkline
            and ctx.close <= ctx.open and ctx.volume < ctx.volume[1]):
                self.candicates.append(ctx.symbol)

# MACD两项大于0，点水0.03，上穿多空线，收盘价大于开盘价，量增
class ZT62808DKLINE_MACD4(ZT62808DKLINE_MACD):
    def __init__(self, name):
        super(ZT62808DKLINE_MACD4, self).__init__(name)

    def on_symbol(self, ctx):
        if (ctx.macd['diff'] > 0
            and ctx.macd['dea'] > 0
            and (abs(ctx.macd['diff'] - ctx.macd['dea']) < 0.03)
            and ctx.low <= ctx.zt62808dkline
            and ctx.high >= ctx.zt62808dkline
            and ctx.close > ctx.open and ctx.volume > ctx.volume[1]):
                self.candicates.append(ctx.symbol)

class ZT62808DKLINE_MACD99(ZT62808DKLINE_MACD):
    def __init__(self, name):
        super(ZT62808DKLINE_MACD99, self).__init__(name)

    def on_symbol(self, ctx):
        if (ctx.macd['diff'] > 0
            and ctx.macd['dea'] > 0
            and ctx.macd['macd'] < 0
            and ctx.macd['macd'] > ctx.macd['macd'][1]
            and ctx.low <= ctx.zt62808dkline
            and ctx.high >= ctx.zt62808dkline
            and ctx.close > ctx.open and ctx.volume > ctx.volume[1]):
                self.candicates.append(ctx.symbol)

# MACD点水0.03，上穿多空线，收盘价大于开盘价，量增
class ZT62808DKLINE_MACD6(ZT62808DKLINE_MACD):
    def __init__(self, name):
        super(ZT62808DKLINE_MACD6, self).__init__(name)

    def on_symbol(self, ctx):
        if ((abs(ctx.macd['diff'] - ctx.macd['dea']) < 0.03)
            and ctx.low <= ctx.zt62808dkline
            and ctx.high >= ctx.zt62808dkline
            and ctx.close > ctx.open and ctx.volume > ctx.volume[1]):
                self.candicates.append(ctx.symbol)

# MACD点水0.03，macd大于0，或macd小于0且macd缩短， 上穿多空线，收盘价大于开盘价，量增
class ZT62808DKLINE_MACD7(ZT62808DKLINE_MACD):
    def __init__(self, name):
        super(ZT62808DKLINE_MACD7, self).__init__(name)

    def on_symbol(self, ctx):
        if ((abs(ctx.macd['diff'] - ctx.macd['dea']) < 0.03)
            and ctx.low <= ctx.zt62808dkline
            and ctx.high >= ctx.zt62808dkline
            and ctx.close > ctx.open
            and ctx.volume > ctx.volume[1]):
                if(ctx.macd['macd'] >= 0
                   or (ctx.macd['macd'] < 0
                       and ctx.macd['macd'] > ctx.macd['macd'][1])):
                        self.candicates.append(ctx.symbol)

class ZT62808DKLINE_MACD8(ZT62808DKLINE_MACD):
    def __init__(self, name):
        super(ZT62808DKLINE_MACD8, self).__init__(name)

    def on_symbol(self, ctx):
        if (ctx.macd['diff'] > 0
            and ctx.macd['dea'] > 0
            and (abs(ctx.macd['diff'] - ctx.macd['dea']) <= 0.06)
            and (abs(ctx.macd['diff'] - ctx.macd['dea']) >= 0.03)
            and ctx.low <= ctx.zt62808dkline
            and ctx.high >= ctx.zt62808dkline
            and ctx.close > ctx.open and ctx.volume > ctx.volume[1]):
                self.candicates.append(ctx.symbol)

class ZT62808DKLINE_MACD9(ZT62808DKLINE_MACD):
    def __init__(self, name):
        super(ZT62808DKLINE_MACD9, self).__init__(name)

    def on_symbol(self, ctx):
        if (ctx.close[2] > ctx.close[3] > ctx.close[4]
            and ctx.volume[2] > ctx.volume[3] > ctx.volume[4]
            and ctx.close < ctx.close[1] < ctx.close[2]
            and ctx.volume < ctx.volume[1] < ctx.volume[2]
            and ctx.close >= ctx.zt62808dkline):
                self.candicates.append(ctx.symbol)

class ZT62808DKLINE_MA0(StockSearch):
    def __init__(self, name):
        super(ZT62808DKLINE_MA0, self).__init__(name)

    def on_init(self,ctx):
        ctx.zt62808dkline = qZT62808(ctx._cur_data_context.raw_data)
        ctx.ma5 = qMA(ctx._cur_data_context.raw_data.close, 5, 'ma5', 'y', 2)

    def on_symbol(self, ctx):
        if ctx.ma5 > ctx.zt62808dkline:
            self.candicates.append(ctx.symbol)

class ZT62808DKLINE_MA1(StockSearch):
    def __init__(self, name):
        super(ZT62808DKLINE_MA1, self).__init__(name)

    def on_init(self,ctx):
        ctx.zt62808dkline = qZT62808(ctx._cur_data_context.raw_data)
        ctx.ma5 = qMA(ctx._cur_data_context.raw_data.close, 5, 'ma5', 'y', 2)

    def on_symbol(self, ctx):
        if ctx.ma5 > ctx.zt62808dkline \
            and ctx.ma5 < ctx.ma5[1] \
            and ctx.ma5[1] < ctx.ma5[2] \
            and ctx.close >= ctx.zt62808dkline \
            and ctx.close < ctx.ma5:
            self.candicates.append(ctx.symbol)
        elif ctx.ma5 <= ctx.zt62808dkline \
            and ctx.ma5 > ctx.ma5[1] \
            and ctx.ma5[1] > ctx.ma5[2] \
            and ctx.close >= ctx.ma5 \
            and ctx.close < ctx.zt62808dkline:
            self.candicates.append(ctx.symbol)

class ZT62808DKLINE_MA2(StockSearch):
    def __init__(self, name):
        super(ZT62808DKLINE_MA2, self).__init__(name)

    def on_init(self,ctx):
        ctx.zt62808dkline = qZT62808(ctx._cur_data_context.raw_data)
        ctx.ma5 = qMA(ctx._cur_data_context.raw_data.close, 5, 'ma5', 'y', 2)

    def on_symbol(self, ctx):
        if ctx.ma5 > ctx.zt62808dkline \
            and ctx.ma5 > ctx.ma5[1] \
            and ctx.ma5[1] < ctx.ma5[2] \
            and ctx.close >= ctx.zt62808dkline \
            and ctx.close < ctx.ma5:
            self.candicates.append(ctx.symbol)
        elif ctx.ma5 <= ctx.zt62808dkline \
            and ctx.ma5 > ctx.ma5[1] \
            and ctx.ma5[1] < ctx.ma5[2] \
            and ctx.close >= ctx.ma5 \
            and ctx.close < ctx.zt62808dkline:
            self.candicates.append(ctx.symbol)

class ZT62808DKLINE_MA3(StockSearch):
    def __init__(self, name):
        super(ZT62808DKLINE_MA3, self).__init__(name)

    def on_init(self,ctx):
        ctx.zt62808dkline = qZT62808(ctx._cur_data_context.raw_data)
        ctx.ma5 = qMA(ctx._cur_data_context.raw_data.close, 5, 'ma5', 'y', 2)

    def on_symbol(self, ctx):
        if ctx.ma5 > ctx.zt62808dkline \
            and ctx.ma5 < ctx.ma5[1] \
            and ctx.ma5[1] < ctx.ma5[2] \
            and ctx.close >= ctx.zt62808dkline \
            and ctx.close < ctx.ma5:
            self.candicates.append(ctx.symbol)

class ZT62808DKLINE_VAR19_VR_MTM_MACD(StockSearch):
    def __init__(self, name):
        super(ZT62808DKLINE_VAR19_VR_MTM_MACD, self).__init__(name)

    def on_init(self, ctx):
        ctx.zt62808dkline = qZT62808(ctx._cur_data_context.raw_data)
        ctx.zt62808var19 = qZT62808_VAR19(ctx._cur_data_context.raw_data)
        ctx.macd = qMACD(ctx._cur_data_context.raw_data.close, 12, 26, 9)
        ctx.vr = qVR(ctx._cur_data_context.raw_data, 26, 6)
        ctx.mtm = qMTM(ctx._cur_data_context.raw_data, 15, 5)

    def on_symbol(self, ctx):
        if((abs(ctx.macd['diff'] - ctx.macd['dea']) <= 0.03)
            and ctx.low <= ctx.zt62808dkline
            and ctx.high >= ctx.zt62808dkline
            and ctx.close > ctx.open
            and ctx.volume > ctx.volume[1]):
            if((ctx.vr['vr'] >= ctx.vr['mavr'] and ctx.mtm['mtm'] >= ctx.mtm['mtmma'])
               or (ctx.vr['vr'] >= ctx.vr['mavr'] and ctx.zt62808var19)
               or (ctx.mtm['mtm'] >= ctx.mtm['mtmma'] and ctx.zt62808var19)):
                self.candicates.append(ctx.symbol)

if __name__ == '__main__':
    #
    import timeit
    start = timeit.default_timer()
    #ConfigUtil.set(data_path='D:\dan\stock\py_stock\quantdigger\data\data')
    ConfigUtil.set(data_path='D:\dan\stock\\tushare_csv\k_data\qfq')
    #set_symbols(['*.SH'])
    #set_symbols(['*.SZ'])
    set_symbols(pcontracts = ['*.SH-1.DAY', '*.SZ-1.DAY', '*.CYB-1.DAY'], dt_start = "2016-01-01", dt_end = "2017-08-11")
    #set_symbols(pcontracts=['*.SZ-1.DAY'], dt_start="2017-02-20", dt_end="2017-06-14")
    #set_symbols(pcontracts=['*.CYB-1.DAY'], dt_start="2017-02-20", dt_end="2017-06-14")
    #set_symbols(pcontracts=['*.SH-1.WEEK', '*.SZ-1.WEEK', '*.CYB-1.WEEK'], dt_start="2015-01-01", dt_end="2017-06-23")
    #algo = MA10MA20('A1')
    #algo = FT62876XY('62876XY')
    #algo = ZT62808DKLINE_MACD('ZT62808DKLINE_MACD')
    algo = ZT62808DKLINE_VAR19_VR_MTM_MACD('ZT62808DKLINE_VAR19_VR_MTM_MACD')
    algo0 = ZT62808DKLINE_MACD0('ZT62808DKLINE_MACD0')
    algo1 = ZT62808DKLINE_MACD1('ZT62808DKLINE_MACD1')
    algo2 = ZT62808DKLINE_MACD2('ZT62808DKLINE_MACD2')
    algo3 = ZT62808DKLINE_MACD1('ZT62808DKLINE_MACD3')
    algo4 = ZT62808DKLINE_MACD4('ZT62808DKLINE_MACD4')
    algo6 = ZT62808DKLINE_MACD6('ZT62808DKLINE_MACD6')
    algo7 = ZT62808DKLINE_MACD7('ZT62808DKLINE_MACD7')
    algo8 = ZT62808DKLINE_MACD8('ZT62808DKLINE_MACD8')
    algo9 = ZT62808DKLINE_MACD9('ZT62808DKLINE_MACD9')
    algo10 = MACD_MA0('MACD_MA0')
    algo11 = MACD_MA1('MACD_MA1')
    algo12 = MACD_MA2('MACD_MA2')
    algo13 = MACD_MA3('MACD_MA3')
    algo14 = MACD_MA4('MACD_MA4')
    algo15 = MACD_MA5('MACD_MA5')
    algo16 = MACD_MA6('MACD_MA6')
    algo17 = MACD_MA7('MACD_MA7')
    algo18 = MACD_MA8('MACD_MA8')
    algo19 = MACD_MA9('MACD_MA9')
    algo1a = MACD_MA10('MACD_MA10')
    algo20 = MACD_ONLY0('MACD_ONLY0')


    algoma0 = ZT62808DKLINE_MA0('ZT62808DKLINE_MA0')
    algoma1 = ZT62808DKLINE_MA1('ZT62808DKLINE_MA1')
    algoma2 = ZT62808DKLINE_MA2('ZT62808DKLINE_MA2')
    algoma3 = ZT62808DKLINE_MA3('ZT62808DKLINE_MA3')
    #profile = add_strategy([algo4, algo7], { 'capital': 500000000.0 })
    #profile = add_strategy([algo10, algo11, algo12, algo13, algo15, algo16], {'capital': 500000000.0})
    profile = add_strategy([algo17, algo18, algo19, algo20], {'capital': 500000000.0})
    #profile = add_strategy([algo20], {'capital': 500000000.0})
    #profile = add_strategy([algoma1, algoma2, algoma3], {'capital': 500000000.0})

    run()

    stop = timeit.default_timer()
    print('Used time is %d seconds' % (stop - start))

    from quantdigger.digger import finance, plotting
    curve = finance.create_equity_curve(profile.all_holdings())
    #plotting.plot_strategy(profile.data('AA.SHFE-1.Minute'), profile.technicals(0),
                            #profile.deals(0), curve.equity.values)
    ## 绘制净值曲线
    plotting.plot_curves([curve.networth])
