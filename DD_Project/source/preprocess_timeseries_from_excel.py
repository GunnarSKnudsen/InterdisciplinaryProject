import pandas as pd
import locale

def preprocess_timeseries_from_excel(_files):
    """

    :param _files:
    :return:
    """
    print('Reading files')
    for file in _files:
        print(f'Reading {file}:')

        dat = pd.read_excel(file, keep_default_na=True)#, dtype={'TICKER SYMBOL': str})
        print(dat)
        #tickers = nasdaq_composite['TICKER SYMBOL'].str.replace(' ', '+')
        #tickers = tickers.astype(str)
        #isins = nasdaq_composite['ISIN CODE'].str.replace(' ', '+')
        #isins = isins.astype(str)
        ## Save list somewhere for re-reading?

    #return tickers, isins