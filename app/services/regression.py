import pandas as pd
import statsmodels.api as sm

class RegressionError(Exception):
    pass

def run_factor_regression(alligned_data):

    # run OLS regression of portfolio excess returns 
    # against fama french 5 factors

    y = alligned_data['portfolio_excess_return']
    x = alligned_data[['Mkt-RF', 'SMB', 'HML', 'RMW', 'CMA']]

    x = sm.add_constant(x)

    if len(y) < 30:
        raise RegressionError(f"Not enough data points for regression: {len(y)} (need at least 30)")
    
    model = sm.OLS(y, x)
    results = model.fit()

    return results

def format_regression_results(results):
      
    #Extract and format regression results for the Spring Boot backend.
    params = results.params
    t_stats = results.tvalues

    return {
        "alpha": round(float(params['const']), 6),
        "betaMkt": round(float(params['Mkt-RF']), 6),
        "betaSmb": round(float(params['SMB']), 6),
        "betaHml": round(float(params['HML']), 6),
        "betaRmw": round(float(params['RMW']), 6),
        "betaCma": round(float(params['CMA']), 6),
        "rSquared": round(float(results.rsquared), 6),
        "tStats": {
            "alpha": round(float(t_stats['const']), 4),
            "mkt": round(float(t_stats['Mkt-RF']), 4),
            "smb": round(float(t_stats['SMB']), 4),
            "hml": round(float(t_stats['HML']), 4),
            "rmw": round(float(t_stats['RMW']), 4),
            "cma": round(float(t_stats['CMA']), 4),
          }
      }

