# -*- coding: utf-8 -*-
##
# @file tquant_indicator.py
# @brief
# @author wondereamer
# @version 0.1
# @date 2015-12-23
import talib
import matplotlib.finance as finance
import numpy as np
import pandas as pd

from quantdigger.technicals.base import \
    TechnicalBase, ndarray, tech_init
from quantdigger.technicals.techutil import register_tech
from quantdigger.widgets.plotter import Plotter, plot_init



def EMA(DF, N):
    return  pd.Series.ewm(DF, span = N, min_periods = N - 1,adjust=True).mean()

def MA(DF, N):
    return pd.Series.rolling(DF,N).mean()

def SMA(DF,N,M):
    DF = DF.fillna(0)
    z = len(DF)
    var = np.zeros(z)
    var[0] = DF[0]
    for i in range (1,z):
        var[i] = (DF[i] * M + var[i-1] *  (N - M)) / N
    for i in range(z):
        DF[i] =var[i]
    return DF


def ATR(DF,N):
    C = DF['close']
    H = DF['high']
    L = DF['low']
    TR1 = MAX(MAX((H-L),ABS(REF(C,1)- H)),ABS(REF(C,1)-L))
    atr =MA(TR1,N)
    return atr

def HHV(DF,N):
    return pd.Series.rolling(DF,N).max()

def LLV(DF,N):
    return pd.Series.rolling(DF,N).min()

def SUM (DF,N):
    return pd.Series.rolling(DF, N).sum()

def ABS (DF):
    return abs(DF)

def MAX (A,B):
    var = IF(A > B, A, B)
    return var

def MIN  (A,B):
    var = IF ( A < B ,A,B )
    return var

def IF (COND,V1,V2):
    return pd.Series(np.where(COND, V1, V2))

def REF(DF,N):
    var = DF.diff(N)
    var = DF - var
    return var

def STD(DF,N):
    return pd.Series.rolling( DF,N).std()

def MACD(DF,FAST,SLOW,MID):
    EMAFAST =EMA(DF,FAST)
    EMASLOW =EMA(DF,SLOW)
    DIFF = EMAFAST-EMASLOW
    DEA = EMA(DIFF,MID)
    MACD = (DIFF- DEA)*2
    DICT = {'DIFF': DIFF, 'DEA': DEA, 'MACD': MACD}
    VAR = pd.DataFrame(DICT)
    return VAR

def KDJ(DF,N,M1,M2):
    C = DF['close']
    H = DF['high']
    L = DF['low']
    RSV =(C- LLV(L,N))/(HHV(H,N)-LLV(L,N)) * 100
    K = SMA(RSV, M1,1)
    D = SMA(K,M2,1)
    J = 3 * K - 2 * D
    DICT = {'KDJ_K': K, 'KDJ_D': D,'KDJ_J': J}
    VAR = pd.DataFrame(DICT)
    return VAR

def OSC(DF,N,M):#变动速率线
    C=DF['close']
    OS = (C- MA(C,N))*100
    MAOSC = EMA(OS,M)
    DICT = {'OSC': OS,'MAOSC' : MAOSC}
    VAR = pd.DataFrame(DICT)
    return VAR

def BBI(DF,N1,N2,N3,N4):#多空指标
    C=DF['close']
    bbi =(MA(C,N1) + MA(C,N2) + MA(C,N3)+ MA(C,N4))/4
    DICT = {'BBI': bbi}
    VAR = pd.DataFrame(DICT)
    return VAR

def BBIBOLL(DF,N1,N2,N3,N4,N,M):#多空布林线
    bbiboll = BBI(DF,N1,N2,N3,N4)
    UPER = bbiboll + M * STD(bbiboll,N)
    DOWN = bbiboll - M * STD(bbiboll,N)
    DICT = {'BBIBOLL': bbiboll, 'UPER': UPER, 'DOWN': DOWN}
    VAR = pd.DataFrame(DICT)
    return VAR

