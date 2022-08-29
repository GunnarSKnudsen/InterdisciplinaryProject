import pickle
import pandas as pd
from datetime import timedelta
import source.calculate_daily_returns_for_period as UCRFP
import logging
from source.datamodels import Trade

class Analyser:

    def __init__(self, _isin, _ri_location, _insider_location):

        file_loc = _ri_location + _isin + '.pickle'
        with open(file_loc, "rb") as f:
            self.company = pickle.load(f)

        # Probably need a try/catch here
        self.insider_data_df = pd.read_csv(_insider_location + self.company.ticker + '.csv', index_col=0,
                                      parse_dates=['FilingDate', 'TradeDate'])
        logging.debug(self.company)


    def analyse(self):

        # Take a look at each of the DD Filigns:
        return_sums = []
        filing_trade_lags = []
        for index, row in self.insider_data_df.iterrows():
            # Read relevant variables
            trade = Trade(*[row[x] for x in ["FilingDate", "TradeDate", "Ticker", "InsiderName", "Title", "TradeType", "Price", "Qty", "Owned", "delta_Own", "Value"]])

            logging.debug(trade)

            # TODO Gunnar: Should I use TradeDate instead of FilingDate? Tom: Answered, but keeping it so Gunnar sees it
            # Aussenegg on 10.07. I would suggest to use the filing date as disclosure date
            # calling it disclosure_date from now on
            disclosure_date = trade.FilingDate

            # Define which time to calculate for
            start = disclosure_date - timedelta(days=20)
            end = disclosure_date + timedelta(days=20)
            returns_in_period = UCRFP.calculate_daily_returns_for_period(self.company.return_index_df, start, end)
            filing_trade_lag = trade.FilingDate - trade.TradeDate
            logging.debug(trade)
            logging.debug(f'Total returns in this period was {returns_in_period.sum()}')
            return_sums.append(returns_in_period)
            filing_trade_lags.append(filing_trade_lag)

        return return_sums, filing_trade_lags

# TODO DEPRECATED
def analyse_single_company(_isin, _ri_location, _insider_location):
    a = Analyser(_isin, _ri_location, _insider_location)

    return a.analyse()


    # Gunnar!!! Stop this nonsensical printing!
    # Step 1: concatenate to CSV
    # Step 2: Calculate "Normal" returns from some index during same time? during previous time?
    # Step 3: Do Step 2 before step 1
    # Step 4: Get help! Work more organized instead of just blindly coding!
    # Step 5: Do Step 4 right away!
    # Figure out which periods to actually use
    # Read up again of why we need previous time period as well!