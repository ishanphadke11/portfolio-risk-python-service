import yfinance as yf
import pandas as pd
import time

class InvalidTickerError(Exception):
    pass

class NoDataError(Exception):
    pass

def fetch_stock_prices(tickers, start_date, end_date):
    # fetch adjusted stock prices for given tickers from yahoo finance

    if not tickers:
        raise ValueError("Tickers list can't be empty")

    # Yahoo Finance rate-limits requests from cloud provider IPs (like Render).
    # We retry up to 3 times with increasing delays to work around transient 429 errors.
    max_attempts = 3
    last_error = None

    for attempt in range(max_attempts):
        try:
            data = yf.download(
                tickers,
                start=start_date,
                end=end_date,
                progress=False,
                auto_adjust=True
            )

            # If we got data, break out of the retry loop
            if not data.empty:
                break

        except Exception as e:
            last_error = e
            # Wait before retrying: 2s, then 4s, then give up
            if attempt < max_attempts - 1:
                time.sleep(2 ** attempt * 2)
            continue

        # If data is empty on this attempt, wait and retry
        if data.empty and attempt < max_attempts - 1:
            time.sleep(2 ** attempt * 2)
    else:
        # All attempts exhausted
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
