import yfinance as yf
import pandas as pd
import numpy as np
import re
from datetime import datetime
#from urllib.error import HTTPError


class yfinance_ticker_reader:
    
    '''
    Class to read a selected stock ticker from yahoo finance API into a pandas dataframe or summary dictionary

    1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo

    period : str
            Valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
            Either Use period parameter or use start and end
        interval : str
            Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
            Intraday data cannot extend last 60 days
        start: str
            Download start date string (YYYY-MM-DD) or _datetime.
            Default is 1900-01-01
        end: str
            Download end date string (YYYY-MM-DD) or _datetime.
            Default is now
    '''

    def __init__(self, ticker = None): 
        
        #instantiate the class
        
        self.ticker = ticker

    def check_periods(self, per_string):
        '''
        Check if a correct period string has been submitted

        Returns True or False
        '''
        per_list = ['1d','5d','1mo','3mo','6mo','1y','2y','5y','10y','ytd','max']

        return per_string in per_list 
    
    def check_intervals(self, int_string):
        '''
        Check if a correct interval string has been submitted

        Returns True or False
        '''
        int_list = ['1m','2m','5m','15m','30m','60m','90m','1h','1d','5d','1wk','1mo','3mo']

        return int_string in int_list 

    def date_string_format(self, date_string):

        if re.match("(\d{4})-(\d{2})-(\d{2})", date_string):

            try:
                datetime_object = datetime.strptime(date_string, '%Y-%m-%d')
                return {'code': 400}
            except Exception as ex:
                print(type(ex).__name__)
                print(type(ex).args)
                return {'code': 201}
        else:
            return {'code': 203}

    def read_ticker_pandas_start_end(self, start = None, end = None, interval = None,period = None, progress = False):
        """
        Returns a dictionary of status code  + yf.Ticker('TICKER') OHLC pandas dataframe

        Args:
        REQUIRED
        INSTANTIATED AT CLASS DEFINITION
        self.ticker : Default = None. Ticker ID associated with a stock/index/crypto/asset/etf to be retrieved using the yfinance API
        start = (string) start extraction period in yyyy-mm-dd format only, Default = None.
        end  = (string) end extraction period in yyyy-mm-dd format only, Default = None.
        interval = (string) datafrequency timeframe, must be in the following list: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo, Default = None.
        progress = (Boolean) , print download progress to terminal, Default = False.
        Returns:
        Dictionary
        'code': 400 = good, 201 = error raised - supplied ticker not recognised, 202 - incorrect date string format, 203 - incorrect date i.e 32 days in month. 204 - incorrect yahoo finance interval supplied
        'ticker stats' : yf.ticker stats dictionay. Returns None if error raised.
        
        Preconditions:
        Supplied ticker is a string.         
        Start and end dates submitted

        Raises:
        HTTPError: if ticker string is not recognised by yahoo fiunance API.
        ValueError: if incorrecte date string format, or date validity submitted
        """

        if not self.check_intervals(interval):
            print("Incorrect yahoo finance interval submitted")
            return {'code': 204, 'ticker ohlc':None}

        start_code = self.date_string_format(start)
        
        if start_code['code'] != 400:
            return {'code': start_code['code'], 'ticker ohlc':None}

        end_code = self.date_string_format(start)
        if end_code['code'] != 400:
            return {'code': end_code['code'], 'ticker ohlc':None}
        
        try:

            return {'code': 400, 'ticker ohlc':yf.download(self.ticker, start=start,end = end,interval = interval,progress=progress)}
        
        except Exception as ex:
            if type(ex).__name__ == 'HTTPError':
                print(type(ex).__name__)
                print("Likely an incorrect Ticker String Submitted")
            else:
                print(type(ex).__name__)
                print(type(ex).args)
            
            return {'code': 201, 'ticker ohlc':None}   
            
    def read_ticker_pandas_period(self,period = None, interval = None, progress = False):
        """
        Returns a dictionary of status code  + yf.Ticker('TICKER') OHLC pandas dataframe

        Args:
        REQUIRED
        INSTANTIATED AT CLASS DEFINITION
        self.ticker : Default = None. Ticker ID associated with a stock/index/crypto/asset/etf to be retrieved using the yfinance API
        period = (string) extraction period, must be in the following list: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max, Default = None.
        interval = (string) datafrequency timeframe, must be in the following list: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo, Default = None.
        progress = (Boolean) , print download progress to terminal, Default = False.
        Returns:
        Dictionary
        'code': 400 = good, 201 = error raised - supplied ticker not recognised, 204 = error raised, incorrect yahoo finance period supplied
        'ticker stats' : yf.ticker stats dictionay. Returns None if error raised.
        
        Preconditions:
        Supplied ticker is a string.         

        Raises:
        HTTPError: if ticker string is not recognised by yahoo fiunance API.
        """

        if not self.check_periods(period):
            print("Incorrect yahoo finance period submitted")
            return {'code': 204, 'ticker ohlc':None}
        
        if not self.check_intervals(interval):
            print("Incorrect yahoo finance interval submitted")
            return {'code': 204, 'ticker ohlc':None}

        try:

            return {'code': 400, 'ticker ohlc':yf.download(self.ticker,period = period,interval = interval, progress=progress)}
        
        except Exception as ex:
            if type(ex).__name__ == 'HTTPError':
                print(type(ex).__name__)
                print("Likely an incorrect Ticker String Submitted")
            else:
                print(type(ex).__name__)
                print(type(ex).args)
            
            return {'code': 201, 'ticker ohlc':None}   
    

    def ticker_info(self):
        """
        Returns a dictionary of stastus code  + stock stats yf.Ticker('TICKER').info

        Args:
        REQUIRED
        self.ticker : Default = None. Ticker ID associated with a stock/index/crypto/asset/etf to be retrieved using the yfinance API

        Returns:
        Dictionary
        'code': 400 = good, 201 = error raised - supplied ticker not recognised
        'ticker stats' : yf.ticker stats dictionay. Returns None if error raised.
        
        Preconditions:
        Supplied ticker is a string.         

        Raises:
        HTTPError: if ticker string is not recognised by yahoo fiunance API.

        """

        dis = yf.Ticker(self.ticker)

        try:
            
            return {'code': 400, 'ticker stats':dis.info}
        
        except Exception as ex:
                if type(ex).__name__ == 'HTTPError':
                    print(type(ex).__name__)
                    print("Likely an incorrect Ticker String Submitted")
                else:
                    print(type(ex).__name__)
                    print(type(ex).args)
                return {'code': 201, 'ticker stats':None}

                
