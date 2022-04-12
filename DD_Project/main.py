# Standard
import pandas as pd
import numpy as np
import pickle

# Time Cleaning
import time
import datetime
from dateutil.relativedelta import relativedelta

# Scraping
import requests
import locale
from pandas.io.json import json_normalize
import io

from os.path import exists

# Constants:
DATA_LOCATION = 'data/'
DATA_LOCATION_INSIDER_RAW = DATA_LOCATION + 'raw/insider/'
DATA_LOCATION_INSIDER_PROCESSED = DATA_LOCATION + 'processed/insider/'
DATA_LOCATION_TIME_SERIES_RAW = DATA_LOCATION + 'raw/timeseries/'
DATA_LOCATION_TIME_SERIES_PROCESSED = DATA_LOCATION + 'processed/timeseries/'


def read_tickers(_filename):
    '''
    Documentation
    :param _filename:
    :return:
    '''
    print('Reading tickers')
    NASDAQ_COMPOSITE = pd.read_excel(_filename, keep_default_na = False, dtype={'TICKER SYMBOL': str})
    tickers = NASDAQ_COMPOSITE['TICKER SYMBOL'].str.replace(' ', '+')
    tickers = tickers.astype(str)
    # Save list somewhere for re-reading?
    return tickers

def read_isins(_filename):
    '''
    Documentation
    :param _filename:
    :return:
    '''
    print('Reading ISINs')
    NASDAQ_COMPOSITE = pd.read_excel(_filename, keep_default_na = False)
    isins = NASDAQ_COMPOSITE['ISIN CODE'].str.replace(' ', '+')
    # Save list somewhere for re-reading?
    return isins


def get_single_directors_dealings(_ticker):
    '''

    :param _ticker:
    :return:
    '''
    print(_ticker)
    print('Trying to get directors dealings for ' + _ticker)
    f = DATA_LOCATION_INSIDER_RAW + _ticker + '.csv'
    if not exists(f):
        insider_data = pd.read_html(
            f'http://www.openinsider.com/screener?s={_ticker}&o=&pl=&ph=&ll=&lh=&fd=1461&fdr=&td=1461&tdr=&fdlyl=&fdlyh=&daysago=&xp=1&xs=1&vl=&vh=&ocl=&och=&sic1=-1&sicl=100&sich=9999&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&sortcol=0&cnt=1000&page=1')
        insider_data = insider_data[-3]
        insider_data['ticker'] = _ticker
        if (insider_data.shape[0] >= 999):
            print(f"POSSIBLE ERROR OCCURED HERE for {_ticker}")

        # Rewrite if nothing is found
        if insider_data.iloc[0, 0] == 'Sort by':
            insider_data = pd.DataFrame(
                columns=['X', 'Filing\xa0Date', 'Trade\xa0Date', 'Ticker', 'Insider Name', 'Title', 'Trade Type',
                         'Price', 'Qty', 'Owned', 'ΔOwn', 'Value', '1d', '1w', '1m', '6m', 'ticker'])
        insider_data.to_csv(DATA_LOCATION_INSIDER_RAW + _ticker + '.csv')

def get_all_directors_dealings(_tickers):
    '''

    :param _tickers:
    :return:
    '''
    counter = 0
    for ticker in _tickers:
        counter = counter + 1
        print(f'Iteration: {counter}')
        get_single_directors_dealings(ticker)


def get_single_timeseries(_ticker, _start_time_unix, _end_time_unix):
    print(_ticker)
    f = DATA_LOCATION_TIME_SERIES_PROCESSED + _ticker + '.csv'
    if not exists(f):
        print('Downloading Timeseries for ' + _ticker)
        url = f'https://query1.finance.yahoo.com/v7/finance/download/{_ticker}?period1={_start_time_unix}&period2={_end_time_unix}&interval=1d&events=history&includeAdjustedClose=true'
        print(url)
        # Refactor here - currently making two calls in one
        #response = requests.get(url).content
        #print(response)

        #if response is not None and response != b'Forbidden':
            #print(pd.read_csv(io.StringIO(response.decode('utf-8'))))
        try:
            time.sleep(2) # Make sure that we don't do more than 3600/2=1800 requests per hour - Yahoo blocks after 2000
            timeseries = pd.read_csv(url)
            timeseries['ticker'] = _ticker
            # Nothing to do here
            timeseries.to_csv(f)
        except:
            print('Didnt work. Probably because of reasons')
        #else:
        #    print('Call returned nothing')
    else:
        print('File already downloaded')


def get_symbol_for_isin(isin):
    url = 'https://query1.finance.yahoo.com/v1/finance/search'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.109 Safari/537.36',
    }

    params = dict(
        q=isin,
        quotesCount=1,
        newsCount=0,
        listsCount=0,
        quotesQueryId='tss_match_phrase_query'
    )

    resp = requests.get(url=url, headers=headers, params=params)
    data = resp.json()
    if 'quotes' in data and len(data['quotes']) > 0:
        return data['quotes'][0]['symbol']
    else:
        return None

def get_all_timeseries(_isins):
    '''

    :param _tickers:
    :return:
    '''
    #Should probably rewrite this to be parameters:
    # Period of interest
    end_time = datetime.datetime.now()
    end_time = datetime.datetime(2021, 12, 31, 23, 59, 59)
    end_time_unix = int(time.mktime(end_time.timetuple()))

    start_time = end_time - relativedelta(years=4)
    start_time = datetime.datetime(2018, 1, 1, 0, 0, 0)
    start_time_unix = int(time.mktime(start_time.timetuple()))

    counter = 0
    for isin in _isins:
        counter = counter + 1
        print(f'Iteration: {counter}')
        print("Trying " + isin)
        # Figure out a way to not do these requests all the time.
        ticker = get_symbol_for_isin(isin)
        if ticker is not None:
            get_single_timeseries(ticker, start_time_unix, end_time_unix)
        else:
            print('NO TIME SERIES FOUND FOR THIS ONE (' + isin + ')')

def get_all_timeseries_from_tickers(_tickers):
    '''

    :param _tickers:
    :return:
    '''
    #Should probably rewrite this to be parameters:
    # Period of interest
    end_time = datetime.datetime.now()
    end_time = datetime.datetime(2021, 12, 31, 23, 59, 59)
    end_time_unix = int(time.mktime(end_time.timetuple()))

    start_time = end_time - relativedelta(years=4)
    start_time = datetime.datetime(2018, 1, 1, 0, 0, 0)
    start_time_unix = int(time.mktime(start_time.timetuple()))

    counter = 0
    for ticker in _tickers:
        counter = counter + 1
        print(f'Iteration: {counter}')
        print("Trying " + ticker)
        get_single_timeseries(ticker, start_time_unix, end_time_unix)


if __name__ == '__main__':
    filename = 'input_data/Nasdaq Composite 16.3.2022 plus dead firms - Knudsen.xlsx'
    # Read both at once?
    tickers = read_tickers(filename)
    isins = read_isins(filename)

    # Download raw data:
    get_all_directors_dealings(tickers)
    #get_all_timeseries(isins)
    get_all_timeseries_from_tickers(tickers)