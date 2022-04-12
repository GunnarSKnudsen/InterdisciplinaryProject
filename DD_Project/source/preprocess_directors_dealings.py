import pandas as pd
import locale

from os import listdir
from os.path import isfile, join


def preprocess_directors_dealings(_raw_location, _preprocessed_location):
    # List of files to process
    filenames = [f for f in listdir(_raw_location) if isfile(join(_raw_location, f))]
    # filenames = ['PCT.csv']
    for f in filenames:
        print(f'Processing {f}')
        insider_data = pd.read_csv(_raw_location + f, index_col=0)

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
        insider_data.to_csv(_preprocessed_location + f)

        # print(insider_data)
