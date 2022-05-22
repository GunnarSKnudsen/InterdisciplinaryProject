import pandas as pd
from os.path import exists


def get_single_directors_dealings(_data_location_insider_raw, _ticker, no_https):
    """
    :param _data_location_insider_raw:
    :param _ticker:
    :return:
    """
    print(_ticker)
    print('Trying to get directors dealings for ' + _ticker)
    f = _data_location_insider_raw + _ticker + '.csv'
    if not exists(f):
        if no_https:
            rq = f'http://openinsider.com/screener?s={_ticker}&o=&pl=&ph=&ll=&lh=&fd=1461&fdr=&td=1461&tdr=&fdlyl=&fdlyh=&daysago=&xp=1&xs=1&vl=&vh=&ocl=&och=&sic1=-1&sicl=100&sich=9999&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&sortcol=0&cnt=1000&page=1'
        else:
            rq = f'https://www.openinsider.com/screener?s={_ticker}&o=&pl=&ph=&ll=&lh=&fd=1461&fdr=&td=1461&tdr=&fdlyl=&fdlyh=&daysago=&xp=1&xs=1&vl=&vh=&ocl=&och=&sic1=-1&sicl=100&sich=9999&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&sortcol=0&cnt=1000&page=1'
        insider_data = pd.read_html(rq)
        insider_data = insider_data[-3]
        insider_data['ticker'] = _ticker
        if insider_data.shape[0] >= 999:
            print(f"POSSIBLE ERROR OCCURED HERE for {_ticker}")

        # Rewrite if nothing is found
        if insider_data.iloc[0, 0] == 'Sort by':
            insider_data = pd.DataFrame(
                columns=['X', 'Filing\xa0Date', 'Trade\xa0Date', 'Ticker', 'Insider Name', 'Title', 'Trade Type',
                         'Price', 'Qty', 'Owned', 'ΔOwn', 'Value', '1d', '1w', '1m', '6m', 'ticker'])
        insider_data.to_csv(_data_location_insider_raw + _ticker + '.csv')


def get_all_directors_dealings(_data_location_insider_raw, _tickers, no_https=False):
    """

    :param _data_location_insider_raw:
    :param _tickers:
    :return:
    """
    counter = 0
    for ticker in _tickers:
        counter = counter + 1
        print(f'Iteration: {counter}')
        get_single_directors_dealings(_data_location_insider_raw, ticker, no_https)
