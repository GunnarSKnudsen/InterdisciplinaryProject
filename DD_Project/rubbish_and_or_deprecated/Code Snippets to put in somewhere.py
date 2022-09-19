# Get baseline!



### Combine timeseries to a single table
timeseries = pd.DataFrame()
dateparse = lambda x: datetime.datetime.strptime(x, '%Y-%m-%d')

for ticker in tickers:
    ts_data = pd.read_csv(DATA_LOCATION_TIME_SERIES_PROCESSED + ticker + '.csv', index_col=0, parse_dates=['Date'], date_parser=dateparse)
    timeseries = pd.concat([timeseries,ts_data])

### Add Information
# Calculate Marketcap
timeseries['MarketCap'] = timeseries.Open * timeseries.Volume
#Volatility - Figure this out!
timeseries['prev_close'] = timeseries.groupby('ticker')['Close'].shift()
timeseries['Returns'] = (timeseries.Close / timeseries.prev_close)-1
timeseries = timeseries.drop('prev_close', 1)

# Export
timeseries.to_csv(DATA_LOCATION_TIME_SERIES_PROCESSED + 'all_concatenated.csv')

### Combine into a single dataframe
#Create a single dataframe to contain all the insider transactions
# Empty dummy
insider = pd.DataFrame()

for ticker in tickers:
    ticker = ticker.replace(' ', '+')
    print(ticker)
    #if ticker not in ['ASML', 'TEAM', 'BIDU', 'CHKP', 'FOXA', 'JD', 'NTES', 'PDD', 'TCOM']:
    insider_data = pd.read_csv(DATA_LOCATION_INSIDER_PROCESSED + ticker + '.csv', index_col=0)
    insider = pd.concat([insider,insider_data])

# Save to file
insider.to_csv(DATA_LOCATION_INSIDER_PROCESSED + 'all_concatenated.csv')

#Show content
insider