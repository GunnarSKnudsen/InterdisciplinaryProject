import pandas as pd
import time
import requests
from os.path import exists


def get_single_timeseries(_data_location_time_series_raw, _ticker, _start_time_unix, _end_time_unix):
    """

    :param _data_location_time_series_raw:
    :param _ticker:
    :param _start_time_unix:
    :param _end_time_unix:
    :return:
    """
    print(_ticker)
    f = _data_location_time_series_raw + _ticker + '.csv'
    if not exists(f):
        print('Downloading Timeseries for ' + _ticker)
        url = f'https://query1.finance.yahoo.com/v7/finance/download/{_ticker}?period1={_start_time_unix}&period2={_end_time_unix}&interval=1d&events=history&includeAdjustedClose=true'
        print(url)
        # Refactor here - currently making two calls in one
        # response = requests.get(url).content
        # print(response)

        # if response is not None and response != b'Forbidden':
        #    print(pd.read_csv(io.StringIO(response.decode('utf-8'))))
        try:
            time.sleep(2)  # Make sure that we don't do more than 3600/2=1800 requests per hour - Yahoo blocks after 2000
            timeseries = pd.read_csv(url)
            timeseries['ticker'] = _ticker
            # Nothing to do here
            timeseries.to_csv(f)
        except:
            print('Didnt work. Probably because of reasons')
        # else:
        #    print('Call returned nothing')
    else:
        print('File already downloaded')


def get_ticker_for_isin(isin):
    """

    :param isin:
    :return:
    """
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


def get_all_timeseries_from_isins(_data_location_time_series_raw, _isins, _start_time_unix, _end_time_unix):
    """

    :param _data_location_time_series_raw:
    :param _isins:
    :param _start_time_unix:
    :param _end_time_unix:
    :return:
    """
    counter = 0
    for isin in _isins:
        counter = counter + 1
        print(f'Iteration: {counter}')
        print("Trying " + isin)
        # Figure out a way to not do these requests all the time.
        ticker = get_ticker_for_isin(isin)
        if ticker is not None:
            get_single_timeseries(_data_location_time_series_raw, ticker, _start_time_unix, _end_time_unix)
        else:
            print('NO TIME SERIES FOUND FOR THIS ONE (' + isin + ')')


def get_all_timeseries_from_tickers(_data_location_time_series_raw, _tickers, _start_time_unix, _end_time_unix):
    """

    :param _data_location_time_series_raw:
    :param _tickers:
    :param _start_time_unix:
    :param _end_time_unix:
    :return:
    """

    counter = 0
    for ticker in _tickers:
        counter = counter + 1
        print(f'Iteration: {counter}')
        print("Trying " + ticker)
        get_single_timeseries(_data_location_time_series_raw, ticker, _start_time_unix, _end_time_unix)
