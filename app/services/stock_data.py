import yfinance as yf
import pandas as pd
import time
import requests

class InvalidTickerError(Exception):
    pass

class NoDataError(Exception):
    pass

def _make_session():
    # Yahoo Finance blocks requests that look like they come from servers/bots.
    # By setting browser-like headers on the session, the request looks like it
    # comes from a real user's browser, which avoids most rate-limiting on cloud hosts.
    session = requests.Session()
    session.headers.update({
        'User-Agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/120.0.0.0 Safari/537.36'
        ),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    })
    return session

def fetch_stock_prices(tickers, start_date, end_date):
    if not tickers:
        raise ValueError("Tickers list can't be empty")

    max_attempts = 3
    last_error = None

    for attempt in range(max_attempts):
        try:
            # Pass our browser-like session to yfinance on every attempt
            session = _make_session()

            data = yf.download(
                tickers,
                start=start_date,
                end=end_date,
                progress=False,
                auto_adjust=True,
                session=session
            )

            if not data.empty:
                break

        except Exception as e:
            last_error = e
            if attempt < max_attempts - 1:
                time.sleep(2 ** attempt * 2)
            continue

        if data.empty and attempt < max_attempts - 1:
            time.sleep(2 ** attempt * 2)
    else:
        if last_error:
            raise NoDataError(f"Failed to fetch data after {max_attempts} attempts: {str(last_error)}")

    if len(tickers) == 1:
        if data.empty:
            raise InvalidTickerError(f"Invalid ticker or no data: {tickers[0]}")

        prices = data['Close']
        if isinstance(prices, pd.Series):
            prices = prices.to_frame(name=tickers[0])
    else:
        prices = data['Close']

        invalid_tickers = []
        for ticker in tickers:
            if ticker not in prices.columns or prices[ticker].isna().all():
                invalid_tickers.append(ticker)

        if invalid_tickers:
            raise InvalidTickerError(f"Invalid ticker(s): {', '.join(invalid_tickers)}")

    if prices.empty or prices.dropna(how='all').empty:
        raise NoDataError(f"No price data available for {start_date} to {end_date}")

    prices = prices.dropna(how='all')

    return prices
