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

class OandaHistoricCandles():
    
    """
    Class to download entire database of price data from a specified forex using the Oanda API
    KJAGGS Apr 2023

    binance_connect_klines_all class

    Keyword Args:
    base currency: e.g USD
    quote currency: e,g EUR
    Final string = "EUR_USD"

    Funxtions
    time_interval_id -> returns dictionary of time intervals untis to skip based upon the key value

    time_first_return -> determines first entry date for a coin held on the binance database. Use 1 day timeframe as default

    datetime_to_timestamp -> convert a datetime string to a timestamp number in microsseconds

    timestamp_to_datetime -> converts timestamp string, in  microseconds, to datetime string

    datetime_iterate -> using start date down;poad the max 500kloine candles. Set start date to next candle and repeat.
    Concatenate datafrmame to master until start date is greater than end date (today)

    """
    
    
    def __init__(self,
        base_currency = "USD",
        quote_currency = "EUR",
        time_interval = "H4",
        start_date = None,
        end_date = None        
        ):

        #set variables to  class self
        self.base_currency = base_currency
        self.quote_currency = quote_currency
        self.time_interval = time_interval
        self.start_date = start_date
        self.end_date = end_date
        
        self.currency_pair = str( self.quote_currency + '_' + self.base_currency)
        
        ##################################################
        #start and end dates are converted to unix timestamp format.
        self.start_date = self.unix_timestamp(self.start_date)
        #print(self.start_date)
        
        #determine if an end date has been supplied
        if self.end_date == None:
            #if no end date specified then data will read until the current time using datetime.now()
            self.end_date = datetime.datetime.strptime(str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')), '%Y-%m-%d %H:%M:%S').timestamp()
        
        #number of candles to read in each data request package
        self.max_no_candles = 999
        
        #number of seconds between each data time interval is caclulated
        #e.g. S5 = 5 seconds = 5
        #1H = 1 hour = 3600 seconds = 3600
        #this value is used to calculate the start time of the next daat request. n + 1
        self.granularity_dict = self.time_interval_id()
              
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
        
        #params is the json data request parameter dictionary , start and end period + time interval specified
        self.params = {
          "from": str(self.i),
          "to": str(self.step_interval),
          #"count": 1001,
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
            #r=instruments.InstrumentsCandles(instrument="GBP_USD",params=self.params)

            data = self.client.request(r)
            results= [{"Time":x['time'],"Open":float(x['mid']['o']),"High":float(x['mid']['h']),
                       "Low":float(x['mid']['l']),"Close":float(x['mid']['c']),
                       "Volume":float(x['volume']),"Complete":x['complete']} for x in data['candles']]
            
            self.df = pd.DataFrame(results)

            
            if self.dataset.empty: self.dataset=self.df.copy()
            else: self.dataset= pd.concat([self.dataset, self.df])
             
            self.i = self.step_size + self.end_step
        
        self.dataset['Time'] = pd.to_datetime(self.dataset.Time, format="%Y-%m-%dT%H:%M:%S.%fZ")
        
        #tz1 = pytz.timezone("UTC")
        #tz2 = pytz.timezone("Europe/London")
        #tz1.localize(self.dataset['Time'])
        #self.dataset['Time New'] = self.dataset['Time'].dt.tz_localize('UTC').dt.tz_convert("Europe/London")
        #self.dataset.index = self.dataset.index.astimezone(tz2)
        #dt = dt.strftime("%Y-%m-%d %H:%M:%S")
        return self.dataset
    
    def unix_timestamp(self,time_data):
    
        self.datetime_format_string = '%Y-%m-%d'
        #int(unix_timestamp(time_start).timestamp())
        return int(datetime.datetime.strptime(str(time_data), self.datetime_format_string).timestamp())
    
    def time_interval_id(self):
        self.time_interval_dict = {'W1':604800,'D1':86400,'H4':14400, 'H1':3600,'M30':1800,'M15':900,'M5':300,'M1':60}
        return self.time_interval_dict
    
if __name__ == "__main__":
    
    ohc = OandaHistoricCandles(time_interval = "M5",base_currency = "USD",quote_currency = "GBP",start_date ='2000-01-01')
    df_out = ohc.extract_candles()
    print(df_out.head(20))
    df_out.to_csv('GBPUSD_M5_OANDA.csv')
