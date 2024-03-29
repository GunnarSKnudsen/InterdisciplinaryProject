import pandas as pd
import pickle
from source.datamodels import Company
import logging
import pandas_market_calendars as mcal
from tools import load_settings

# Read in settings
settings = load_settings()
types_of_interest = settings["types_of_interest"]
investigation_periods = settings["investigation_periods"]

earliest_timestamp = list(investigation_periods.values())[0][0]
latest_timestamp = list(investigation_periods.values())[-1][1]

start_time, end_time = settings["start_time"], settings["end_time"]

def preprocess_timeseries_from_excel(_mainfile, _files, _market_timeseries, _output_location, _insider_location, _FIX_ROWS, STOCK_EXCHANGE):
    '''
        Method for preprocessing the entire dataset. Includes the market timeseries now, so that we can handle missing dates easier in later steps
        Input:
            _mainfile: contains companies to be analysed
            _files: list of files containing return index
            _market_timeseries: timeseries that are used as a baseline
            _output_location: location of processed files
            _FIX_ROWS: string of either 'discard' or 'interpolate' - Defines how we handle dates that are missing in either dataset
        Returns:
            For some reason it does
    '''

    # Read in information about companies
    all_companies = pd.read_excel(_mainfile, keep_default_na=False, dtype={'TICKER SYMBOL': str, 'DATASTREAM CODE': str})

    # Create a calendar
    market_cal = mcal.get_calendar(STOCK_EXCHANGE)
    trading_days = market_cal.schedule(start_date=start_time, end_date=end_time)

    # Define outputs
    output_files = []
    market_notcompany = []
    company_notmarket = []
    logging.debug('Reading files')

    # drop non-trading days
    _market_timeseries = _market_timeseries[_market_timeseries.index.isin(trading_days.index)]

    # Go through each file containing RIs
    for file in _files:
        logging.debug(f'Reading {file}:')

        dat = pd.read_excel(file, keep_default_na=True, header=4, skiprows=[5])

        # Each column contains the return index
        for col in dat.columns.values:
            # Handle data
            datastream_code = col.replace("(RI)", "")

            # Fix known bug
            if col[:8] == "Unnamed:":
                continue

            if datastream_code == 'Code':
                continue

            # Define fields to be stored
            company_information_df = all_companies[all_companies['DATASTREAM CODE'] == datastream_code]
            company_fields = ["Type", "ISIN CODE", "NAME", "TICKER SYMBOL", "BASE OR ST DATE", "DATE/TIME (DS End Date)"]
            company_fields_renamed = ["company_type", "isin", "name", "ticker", "start_date", "end_date"]

            company_data = {name:company_information_df[cf].item() for name, cf in zip(company_fields_renamed, company_fields)}

            # generate dataframe
            ri_df = dat[['Code', col]].rename(columns={'Code': 'Date', col: 'ReturnIndex'})
            # Set index - Should be done during preprocessing! # Is now moved to correct file
            ri_df['Date'] = pd.to_datetime(ri_df['Date'])
            ri_df.set_index('Date', inplace=True)
            ri_df = ri_df.loc[company_data["start_date"]:company_data["end_date"]]

            # Join the dataframe together
            joined_df = ri_df.join(_market_timeseries, rsuffix="_market", lsuffix="_company", how="outer")

            if _FIX_ROWS == 'discard':
                # We only want to consider days where both market and company data has data
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
                joined_df['ReturnIndex'] = joined_df['ReturnIndex'].interpolate(limit_area="inside")
                joined_df['RI_market'] = joined_df['RI_market'].interpolate(limit_area="inside")

            #Calculate percentage change:
            joined_df['company_return_percentage_change'] = joined_df['ReturnIndex'].pct_change()
            joined_df['market_RI_percentage_change'] = joined_df['RI_market'].pct_change() # if we use yahoo data this is the adj close instead of the RI
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

            # Add directors dealings to company object
            company_data["insider_data_df"] = insider_data_df

            # Save as Company object
            c = Company(**company_data)
            with open(output_file, "wb") as f:
                pickle.dump(c, f)
            logging.debug("Finished file " + output_file)
            print("Finished file " + output_file)

    return output_files