import pandas as pd


def get_MC_input(Monte_Carlo_df, portfolios, portfolio):
    """Determines two inputs for instanciating the Monte Carlo class

    Args:
        Monte_Carlo_df (daataframe): prices from API call containing all tickers in our universe of portfolios
        portfolios (daataframe): four portfolios selected for analysis
        portfolio (str): a specific portfolio for which Monte Carlo class is to be instantiated

    Returns:
        A list of adjusted for the selected portfolio prices dataframe and the corresponding list of weights

    """
    
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