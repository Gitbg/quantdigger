# -*- coding: utf-8 -*-
import matplotlib

matplotlib.use('TkAgg')

import matplotlib.pyplot as plt
import pandas as pd
from quantdigger.technicals import qBIAS

# 创建画布
fig, ax = plt.subplots()
# 加载数据
price_data = pd.read_csv("./work/IF000.SHFE-10.Minute.csv",
                         index_col=0, parse_dates=True)

# 创建平均线
qbias = qBIAS(price_data, 6, 12, 24, 'BIAS')

# 绘制指标
qbias.plot(ax)
plt.show()
