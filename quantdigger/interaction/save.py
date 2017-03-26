import os
import pandas as pd

def save_candicates(root_path, strategy, date, pcontract, candicates):
    strpcon = str(pcontract).upper()
    contract, period = tuple(strpcon.split('-'))
    code, exch = tuple(contract.split('.'))
    period = period.replace('.', '')
    dir = os.path.join(root_path, period, strategy, date._date_repr)
    if(os.path.exists(dir) != True):
        os.makedirs(dir)
    fname = os.path.join(dir, exch + ".csv")
    df = pd.DataFrame(candicates)
    df.to_csv(fname)