import pandas as pd
import locale

from os import listdir
from os.path import isfile, join

def preprocess_directors_dealings(_raw_location, _preprocessed_location):
    """
        Method for cleansing the scraped directors dealings.
        Input:
            _raw_location: Location of scraped data
            _preprocessed_location: Location to store data for later analysis
    """

    # List of files to process
    filenames = [f for f in listdir(_raw_location) if isfile(join(_raw_location, f))]
    for f in filenames:
        # Read in companys' data
        insider_data = pd.read_csv(_raw_location + f, index_col=0)

        # If we got companyName
        if insider_data.shape[1] == 18:
            insider_data.columns = ['X', 'FilingDate', 'TradeDate', 'Ticker', 'CompanyName', 'InsiderName', 'Title',
                                    'TradeType', 'Price', 'Qty', 'Owned', 'delta_Own', 'Value', '1d', '1w', '1m', '6m',
                                    'ticker']
        # And then rename columns
        if insider_data.shape[1] == 17:
            insider_data.columns = ['X', 'FilingDate', 'TradeDate', 'Ticker', 'InsiderName', 'Title', 'TradeType',
                                    'Price', 'Qty', 'Owned', 'delta_Own', 'Value', '1d', '1w', '1m', '6m', 'ticker']

        # Process datatypes accordingly
        insider_data['FilingDate'] = pd.to_datetime(insider_data['FilingDate'])
        insider_data['TradeDate'] = pd.to_datetime(insider_data['TradeDate'])
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