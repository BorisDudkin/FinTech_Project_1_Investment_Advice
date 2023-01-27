import pandas as pd

def get_MC_input(Monte_Carlo_df, portfolios, portfolio, init_investment, invest_period):
    portfolio_df=portfolios.loc[:,portfolio]
    portfolio_df=portfolio_df[portfolio_df > 0]
    portfolio_df=portfolio_df.to_frame('weights')
    symbols=list(portfolio_df.index)
    weights=list(portfolio_df['weights'])
    MC_df=Monte_Carlo_df.loc[:,symbols]
    return [MC_df, weights, init_investment, invest_period]