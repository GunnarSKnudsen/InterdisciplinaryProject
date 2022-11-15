import pandas as pd
import logging
import datetime
import asyncio
import aiohttp
import os

def get_all_directors_dealings_async(_data_location_insider_raw, _data, _download_type, from_date, to_date):
    '''
        Download all directors dealings from openinsider.com in an async method and stores them for later processing
        Input:
            _data_location_insider_Raw: Location where data will be stored
            _data: from read_tickers_and_isins() that contains a ticker symbol
            _download_type: define which types of transactions will be considered
            _from_date: datetime
            _to_date: datetime
    '''
    
    # Generate part of URL that defines download type
    dl_type_string = ''
    for t in _download_type:
        dl_type_string = dl_type_string + ('&x' + t.lower() + '=1')

    # go through all companies
    counter = 0
    params = []
    for index, row in _data.iterrows():
        counter = counter + 1
        ticker = row['TICKER SYMBOL']

        # Handle missing dates
        if from_date == 'NA':
            from_date = datetime.datetime.now()
        if to_date == 'NA':
            to_date = datetime.datetime.now()

        # Generate string
        dl_date_string = '&fdr=' + (f'{from_date.month:02d}') + '%2F' + (f'{from_date.day:02d}') + '%2F' + (
            f'{from_date.year:04d}') + '+-+' + (f'{to_date.month:02d}') + '%2F' + (f'{to_date.day:02d}') + '%2F' + (
                             f'{to_date.year:04d}')

        # Store parameters
        params.append([_data_location_insider_raw, ticker, from_date, to_date, dl_type_string, dl_date_string, counter])

    sema = asyncio.BoundedSemaphore(100)

    # Define scraper
    async def get_single_directors_dealings_async(_data_location_insider_raw, _ticker, _from_date, _to_date,
                                                  _dl_type_string, _dl_date_string, counter):
        # Define call
        max_pagination = 100000
        html_url = f'http://www.openinsider.com/screener?s={_ticker}&o=&pl=&ph=&ll=&lh=&fd=-1{_dl_date_string}&td=0&tdr=&fdlyl=&fdlyh=&daysago={_dl_type_string}&vl=&vh=&ocl=&och=&sic1=-1&sicl=100&sich=9999&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&sortcol=0&cnt={max_pagination}&page=1'
        
        # Location of transaction
        filepath = _data_location_insider_raw + _ticker + '.csv'
        if os.path.exists(filepath):
            # If file is already downloaded, we don't rerun it
            return

        # Call an async session
        async with sema, aiohttp.ClientSession() as session:
            async with session.get(html_url) as resp:
                # Read in an entry
                assert resp.status == 200
                data = await resp.read()
                logging.debug(f'{counter}: Downloading data for ticker {_ticker} for period from {_from_date} to {_to_date}')

                insider_data = pd.read_html(data)
                insider_data = insider_data[-3]
                insider_data['ticker'] = _ticker

                # Check if pagination causes errors
                if insider_data.shape[0] >= max_pagination - 1:
                    logging.warning(f"POSSIBLE ERROR OCCURED HERE for {_ticker}")

                # Rewrite if nothing is found
                if insider_data.iloc[0, 0] == 'Sort by':
                    insider_data = pd.DataFrame(
                        columns=['X', 'Filing\xa0Date', 'Trade\xa0Date', 'Ticker', 'Insider Name', 'Title',
                                 'Trade Type',
                                 'Price', 'Qty', 'Owned', 'ΔOwn', 'Value', '1d', '1w', '1m', '6m', 'ticker'])
                # Save results
                insider_data.to_csv(filepath)
                logging.debug(insider_data.shape)

    # Create event look
    loop = asyncio.get_event_loop()
    # Organize tasks
    tasks = [loop.create_task(get_single_directors_dealings_async(*paramset)) for paramset in params]
    # Run all scrapes
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()