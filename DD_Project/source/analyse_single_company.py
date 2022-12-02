import logging

class Analyser:
    '''
    Class that used to have more functions, right now it is just used for finding out the lags of the filings,
    but it could be used for more things in the future
    '''

    def __init__(self, company):
        self.company = company
        logging.debug(self.company)


    def analyse(self):
        '''
        Calculates the lags and returns them. Unit = hours.
        '''

        # Take a look at each of the DD Filigns:
        filing_trade_lags = []
        
        for index, row in self.company.insider_data_df.iterrows():
            # Read relevant variables
            filing_trade_lag = row["FilingDate"] - row["TradeDate"]
            filing_trade_lags.append(filing_trade_lag.total_seconds()/60/60)

        return filing_trade_lags


def analyse_single_company(company):
    '''
    Wrapper for the Analyser class
    '''

    a = Analyser(company)

    return a.analyse()
