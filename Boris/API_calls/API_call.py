# A Database CLI Application

# Import modules
import pandas as pd
import os
from dotenv import load_dotenv
import datetime
import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import REST, TimeFrame



# Load .env file
load_dotenv()

# Set the variables for the Alpaca API and secret keys
alpaca_api_key = os.getenv("ALPACA_API_KEY")
alpaca_secret_key = os.getenv("ALPACA_SECRET_KEY")
def get_closing_prices(symbols, days):

    # The Alpaca Parameters for timeframe and daterange
    # `today` is a timestamp using Pandas Timestamp
    # `a_year_ago` is calculated using Pandas Timestamp and Timedelta
    timeframe = '1Day'
    start_date = datetime.date.today() - datetime.timedelta(days=int(days))
    end_date = datetime.date.today() - datetime.timedelta(days=int(1))

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

    return (prices_df_Monte_Carlo)

def get_crypto(symbols, days):
    # Setup instance of Alpaca API
    rest_api = tradeapi.REST(alpaca_api_key, alpaca_secret_key,'https://paper-api.alpaca.markets')
    
    # Start and end dates for historical data
    start_date = datetime.date.today() - datetime.timedelta(days=int(days))
    end_date = datetime.date.today() - datetime.timedelta(days=int(1))
    
    dfs=[]   
    for symbol in symbols:
        symbol = symbol.replace("-", "")
        symbol = rest_api.get_crypto_bars(symbol, TimeFrame.Day, start_date, end_date).df
        symbol=symbol[symbol['exchange']=='CBSE']
        symbol=symbol.drop('exchange', axis=1)
        dfs.append(symbol)
        
    # Retrieve daily price data for BTC and ETH cryptocurrencies
#     BTC = rest_api.get_crypto_bars("BTCUSD", TimeFrame.Day, start_date, end_date).df
#     ETH = rest_api.get_crypto_bars("ETHUSD", TimeFrame.Day, start_date, end_date).df
    
    
#     ETH=ETH[ETH['exchange']=='CBSE']
#     BTC=BTC[BTC['exchange']=='CBSE']
    
#     ETH=ETH.drop('exchange', axis=1)
#     BTC=BTC.drop('exchange', axis=1)
    crypto_symbols=['BTC-USD','ETH-USD']
    crypto_df = pd.concat(dfs, axis=1, keys=crypto_symbols)
                       
    return crypto_df