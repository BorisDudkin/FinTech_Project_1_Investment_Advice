import pandas as pd

def get_breakdowns(df, column):
    df_name = column+"_df"
    df_name=df.groupby([column])['weights'].sum()
    df_name=df_name.to_frame('weights')
    df_name=df_name.loc[df_name['weights']>0]
    df_name=df_name.sort_values('weights', axis = 0, ascending=False)
    return df_name
        
def get_sector_industry_weights(portfolios_df, sectors_mapping_df):
    # Set Ticker as index:
    sectors_mapping_df=sectors_mapping_df.reset_index()
    portfolios_df=portfolios_df.reset_index()
    portfolios_df.columns = ['Ticker', 'weights']
    portfolios_df=portfolios_df.set_index('Ticker')
    sectors_mapping_df=sectors_mapping_df.set_index('Ticker')   
       
    # concatenate dataframes and get weights by groupping by sectors and names:
    all_df=pd.concat([sectors_mapping_df, portfolios_df], axis=1)
    all_df=all_df.loc[all_df['weights']>0]
    all_df=all_df.sort_values('weights', axis = 0, ascending=False)
    all_columns=all_df.columns.values.tolist()[:-1]
    
    breakdown_list=[get_breakdowns(all_df, column) for column in all_columns]
    breakdown_list.append(all_df)
    
    return breakdown_list