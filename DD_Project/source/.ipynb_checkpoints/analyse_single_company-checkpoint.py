import pickle
import pandas as pd
from datetime import timedelta


import source.calculate_daily_returns_for_period as UCRFP

def analyse_single_company(_isin, _ri_location, _insider_location):
    print("Hey")
    file_loc = _ri_location + _isin + '.pickle'
    with open(file_loc, "rb") as f:
        type = pickle.load(f)
        isin = pickle.load(f)
        name = pickle.load(f)
        ticker = pickle.load(f)
        start_date = pickle.load(f)
        end_date = pickle.load(f)
        return_index_df = pickle.load(f)

    # Probably need a try/catch here
    insider_data_df = pd.read_csv(_insider_location + ticker + '.csv', index_col=0, parse_dates=['FilingDate', 'TradeDate'])

    print("Read in a company. This is the information we have:")
    print(f'Type = {type}')
    print(f'isin = {isin}')
    print(f'name = {name}')
    print(f'ticker = {ticker}')
    print(f'start_date = {start_date}')
    print(f'end_date = {end_date}')
    print("----------")
    #print("Directors Dealings:")
    #print(insider_data_df)
    print("----------")
    #print("TimeSeries:")
    #print(return_index_df)

    # Testing out returns function
    start = '2018-01-01 00:00:00'
    end = '2020-01-01 00:00:00'
    UCRFP.calculate_daily_returns_for_period(return_index_df, start, end)

    #Take a look at each of the DD Filigns:
    for index, row in insider_data_df.iterrows():
        # Read relevant variables
        FilingDate = row['FilingDate']
        TradeDate = row['TradeDate']
        Ticker = row['Ticker']
        InsiderName =row ['InsiderName']
        Title = row['Title']
        TradeType = row['TradeType']
        Price = row['Price']
        Qty = row['Qty']
        Owned = row['Owned']
        delta_Own = row['delta_Own']
        Value = row['Value']

        # Figure out if this is correct
        date_to_consider = FilingDate # Should I TradeDate instead of FilingDate?

        # Define which time to calculate for
        start = date_to_consider - timedelta(days=20)
        end = date_to_consider + timedelta(days=20)
        returns_in_period = UCRFP.calculate_daily_returns_for_period(return_index_df, start, end)

        print("----------------------------------")
        print("----------------------------------")
        print(f'FilingDate: {FilingDate}')
        print(f'TradeDate: {TradeDate}')
        print(f'InsiderName: {InsiderName}')
        print(f'Title: {Title}')
        print(f'TradeType: {TradeType}')
        print(f'Price: {Price}')
        print(f'Qty: {Qty}')
        print(f'Owned: {Owned}')
        print(f'delta_Own: {delta_Own}')
        print(f'Value: {Value}')

        print(f'Total returns in this period was {returns_in_period.sum()}')

        # Gunnar!!! Stop this nonsensical printing!
        # Step 1: concatenate to CSV
        # Step 2: Calculate "Normal" returns from some index during same time? during previous time?
        # Step 3: Do Step 2 before step 1
        # Step 4: Get help! Work more organized instead of just blindly coding!
        # Step 5: Do Step 4 right away!
        # Figure out which periods to actually use
        # Read up again of why we need previous time period as well!
        
        break