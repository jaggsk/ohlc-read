# -*- coding: utf-8 -*-
"""
Created on Sat Mar 18 00:47:40 2023

@author: jaggs
"""

import pandas as pd
from alpha_vantage.timeseries import TimeSeries 
from alpha_vantage.foreignexchange import ForeignExchange

av_api = 'UNQ7SFDJYUGOMW3I'

##ts = TimeSeries(key=av_api,output_format='pandas')

#fx = ForeignExchange(key = av_api, output_format = 'pandas')
#eurusd = fx.get_currency_exchange_daily("USD","EUR", outputsize = 'full')[0]
#print(eurusd)

#eurusd = fx.get_currency_exchange_intraday("USD","EUR", interval = '60min',outputsize = 'compact')[0]
#print(eurusd)

def alpha_vantage_fx_ohlc(base_currency = 'USD', exchange_currency = 'EUR',output_id = 'full'):
    '''
    Function to return an ohlc pandas dataframe for a slected fx currency pair
    base_currency = in initial for the base curreny - x axis
    exchange_currency = in initial for the exchange curreny - y axis
    output_id = full or compact
    PRECONDTITION: ticker and output_id have been correctly defined by user
    KJAGGS MAR 2023
    '''
    fx = ForeignExchange(key = av_api, output_format = 'pandas')
    #if output_id == 'full':
    av_df = fx.get_currency_exchange_daily(base_currency, exchange_currency, outputsize = output_id)[0]
    #else:
    #av_df = ts.get_daily(ticker, outputsize = output_id)[0]
        
    return av_df

def alpha_vantage_ts_ohlc(ticker = 'AAPL', output_id = 'full'):
    '''
    Function to return an ohlc pandas dataframe for a slected stock ticker
    ticker = ticker initials fpr slected stock
    output_id = full or compact
    PRECONDTITION: ticker and output_id have been correctly defined by user
    KJAGGS MAR 2023
    '''
    ts = TimeSeries(key=av_api,output_format='pandas')
    if output_id == 'full':
        av_df = ts.get_daily(ticker, outputsize = output_id)[0]
    else:
        av_df = ts.get_daily(ticker, outputsize = output_id)[0]
        
    return av_df

#df = alpha_vantage_ts_ohlc(ticker = 'AAPL', output_id = 'compact')
df = alpha_vantage_fx_ohlc(base_currency = 'USD', exchange_currency = 'EUR',output_id = 'compact')
print(df)