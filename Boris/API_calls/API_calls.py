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
def get_api_data(tickers, days, timeframe='1Day'):
   
    #separate crypto and non-crypto tickers:
    crypto_tickers=[]
    for ticker in tickers:
        if len(ticker)>3 and ticker[3]=="-":
            crypto_tickers.append(ticker)
    
    other_tickers = [ticker for ticker in tickers if ticker not in crypto_tickers]       
    
    # NON-CRYPTO PART
    # The Alpaca Parameters for timeframe and daterange
    # `today` is a timestamp using Pandas Timestamp
    # `a_year_ago` is calculated using Pandas Timestamp and Timedelta
    timeframe = timeframe
    start_date = datetime.date.today() - datetime.timedelta(days=int(days))
    end_date = datetime.date.today() - datetime.timedelta(days=int(1))

    # The Alpaca tradeapi.REST object
    alpaca = tradeapi.REST(
        alpaca_api_key,
        alpaca_secret_key,
        api_version="v2")

    # Use the Alpaca get_bars function to get the closing prices for the stocks.
    portfolio_prices_df = alpaca.get_bars(
        other_tickers,
        timeframe,
        start=start_date,
        end=end_date
    ).df
    
    portfolio_prices_df.index=portfolio_prices_df.index.date
    # For the new closing_prices_df DataFrame, keep only the date component
    # portfolio_prices_df.index = portfolio_prices_df.index.date
    # Reorganize the DataFrame to have a MultiIndex.
    dfs = [
        portfolio_prices_df[portfolio_prices_df['symbol']==symbol].drop('symbol', axis=1)
        for symbol in other_tickers
    ]
    prices_Monte_Carlo_df = pd.concat([x for x in dfs], axis=1, keys=other_tickers)
        
    # CRYPTO PART
    # Setup instance of Alpaca API for crypto
    rest_api = tradeapi.REST(alpaca_api_key, alpaca_secret_key,'https://paper-api.alpaca.markets')
    
    #create a list for dataframes for crypto calls
    dfs=[]   
    for symbol in crypto_tickers:
        symbol = symbol.replace("-", "")
        symbol = rest_api.get_crypto_bars(symbol, TimeFrame.Day, start_date, end_date).df
        symbol=symbol[symbol['exchange']=='CBSE']
        symbol=symbol.drop('exchange', axis=1)
        dfs.append(symbol)
    
    crypto_df = pd.concat(dfs, axis=1, keys=crypto_tickers)
    crypto_df.index=crypto_df.index.date
    
    # merge non-crypto and crypto parts:
    total_df=prices_Monte_Carlo_df.merge(crypto_df, how='inner', left_index=True, right_index=True)
    total_df=total_df.dropna()
    total_df = total_df.drop_duplicates()
    
    return total_df

