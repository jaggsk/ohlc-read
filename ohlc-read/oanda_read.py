# -*- coding: utf-8 -*-
"""
Created on Mon Apr  3 08:18:53 2023

@author: jaggs
"""


###########################################
#import libraries
import pandas as pd
from oandapyV20 import API 
import oandapyV20.endpoints.instruments as instruments
import os
import time
import datetime
#import requests

##########################################
#import account password, ID number, api key
#USER REQUIRED TO STORE IN ENVIRONMENT VARIABLES OR SIMILAR
account_pwd = os.environ.get('OANDA_API_PASSWORD')
account_id = os.environ.get('OANDA_ACCOUNT_ID')
api_key = os.environ.get('OANDA_API_KEY')

#strip apostrophes from string
api_key = api_key.replace("'", "")


#print(os.environ.get('OANDA_API_KEY'))
#print(os.environ.get('OANDA_ACCOUNT_ID'))
#print(os.environ.get('OANDA_API_PASSWORD'))

class OandaRecentCandles():
    """
    Class to download last n candles of price data from a specified instrument using the Oanda API
    KJAGGS Apr 2023

    Keyword Args:
    base currency: e.g USD - Required
    quote currency: e,g EUR - Required
    Time Interval e.g H4 - refers to granularity in OandaAPI
    Price Candles options 'M' or 'MBA' - 'mid', 'bid','ask'

    ***NOTE*** TIME SETTINGS ARE UTC, REF ZERO HOURS

    Functions
    time_interval_id -> returns dictionary of time intervals untis to skip based upon the key value

    time_first_return -> determines first entry date for a coin held on the binance database. Use 1 day timeframe as default

    datetime_to_timestamp -> convert a datetime string to a timestamp number in microsseconds

    timestamp_to_datetime -> converts timestamp string, in  microseconds, to datetime string

    datetime_iterate -> using start date download the max kline candles. Set start date to next candle and repeat.
    Concatenate datafrmame to master until start date is greater than end date (today)

    """
    def __init__(self,
            base_currency = None,
            quote_currency = None,
            time_interval = None,
            MBA_candles = False,
            no_candles = None, 
            #price_candles = None,
            complete_only = True    
            ):

            #set variables to  class self
            self.base_currency = base_currency
            self.quote_currency = quote_currency
            self.time_interval = time_interval
            self.MBA_candles = MBA_candles
            self.no_candles = no_candles
            #self.price_candles = price_candles
            self.complete_only = complete_only

            #create trading pair from base and quote currency
            self.currency_pair = str( self.quote_currency + '_' + self.base_currency)   

            if self.MBA_candles == False:
                self.price_candles = "M"
            else:
                self.price_candles = "MBA"

            #params is the json data request parameter dictionary , start and end period + time interval specified
            self.params = {
                "price" :str(self.price_candles),
                "count": self.no_candles,
                "alignmentTimezone" : 'UTC',
                'dailyAlignment': str(0),
                "granularity": str(self.time_interval)
                }

            granularity_list = oanda_granularity_list()

            #connect to oanda API      
            self.client = API(api_key)


    def get_candles(self):

        r=instruments.InstrumentsCandles(instrument=self.currency_pair,params=self.params)

        data = self.client.request(r)
        #print(data)
            
        if self.MBA_candles == False:
            results= [{"Time":x['time'],"Open":float(x['mid']['o']),"High":float(x['mid']['h']),
                    "Low":float(x['mid']['l']),"Close":float(x['mid']['c']),
                    "Volume":float(x['volume']),"Complete":x['complete']} for x in data['candles']]
        else:
            results= [{"Time":x['time'],"Open":float(x['mid']['o']),"High":float(x['mid']['h']),
                    "Low":float(x['mid']['l']),"Close":float(x['mid']['c']),
                    "Open Bid":float(x['bid']['o']),"High Bid":float(x['bid']['h']),
                    "Low Bid":float(x['bid']['l']),"Close Bid":float(x['bid']['c']),
                    "Open Ask":float(x['ask']['o']),"High Ask":float(x['ask']['h']),
                    "Low Ask":float(x['ask']['l']),"Close Ask":float(x['ask']['c']),
                    "Volume":float(x['volume']),"Complete":x['complete']} for x in data['candles']]

        self.df = pd.DataFrame(results)
        


        if self.complete_only == True:
            self.df = self.df[self.df.Complete == True]

        self.df['Time'] = pd.to_datetime(self.df.Time, format="%Y-%m-%dT%H:%M:%S.%fZ")
        self.df.set_index('Time', inplace=True)

        return self.df
            

