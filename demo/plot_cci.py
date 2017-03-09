# -*- coding: utf-8 -*-
import matplotlib

matplotlib.use('TkAgg')

import matplotlib.pyplot as plt
import pandas as pd
from quantdigger.technicals import CCI

# 创建画布
fig, ax = plt.subplots()
# 加载数据
price_data = pd.read_csv("D:\dan\stock\py_stock\quantdigger\data\data\\1DAY\SH\\600019.csv",
                         index_col=0, parse_dates=True)

cci = CCI(price_data.high, price_data.low, price_data.close, 14, 'CCI', 'y', 2)
# 绘制指标
cci.plot(ax)
plt.show()
