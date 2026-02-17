import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

class InvalidTickerError(Exception):
    pass

class NoDataError(Exception):
    pass

def fetch_stock_prices(tickers, start_date, end_date):
    # fetch adjusted stock prices for given tickers from yahoo finance

    if not tickers:
        raise ValueError("Tickers list can't be empty")
    
    
    #Download data
    data = yf.download(tickers, start=start_date, end=end_date, progress=False, auto_adjust=True)

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

    # Drop rows where all values are NaN
    prices = prices.dropna(how='all')

    return prices