# -*- coding: utf-8 -*-
import matplotlib

matplotlib.use('TkAgg')

import matplotlib.pyplot as plt
import pandas as pd
from quantdigger.technicals import aBIAS

# 创建画布
fig, ax = plt.subplots()
# 加载数据
price_data = pd.read_csv("D:\dan\stock\py_stock\quantdigger\data\data\\1DAY\SH\\600022.csv",
                         index_col=0, parse_dates=True)

abias = aBIAS(price_data.close, 6, 'BIAS', 'y', 2)
# 绘制指标
abias.plot(ax)
plt.show()
