
def calculate_daily_returns_for_period(_ts, _start, _end):

    # Calculate returns
    returns = (_ts - _ts.shift(1)) / _ts.shift(1)

    if not _start and not _end:
        return returns

    # Filter for selected period - Should do error handling here (E.g. Dead, before/After, ...)
    filtered_returns = returns.loc[_start:_end]["ReturnIndex"]

    return filtered_returns


def calculate_daily_returns(_ts):
    return calculate_daily_returns_for_period(_ts, None, None)
