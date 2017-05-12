# -*- coding: utf-8 -*-
from quantdigger.technicals.base import \
    TechnicalBase, ndarray, tech_init
from quantdigger.technicals.techutil import register_tech
from quantdigger.widgets.plotter import Plotter, plot_init
from funcat.api import (
    OPEN, HIGH, LOW, CLOSE, VOLUME, VOL,
    ABS, MAX, HHV, LLV,
    REF, IF, SUM, STD,
    MA, EMA, SMA,
)
from funcat.time_series import NumericSeries

@register_tech('fMA')
class fMA(TechnicalBase):
    """ 移动平均线指标。 """
    @tech_init
    def __init__(self, data, n, name='fMA',
                 style='y', lw=1):
        """ data (NumberSeries/np.ndarray/list) """
        super(fMA, self).__init__(name)
        # 必须的函数参数
        self._args = [NumericSeries(ndarray(data)), n]

    def _rolling_algo(self, data, n, i):
        """ 逐步运行函数。"""
        ## @todo 因为用了向量化方法，速度降低
        return (MA(data, n)[i], )

    def _vector_algo(self, data, n):
        """向量化运行, 结果必须赋值给self.values。

        Args:
            data (np.ndarray): 数据
            n (int): 时间窗口大小
        """
        ## @NOTE self.values为保留字段！
        # 绘图和指标基类都会用到self.values
        self.values = MA(data, n).series

    def plot(self, widget):
        """ 绘图，参数可由UI调整。 """
        self.widget = widget
        self.plot_line(self.values, self.style, lw=self.lw)

__all__ = ['fMA']