def PBX(DF,N1,N2,N3,N4,N5,N6):#瀑布线
    C= DF['close']
    PBX1 = (EMA(C,N1) + EMA(C,2*N1) + EMA(C,4*N1) )/3
    PBX2 = (EMA(C,N2) + EMA(C,2*N2) + EMA(C,4*N2) )/3
    PBX3 = (EMA(C,N3) + EMA(C,2*N3) + EMA(C,4*N3) )/3
    PBX4 = (EMA(C,N4) + EMA(C,2*N4) + EMA(C,4*N4) )/3
    PBX5 = (EMA(C,N5) + EMA(C,2*N5) + EMA(C,4*N5) )/3
    PBX6 = (EMA(C,N6) + EMA(C,2*N6) + EMA(C,4*N6) )/3
    DICT = {'PBX1': PBX1, 'PBX2': PBX2,'PBX3': PBX3,'PBX4': PBX4,'PBX5': PBX5,'PBX6': PBX6}
    VAR = pd.DataFrame(DICT)
    return VAR

def BOLL(DF,N):#布林线
    C = DF['close']
    boll = MA(C,N)
    UB   = boll + 2 * STD(C,N)
    LB   = boll - 2 * STD(C,N)
    DICT = {'BOLL': boll, 'UB': UB, 'LB': LB}
    VAR = pd.DataFrame(DICT)
    return VAR

def ROC(DF,N,M):#变动率指标
    C = DF['close']
    roc = 100 * (C - REF(C,N)) / REF(C,N)
    MAROC = MA(roc,M)
    DICT = {'ROC': roc, 'MAROC': MAROC}
    VAR = pd.DataFrame(DICT)
    return VAR

def MTM(DF,N,M):#动量线
    C = DF['close']
    MTM = C - REF(C, N)
    MTMMA= MA(MTM, M)
    DICT = {'MTM': MTM, 'MTMMA': MTMMA}
    VAR = pd.DataFrame(DICT)
    return VAR

def MFI(DF,N):#资金指标
    C = DF['close']
    H = DF['high']
    L = DF['low']
    VOL = DF['vol']
    TYP = (C + H + L) / 3
    V1 = SUM(IF(TYP > REF(TYP, 1), TYP * VOL, 0), N) / SUM(IF(TYP < REF(TYP, 1), TYP * VOL, 0), N)
    mfi = 100 - (100 / (1 + V1))
    DICT = {'MFI': mfi}
    VAR = pd.DataFrame(DICT)
    return VAR

def SKDJ(DF,N,M):
    CLOSE = DF['close']
    LOWV = LLV(DF['low'], N)
    HIGHV =HHV(DF['high'], N)
    RSV = EMA((CLOSE - LOWV) / (HIGHV - LOWV) * 100, M)
    K = EMA(RSV, M)
    D = MA(K, M)
    DICT = {'SKDJ_K': K, 'SKDJ_D': D}
    VAR = pd.DataFrame(DICT)
    return VAR

def WR(DF,N,N1):#威廉指标
    HIGH = DF['high']
    LOW = DF['low']
    CLOSE = DF['close']
    WR1=100 * (HHV(HIGH, N) - CLOSE) / (HHV(HIGH, N) - LLV(LOW, N))
    WR2=100 * (HHV(HIGH, N1) - CLOSE) / (HHV(HIGH, N1) - LLV(LOW, N1))
    DICT = {'WR1': WR1, 'WR2': WR2}
    VAR = pd.DataFrame(DICT)
    return VAR

def BIAS(DF,N1,N2,N3):#乖离率
    CLOSE = DF['close']
    BIAS1=(CLOSE - MA(CLOSE, N1)) / MA(CLOSE, N1) * 100
    BIAS2=(CLOSE - MA(CLOSE, N2)) / MA(CLOSE, N2) * 100
    BIAS3=(CLOSE - MA(CLOSE, N3)) / MA(CLOSE, N3) * 100
    DICT = {'BIAS1': BIAS1, 'BIAS2': BIAS2, 'BIAS3': BIAS3}
    VAR = pd.DataFrame(DICT)
    return VAR

def RSI(DF,N1,N2,N3):#相对强弱指标RSI1:SMA(MAX(CLOSE-LC,0),N1,1)/SMA(ABS(CLOSE-LC),N1,1)*100;
    CLOSE =DF['close']
    LC=REF(CLOSE, 1)
    RSI1=SMA(MAX(CLOSE - LC, 0), N1, 1) / SMA(ABS(CLOSE - LC), N1, 1) * 100
    RSI2=SMA(MAX(CLOSE - LC, 0), N2, 1) / SMA(ABS(CLOSE - LC), N2, 1) * 100
    RSI3=SMA(MAX(CLOSE - LC, 0), N3, 1) / SMA(ABS(CLOSE - LC), N3, 1) * 100
    DICT = {'RSI1': RSI1, 'RSI2': RSI2, 'RSI3': RSI3}
    VAR = pd.DataFrame(DICT)
    return VAR

