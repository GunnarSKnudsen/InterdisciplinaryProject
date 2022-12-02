import pandas as pd

from os import listdir
from os.path import isfile, join
from os.path import exists


def analyze_generate_summary_of_data(_tickers, _isins, _insider_data_location, _timeseries_data_location):
    # Assert that these are equal?
    print(len(_tickers))
    print(len(_isins))

    #_tickers = _tickers.head(10)
    #_isins = _isins.head(10)

    # General
    tickers = []
    isins = []

    # Directors Dealings Data
    directors_dealings_download = []
    directors_dealings_counts = []
    n_traders_dd = []
    total_quantity_dd = []
    total_value_dd = []

    # Timeseries
    timeseries_download = []
    timeseries_counts = []
    timeseries_starts = []
    timeseries_ends = []
    # Add information about returtns?

    for i in range(len(_tickers)):
        # Figure out which ones to look for
        ticker = _tickers[i]
        isin = _isins[i]

        tickers.append(ticker)
        isins.append(isin)

        # Read in Directors Dealigns
        filename_directors_dealings = _insider_data_location + ticker + '.csv'
        if exists(filename_directors_dealings):
            # Read parsed data
            directors_dealings_data = pd.read_csv(filename_directors_dealings)
            print(f'{i}: {ticker}: {len(directors_dealings_data)} ({filename_directors_dealings})')

            # Do calculations
            total_qty = sum(directors_dealings_data['Qty'])
            total_value = sum(directors_dealings_data['Value'])
            # This NEEDS fixing in preprocessing - but too lazy right now
            try:
                how_many_traded = len(set(directors_dealings_data['Insider Name']))  # Frick! Needs more preprocessing - is named differently
            except:
                how_many_traded = len(set(directors_dealings_data['InsiderName']))  # Frick! Needs more preprocessing - is named differently

            # Append to results
            directors_dealings_download.append(True)
            directors_dealings_counts.append(len(directors_dealings_data))
            n_traders_dd.append(how_many_traded)
            total_quantity_dd.append(total_qty)
            total_value_dd.append(total_value)

        else:
            print("File not found")
            directors_dealings_download.append(False)
            directors_dealings_counts.append(0)
            n_traders_dd.append(0)
            total_quantity_dd.append(0)
            total_value_dd.append(0)

        # Read in Directors Dealigns
        filename_timeseries = _timeseries_data_location + ticker + '.csv'
        print('Searching for ' + filename_timeseries)
        if exists(filename_timeseries):
            print("cool beans")
            timeseries_data = pd.read_csv(filename_timeseries)
            timeseries_counts.append(len(timeseries_data))
            timeseries_starts.append(timeseries_data['Date'].min())
            timeseries_ends.append(timeseries_data['Date'].max())


            timeseries_download.append(True)
        else:
            print("Not so cool beans")
            timeseries_counts.append(0)
            timeseries_download.append(False)
            timeseries_starts.append(None)
            timeseries_ends.append(None)

    results_dataframe = pd.DataFrame({'ticker': tickers,
                                      'isins': isins,
                                      'directors_dealings_downloaded': directors_dealings_download,
                                      'timeseries_downloaded': timeseries_download,
                                      'dd_n_dealings': directors_dealings_counts,
                                      'dd_n_traders':  n_traders_dd,
                                      'dd_total_quantity': total_quantity_dd,
                                      'dd_total_value': total_value_dd,
                                      'ts_rows': timeseries_counts,
                                      'ts_from': timeseries_starts,
                                      'ts_to': timeseries_ends
                                      })
    results_dataframe.to_excel('data/summary_of_scraping.xlsx')
    results_dataframe.to_csv('data/summary_of_scraping.csv')
    print(results_dataframe)