import numpy as np
import pandas_market_calendars as mcal
import logging

def run(company_return, T0, T1, T2):
    '''
    Method for finding the various cut-off dates.
    Left to do:
        Write proper documentation here
        Refactoring? This is the wrong place to write this, but company_return should be renamed project-wide.
        Out T1 is one day after what I intuitively would imagine. let's discuss this! (Ensures that L2 = 40, instead of 41 - but feels "off"
    Input:
        company_return: dataframe containing market- and company data
        T0: write desc
        T1: write desc
        T2: write desc
    Returns:
        four time series for the various event windows:
            estimation_window_market_return: pd.Series
            estimation_window_company_return: pd.Series
            event_window_market_return: pd.Series
            event_window_company_return: pd.Series
    '''
    ## Estimation Window
    ### For estimating alphas and betas
    estimation_window_index = (company_return.index >= T0) & (company_return.index < T1)
    estimation_window_timeseries = company_return[estimation_window_index]
    
    ## Event-Window
    ## Time surrounding the event
    event_window_index = (company_return.index >= T1) & (company_return.index <= T2)
    event_window_timeseries = company_return[event_window_index]
    

    # Calculate percentage returns
    estimation_window_market_return = estimation_window_timeseries['market_return']
    estimation_window_company_return = estimation_window_timeseries['company_return']

    event_window_market_return = event_window_timeseries['market_return']
    event_window_company_return = event_window_timeseries['company_return']

    logging.debug('shapes (Shouldn''t be an issue after better preprocessing)')
    logging.debug(f'# estimation_window_market_return: {estimation_window_market_return.shape}')
    logging.debug(f'# estimation_window_market_return: {estimation_window_market_return.shape}')
    logging.debug(f'# event_window_market_return: {event_window_market_return.shape}')
    logging.debug(f'# event_window_company_return: {event_window_company_return.shape}')

    return estimation_window_market_return, estimation_window_company_return, event_window_market_return, event_window_company_return
