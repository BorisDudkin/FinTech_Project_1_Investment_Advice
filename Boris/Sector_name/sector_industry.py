import pandas as pd


def get_breakdowns(df, column):

    """for each indicator (sector, industry, investment style, name) geneartes groupby summing by weights

    Args:
        df (daataframe): dataframe of the full information inclding sectors, industry, investment styles and names for all the tickers in the seelcted portfolio
        column (str): sector, industry, investment style, name

    Returns:
        A dataframe with weights grouped by one of the indicators (sector, industry, investment style, name) as as sum

    """

    df_name = column+"_df"
    df_name=df.groupby([column])['weights'].sum()
    df_name=df_name.to_frame('weights')
    df_name=df_name.loc[df_name['weights']>0]
    df_name=df_name.sort_values('weights', axis = 0, ascending=False)
    return df_name
        
def get_sector_industry_weights(portfolios_df, sectors_mapping_df):

    """generates breakdowns by sector, industry, investment style and company/etf names

    Args:
        portfolios_df (daataframe): a dataframe of the selected portolio (assets and weights)
        sectors_mapping_df (daataframe): a dataframe of sector, industry, investment style and compay/etf name for each tickeer in our investment universe

    Returns:
        A list of breakdowns by sector, industry, investment style, company/etf name for a selected portfolio

    """
        
    # Set Ticker as index:
    sectors_mapping_df=sectors_mapping_df.reset_index()
    portfolios_df=portfolios_df.reset_index()
    portfolios_df.columns = ['Ticker', 'weights']
    portfolios_df=portfolios_df.set_index('Ticker')
    sectors_mapping_df=sectors_mapping_df.set_index('Ticker')   
       
    # concatenate dataframes and get weights by groupping by sectors and names:
    all_df=pd.concat([sectors_mapping_df, portfolios_df], axis=1)
    #selects assets for whcih weights are not equal to 0
    all_df=all_df.loc[all_df['weights']>0]
    all_df=all_df.sort_values('weights', axis = 0, ascending=False)
    #creates a list of column names for further list comprehansion (industry, investment style, name)
    all_columns=all_df.columns.values.tolist()[:-1]
    
    #using get_breakdowns function above create a list of breakdown by sector, industry, ticker name and market cap
    breakdown_list=[get_breakdowns(all_df, column) for column in all_columns]
    breakdown_list.append(all_df)
    
    return breakdown_list