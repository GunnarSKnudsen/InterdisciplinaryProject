# Standard
import pandas as pd


def read_tickers_and_isins(_filename):
    """

    :param _filename:
    :return:
    """
    print('Reading tickers')
    nasdaq_composite = pd.read_excel(_filename, keep_default_na=False, dtype={'TICKER SYMBOL': str})
    tickers = nasdaq_composite['TICKER SYMBOL'].str.replace(' ', '+')
    tickers = tickers.astype(str)
    isins = nasdaq_composite['ISIN CODE'].str.replace(' ', '+')
    isins = isins.astype(str)
    # Save list somewhere for re-reading?

    return tickers, isins