def ADTM(DF,N,M):#动态买卖气指标
    HIGH = DF['high']
    LOW = DF['low']
    OPEN = DF['open']
    DTM=IF(OPEN <= REF(OPEN, 1), 0, MAX((HIGH - OPEN), (OPEN - REF(OPEN, 1))))
    DBM=IF(OPEN >= REF(OPEN, 1), 0, MAX((OPEN - LOW), (OPEN - REF(OPEN, 1))))
    STM=SUM(DTM, N)
    SBM=SUM(DBM, N)
    ADTM1=IF(STM > SBM, (STM - SBM) / STM, IF( STM == SBM , 0, (STM - SBM) / SBM))
    MAADTM=MA(ADTM1, M)
    DICT = {'ADTM': ADTM1, 'MAADTM': MAADTM}
    VAR = pd.DataFrame(DICT)
    return VAR

def DDI(DF,N,N1,M,M1):#方向标准离差指数
    H = DF['high']
    L = DF['low']
    DMZ=IF((H + L) <= (REF(H, 1) + REF(L, 1)), 0, MAX(ABS(H - REF(H, 1)), ABS(L - REF(L, 1))))
    DMF=IF((H + L) >= (REF(H, 1) + REF(L, 1)), 0, MAX(ABS(H - REF(H, 1)), ABS(L - REF(L, 1))))
    DIZ=SUM(DMZ, N) / (SUM(DMZ, N) + SUM(DMF, N))
    DIF=SUM(DMF, N) / (SUM(DMF, N) + SUM(DMZ, N))
    ddi=DIZ - DIF
    ADDI=SMA(ddi, N1, M)
    AD=MA(ADDI, M1)
    DICT = {'DDI':ddi,'ADDI':ADDI,'AD':AD}
    VAR = pd.DataFrame(DICT)
    return VAR

def VR(DF,N,M):
    CLOSE = DF['close']
    VOL = DF['volume']
    TH = SUM(IF(CLOSE > REF(CLOSE, 1), VOL, 0), N)
    TL = SUM(IF(CLOSE < REF(CLOSE, 1), VOL, 0), N)
    TQ = SUM(IF(CLOSE < REF(CLOSE, 1), VOL, 0), N)
    VR = 100 * (TH * 2 + TQ) / (TL * 2 + TQ)
    MAVR = MA(VR, M)

    DICT = {'VR': VR, 'MAVR': MAVR}
    VAR = pd.DataFrame(DICT)
    return VAR

def FT62876XY(DF):
    H = DF['high']
    L = DF['low']
    O = DF['open']
    C = DF['close']

    AA = (O + H + L + C) / 4
    BB = MA(AA, 3)
    B1 = HHV(AA, 60)
    B2 = LLV(AA, 60)
    B3 = B1 - B2
    B4 = EMA((AA - B2) / B3, 2) * 100
    '''
    A1 = HHV(AA, 15)
    A2 = LLV(AA, 15)
    A3 = A1 - A2
    A4 = EMA((AA - A2) / A3, 2) * 100
    C1 = HHV(AA, 240)
    C2 = LLV(AA, 240)
    C3 = C1 - C2
    C4 = EMA((AA - C2) / C3, 2) * 100
    '''
    Y = (B4 < REF(B4, 1)) & (B4 > 90) & (BB < REF(BB, 1))
    X = (B4 > REF(B4, 1)) & (B4 < 5) & (C > REF(C, 1))
    DICT = {'X': X, 'Y': Y}
    VAR = pd.DataFrame(DICT)
    return VAR

