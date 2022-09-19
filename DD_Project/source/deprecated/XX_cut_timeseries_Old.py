import numpy as np
import pandas_market_calendars as mcal
import logging

def run(company_return, market_timeseries, T0_, T1, T1_, T2):
    ## Estimation Window
    ### For estimating alphas and betas
    estimation_window_index_market = (market_timeseries.index >= T0_) & (market_timeseries.index < T1)
    estimation_window_index_company = (company_return.index >= T0_) & (company_return.index < T1)

    estimation_window_market_timeseries = market_timeseries[estimation_window_index_market]
    estimation_market_count = estimation_window_market_timeseries.shape[0]

    estimation_window_company_timeseries = company_return[estimation_window_index_company]
    estimation_company_count = estimation_window_company_timeseries.shape[0]

    ## Event-Window
    event_window_index_market = (market_timeseries.index >= T1_) & (market_timeseries.index < T2)
    event_window_index_company = (company_return.index >= T1_) & (company_return.index < T2)

    event_window_market_timeseries = market_timeseries[event_window_index_market]
    event_market_count = event_window_market_timeseries.shape[0]

    event_window_company_timeseries = company_return[event_window_index_company]
    event_company_count = event_window_company_timeseries.shape[0]

    logging.debug('shape before aggregating')
    logging.debug(f'# estimation_window_market_timeseries: {estimation_window_market_timeseries.shape}')
    logging.debug(f'# estimation_window_company_timeseries: {estimation_window_company_timeseries.shape}')
    logging.debug(f'# event_window_market_timeseries: {event_window_market_timeseries.shape}')
    logging.debug(f'# event_window_company_timeseries: {event_window_company_timeseries.shape}')


    # Unify indexing, so that both contain same amount of trading days.
    if (estimation_company_count > estimation_market_count):
        idx = estimation_window_company_timeseries.index
        estimation_window_market_timeseries = estimation_window_market_timeseries.reindex(idx, fill_value = np.NaN)
        # Fill missing with previous observation
        estimation_window_market_timeseries['Adj Close'] = estimation_window_market_timeseries['Adj Close'].fillna(method='ffill')
        estimation_window_market_timeseries['Adj Close'] = estimation_window_market_timeseries['Adj Close'].fillna(method='bfill')
    if (estimation_market_count > estimation_company_count):
        idx = estimation_window_market_timeseries.index
        estimation_window_company_timeseries = estimation_window_company_timeseries.reindex(idx, fill_value = np.NaN)
        # Fill missing with previous observation
        estimation_window_company_timeseries['ReturnIndex'] = estimation_window_company_timeseries['ReturnIndex'].fillna(method='ffill')
        estimation_window_company_timeseries['ReturnIndex'] = estimation_window_company_timeseries['ReturnIndex'].fillna(method='bfill')


    # Unify indexing, so that both contain same amount of trading days.
    if (event_company_count > event_market_count):
        idx = event_window_company_timeseries.index
        event_window_market_timeseries = event_window_market_timeseries.reindex(idx, fill_value = np.NaN)
        # Fill missing with previous observation
        event_window_market_timeseries['Adj Close'] = event_window_market_timeseries['Adj Close'].fillna(method='ffill')
        event_window_market_timeseries['Adj Close'] = event_window_market_timeseries['Adj Close'].fillna(method='bfill')
    if (event_market_count > event_company_count):
        idx = event_window_market_timeseries.index
        event_window_company_timeseries = event_window_company_timeseries.reindex(idx, fill_value = np.NaN)
        # Fill missing with previous observation
        event_window_company_timeseries['ReturnIndex'] = event_window_company_timeseries['ReturnIndex'].fillna(method='ffill')
        event_window_company_timeseries['ReturnIndex'] = event_window_company_timeseries['ReturnIndex'].fillna(method='bfill')

    # Calculate percentage returns
    estimation_window_market_return = estimation_window_market_timeseries['Adj Close'].pct_change()
    estimation_window_company_return = estimation_window_company_timeseries['ReturnIndex'].pct_change()

    event_window_market_return = event_window_market_timeseries['Adj Close'].pct_change()
    event_window_company_return = event_window_company_timeseries['ReturnIndex'].pct_change()

    ## Remove the fake first date
    estimation_window_market_return = estimation_window_market_return.iloc[1:]
    estimation_window_company_return = estimation_window_company_return.iloc[1:]

    event_window_market_return = event_window_market_return.iloc[1:]
    event_window_company_return = event_window_company_return.iloc[1:]

    logging.debug('shape after aggregating')
    logging.debug(f'# estimation_window_market_return: {estimation_window_market_return.shape}')
    logging.debug(f'# estimation_window_market_return: {estimation_window_market_return.shape}')
    logging.debug(f'# event_window_market_return: {event_window_market_return.shape}')
    logging.debug(f'# event_window_company_return: {event_window_company_return.shape}')

    return estimation_window_market_return, estimation_window_company_return, event_window_market_return, event_window_company_return


