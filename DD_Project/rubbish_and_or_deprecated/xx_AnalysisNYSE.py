#%%

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

import os
from os.path import exists

import statsmodels.api as sm
from statsmodels import regression


import matplotlib.pyplot as plt

# Import User Defined functions
import source.read_tickers_and_isins as URTI
import source.get_directors_dealings as UGDD
import source.get_timeseries as UGT
import source.analyze_get_summary_of_data as AGSOD
import source.preprocess_directors_dealings as UPDD
import source.preprocess_timeseries as UPTS
import source.preprocess_timeseries_from_excel as UPTFE
import source.analyse_single_company as UASC
import source.calculate_daily_returns_for_period as CDRFP
from tqdm import tqdm


#%%




NAME = "Niedermayer"
DATA_LOCATION = f'data/{NAME}/'
DATA_LOCATION_INSIDER_RAW = DATA_LOCATION + 'raw/insider/'
DATA_LOCATION_INSIDER_PROCESSED = DATA_LOCATION + 'processed/insider/'
DATA_LOCATION_TIME_SERIES_RAW = DATA_LOCATION + 'raw/timeseries/'
DATA_LOCATION_TIME_SERIES_PROCESSED = DATA_LOCATION + 'processed/timeseries/'
DATA_LOCATION_RI = DATA_LOCATION + 'processed/RI/'

_ri_location = DATA_LOCATION_RI
_insider_location = DATA_LOCATION_INSIDER_PROCESSED


file_locs_ = os.listdir(_ri_location)
file_locs = [_ri_location + f for f in file_locs_]
return_index_dfs = []
isins = []
print("loading return series...")
for file_loc in tqdm(file_locs):
    with open(file_loc, "rb") as f:
        type = pickle.load(f)
        isin = pickle.load(f)
        name = pickle.load(f)
        ticker = pickle.load(f)
        start_date = pickle.load(f)
        end_date = pickle.load(f)
        return_index_df = pickle.load(f)
    return_index_dfs.append(return_index_df)
    isins.append(isin)

company_return = return_index_df

print("calculate returns")
returns_df = [CDRFP.calculate_daily_returns(ts) for ts in return_index_dfs]

print("concatenate")
df_returns = pd.concat(returns_df[:10000], axis=1) # TODO remove the slice
df_return_index = pd.concat(return_index_dfs[:10], axis=1)

print(df_returns.head())

plt.rc('font', family='serif')
plt.rc('xtick')
plt.rc('ytick')

fig = plt.figure(figsize=(7, 5))
ax = fig.add_subplot(1, 1, 1)

returns_companies = df_returns.mean(axis=1)
returns_companies.plot(color="k", linewidth=0.7)

ax.set_xlabel('Time (Years)')
ax.set_ylabel('Mean Daily Return')

interval_borders = ["2020-02-01"] # TODO see if it makes sense to actually take first of Feb
for int_ in interval_borders:
    plt.axvline(x = int_, color = 'red', label = 'DD Event time', linewidth = 1)

plt.savefig(DATA_LOCATION +"visualisations/NYSE_daily_returns.jpg", dpi=600)


pickles = os.listdir(DATA_LOCATION_RI)[:100]  # TODO remove restriction
ISINs = [rick[:-7] for rick in pickles]


#from dask.distributed import Client
# client = Client(threads_per_worker=4, n_workers=8)
# futures = client.map(lambda isin: UASC.analyse_single_company(isin, DATA_LOCATION_RI, DATA_LOCATION_INSIDER_PROCESSED), ISINs)
# outputs = client.gather(futures)

outputs = []
for isin in tqdm(ISINs):
    outputs.append(UASC.analyse_single_company(isin, DATA_LOCATION_RI, DATA_LOCATION_INSIDER_PROCESSED))

sum_returns = sum([x[0] for x in outputs], [])
filing_trade_lags = sum([x[1] for x in outputs], [])


from matplotlib import pyplot as plt
import numpy as np

lag_in_hours = np.asarray(filing_trade_lags)
negative_lag_mask = lag_in_hours < 0
positive_lag = lag_in_hours[~negative_lag_mask]
print(f"Negative lag for {negative_lag_mask.sum()} out of {len(negative_lag_mask)} trades.")
plt.hist(np.log(positive_lag), bins="auto")

plt.savefig(DATA_LOCATION +"visualisations/log_transformed_lags.jpg", dpi=600)

without_outliers = positive_lag[positive_lag < 400]
plt.hist(without_outliers, bins="auto")
plt.xticks(np.arange(0, max(without_outliers) + 1, 24))

plt.savefig(DATA_LOCATION +"visualisations/lags_without_outliers.jpg", dpi=600)