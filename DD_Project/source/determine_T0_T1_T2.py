import logging

def run(L1_length, L2_length, event_timestamp, company_return, market_timeseries):

    T1_c_iloc = company_return.index.get_loc(event_timestamp) - int(L2_length / 2)
    T1_m_iloc = market_timeseries.index.get_loc(event_timestamp) - int(L2_length / 2)
    T1_c = company_return.index[T1_c_iloc]
    T1_m = market_timeseries.index[T1_m_iloc]
    # Do this magic BEFORE calculating T0 - Otherwise we risk breaking!
    T1 = min(T1_c, T1_m)
    logging.debug(f'Found T1: {str(T1)}')

    T2_c_iloc = company_return.index.get_loc(event_timestamp) + int(L2_length / 2)
    T2_m_iloc = market_timeseries.index.get_loc(event_timestamp) + int(L2_length / 2)
    T2_c = company_return.index[T2_c_iloc]
    T2_m = market_timeseries.index[T2_m_iloc]
    T2 = max(T2_c, T2_m)
    logging.debug(f'Found T2: {str(T2)}')

    # Estimation Window:
    # T0 = T1 - datetime.timedelta(days = L1_length) # Tom: trading days not just timedelta but that seems fixed already

    T0_c_iloc = company_return.index.get_loc(T1) - L1_length
    T0_m_iloc = market_timeseries.index.get_loc(T1) - L1_length
    T0_c = company_return.index[T0_c_iloc]
    T0_m = market_timeseries.index[T0_m_iloc]
    T0 = min(T0_c, T0_m)
    logging.debug(f'Found T0: {str(T0)}')

    ## Break T0 and T1 to cheat so we don't start with NAs
    T1_ = company_return.index[company_return.index.get_loc(T1) - 1]
    T0_ = company_return.index[company_return.index.get_loc(T0) - 1]

    logging.debug(f'------------------------------')
    logging.debug(f'Event occurred at             {event_timestamp}')
    logging.debug(f'Estimation Window ({str(L1_length)} days): from {str(T0)} to {str(T1)}')
    logging.debug(f'Event Window      ( {str(L2_length)} days): from {str(T1)} to {str(T2)}')

    return T0_, T1_, T0, T1, T2

def run2(L1_length, L2_length, event_timestamp, trading_days):
    import pandas_market_calendars as mcal
    import pandas as pd
    # Create a calendar
    nyse = mcal.get_calendar('NYSE')
    # create random datetime timestamp
    event_timestamp = pd.to_datetime(event_timestamp)
    start_date = event_timestamp - pd.Timedelta(days=L1_length*2 + L2_length)
    end_date = event_timestamp + pd.Timedelta(days=L2_length*2)

    relevant_days = nyse.valid_days(start_date=start_date, end_date=end_date).map(lambda x: x.replace(tzinfo=None))
    logging.getLogger().setLevel(logging.DEBUG)

    # get index of event_timestamp
    event_timestamp_index = relevant_days.get_loc(event_timestamp)
    T0_ = relevant_days[event_timestamp_index - L1_length - int(L2_length / 2)]
    T1_ = relevant_days[event_timestamp_index - int(L2_length/2) - 1]
    T1 = relevant_days[event_timestamp_index - int(L2_length/2)]
    T2 = relevant_days[event_timestamp_index + int(L2_length/2) - 1]
    T0 = "dummy"

    return T0_, T1_, T0, T1, T2