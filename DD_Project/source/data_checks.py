
class DataSizeException(Exception):
    pass

def run(L1_length, L2_length, event_timestamp, company_return, market_timeseries):

    # Check if we have enough data to run analysis:
    ## I get a bunch of Out of bounds errors when events happen too close to the border of available data. Did a bunch of cleansing, before realiing that it is WAY easier to just throw errors then.
    ## Let's see if we can handle this better...

    # Constants that are being checked
    ## We need to have this data:
    required_days_before_event = L1_length + L2_length/2
    required_days_after_event = L2_length/2

    ## We have this data:
    company_length = company_return.shape[0]
    market_length = market_timeseries.shape[0]

    ### This is the location of the event that is being checked:
    event_index_company = company_return.index.get_loc(event_timestamp)
    event_index_market = market_timeseries.index.get_loc(event_timestamp)

    # I want all errors logged, hence a flag - would make way more sense to break in the check itself
    ERROR_HAS_OCCURED = 0
    msg = ""

    if (required_days_before_event > event_index_company):
        msg += f"""Analysis can't be done. Requires at least {required_days_before_event} trading days before the event. 
                However we only have {event_index_company} entries prior in the company data  \n
                """
        ERROR_HAS_OCCURED = 1

    if (required_days_before_event > event_index_market):
        msg += f"""Analysis can't be done. Requires at least {required_days_before_event} trading days before the event.
                However we only have {event_index_market} entries prior in the market data  \n
                """
        ERROR_HAS_OCCURED = 1

    if (required_days_after_event > (company_length - event_index_company)):
        msg += f"""Analysis can't be done. Requires at least {required_days_after_event} trading days AFTER the event.
                However we only have {(company_length - event_index_company)} entries available after in the company 
                data  \n
                """
        ERROR_HAS_OCCURED = 1

    if (required_days_after_event > (market_length - event_index_market)):
        msg += f"""Analysis can't be done. Requires at least {required_days_after_event} trading days AFTER the event.
                However we only have {(market_length - event_index_market)} entries available after in the market data
                \n
                """
        ERROR_HAS_OCCURED = 1

    if ERROR_HAS_OCCURED == 1:
        raise DataSizeException(msg)

if __name__ == "__main__":
    import datetime
    import pandas as pd
    L1_length, L2_length = 10, 4
    index = [datetime.datetime(2016, 3, 1+i, 0, 0, 0) for i in range(L1_length+L2_length)]
    company_return = pd.DataFrame(index=index)
    market_timeseries = pd.DataFrame(index=index)

    # simplified checks: here all days are trading days

    event_timestamp = datetime.datetime(2016, 3, 13, 0, 0, 0)
    try:
        run(L1_length, L2_length, event_timestamp, company_return, market_timeseries)
    except DataSizeException as exc:
        print(exc)


    event_timestamp = datetime.datetime(2016, 3, 14, 0, 0, 0)
    try:
        run(L1_length, L2_length, event_timestamp, company_return, market_timeseries)
    except DataSizeException as exc:
        print(exc)

    # TODO is the event just a dot on the timeline or a whole day?
    #   Is the whole interval L1 + L2/2 + 1 + L2/2?