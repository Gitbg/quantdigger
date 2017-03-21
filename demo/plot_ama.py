# -*- coding: utf-8 -*-
import matplotlib

matplotlib.use('TkAgg')

import matplotlib.pyplot as plt
import pandas as pd
from quantdigger.technicals import aMA, qMA

# 创建画布
fig, ax = plt.subplots()
# 加载数据
price_data = pd.read_csv("./work/IF000.SHFE-10.Minute.csv",
                         index_col=0, parse_dates=True)

# 创建平均线
ama10 = aMA(price_data.close, 10, 'MA10', 'y', 2)
ama60 = aMA(price_data.close, 60, 'MA60', 'b', 2)
# 绘制指标
ama10.plot(ax)
ama60.plot(ax)
plt.show()
