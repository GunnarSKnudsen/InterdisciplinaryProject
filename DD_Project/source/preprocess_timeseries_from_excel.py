import pandas as pd
import pickle
import locale


def preprocess_timeseries_from_excel(_mainfile, _files, _output_location):
    """
    This file needs refactoring BAD! Should maybe split into two different files?

    :param _files:
    :return:
    """

    # Read in information about companies
    all_companies = pd.read_excel(_mainfile, keep_default_na=False, dtype={'TICKER SYMBOL': str, 'DATASTREAM CODE': str})

    output_files = []

    print('Reading files')
    for file in _files:
        print(f'Reading {file}:')

        dat = pd.read_excel(file, keep_default_na=True, header=4, skiprows=[5])#, skiprows=[0,5])#, dtype={'TICKER SYMBOL': str})

        for col in dat.columns.values:
            datastream_code = col.replace("(RI)", "")

            if col[:8] == "Unnamed:":
                continue

            if datastream_code == 'Code':
                continue
            company_information_df = all_companies[all_companies['DATASTREAM CODE'] == datastream_code]

            type = company_information_df['Type'].item()
            isin = company_information_df['ISIN CODE'].item()
            name = company_information_df['NAME'].item()
            ticker = company_information_df['TICKER SYMBOL'].item()
            start_date = company_information_df['BASE OR ST DATE'].item()
            end_date = company_information_df['DATE/TIME (DS End Date)'].item()

            ri_df = dat[['Code', col]].rename(columns={'Code': 'Date', col: 'ReturnIndex'})
            # Set index - Should be done during preprocessing! # Is now moved to correct file
            ri_df['Date'] = pd.to_datetime(ri_df['Date'])
            ri_df.set_index('Date', inplace=True)  # , drop=False, append=False, inplace=False, verify_integrity=False)#.drop('Date', 1)
            ri_df = ri_df.loc[start_date:end_date]

            output_file = _output_location + isin + '.pickle'
            output_files.append(output_file)
            with open(output_file, "wb") as f:
                pickle.dump(type, f)
                pickle.dump(isin, f)
                pickle.dump(name, f)
                pickle.dump(ticker, f)
                pickle.dump(start_date, f)
                pickle.dump(end_date, f)
                pickle.dump(ri_df, f)
            print("Finished file " + output_file)

    return output_files