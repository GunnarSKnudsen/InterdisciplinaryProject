## Imports
### Time Cleaning
import time
import datetime

### Other normal libraries
import logging
import os
from os.path import exists

### Import User Defined functions
import source.read_tickers_and_isins as URTI
import source.get_directors_dealings as UGDD
import source.preprocess_directors_dealings as UPDD
import source.preprocess_timeseries as UPTS
import source.preprocess_timeseries_from_excel as UPTFE
import source.get_market_data as UGMD
from tools import load_settings

### Set logging
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d/%m/%Y %H:%M:%S')

settings = load_settings()
STOCK_EXCHANGE = settings["STOCK_EXCHANGE"]
NAME = settings["NAME"]
prepare_and_download = settings["prepare_and_download"]

## Which files to be handled
INPUT_FILE = f'input_data/{NAME}/{STOCK_EXCHANGE} Composite 16.3.2022 plus dead firms - {NAME}.xlsx'
TIMESERIES_FILES = [f'input_data/{NAME}/{STOCK_EXCHANGE} Composite 16.3.2022 plus dead firms - {NAME} - RI - Part {i}.xlsx' for i in range(1,settings["n_input_files"]+1)]
DATA_PATH_MARKET = f"input_data/{NAME}/{STOCK_EXCHANGE.upper()}_market_data.csv"

# Locations to store stuff and stuff
DATA_LOCATION = f'data/{NAME}/'
DATA_LOCATION_INSIDER_RAW = DATA_LOCATION + 'raw/insider/'
DATA_LOCATION_INSIDER_PROCESSED = DATA_LOCATION + 'processed/insider/'
DATA_LOCATION_TIME_SERIES_RAW = DATA_LOCATION + 'raw/timeseries/'
DATA_LOCATION_TIME_SERIES_PROCESSED = DATA_LOCATION + 'processed/timeseries/'
DATA_LOCATION_RI = DATA_LOCATION + 'processed/RI/'
DATA_LOCATION_RI_interpolate  = DATA_LOCATION + 'processed/RI_interpolate/'
DATA_LOCATION_RI_discard = DATA_LOCATION + 'processed/RI_discard/'
DATA_LOCATION_MARKET = DATA_LOCATION + 'raw/market/'

# Create folders if they are not present
locations = [DATA_LOCATION, DATA_LOCATION_INSIDER_RAW, DATA_LOCATION_INSIDER_PROCESSED, DATA_LOCATION_TIME_SERIES_RAW,
             DATA_LOCATION_TIME_SERIES_PROCESSED, DATA_LOCATION_RI, DATA_LOCATION_MARKET, DATA_LOCATION_RI_interpolate, DATA_LOCATION_RI_discard]

for loc in locations:
    if not exists(loc):
        os.makedirs(loc)

# Period of interest
end_time = datetime.datetime(2021, 12, 31, 23, 59, 59)
end_time_unix = int(time.mktime(end_time.timetuple()))
start_time = datetime.datetime(2018, 1, 1, 0, 0, 0)
start_time_unix = int(time.mktime(start_time.timetuple()))
download_type = ['P', 'S', 'A', 'D', 'G', 'F', 'M', 'X', 'C', 'W']

# Download market data
start_time = datetime.datetime(2016, 3, 21, 0, 0, 0)
_start_time_unix = int(time.mktime(start_time.timetuple()))

end_time = datetime.datetime(2022, 3, 21, 23, 59, 59)
_end_time_unix = int(time.mktime(end_time.timetuple()))

## download market_data
market_timeseries = UGMD.get_market_data(settings["_ticker"], _start_time_unix, _end_time_unix, DATA_LOCATION_MARKET, DATA_PATH_MARKET)

if prepare_and_download:

    # Read which companies should be analyzed
    data = URTI.read_tickers_and_isins(INPUT_FILE)
    # Download the dealings
    UGDD.get_all_directors_dealings_async(DATA_LOCATION_INSIDER_RAW, data, download_type, "DATE/TIME (DS End Date)")
    # Cleanse the dealings
    UPDD.preprocess_directors_dealings(DATA_LOCATION_INSIDER_RAW, DATA_LOCATION_INSIDER_PROCESSED)
    tickers, isins = data["TICKER SYMBOL"], data["ISIN CODE"]
    # Preprocess raw data
    ## Don't think this one is needed anymore:
    UPTS.preprocess_timeseries(DATA_LOCATION_TIME_SERIES_RAW, DATA_LOCATION_TIME_SERIES_PROCESSED)

# Process the timeseries from Professor
## Currently doing both methods - then we can change input dataset in the notebook.
processed_files = UPTFE.preprocess_timeseries_from_excel(INPUT_FILE, TIMESERIES_FILES, market_timeseries, DATA_LOCATION_RI_discard, DATA_LOCATION_INSIDER_PROCESSED, 'discard', STOCK_EXCHANGE.upper())
processed_files = UPTFE.preprocess_timeseries_from_excel(INPUT_FILE, TIMESERIES_FILES, market_timeseries, DATA_LOCATION_RI_interpolate, DATA_LOCATION_INSIDER_PROCESSED, 'interpolate', STOCK_EXCHANGE.upper())