def run2(company_return, market_timeseries, T0_, T1, T1_, T2, trading_days):
    # Create a calendar
    nyse = mcal.get_calendar('NYSE')

    #estimation_days = nyse.schedule(start_date=T0_, end_date=T1)
    estimation_days = trading_days[(trading_days >= T0_) & (trading_days<=T1)]


    estimation_days = estimation_days.drop(columns= ['market_open', 'market_close'])
    estimation_days.index.name = "Date"

    #event_days = nyse.schedule(start_date=T1_, end_date=T2)
    event_days = trading_days[(trading_days >= T1_) & (trading_days<=T2)]
    event_days = event_days.drop(columns= ['market_open', 'market_close'])
    event_days.index.name = "Date"

    ## Estimation Window
    ### For estimating alphas and betas
    import pandas as pd
    def get_window(df_input, nyse_days):

        df = pd.merge(df_input, nyse_days, on=['Date'], how='left', indicator='Exist')
        df = df[df.Exist == 'both']
        df = df.drop(columns=['Exist'])
        return df


    estimation_window_market_timeseries = get_window(market_timeseries, estimation_days)
    estimation_window_company_timeseries = get_window(company_return, estimation_days)
    event_window_market_timeseries = get_window(market_timeseries, event_days)
    event_window_company_timeseries = get_window(company_return, event_days)

    logging.debug('shape before aggregating')
    logging.debug(f'# estimation_window_market_timeseries: {estimation_window_market_timeseries.shape}')
    logging.debug(f'# estimation_window_company_timeseries: {estimation_window_company_timeseries.shape}')
    logging.debug(f'# event_window_market_timeseries: {event_window_market_timeseries.shape}')
    logging.debug(f'# event_window_company_timeseries: {event_window_company_timeseries.shape}')

    """
    # Unify indexing, so that both contain same amount of trading days.
    if (estimation_company_count > estimation_market_count):
        idx = estimation_window_company_timeseries.index
        estimation_window_market_timeseries = estimation_window_market_timeseries.reindex(idx, fill_value=np.NaN)
        # Fill missing with previous observation
        estimation_window_market_timeseries['Adj Close'] = estimation_window_market_timeseries['Adj Close'].fillna(
            method='ffill')
    if (estimation_market_count > estimation_company_count):
        idx = estimation_window_market_timeseries.index
        estimation_window_company_timeseries = estimation_window_company_timeseries.reindex(idx, fill_value=np.NaN)
        # Fill missing with previous observation
        estimation_window_company_timeseries['ReturnIndex'] = estimation_window_company_timeseries[
            'ReturnIndex'].fillna(method='ffill')

    # Unify indexing, so that both contain same amount of trading days.
    if (event_company_count > event_market_count):
        idx = event_window_company_timeseries.index
        event_window_market_timeseries = event_window_market_timeseries.reindex(idx, fill_value=np.NaN)
        # Fill missing with previous observation
        event_window_market_timeseries['Adj Close'] = event_window_market_timeseries['Adj Close'].fillna(method='ffill')
    if (event_market_count > event_company_count):
        idx = event_window_market_timeseries.index
        event_window_company_timeseries = event_window_company_timeseries.reindex(idx, fill_value=np.NaN)
        # Fill missing with previous observation
        event_window_company_timeseries['ReturnIndex'] = event_window_company_timeseries['ReturnIndex'].fillna(
            method='ffill')
    """
    # Calculate percentage returns
    estimation_window_market_return = estimation_window_market_timeseries['Adj Close'].pct_change()
    estimation_window_company_return = estimation_window_company_timeseries['ReturnIndex'].pct_change()

    event_window_market_return = event_window_market_timeseries['Adj Close'].pct_change()
    event_window_company_return = event_window_company_timeseries['ReturnIndex'].pct_change()

    ## Remove the fake first date
    estimation_window_market_return = estimation_window_market_return.iloc[1:]
    estimation_window_company_return = estimation_window_company_return.iloc[1:]

    event_window_market_return = event_window_market_return.iloc[1:]
    event_window_company_return = event_window_company_return.iloc[1:]

    logging.debug('shape after aggregating')
    logging.debug(f'# estimation_window_market_return: {estimation_window_market_return.shape}')
    logging.debug(f'# estimation_window_market_return: {estimation_window_market_return.shape}')
    logging.debug(f'# event_window_market_return: {event_window_market_return.shape}')
    logging.debug(f'# event_window_company_return: {event_window_company_return.shape}')


    return estimation_window_market_return, estimation_window_company_return, event_window_market_return, event_window_company_return


if __name__ == '__main__':
    # unpickle arguments

    import pickle
    with open("tests/arguments/cut_timeseries_na.pickle", 'rb') as f:
        args = pickle.load(f)

    #estimation_window_market_return, estimation_window_company_return, event_window_market_return, event_window_company_return = run(**args)
    #print(estimation_window_market_return[0])


    estimation_window_market_return, estimation_window_company_return, event_window_market_return, event_window_company_return = run2(**args)
    logging.debug(estimation_window_market_return[0])