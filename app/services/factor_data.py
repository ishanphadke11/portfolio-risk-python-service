import pandas as pd
from flask import current_app

class FactorDataError(Exception):
    pass

def load_factor_data(start_date, end_date, data_path=None):
    # load and clean fama french 5 factor data from local csv

    if data_path is None:
        data_path = current_app.config["FF_DATA_PATH"]

    try:
        df = pd.read_csv(data_path, skiprows=3, index_col=0)
    except FileNotFoundError:
        raise FactorDataError(f"Factor data file not found {data_path}")
    
    df.index = pd.to_datetime(df.index, format="%Y%m%d", errors="coerce")
    df = df.dropna(subset=[df.columns[0]])

    df = df / 100

    df = df.loc[start_date:end_date]

    if df.empty:
        raise FactorDataError(f"No factor data available for {start_date} to {end_date}")
    
    return df