import logging

class TimeSeriesMismatchException(Exception):
    pass

def run(L1_length, L2_length, event_timestamp, company_return): #, market_timeseries):
    '''
    Method to find the various time points surrounding an event.
    Todo:
        Check if error output makes sense
        Check if T1 should be a day earlier?
        refactor company_return
    Input:
        L1_length: an integer
        L2_length: an integer
        event_timestamp: a timestamp
        company_return: dataframe with returns
    '''
    
    # Find first date
    T1_iloc = company_return.index.get_loc(event_timestamp) - int(L2_length / 2)
    T1_date = company_return.index[T1_iloc]
    logging.debug(f'Found T1 to be {T1_date} on index {T1_iloc}')
    
    # Find second date
    T2_iloc = company_return.index.get_loc(event_timestamp) + int(L2_length / 2)
    T2_date = company_return.index[T2_iloc]
    logging.debug(f'Found T2 to be {T2_date} on index {T2_iloc}')
    
    # Find third date
    T0_iloc = company_return.index.get_loc(T1_date) - L1_length
    T0_date = company_return.index[T0_iloc]
    logging.debug(f'Found T0 to be {T0_date} on index {T0_iloc}')
    
    # Do some additional error handling
    ## Check if these errors still make sense
    ## Are they still neccesary?
    msg, ERRORS = "", {}
    problem = f"While the preliminary checks passed, the market timeseries seems to go further back in time\n"
    problem += f"with a window of length L1 because there might be a lower rate of trading days than in the company return series \n"
    problem += f"So as a result we take more than L1 days in the company timeseries and run into a problem when we want to \n"
    if T0_date not in company_return.index:
        msg += problem
        msg += f"Result: {T0_date} is not in the company timeseries"
        ERRORS["T0 not in company_return.index"] = 1
    else:
        if company_return.index.get_loc(T0_date) == 0:
            msg += problem
            msg += "Do not have an extra day, so we cant append the cheat day to later calculate the returns"
            ERRORS["company_return.index.get_loc(T0) == 0"] = 1
    # This error no longer makes sense:
    #if T0_date not in market_timeseries.index:
    #    msg += f"{T0_date} is not in the market timeseries, probably because of some mismatch in the trading days"
    #    ERRORS["T0 not in market_timeseries.index"] = 1

    if msg:
        return "dummy", "dummy", "dummy", T0_date, T1_date, T2_date, ERRORS, msg


    # Explain what happened
    logging.debug(f'------------------------------')
    logging.debug(f'Event occurred at             {event_timestamp}')
    logging.debug(f'Estimation Window ({str(L1_length)} days): from {str(T0_date)} to {str(T1_date)}')
    logging.debug(f'Event Window      ( {str(L2_length)} days): from {str(T1_date)} to {str(T2_date)}')

    return T0_iloc, T1_iloc, T2_iloc, T0_date, T1_date, T2_date, ERRORS, msg