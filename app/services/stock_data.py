import yfinance as yf
import pandas as pd
import time
import os
import diskcache

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


# Disk-backed cache — persists across service restarts, safe for multi-worker gunicorn
_CACHE_DIR = os.getenv("CACHE_DIR", "/tmp/stock_price_cache")
_cache = diskcache.Cache(_CACHE_DIR)
_CACHE_TTL = 86400  # 24 hours


def fetch_stock_prices(tickers, start_date, end_date):
    """
    Fetch closing prices for all tickers.

    Cached tickers are served from disk. All uncached tickers are fetched
    in a single yf.download() call — one API request regardless of portfolio size.
    """
    if not tickers:
        raise ValueError("Tickers list can't be empty")

    prices = {}
    uncached = []

    for ticker in tickers:
        series = _get_cached(ticker, start_date, end_date)
        if series is not None:
            prices[ticker] = series
        else:
            uncached.append(ticker)

    # Fetch all uncached tickers in ONE yfinance call instead of N separate calls
    if uncached:
        fetched = _batch_fetch(uncached, start_date, end_date)
        prices.update(fetched)

    if not prices:
        raise NoDataError(f"No price data available for {start_date} to {end_date}")

    result = pd.DataFrame({t: s for t, s in prices.items() if not s.empty})

    if result.empty or result.dropna(how='all').empty:
        raise NoDataError(f"No price data available for {start_date} to {end_date}")

    return result.dropna(how='all')


def _get_cached(ticker, start_date, end_date):
    """Return cached Close price series if still fresh, else None."""
    cache_key = (ticker, start_date, end_date)
    entry = _cache.get(cache_key)
    if entry is None:
        return None
    fetched_at, series = entry
    if time.time() - fetched_at > _CACHE_TTL:
        return None
    return series


def _store_cached(ticker, start_date, end_date, series):
    """Write a Close price series to the disk cache."""
    _cache.set((ticker, start_date, end_date), (time.time(), series))


def _batch_fetch(tickers, start_date, end_date):
    """
    Download all tickers in a single yfinance call with retry + exponential backoff.

    yf.download() with multiple tickers returns a MultiIndex DataFrame where
    raw['Close'] gives a DataFrame with one column per ticker.
    For a single ticker, raw['Close'] gives a plain Series.
    """
    max_attempts = 3
    last_error = None
    was_rate_limited = False

    for attempt in range(max_attempts):
        try:
            raw = yf.download(
                tickers if len(tickers) > 1 else tickers[0],
                start=start_date,
                end=end_date,
                auto_adjust=True,
                progress=False,
                threads=False,  # avoid spawning threads inside gunicorn workers
            )

            result = {}

            if len(tickers) == 1:
                ticker = tickers[0]
                if not raw.empty and 'Close' in raw.columns:
                    series = _normalize_index(raw['Close'].dropna())
                    _store_cached(ticker, start_date, end_date, series)
                    result[ticker] = series
            else:
                # Multi-ticker: raw['Close'] is a DataFrame with ticker columns
                if not raw.empty and 'Close' in raw.columns.get_level_values(0):
                    close_df = raw['Close']
                    for ticker in tickers:
                        if ticker in close_df.columns:
                            series = _normalize_index(close_df[ticker].dropna())
                            _store_cached(ticker, start_date, end_date, series)
                            result[ticker] = series

            return result

        except Exception as e:
            last_error = e
            if _is_rate_limit_error(e):
                was_rate_limited = True
                if attempt < max_attempts - 1:
                    time.sleep(2 ** attempt * 5)
            else:
                if attempt < max_attempts - 1:
                    time.sleep(2 ** attempt * 2)

    if was_rate_limited:
        raise RateLimitError("Yahoo Finance rate limit exceeded. Please try again in a few minutes.")
    if last_error:
        raise NoDataError(f"Failed to fetch price data: {str(last_error)}")
    raise NoDataError("Failed to fetch stock data")


def _normalize_index(series):
    """Strip timezone info so the date index aligns with factor data."""
    if hasattr(series.index, 'tz') and series.index.tz is not None:
        series.index = series.index.tz_localize(None)
    return series


def _is_rate_limit_error(e):
    if YFRateLimitError and isinstance(e, YFRateLimitError):
        return True
    msg = str(e).lower()
    return "429" in msg or "too many requests" in msg or "rate limit" in msg
