
def run(L1_length, L2_length, event_timestamp, company_return):#, market_timeseries):
    '''
    Documentation not yet written
    GSK Might have broken this now...
    '''

    # Check if we have enough data to run analysis:
    ## I get a bunch of Out of bounds errors when events happen too close to the border of available data. Did a bunch of cleansing, before realiing that it is WAY easier to just throw errors then.
    ## Let's see if we can handle this better...

    # Constants that are being checked
    ## We need to have this data:
    required_days_before_event = (L1_length + L2_length/2 ) +1 # Added one day, as the first return index pct is always nan.
    required_days_after_event = L2_length/2 + 1 #  TODO had to add 1 to prevent an error in determining T0 T1 T2, perhaps think instead of adding numbers some time?

    ## We have this data:
    company_length = company_return.shape[0]
    #market_length = market_timeseries.shape[0]

    # I want all errors logged, hence a flag - would make way more sense to break in the check itself
    ERROR_OCCURED = {}
    msg = ""

    #if event_timestamp not in market_timeseries.index:
    #    msg += f" {event_timestamp} cannot be found in the market timeseries. For now skip, perhaps find a better way to not drop data"
    #    ERROR_OCCURED["event_timestamp not in market"] = 1
    #else:
    #    event_index_market = market_timeseries.index.get_loc(event_timestamp)

    #    if (required_days_before_event > event_index_market):
    #        msg += f"""Analysis can't be done. Requires at least {required_days_before_event} trading days before the event.
    #                However we only have {event_index_market} entries prior in the market data  \n
    #                """
    #        ERROR_OCCURED["required_days_before_event > event_index_market"] = 1

    #    if (required_days_after_event > (market_length - event_index_market)):
    #        msg += f"""Analysis can't be done. Requires at least {required_days_after_event} trading days AFTER the event.
    #                However we only have {(market_length - event_index_market)} entries available after in the market data
    #                \n
    #                """
    #        ERROR_OCCURED["required_days_after_event > (market_length - event_index_market)"] = 1

    if event_timestamp not in company_return.index:
        msg += f" {event_timestamp} cannot be found in the company return series. For now skip, perhaps find a better way to not drop data"
        ERROR_OCCURED["event_timestamp not in the company return data"] = 1
    else:

        event_index_company = company_return.index.get_loc(event_timestamp)

        if (required_days_before_event > event_index_company):
            msg += f"""Analysis can't be done. Requires at least {required_days_before_event} trading days before the event. 
                    However we only have {event_index_company} entries prior in the company data  \n
                    """
            ERROR_OCCURED["Not enough days before event in company data"] = 1


        if (required_days_after_event > (company_length - event_index_company)):
            msg += f"""Analysis can't be done. Requires at least {required_days_after_event} trading days AFTER the event.
                    However we only have {(company_length - event_index_company)} entries available after in the company 
                    data  \n
                    """
            ERROR_OCCURED["Don't have enough trading days after event"] = 1


    if ERROR_OCCURED:
        return ERROR_OCCURED, msg

#if __name__ == "__main__":
#    import datetime
#    import pandas as pd
#    L1_length, L2_length = 10, 4
#    index = [datetime.datetime(2016, 3, 1+i, 0, 0, 0) for i in range(L1_length+L2_length)]
#    company_return = pd.DataFrame(index=index)
#    market_timeseries = pd.DataFrame(index=index)

    # simplified checks: here all days are trading days

#    event_timestamp = datetime.datetime(2050, 3, 13, 0, 0, 0)
#    try:
#        run(L1_length, L2_length, event_timestamp, company_return, market_timeseries)
#    except DataSizeException as exc:
#        print(exc)


#    event_timestamp = datetime.datetime(2050, 3, 14, 0, 0, 0)
#    try:
#        run(L1_length, L2_length, event_timestamp, company_return, market_timeseries)
#    except DataSizeException as exc:
#        print(exc)

    # TODO is the event just a dot on the timeline or a whole day?
    #   Is the whole interval L1 + L2/2 + 1 + L2/2?