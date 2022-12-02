import pandas as pd
import pickle
from source.datamodels import Company
import logging

def get_market_data(_ticker, _start_time_unix, _end_time_unix, _output_location, market_path=None):
    '''
    Extracts market data for a given interval for a certain ticker. Stores as a csv, if needed later.
    Arguments:
        _ticker: a string
        _start_time_unix: an integer
        _end_time_unix: an integer
        _output_location: where the file will be stored
        market_path: location of previously downloaded file
    Returns:
        a dataframe of market data
    '''
    
    # Download data
    if market_path:
        market_timeseries = pd.read_csv(market_path, sep=";", decimal=",")
        market_timeseries["Date"] = pd.to_datetime(market_timeseries["Date"], format="%d.%m.%Y")
    else:
        print("No market data path provided, downloading data from Yahoo Finance")
        url = f'https://query1.finance.yahoo.com/v7/finance/download/{_ticker}?period1={_start_time_unix}&period2={_end_time_unix}&interval=1d&events=history&includeAdjustedClose=true'
        market_timeseries = pd.read_csv(url)
        market_timeseries = market_timeseries[["Adj Close"]]
        market_timeseries = market_timeseries.rename(columns={"Adj Close": "RI_market"})

    market_timeseries = market_timeseries.set_index('Date')
    market_timeseries.index = market_timeseries.index.astype('datetime64[ns]')

    # Store and return
    market_timeseries.to_csv(_output_location+'/market_data.csv')

    return market_timeseries