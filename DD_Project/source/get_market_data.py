import pandas as pd
import pickle
from source.datamodels import Company
import logging

def get_market_data(_ticker, _start_time_unix, _end_time_unix, _output_location):
    '''
    Extracts market data for a given interval for a certain ticker. Stores as a csv, if needed later.
    Arguments:
        ticker: a string
        start_time: an integer
        end_time: an integer
        file_location: where the file will be stored
    Returns:
        a dataframe of market data
    '''
    
    # Download data
    url = f'https://query1.finance.yahoo.com/v7/finance/download/{_ticker}?period1={_start_time_unix}&period2={_end_time_unix}&interval=1d&events=history&includeAdjustedClose=true'
    market_timeseries = pd.read_csv(url)

    market_timeseries = market_timeseries.set_index('Date')
    market_timeseries.index = market_timeseries.index.astype('datetime64[ns]')

    trading_days = market_timeseries.index

    # Store and return
    market_timeseries.to_csv(_output_location+'/market_data.csv')

    return market_timeseries