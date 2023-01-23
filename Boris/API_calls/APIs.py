# A Database CLI Application

# Import modules
import pandas as pd
import os
import alpaca_trade_api as tradeapi
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Set the variables for the Alpaca API and secret keys
alpaca_api_key = os.getenv("ALPACA_API_KEY")
alpaca_secret_key = os.getenv("ALPACA_SECRET_KEY")
def get_closing_prices(symbols, start, end):

    # The Alpaca Parameters for timeframe and daterange
    # `today` is a timestamp using Pandas Timestamp
    # `a_year_ago` is calculated using Pandas Timestamp and Timedelta
    timeframe = '1Day'
    start_date = pd.Timestamp(start, tz="America/New_York").isoformat()
    end_date = pd.Timestamp(end, tz="America/New_York").isoformat()

    # The Alpaca tradeapi.REST object
    alpaca = tradeapi.REST(
        alpaca_api_key,
        alpaca_secret_key,
        api_version="v2")

    # Use the Alpaca get_bars function to get the closing prices for the stocks.
    portfolio_prices_df = alpaca.get_bars(
        symbols,
        timeframe,
        start=start_date,
        end=end_date
    ).df
    
    # For the new closing_prices_df DataFrame, keep only the date component
    # portfolio_prices_df.index = portfolio_prices_df.index.date
    # Reorganize the DataFrame to have a MultiIndex.
    dfs = [
        portfolio_prices_df[portfolio_prices_df['symbol']==symbol].drop('symbol', axis=1)
        for symbol in symbols
    ]
    prices_df_Monte_Carlo = pd.concat([x for x in dfs], axis=1, keys=symbols)
    
    # Create an empty DataFrame for holding the closing prices
    closing_prices_df = pd.DataFrame()
    for symbol in symbols:
        closing_prices_df[symbol] = portfolio_prices_df['close'][portfolio_prices_df['symbol']==symbol]

    return (prices_df_Monte_Carlo, closing_prices_df)
