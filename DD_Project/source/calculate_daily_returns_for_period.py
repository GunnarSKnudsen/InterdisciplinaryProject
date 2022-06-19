import pandas as pd

def calculate_daily_returns_for_period(_ts, _start, _end):

    # Ignore these
    #print(_start)
    #print(_end)
    #print(len(_ts))

    # Clone because of reasons
    ts = _ts.copy()

    # Calculate returns
    ts['returns'] = (ts - ts.shift(1)) / ts.shift(1)

    if not _start and not _end:
        return ts["returns"]

    # Filter for selected period - Should do error handling here (E.g. Dead, before/After, ...)
    filtered_ts = ts.loc[_start:_end]
    filtered_ts = filtered_ts['returns']

    #print(f"Total returns for period is {filtered_ts['returns'].sum()}")

    return filtered_ts


def calculate_daily_returns(_ts):
    return calculate_daily_returns_for_period(_ts, None, None)