# -*- coding: utf-8 -*-
import matplotlib

matplotlib.use('TkAgg')

import matplotlib.pyplot as plt
import pandas as pd
from quantdigger.technicals import qMACD

# 创建画布
fig, ax = plt.subplots()
# 加载数据
price_data = pd.read_csv("./work/IF000.SHFE-10.Minute.csv",
                         index_col=0, parse_dates=True)

# 创建平均线
qmacd = qMACD(price_data['close'], 12, 26, 9, 'qMACD')

# 绘制指标
qmacd.plot(ax)
plt.show()
