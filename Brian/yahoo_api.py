from dotenv import load_dotenv
import os
import http.client
import json
import pandas as pd
class yahoo_api:
    def yahoo_api_call(ticker,interval='1d'):
        env_check=load_dotenv()
        if env_check==False:
            print("Error- No .env file was found. Please make a .env file in this directory with your X-RapidAPI Key.")
        load_dotenv()
        headers= {
        'X-RapidAPI-Key': os.getenv("X-RapidAPI-Key"),
        'X-RapidAPI-Host': "mboum-finance.p.rapidapi.com"
        }
        conn = http.client.HTTPSConnection("mboum-finance.p.rapidapi.com")

        conn.request("GET", f"/hi/history?symbol={ticker}&interval={interval}&diffandsplits=false", headers=headers)

        res = conn.getresponse()
        data = res.read()
        results=data.decode("utf-8")
        dictionary=json.loads(results)
        items=dictionary['items']
        dataframe=pd.DataFrame(items).T.set_index('date').drop(columns=['date_utc','adjclose'])
        return(dataframe)
    
    def dataframe_maker(weights):
        weights={x:y for x,y in weights.items() if y!=0} #Removes any tickers with zero weight before making the API call
        weight_series=pd.Series(weights) #Converts the weights dictionary to a series
        tickers_list=list(weight_series.index) #Creates a list of ticker names
        dataframe_list=[] #Creating an empty list to hold a dataframe for each ticker called
        for ticker in tickers_list:
            dataframe_list.append(yahoo_api_call(ticker))  #Uses the previous function to make a dataframe for each ticker, then puts each dataframe in a list.
        df_historical=pd.concat(dataframe_list,axis=1,keys=tickers_list) #Joins each dataframe in the list into one, and labels them according to the tickers
        df_historical.dropna(how='any',inplace=True) #Drops missing values
        close_values=[] #An empty list to hold close values
        for ticker in tickers_list: 
            close_values.append(df_historical[ticker]['close']) #Adding the close column to the list
        close_df=pd.DataFrame(close_values).T #Creating a dataframe of close values
        close_df.columns=tickers_list #Giving the ticker names to the columns
        daily_returns=close_df.pct_change().dropna()
        weighted_daily_returns=daily_returns*weight_series
        return({'Historical prices':df_historical,'Historical close prices':close_df,'Daily returns':daily_returns,'Weighted daily returns':weighted_daily_returns})