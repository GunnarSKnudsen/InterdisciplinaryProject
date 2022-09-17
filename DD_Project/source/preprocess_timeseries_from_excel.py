import pandas as pd
import pickle
from source.datamodels import Company
import logging

def preprocess_timeseries_from_excel(_mainfile, _files, _market_timeseries, _output_location, _FIX_ROWS):
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

    output_files = []

    logging.debug('Reading files')
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
                mask1 = joined_df['ReturnIndex'].notnull()
                mask2 = joined_df['Adj Close'].notnull()

                joined_df = joined_df.loc[mask1 & mask2]

            if _FIX_ROWS == 'interpolate':
                # Keeping more data, but generating syntetic data as well.
                ## Really need to consider what happens here after period end. E.g. we are interpolating until end of data. Maybe only interpolate to last point in each series?
                joined_df['ReturnIndex'] = joined_df['ReturnIndex'].interpolate()
                joined_df['Open'] = joined_df['Open'].interpolate()
                joined_df['High'] = joined_df['High'].interpolate()
                joined_df['Low'] = joined_df['Low'].interpolate()
                joined_df['Close'] = joined_df['Close'].interpolate()
                joined_df['Adj Close'] = joined_df['Adj Close'].interpolate()
                joined_df['Volume'] = joined_df['Volume'].interpolate()

            #Calculate percentage change:
            joined_df['company_return_percentage_change'] = joined_df['ReturnIndex'].pct_change()
            joined_df['market_open_percentage_change'] = joined_df['Open'].pct_change()
            joined_df['market_high_percentage_change'] = joined_df['High'].pct_change()
            joined_df['market_low_percentage_change'] = joined_df['Low'].pct_change()
            joined_df['market_close_percentage_change'] = joined_df['Close'].pct_change()
            joined_df['market_adj_close_percentage_change'] = joined_df['Adj Close'].pct_change()
            joined_df['market_volume_percentage_change'] = joined_df['Volume'].pct_change()
            # Clone columns of interest for no real reason...
            joined_df['company_return'] = joined_df['company_return_percentage_change']
            joined_df['market_return'] = joined_df['market_adj_close_percentage_change']

            # Decide on only keeping a smaller set of columns
            ri_df = joined_df[['ReturnIndex', 'company_return', 'market_return']]

            # store and save
            company_data["return_index_df"] = ri_df

            output_file = f"{_output_location}{company_data['isin']}.pickle"
            output_files.append(output_file)

            # Save as Company object
            c = Company(**company_data)
            with open(output_file, "wb") as f:
                pickle.dump(c, f)
            logging.debug("Finished file " + output_file)
            print("Finished file " + output_file)

    return output_files