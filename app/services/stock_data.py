import yfinance as yf
import pandas as pd
import time

try:
    from yfinance.exceptions import YFRateLimitError
except ImportError:
    YFRateLimitError = None


class InvalidTickerError(Exception):
    pass


class NoDataError(Exception):
    pass


class RateLimitError(Exception):
    pass


def fetch_stock_prices(tickers, start_date, end_date):
    if not tickers:
        raise ValueError("Tickers list can't be empty")

    prices = {}

    for i, ticker in enumerate(tickers):
        # small delay between each ticker to avoid hitting Yahoo Finance rate limits
        if i > 0:
            time.sleep(0.5)
        prices[ticker] = _fetch_single_ticker(ticker, start_date, end_date)

    result = pd.DataFrame(prices)

    if result.empty or result.dropna(how='all').empty:
        raise NoDataError(f"No price data available for {start_date} to {end_date}")

    return result.dropna(how='all')


def _fetch_single_ticker(ticker, start_date, end_date):
    max_attempts = 3
    last_error = None
    was_rate_limited = False

    for attempt in range(max_attempts):
        try:
            data = yf.Ticker(ticker).history(start=start_date, end=end_date, auto_adjust=True)

            if not data.empty and 'Close' in data.columns:
                series = data['Close']
                # strip timezone so index aligns with factor data
                if series.index.tz is not None:
                    series.index = series.index.tz_localize(None)
                return series

        except Exception as e:
            last_error = e
            if _is_rate_limit_error(e):
                was_rate_limited = True
                if attempt < max_attempts - 1:
                    time.sleep(2 ** attempt * 5)
            else:
                if attempt < max_attempts - 1:
                    time.sleep(2 ** attempt * 2)
            continue

    if was_rate_limited:
        raise RateLimitError("Yahoo Finance rate limit exceeded. Please try again in a few minutes.")
    if last_error:
        raise NoDataError(f"Failed to fetch data for {ticker}: {str(last_error)}")
    raise InvalidTickerError(f"Invalid ticker or no data: {ticker}")


def _is_rate_limit_error(e):
    if YFRateLimitError and isinstance(e, YFRateLimitError):
        return True
    msg = str(e).lower()
    return "429" in msg or "too many requests" in msg or "rate limit" in msg
