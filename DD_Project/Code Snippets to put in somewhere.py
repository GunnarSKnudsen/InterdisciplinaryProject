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

# Show table
timeseries

# tickers = ['GOBI']

### Process data
#This step is still somewhat broken
if REPROCESS_INSIDER_DATA:
    for ticker in tickers:
        ticker = ticker.replace(' ', '+')
        # print(ticker)
        ## Poor mans exception handling:
        # if ticker not in ['ASML', 'TEAM', 'BIDU', 'CHKP', 'FOXA', 'JD', 'NTES', 'PDD', 'TCOM']:
        # Read in the downloaded data
        insider_data = pd.read_csv(DATA_LOCATION_INSIDER_RAW + ticker + '.csv', index_col=0)

        # Process datatypes accordingly
        insider_data['Filing\xa0Date'] = pd.to_datetime(insider_data['Filing\xa0Date'])
        insider_data['Trade\xa0Date'] = pd.to_datetime(insider_data['Trade\xa0Date'])
        ## 'Trade\xa0Type' - should this be decoded?
        insider_data['Price'] = insider_data['Price'].astype(str).map(lambda x: x.replace(',', '').strip('+'))
        insider_data['Price'] = insider_data['Price'].map(lambda x: locale.atof(x.strip('$')))
        insider_data['Qty'] = pd.to_numeric(
            (insider_data['Qty']).astype(str).map(lambda x: x.replace(',', '').strip('+')))
        insider_data['Value'] = pd.to_numeric(
            insider_data['Value'].map(lambda x: locale.atof(x.replace(',', '').replace('$', ''))))
        # insider_data['ΔOwn']=insider_data['ΔOwn'].map(lambda x: locale.atof(x.replace(',', '').replace('%','')))

        # Better naming of columns
        insider_data.columns = insider_data.columns.map(lambda x: x.replace('\xa0', '').replace('Δ', 'delta_'))
        insider_data.to_csv(DATA_LOCATION_INSIDER_PROCESSED + ticker + '.csv')

        # Usefull helpers for when I finish this step
        # insider_data
        # print(insider_data.columns.tolist())
        # insider_data.dtypes

        # display(insider_data)

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