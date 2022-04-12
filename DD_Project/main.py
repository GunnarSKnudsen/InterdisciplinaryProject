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

# Import User Defined functions
import source.read_tickers_and_isins as URTI
import source.get_directors_dealings as UGDD
import source.get_timeseries as UGT
import source.analyze_get_summary_of_data as AGSOD
import source.preprocess_directors_dealings as UPDD


if __name__ == '__main__':
    # Constants:

    # File from professor
    filename = 'input_data/Nasdaq Composite 16.3.2022 plus dead firms - Knudsen.xlsx'

    # Locations to store stuff and stuff
    DATA_LOCATION = 'data/'
    DATA_LOCATION_INSIDER_RAW = DATA_LOCATION + 'raw/insider/'
    DATA_LOCATION_INSIDER_PROCESSED = DATA_LOCATION + 'processed/insider/'
    DATA_LOCATION_TIME_SERIES_RAW = DATA_LOCATION + 'raw/timeseries/'
    DATA_LOCATION_TIME_SERIES_PROCESSED = DATA_LOCATION + 'processed/timeseries/'

    # Period of interest
    end_time = datetime.datetime(2021, 12, 31, 23, 59, 59)
    end_time_unix = int(time.mktime(end_time.timetuple()))

    start_time = datetime.datetime(2018, 1, 1, 0, 0, 0)
    start_time_unix = int(time.mktime(start_time.timetuple()))

    # Read which companies should be analyzed
    tickers, isins = URTI.read_tickers_and_isins(filename)

    # Download raw data:
    # UGDD.get_all_directors_dealings(DATA_LOCATION_INSIDER_RAW, tickers)
    # # UGT.get_all_timeseries_from_isins(DATA_LOCATION_TIME_SERIES_RAW, isins, start_time_unix, end_time_unix)  # Maybe this will be of use? - But does too many requests
    # UGT.get_all_timeseries_from_tickers(DATA_LOCATION_TIME_SERIES_RAW, tickers, start_time_unix, end_time_unix)

    # Preprocess raw data
    UPDD.preprocess_directors_dealings(DATA_LOCATION_INSIDER_RAW, DATA_LOCATION_INSIDER_PROCESSED)

    # Move to processed location:
    AGSOD.generate_summary_of_data(tickers, isins, DATA_LOCATION_INSIDER_PROCESSED, DATA_LOCATION_TIME_SERIES_RAW)