def ZT62808VAR19(DF):
    C = DF['close']

    VAR1 = (C > REF(C, 1)) & (C > REF(C, 2))
    VARD = (C < REF(C, 1)) & (C < REF(C, 2))
    VARE = REF(VARD, 1) & (C >= REF(C, 1)) & (C <= REF(C, 2))
    VARF = REF(VARE, 1) & (C <= REF(C, 1)) & (C >= REF(C, 2))
    VAR10 = REF(VARF, 1) & (C >= REF(C, 1)) & (C <= REF(C, 2))
    VAR11 = REF(VAR10, 1) & (C <= REF(C, 1)) & (C >= REF(C, 2))
    VAR12 = REF(VAR11, 1) & (C >= REF(C, 1)) & (C <= REF(C, 2))
    VAR13 = REF(VAR12, 1) & (C <= REF(C, 1)) & (C >= REF(C, 2))
    VAR14 = REF(VAR13, 1) & (C >= REF(C, 1)) & (C <= REF(C, 2))
    VAR15 = REF(VAR14, 1) & (C <= REF(C, 1)) & (C >= REF(C, 2))
    VAR16 = REF(VAR15, 1) & (C >= REF(C, 1)) & (C <= REF(C, 2))
    VAR17 = REF(VAR16, 1) & (C <= REF(C, 1)) & (C >= REF(C, 2))
    VAR18 = REF(VAR17, 1) & (C >= REF(C, 1)) & (C <= REF(C, 2))
    VAR19 = REF(VARD | VARE | VARF | VAR10 | VAR11 | VAR12 | VAR13 | VAR14 | VAR15 | VAR16 | VAR17 | VAR18, 1) & VAR1

    return VAR19

def ZT62808(DF):
    H = DF['high']
    L = DF['low']
    O = DF['open']
    C = DF['close']

    X = (3 * C + L + O + H) / 6
    DKLINE = (20 * X + 19 * REF(X, 1) + 18 * REF(X, 2) + 17 * REF(X, 3) + 16 * REF(X, 4)
              + 15 * REF(X, 5) + 14 * REF(X, 6) + 13 * REF(X, 7) + 12 * REF(X, 8)
              + 11 * REF(X, 9) + 10 * REF(X, 10) + 9 * REF(X, 11) + 8 * REF(X, 12)
              + 7 * REF(X, 13) + 6 * REF(X, 14) + 5 * REF(X, 15) + 4 * REF(X, 16)
              + 3 * REF(X, 17) + 2 * REF(X, 18) + REF(X, 20)) / 210

    return DKLINE

@register_tech('qZT62808')
class qZT62808(TechnicalBase):
    @tech_init
    def __init__(self, df, name = 'qZT62808', style='y', lw=1):
        super(qZT62808, self).__init__(name)
        self._args = [df]

    def _vector_algo(self, df):
        values = ZT62808(df)
        self.values = ndarray(values)

    def plot(self, widget):
        self.widget = widget
        self.plot_line(self.values, self.style, lw = self.lw)

@register_tech('qZT62808_VAR19')
class qZT62808_VAR19(TechnicalBase):
    @tech_init
    def __init__(self, df, name = 'qZT62808_VAR19', style='y', lw=1):
        super(qZT62808_VAR19, self).__init__(name)
        self._args = [df]

    def _vector_algo(self, df):
        values = ZT62808VAR19(df)
        self.values = ndarray(values)

    def plot(self, widget):
        self.widget = widget
        self.plot_line(self.values, self.style, lw = self.lw)

@register_tech('qFT62876XY')
class qFT62876XY(TechnicalBase):
    @tech_init
    def __init__(self, df, name = 'qFT62876XY',
                 styles=('y', 'b'), lw = 1):
        super(qFT62876XY, self).__init__(name)
        self._args = [df]

    def _rolling_algo(self, df, i):
        var = FT62876XY(df)
        return (ndarray(var['X'])[i], ndarray(var['Y'])[i])

    def _vector_algo(self, df):
        var = FT62876XY(df)
        self.values = {
                    'x': ndarray(var['X']),
                    'y': ndarray(var['Y']),
                }

    def plot(self, widget):
        self.widget = widget
        self.plot_line(self.values['x'], self.styles[0], lw=self.lw)
        self.plot_line(self.values['y'], self.styles[1], lw=self.lw)

@register_tech('qMTM')
class qMTM(TechnicalBase):
    @tech_init
    def __init__(self, df, n, m, name = 'qMTM', style=('y', 'b'), lw=1):
        super(qMTM, self).__init__(name)
        self._args = [df, n, m]

    def _vector_algo(self, df, n, m):
        values = MTM(df, n, m)
        self.values = {
            'mtm': ndarray(values['MTM']),
            'mtmma':ndarray(values['MTMMA'])
        }

    def plot(self, widget):
        self.widget = widget
        self.plot_line(self.values['mtm'], self.style[0], lw = self.lw)
        self.plot_line(self.values['mtmma'], self.style[1], lw=self.lw)

