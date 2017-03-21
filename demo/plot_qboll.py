# -*- coding: utf-8 -*-
import matplotlib

matplotlib.use('TkAgg')

import matplotlib.pyplot as plt
import pandas as pd
from quantdigger.technicals import qBOLL

# 创建画布
fig, ax = plt.subplots()
# 加载数据
price_data = pd.read_csv("D:\dan\stock\py_stock\quantdigger\data\data\\1DAY\SH\\600019.csv",
                         index_col=0, parse_dates=True)

qboll = qBOLL(price_data, 14, 'BOLL')
# 绘制指标
qboll.plot(ax)
plt.show()
