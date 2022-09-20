import logging

class Analyser:
    '''
    Documentation not yet written
    '''

    def __init__(self, company):
        '''
        Documentation not yet written
        '''
        self.company = company
        logging.debug(self.company)


    def analyse(self):
        '''
        Documentation not yet written
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
    Documentation not yet written
    '''


    a = Analyser(company)

    return a.analyse()
