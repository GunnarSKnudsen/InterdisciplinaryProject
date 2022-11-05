import pandas as pd
import pickle
from source.datamodels import Company
import logging
import pandas_market_calendars as mcal
from tools import load_settings

settings = load_settings()
types_of_interest = settings["types_of_interest"]
investigation_periods = settings["investigation_periods"]

earliest_timestamp = list(investigation_periods.values())[0][0]
latest_timestamp = list(investigation_periods.values())[-1][1]

def preprocess_timeseries_from_excel(_mainfile, _files, _market_timeseries, _output_location, _insider_location, _FIX_ROWS, STOCK_EXCHANGE):
    '''
        Method for preprocessing the entire dataset. Includes the market timeseries now, so that we can handle missing dates easier in later steps
        Input:
            _mainfile:
            _files:
            _market_timeseries: timeseries that are used as a baseline
            _output_location: location of processed files
            _FIX_ROWS: string of either 'discard' or 'interpolate' - Defines how we handle dates that are missing in either dataset
        Returns:
            For some reason it does
    '''

    # Do some assert'ive() stuff about FIX_ROWS.

    # Read in information about companies
    all_companies = pd.read_excel(_mainfile, keep_default_na=False, dtype={'TICKER SYMBOL': str, 'DATASTREAM CODE': str})

    # Create a calendar
    market_cal = mcal.get_calendar(STOCK_EXCHANGE)
    trading_days = market_cal.schedule(start_date=earliest_timestamp, end_date=latest_timestamp)


    output_files = []
    market_notcompany = []
    company_notmarket = []
    logging.debug('Reading files')

    # drop non-trading days
    _market_timeseries = _market_timeseries[_market_timeseries.index.isin(trading_days.index)]

    for file in _files:
        logging.debug(f'Reading {file}:')

        dat = pd.read_excel(file, keep_default_na=True, header=4, skiprows=[5])

        for col in dat.columns.values:
            # Handle data
            datastream_code = col.replace("(RI)", "")

            if col[:8] == "Unnamed:":
                continue

            if datastream_code == 'Code':
                continue


            company_information_df = all_companies[all_companies['DATASTREAM CODE'] == datastream_code]
            company_fields = ["Type", "ISIN CODE", "NAME", "TICKER SYMBOL", "BASE OR ST DATE", "DATE/TIME (DS End Date)"]
            company_fields_renamed = ["company_type", "isin", "name", "ticker", "start_date", "end_date"]

            company_data = {name:company_information_df[cf].item() for name, cf in zip(company_fields_renamed, company_fields)}

            ri_df = dat[['Code', col]].rename(columns={'Code': 'Date', col: 'ReturnIndex'})
            # Set index - Should be done during preprocessing! # Is now moved to correct file
            ri_df['Date'] = pd.to_datetime(ri_df['Date'])
            ri_df.set_index('Date', inplace=True)
            ri_df = ri_df.loc[company_data["start_date"]:company_data["end_date"]]

            # Join the dataframe together
            joined_df = ri_df.join(_market_timeseries, rsuffix="_market", lsuffix="_company", how="outer")


            if _FIX_ROWS == 'discard':
                # We only want to consider days where both market and company data has data

                #mask1 = joined_df['Adj Close'].notnull()
                mask1 = joined_df['RI_market'].notnull()
                mask2 = joined_df['ReturnIndex'].notnull()
                mask = mask1 & mask2


                # for report for professor
                if (mask1 & ~mask2).any():
                    market_notcompany.append((datastream_code, company_data["start_date"], company_data["end_date"], joined_df.copy()))
                if (~mask1 & mask2).any():
                    company_notmarket.append((datastream_code, company_data["start_date"], company_data["end_date"], joined_df.copy()))

                joined_df = joined_df.loc[mask]




            if _FIX_ROWS == 'interpolate':
                # Keeping more data, but generating syntetic data as well.
                ## Really need to consider what happens here after period end. E.g. we are interpolating until end of data. Maybe only interpolate to last point in each series?
                joined_df['ReturnIndex'] = joined_df['ReturnIndex'].interpolate(limit_area="inside")
                #joined_df['Open'] = joined_df['Open'].interpolate(limit_area="inside")
                #joined_df['High'] = joined_df['High'].interpolate(limit_area="inside")
                #joined_df['Low'] = joined_df['Low'].interpolate(limit_area="inside")
                #joined_df['Close'] = joined_df['Close'].interpolate(limit_area="inside")
                #joined_df['Adj Close'] = joined_df['Adj Close'].interpolate(limit_area="inside")
                #joined_df['Volume'] = joined_df['Volume'].interpolate(limit_area="inside")
                joined_df['RI_market'] = joined_df['RI_market'].interpolate(limit_area="inside")

            #Calculate percentage change:
            joined_df['company_return_percentage_change'] = joined_df['ReturnIndex'].pct_change()
            #joined_df['market_open_percentage_change'] = joined_df['Open'].pct_change()
            #joined_df['market_high_percentage_change'] = joined_df['High'].pct_change()
            #joined_df['market_low_percentage_change'] = joined_df['Low'].pct_change()
            #joined_df['market_close_percentage_change'] = joined_df['Close'].pct_change()
            #joined_df['market_adj_close_percentage_change'] = joined_df['Adj Close'].pct_change()
            joined_df['market_RI_percentage_change'] = joined_df['RI_market'].pct_change() # if we use yahoo data this is the adj close instead of the RI
            #joined_df['market_volume_percentage_change'] = joined_df['Volume'].pct_change()
            # Clone columns of interest for no real reason...
            joined_df['company_return'] = joined_df['company_return_percentage_change']
            joined_df['market_return'] = joined_df['market_RI_percentage_change']

            # Decide on only keeping a smaller set of columns
            ri_df = joined_df[['ReturnIndex', 'company_return', 'market_return']]

            # store and save
            company_data["return_index_df"] = ri_df
            output_file = f"{_output_location}{company_data['isin']}.pickle"
            output_files.append(output_file)

            # add insider data
            filename = _insider_location + company_data["ticker"] + '.csv'
            filename = filename.replace(" ", "+")  # HBB+WI in files and HBB WI as Ticker in base Excel
            insider_data_df = pd.read_csv(filename, index_col=0, parse_dates=['FilingDate', 'TradeDate'])

            # filter data
            filing_dates = insider_data_df.FilingDate.apply(lambda x: x.floor("d"))

            mask = (filing_dates >= earliest_timestamp) & (filing_dates <= latest_timestamp)
            insider_data_df = insider_data_df[mask]
            mask = insider_data_df.TradeType.apply(lambda x: x in types_of_interest)
            insider_data_df = insider_data_df[mask]



            company_data["insider_data_df"] = insider_data_df

            # Save as Company object
            c = Company(**company_data)
            with open(output_file, "wb") as f:
                pickle.dump(c, f)
            logging.debug("Finished file " + output_file)
            print("Finished file " + output_file)

    returns_mnc = []
    for mnc in market_notcompany:
        code, start, end, df = mnc
        return_ = df.loc[start:end]['ReturnIndex'].isna()
        returns_mnc.append(return_)

    #notcompany = pd.concat(returns_mnc, axis=1)
    #returns_cnm = []
    #for cnm in company_notmarket:
    #    code, start, end, df = cnm
    #    #return_ = df.loc[start:end]['Adj Close'].isna()
    #    return_ = df.loc[start:end]['RI_market'].isna()
    #    returns_cnm.append(return_)
    #
    #notmarket = pd.concat(returns_cnm, axis=1)
    #
    #notcompany_agg = notcompany.sum(axis=1)[464:1550]
    #notcompany_wd = pd.DataFrame({"counts":notcompany_agg, "weekday": notcompany_agg.index.weekday})
    #agg = notcompany_wd.groupby("weekday").sum()
    #agg.index = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    #print(agg)
    #
    #notmarket_agg = notmarket.sum(axis=1)[464:1550]
    #notmarket_wd = pd.DataFrame({"counts":notmarket_agg, "weekday": notmarket_agg.index.weekday})
    #agg = notmarket_wd.groupby("weekday").sum()
    #agg.index = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    #print(agg)


    return output_files