# -*- coding: utf-8 -*-
"""
Created on Sat Mar 25 09:19:52 2023

@author: jaggs
"""

import pandas as pd
import fxcmpy

login = 'D25940464'
password = 'Mako7'
fxcm_api = '52d7618c60e466a2cabb1bc5470845c09c3220c0'
api = fxcmpy.fxcmpy(access_token = fxcm_api,log_level = 'error')


def get_fxcm_tickers():
    
    print(api.get_instruments())

def get_fxcm_candles(ticker = 'EUR/USD', tstart = '2000-01-01', tend = '2023-03-24'):
    
    '''
    Function to read historical bid/ask data from fxcm using python api
    Use get_fxcm tickers to see list of assets/currencies available
    period must be one of ['m1', 'm5', 'm15', 'm30', 'H1', 'H2', 'H3', 'H4', 'H6', 'H8', 'D1', 'W1', 'M1']
    can also specify number of candles , number = 10000
    K JAGGS 25/03/2023
    '''
    
    print(api.get_candles(ticker, period = 'm1',start = '2010-01-01', end = '2010-01-10'))
    
    
get_fxcm_candles()

#get_fxcm_tickers()

api.close()
