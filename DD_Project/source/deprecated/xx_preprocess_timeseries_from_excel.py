import pandas as pd
import pickle
from source.datamodels import Company
import logging

def preprocess_timeseries_from_excel(_mainfile, _files, _output_location):

    # Read in information about companies
    all_companies = pd.read_excel(_mainfile, keep_default_na=False, dtype={'TICKER SYMBOL': str, 'DATASTREAM CODE': str})

    output_files = []

    logging.debug('Reading files')
    for file in _files:
        logging.debug(f'Reading {file}:')

        dat = pd.read_excel(file, keep_default_na=True, header=4, skiprows=[5])

        for col in dat.columns.values:
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

            company_data["return_index_df"] = ri_df

            output_file = f"{_output_location}{company_data['isin']}.pickle"
            output_files.append(output_file)

            # Save as Company object
            c = Company(**company_data)
            with open(output_file, "wb") as f:
                pickle.dump(c, f)
            logging.debug("Finished file " + output_file)

    return output_files