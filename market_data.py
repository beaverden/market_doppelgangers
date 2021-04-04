import ib_insync
from datetime import datetime
import pandas as pd

"""
    This file just pulls the SPY data from IB, does a few conversions in the dataframe
    and drops it to market_returns.csv
    Nothing to see here
"""

ib = ib_insync.IB()
ib.connect('127.0.0.1', port=7497, clientId=0, readonly=True)
print('Connected: %d, ServerVersion: %s' % (ib.isConnected(), ib.client.serverVersion()))

market = ib_insync.Stock('SPY', 'SMART', 'USD')

market_data = ib.reqHistoricalData(market,
                           endDateTime=datetime.now(),
                           barSizeSetting='1 hour',
                           durationStr='3 Y',
                           whatToShow='TRADES',
                           useRTH=True,
                           timeout=0)
data1 = ib_insync.util.df(market_data)

data1.date = pd.to_datetime(data1.date)
data1.date = pd.to_datetime(data1.date, format='%Y-%m-%d %H:%M:%S')
data1.rename(columns={'barCount': 'openinterest', 'date': 'datetime'}, inplace=True)
data1.drop(columns=['average'], inplace=True)
data1.to_csv(path_or_buf='market_returns.csv', index=False)
