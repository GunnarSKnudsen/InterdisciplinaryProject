import pandas as pd

def read_tickers_and_isins(_filename):
    print('Reading tickers')
    data = pd.read_excel(_filename, keep_default_na=False, dtype={'TICKER SYMBOL': str})
    tickers = data['TICKER SYMBOL'].str.replace(' ', '+')
    tickers = tickers.astype(str)
    isins = data['ISIN CODE'].str.replace(' ', '+')
    isins = isins.astype(str)

    data['TICKER SYMBOL'] = tickers
    data['ISIN CODE'] = isins
    # Save list somewhere for re-reading?
    # display(data)
    return data