class OandaHistoricCandles():
    
    """
    Class to download database of price data from a specified instrument using the Oanda API
    KJAGGS Apr 2023

    Keyword Args:
    base currency: e.g USD - Required
    quote currency: e,g EUR - Required
    Time Interval e.g H4 - refers to granularity in OandaAPI
    Price Candles options 'M' or 'MBA' - 'mid', 'bid','ask'
    Start Date - Required, format "YYYY-MM-DD"
    End Date - , format "YYYY-MM-DD". if None then read up to datetime now()

    ***NOTE*** TIME SETTINGS ARE UTC, REF ZERO HOURS

    """
    
    
    def __init__(self,
        base_currency = None,
        quote_currency = None,
        time_interval = None,
        MBA_candles = False,
        start_date = None,
        end_date = None,
        complete_only = True        
        ):

        #set variables to  class self
        self.base_currency = base_currency
        self.quote_currency = quote_currency
        self.time_interval = time_interval
        self.MBA_candles = MBA_candles
        self.start_date = start_date
        self.end_date = end_date
        self.complete_only = complete_only
        
        #create trading pair from base and quote currency
        self.currency_pair = str( self.quote_currency + '_' + self.base_currency)
        
        ##################################################
        #start and end dates are converted to unix timestamp format.
        self.start_date = self.unix_timestamp(self.start_date)
    
        if self.MBA_candles == False:
                self.price_candles = "M"
        else:
            self.price_candles = "MBA"
        
        #determine if an end date has been supplied
        if self.end_date == None:
            #if no end date specified then data will read until the current time using datetime.now()
            self.end_date = datetime.datetime.strptime(str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '%Y-%m-%d %H:%M:%S').timestamp()
        else:
            self.end_date = self.unix_timestamp(self.end_date)
        
        #number of candles to read in each data request package
        self.max_no_candles = 999
        
        #number of seconds between each data time interval is caclulated
        #e.g. S5 = 5 seconds = 5
        #1H = 1 hour = 3600 seconds = 3600
        #this value is used to calculate the start time of the next daat request. n + 1
        self.granularity_dict = self.time_interval_id()

        #connect to oanda API      
        self.client = API(api_key)

        
    def extract_candles(self):
        
        #self.i is used to iterate over a specfied number of candles at the reqyuested time interval.
        #i is always the start/first candle in the data request
        self.i = self.start_date

        #iterate step size in seconds - retrieved using granularity as the dictionary key
        self.step_size = self.granularity_dict[self.time_interval]
        #request step size in unix timestamp format
        self.step_unix = self.max_no_candles * self.step_size
        #end request date/time referenced to start (i)
        self.step_interval = self.i + self.step_unix
        
        if self.MBA_candles == False:
            self.price_candles = "M"
        else:
            self.price_candles = "MBA"

        #params is the json data request parameter dictionary , start and end period + time interval specified
        self.params = {
          "from": str(self.i),
          "to": str(self.step_interval),
          "price" :str(self.price_candles),
          #"count": 1001,
          "alignmentTimezone" : 'UTC',
          'dailyAlignment': str(0),
          "granularity": str(self.time_interval)
        }
        
        #create empty host dataframe
        self.dataset=pd.DataFrame()
        
        while self.i < self.end_date:
            
            self.end_step = self.i + self.step_unix
            
            if self.end_step >= self.end_date:
                self.end_step = self.end_date
            
            #print(datetime.datetime.utcfromtimestamp(self.i).strftime('%Y-%m-%d %H:%M:%S'))
            #print(datetime.datetime.utcfromtimestamp(self.end_step).strftime('%Y-%m-%d %H:%M:%S'))

            #update the params dictionary with the latest start and end time periods
            self.params["from"] = str(self.i)
            self.params["to"] = str(self.end_step)
            
         
            r=instruments.InstrumentsCandles(instrument=self.currency_pair,params=self.params)

            data = self.client.request(r)
            #print(data)
            
            if self.MBA_candles == False:
                results= [{"Time":x['time'],"Open":float(x['mid']['o']),"High":float(x['mid']['h']),
                        "Low":float(x['mid']['l']),"Close":float(x['mid']['c']),
                        "Volume":float(x['volume']),"Complete":x['complete']} for x in data['candles']]
            else:
                results= [{"Time":x['time'],"Open":float(x['mid']['o']),"High":float(x['mid']['h']),
                        "Low":float(x['mid']['l']),"Close":float(x['mid']['c']),
                        "Open Bid":float(x['bid']['o']),"High Bid":float(x['bid']['h']),
                        "Low Bid":float(x['bid']['l']),"Close Bid":float(x['bid']['c']),
                        "Open Ask":float(x['ask']['o']),"High Ask":float(x['ask']['h']),
                        "Low Ask":float(x['ask']['l']),"Close Ask":float(x['ask']['c']),
                        "Volume":float(x['volume']),"Complete":x['complete']} for x in data['candles']]

            self.df = pd.DataFrame(results)

            
            if self.dataset.empty: 
                self.dataset=self.df.copy()
            else: 
                self.dataset= pd.concat([self.dataset, self.df])
             
            #self.i = self.step_size + self.end_step
            self.i = self.end_step
        
        if self.complete_only == True:
            self.dataset = self.dataset[self.dataset.Complete == True]

        self.dataset['Time'] = pd.to_datetime(self.dataset.Time, format="%Y-%m-%dT%H:%M:%S.%fZ")
        self.dataset.set_index('Time', inplace=True)

        return self.dataset
    
    def unix_timestamp(self,time_data):
        self.datetime_format_string = '%Y-%m-%d'
        return int(datetime.datetime.strptime(str(time_data), self.datetime_format_string).timestamp())
    
    def time_interval_id(self):
        self.time_interval_dict = {'M':3000000,'W':604800,'D':86400,
                                   'H12':43200,'H8':28800,'H6':21600,'H4':14400, 'H3':10800, 'H2':7200, 'H1':3600,
                                   'M30':1800,'M15':900,'M10':600,'M5':300,'M4':240,'M2':120,'M1':60,
                                   'S30':30,'S15':15,'S10':10,'S5':5}
        return self.time_interval_dict
    
    def candle_check(self):
        #To Complete
        return None

def oanda_granularity_list():
    '''
    ()->(list of strings)
    Return a list of all granularity strings compatible with the Oanda API
    '''
    return  ['M','W','D','H12','H8','H6','H4','H3','H2','H1',
                'M30','M15','M10','M5','M4','M2','M1','S30','S15','S10','S5'] 


