import pandas as pd

def calculate_stock_returns(prices):
    returns = prices.pct_change().dropna(how='all')
    return returns

def calculate_portfolio_weights(holdings, prices):
    quantities = {h['ticker']: h['quantity'] for h in holdings}

    dollar_values = prices.multiply(
        pd.Series(quantities)
    )

    total_value = dollar_values.sum(axis=1)
    weights = dollar_values.div(total_value, axis=0)

    return weights

def calculate_portfolio_returns(holdings, prices):
    returns = calculate_stock_returns(prices)
    weights = calculate_portfolio_weights(holdings, prices)

    weights = weights.loc[returns.index]

    portfolio_returns = (returns * weights).sum(axis=1)

    return portfolio_returns

def allign_data(portfolio_returns, factor_data):
    combined = pd.DataFrame({
        'portfolio_return': portfolio_returns
    }).join(factor_data, how='inner')

    combined['portfolio_excess_return'] = combined['portfolio_return'] - combined['RF']

    combined = combined.drop(columns=['portfolio_return', 'RF'])

    return combined