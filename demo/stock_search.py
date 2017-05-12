# -*- coding: utf-8 -*-

# @file stock_search.py
# @brief 选股的例子
# @author wondereamer
# @version 0.2
# @date 2015-12-09

from quantdigger import *
from quantdigger.interaction.save import save_candicates
from quantdigger.technicals import qMA

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



if __name__ == '__main__':
    #
    import timeit
    start = timeit.default_timer()
    ConfigUtil.set(data_path='D:\dan\stock\py_stock\quantdigger\data\data')
    #ConfigUtil.set(data_path='D:\dan\stock\\tushare_csv\k_data\hfq')
    set_symbols(['*.SH'])
    #set_symbols(['*.SZ'])
    #set_symbols(['*.SH-1.DAY'])
    algo = MA10MA20('A1')
    profile = add_strategy([algo], { 'capital': 500000000.0 })

    run()

    stop = timeit.default_timer()
    print('Used time is %d seconds' % (stop - start))

    from quantdigger.digger import finance, plotting
    curve = finance.create_equity_curve(profile.all_holdings())
    #plotting.plot_strategy(profile.data('AA.SHFE-1.Minute'), profile.technicals(0),
                            #profile.deals(0), curve.equity.values)
    ## 绘制净值曲线
    plotting.plot_curves([curve.networth])
