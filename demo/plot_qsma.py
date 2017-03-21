# -*- coding: utf-8 -*-
import matplotlib

matplotlib.use('TkAgg')

import matplotlib.pyplot as plt
import pandas as pd
from quantdigger.technicals import qSMA

# 创建画布
fig, ax = plt.subplots()
# 加载数据
price_data = pd.read_csv("./work/IF000.SHFE-10.Minute.csv",
                         index_col=0, parse_dates=True)

# 创建平均线
qsma10 = qSMA(price_data.close, 10, 1, 'SMA10', 'y', 2)
qsma20 = qSMA(price_data.close, 20, 1, 'SMA20', 'b', 2)
# 绘制指标
qsma10.plot(ax)
qsma20.plot(ax)
plt.show()