@register_tech('qVR')
class qVR(TechnicalBase):
    @tech_init
    def __init__(self, df, n, m, name = 'qVR', style=('y', 'b'), lw=1):
        super(qVR, self).__init__(name)
        self._args = [df, n, m]

    def _vector_algo(self, df, n, m):
        values = VR(df, n, m)
        self.values = {
            'vr': ndarray(values['VR']),
            'mavr':ndarray(values['MAVR'])
        }

    def plot(self, widget):
        self.widget = widget
        self.plot_line(self.values['vr'], self.style[0], lw = self.lw)
        self.plot_line(self.values['mavr'], self.style[1], lw=self.lw)

@register_tech('qMA')
class qMA(TechnicalBase):
    """ 移动平均线指标。 """
    @tech_init
    def __init__(self, data, n, name='qMA',
                 style='y', lw=1):
        """ data (NumberSeries/np.ndarray/list) """
        super(qMA, self).__init__(name)
        # 必须的函数参数
        self._args = [data, n]

    def _rolling_algo(self, data, n, i):
        """ 逐步运行函数。"""
        ## @todo 因为用了向量化方法，速度降低
        return (ndarray(MA(data, n))[i])

    def _vector_algo(self, data, n):
        """向量化运行, 结果必须赋值给self.values。

        Args:
            data (np.ndarray): 数据
            n (int): 时间窗口大小
        """
        ## @NOTE self.values为保留字段！
        # 绘图和指标基类都会用到self.values
        self.values = ndarray(MA(data, n))

    def plot(self, widget):
        """ 绘图，参数可由UI调整。 """
        self.widget = widget
        self.plot_line(self.values, self.style, lw=self.lw)


@register_tech('qSMA')
class qSMA(TechnicalBase):
    @tech_init
    def __init__(self, close, n, m, name = 'qSMA', style='y', lw=1):
        super(qSMA, self).__init__(name)
        self._args = [close, n, m]

    def _vector_algo(self, close, n, m):
        values = SMA(close, n, m)
        self.values = ndarray(values)

    def plot(self, widget):
        self.widget = widget
        self.plot_line(self.values, self.style, lw = self.lw)

@register_tech('qRSI')
class qRSI(TechnicalBase):
    @tech_init
    def __init__(self, df, n1, n2, n3, name = 'qRSI',
                 styles=('y', 'b', 'g'), lw = 1):
        super(qRSI, self).__init__(name)
        self._args = [df, n1, n2, n3]

    def _rolling_algo(self, df, n1, n2, n3, i):
        var = RSI(df, n1, n2, n3)
        return (ndarray(var['RSI1'])[i], ndarray(var['RSI2'])[i], ndarray(var['RSI3'])[i])

    def _vector_algo(self, df, n1, n2, n3):
        var = RSI(df, n1, n2, n3)
        self.values = {
                    'rsi1': ndarray(var['RSI1']),
                    'rsi2': ndarray(var['RSI2']),
                    'rsi3': ndarray(var['RSI3'])
                }

    def plot(self, widget):
        self.widget = widget
        self.plot_line(self.values['rsi1'], self.styles[0], lw=self.lw)
        self.plot_line(self.values['rsi2'], self.styles[1], lw=self.lw)
        self.plot_line(self.values['rsi3'], self.styles[2], lw=self.lw)

@register_tech('qBIAS')
class qBIAS(TechnicalBase):
    @tech_init
    def __init__(self, df, n1, n2, n3, name = 'qBIAS',
                 styles=('y', 'b', 'g'), lw = 1):
        super(qBIAS, self).__init__(name)
        self._args = [df, n1, n2, n3]

    def _rolling_algo(self, df, n1, n2, n3, i):
        var = BIAS(df, n1, n2, n3)
        return (ndarray(var['BIAS1'])[i], ndarray(var['BIAS2'])[i], ndarray(var['BIAS3'])[i])

    def _vector_algo(self, df, n1, n2, n3):
        var = BIAS(df, n1, n2, n3)
        self.values = {
                    'bias1': ndarray(var['BIAS1']),
                    'bias2': ndarray(var['BIAS2']),
                    'bias3': ndarray(var['BIAS3'])
                }

    def plot(self, widget):
        self.widget = widget
        self.plot_line(self.values['bias1'], self.styles[0], lw=self.lw)
        self.plot_line(self.values['bias2'], self.styles[1], lw=self.lw)
        self.plot_line(self.values['bias3'], self.styles[2], lw=self.lw)

