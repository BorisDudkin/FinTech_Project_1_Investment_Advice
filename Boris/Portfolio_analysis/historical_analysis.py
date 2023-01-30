# Import Pandas and Numpy library
import pandas as pd
import numpy as np


def get_historical_analysis(daily_returns_df, portfolios_df, trading_days):
    trading_days = 252
    #this might not be needed later
    symbols = list(portfolios_df.index)
    
    #clean the data for stock splits by removing 100% changes
    # daily_returns_df[daily_returns_df<=-0.5]=0

    # construct prices only for assets in our portfolios dataframe:
    daily_returns_df=daily_returns_df.loc[:,symbols]

    #number of observations:
    n_days=len(daily_returns_df.index)
    years=int(round(n_days/trading_days))
    #adjust n_days to exct number of years
    n_days_analysis=years*trading_days

#     # select dataframe for exact number of years:
    daily_returns_df=daily_returns_df.iloc[-n_days_analysis:,:]


    # Calculate the cumulative returns for all assets in our portfolios
    # NOTE: this will be our first return value!
    cumulative_returns_assets =  (1 + daily_returns_df).cumprod()

    # Create wegihted portfolio retruns by applying .dot to daily asseet retruns and their weights:
    weighted_returns_portfolio=daily_returns_df.dot(portfolios_df)

    # Calculatethe cumulative returns of the 4 portfolios
    # NOTE: this will be our first return value!
    cumulative_returns_portfolios =  (1 + weighted_returns_portfolio).cumprod()

    returns_list=[]
    col_list=[]
    for i in range(1, years+1):
        weighted_returns=weighted_returns_portfolio.iloc[-i*trading_days:,:]
        cum_returns_portfolios =  (1 + weighted_returns).cumprod()
        df=(cum_returns_portfolios.iloc[-1,:]-1)*100
        returns=str(i)+'Y Returns in %'
        # df=df.reset_index()
        df.columns = [returns]
        # df.set_index('Portfolio')
        returns_list.append(df)
        col_list.append(returns)
    returns_list   
    col_list

    df_retuns=pd.concat(returns_list, axis=1)
    df_retuns.columns=col_list


    # Section Risk Analysis
    # Calculate and sort the standard deviation for all 4 portfolios and the S&P 500
    standard_deviation = weighted_returns_portfolio.std()

    # Calculate and sort the annualized standard deviation (252 trading days) of the 4 portfolios
    
    annualized_standard_deviation = standard_deviation * np.sqrt(trading_days)

    # Calculate the annual average return data for the for fund portfolios
    # Use 252 as the number of trading days in the year
    average_annual_funds_daily_returns = weighted_returns_portfolio.mean()*trading_days
    average_annual_funds_daily_returns

    # Calculate the annualized Sharpe Ratios for each of the 4 portfolios.
    sharpe_ratio = average_annual_funds_daily_returns / annualized_standard_deviation
    SR_df=sharpe_ratio.to_frame()
    SR_df.columns= ['Sharpe Ratio']
    results=pd.concat([df_retuns, SR_df], axis=1)
    
    return [results, cumulative_returns_portfolios, cumulative_returns_assets, years]

