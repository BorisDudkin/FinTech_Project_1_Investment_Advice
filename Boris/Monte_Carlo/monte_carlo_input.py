import pandas as pd

def get_MC_input(Monte_Carlo_df, portfolios, portfolio):
    
    # select the portfolio from four portfolios df
    portfolio_df=portfolios.loc[:,portfolio]
    
    # select non-zero elements
    portfolio_df=portfolio_df[portfolio_df > 0]
    
    # rename the column to weights
    portfolio_df=portfolio_df.to_frame('weights')
    
    # get the list of tickers
    symbols=list(portfolio_df.index)
    
    # get the list of weights
    weights=list(portfolio_df['weights'])
    
    # get prices df only for tickers in the selected portfolio
    MC_df=Monte_Carlo_df.loc[:,symbols]
    
    return [MC_df, weights]