@register_tech('qMACD')
class qMACD(TechnicalBase):
    @tech_init
    def __init__(self, df, fast, slow, mid, name = 'qMACD',
                 styles=('y', 'b', 'g'), lw = 1):
        super(qMACD, self).__init__(name)
        self._args = [df, fast, slow, mid]

    def _rolling_algo(self,df, fast, slow, mid, i):
        var = MACD(df, fast, slow, mid)
        return (ndarray(var['DIFF'])[i], ndarray(var['DEA'])[i], ndarray(var['MACD'])[i])

    def _vector_algo(self, df, fast, slow, mid):
        var = MACD(df, fast, slow, mid)
        self.values = {
                    'diff': ndarray(var['DIFF']),
                    'dea': ndarray(var['DEA']),
                    'macd': ndarray(var['MACD'])
                }

    def plot(self, widget):
        self.widget = widget
        self.plot_line(self.values['diff'], self.styles[0], lw=self.lw)
        self.plot_line(self.values['dea'], self.styles[1], lw=self.lw)
        self.plot_line(self.values['macd'], self.styles[2], lw=self.lw)

@register_tech('qBOLL')
class qBOLL(TechnicalBase):
    """ 布林带指标。 """
    @tech_init
    def __init__(self, data, n, name='qBOLL',
                 styles=('y', 'b', 'g'), lw=1):
        super(qBOLL, self).__init__(name)
        ### @TODO 只有在逐步运算中需给self.values先赋值,
        ## 去掉逐步运算后删除
        #self.values = OrderedDict([
                #('upper', []),
                #('middler', []),
                #('lower', [])
                #])
        self._args = [data, n]

    def _rolling_algo(self, data, n, i):
        """ 逐步运行函数。"""
        var = BOLL(data, n)
        return (ndarray(var['UB'])[i], ndarray(var['BOLL'])[i], ndarray(var['LB'])[i])

    def _vector_algo(self, data, n):
        """向量化运行"""

        var = BOLL(data, n)
        self.values = {
                'upper': ndarray(var['UB']),
                'middler': ndarray(var['BOLL']),
                'lower': ndarray(var['LB'])
                }

    def plot(self, widget):
        """ 绘图，参数可由UI调整。 """
        self.widget = widget
        self.plot_line(self.values['upper'], self.styles[0], lw=self.lw)
        self.plot_line(self.values['middler'], self.styles[1], lw=self.lw)
        self.plot_line(self.values['lower'], self.styles[2], lw=self.lw)

class Volume(Plotter):
    ## @TODO 改成技术指标
    """ 柱状图。 """
    @plot_init
    def __init__(self, open, close, volume, name='volume',
                 colorup='r', colordown='b', width=1):
        super(Volume, self).__init__(name, None)
        self.values = ndarray(volume)

    def plot(self, widget):
        self.widget = widget
        finance.volume_overlay(widget, self.open, self.close, self.volume,
                               self.colorup, self.colordown, self.width)

## @TODO merge Line and LineWithX and move to plotting module
class Line(Plotter):
    """ 画线 """
    @plot_init
    def __init__(self, ydata, name='Line', style='black', lw=1):
        super(Line, self).__init__(name, None)
        self.values = ydata

    def plot(self, widget):
        self.widget = widget
        self.plot_line(self.values, self.style, lw=self.lw)


class LineWithX(Plotter):
    """ 画线 """
    @plot_init
    def __init__(self, xdata, ydata, name='LineWithX', style='black', lw=1, ms=1):
        super(LineWithX, self).__init__(name, None)
        self.values = ydata
        self._xdata = xdata

    def plot(self, widget):
        self.widget = widget
        self.plot_line(self.xdata, self.values, self.style, lw=self.lw, ms=self.ms)

# 'qBOLL', 'qCCI', 'qBIAS','qRSI'
__all__ = ['qMA', 'qBOLL', 'qSMA', 'qRSI','qBIAS', 'qMACD',
           'qFT62876XY', 'qZT62808', 'qZT62808_VAR19', 'Volume',
           'qMTM', 'qVR', 'Line', 'LineWithX']
