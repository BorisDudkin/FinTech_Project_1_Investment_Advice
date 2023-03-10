import pandas as pd
import sqlalchemy
import streamlit as st
import sys
import os
from dotenv import load_dotenv
import datetime
import time
import alpaca_trade_api as tradeapi
from alpaca_trade_api.rest import REST, TimeFrame
from pathlib import Path

import plotly.graph_objects as go
import plotly.express as px

import holoviews as hv
import hvplot.pandas
import hvplot
from bokeh.models import HoverTool

sys.path.append('..\\Boris\\')
sys.path.append('..\\Adam\\')

# import math
from yahoo_api import yahoo_api_call
from Score_calculator.questionnaire_st import get_bucket
from Sector_name.sector_industry import get_sector_industry_weights
from Static_data.static_data import step, capacity_questions, n_days, timeframe
from Monte_Carlo.monte_carlo_input import get_MC_input
# from API_calls.API_calls import get_api_data
from MonteCarlo.MonteCarloEdited import MCSimulation

#create internet page name
st.set_page_config(page_title="Investment Advisor 💰", layout='wide')

# Section 1: Establishing database connection for extracting data:
# 1) Create Database connection string to a database where questionnaires, weights, portfolios and securitiy deail tables are stored (position data)
database_connection_string = 'sqlite:///Resources/investor.db'

# 2) Create an engine to interact with the database
engine = sqlalchemy.create_engine(database_connection_string)

# Section 2: Create a set up for ALPACA API Calls:
# Load .env file
load_dotenv()

# Set the variables for the Alpaca API and secret keys
alpaca_api_key = os.getenv("ALPACA_API_KEY")
alpaca_secret_key = os.getenv("ALPACA_SECRET_KEY")

# st.cache enhances the performance of the app in the following way: 
# If Streamlit runs the function for the first time and stores the result in a local cache.
# Then, next time the function is called, if the function nae, its body and parameters have not changed Streamlit knows it can skip executing the function altogether. 
# Instead, it just reads the output from the local cache and passes it on to the caller.
# Call api to fetch market data
@st.cache
def get_api_data(weights_df):
    if isinstance(weights_df,pd.DataFrame): #Checks that the input is a dataframe
        tickers_list=list(weights_df.index) #Converts the index to a list
    elif isinstance(weights_df,list): #Checks that the input is a list
        tickers_list=weights_df
    dataframe_list=[] #This list will hold the dataframes resulting from the api call
    api_calls_made=0 #Creates a variable to set the number of api calls
    for ticker in tickers_list: #For each ticker, checks if there have been less than 10 calls made and will call the api. Then, will update the number of calls. When it gets too high, the loop will stop for 100 seconds before continuing.
        if api_calls_made<10:
            dataframe_list.append(yahoo_api_call(ticker))
            api_calls_made+=1
        else:
            time.sleep(100)
            print("Waiting 100 seconds to avoid overloading the API")
            dataframe_list.append(yahoo_api_call(ticker))
            api_calls_made=1
    df_historical=pd.concat(dataframe_list,axis=1,keys=tickers_list) #Builds the dataframe from the list
    df_historical.dropna(how='any',inplace=True) #Removes na values
    df_historical=df_historical[~(df_historical==0).any(axis=1)] #Removes rows with any zero values
    column_names=list(df_historical)
    close_column_names=[]
    for tup in column_names:
        if 'close' in tup:
            close_column_names.append(tup)
    ticker_names=[]
    for tup in close_column_names:
        ticker_names.append(tup[0])
    close_returns_df=df_historical[close_column_names].pct_change().dropna()
    close_returns_df.columns=ticker_names
    return(df_historical,close_returns_df)

# the function below transforms db tables to dataframes for further processing:
def read_table_to_df(table, engine):
    return pd.read_sql_table(table, con=engine)

# Section 3: upload relevant tables to dataframes for further analysis
capacity_tables=capacity_questions
risk_capacity=[]
for table in capacity_tables:
    pd_name= table+"_df"
    pd_name = read_table_to_df(table, engine)
    pd_name=pd_name.set_index('Questions')
    risk_capacity.append(pd_name)
         
# read tolerance questionnaire into a dataframes risk_tolerance:
risk_tolerance_df =  read_table_to_df('risk_tolerance_questions', engine)
risk_tolerance_df=risk_tolerance_df.set_index('Questions')

# read portfolios into a portfolios_df dataframe:
portfolios_df =  read_table_to_df('portfolios', engine)
portfolios_df=portfolios_df.set_index('Risk_tolerance')

# read sectors into a sectors_mapping_df dataframe:
sectors_mapping_df =  read_table_to_df('sector_mapping', engine)
sectors_mapping_df=sectors_mapping_df.set_index('Sector')

# Section 4: create an API call and store Monte Carlo input data and daily returns data for the set of our portfolios
tickers_api_call = portfolios_df.columns.to_list()
api_call_df, daily_returns_df=get_api_data(tickers_api_call)


# Section 5 - GAtheering data from an investor and generating risk scores (capacity score and tolerance score based on the answers to the questionnaires
# will display the questionnaire to determine the risk tolearance and risk capacity profiles of an investor:

with st.sidebar:
    
    st.header('Questionnaire:')
    
    st.subheader('Initial investment')
    initial_investment = st.number_input('How much money would you like to invest (in USD)?', min_value=500, value=500, step=500)

    st.subheader('Investment time horizon')
    time_horizon = int(st.number_input('What is your planned investment time horizon (in years)?', value = 1, step=1))
    
    st.subheader('Select between 0 and 1, where: 0 is Strongly Disagree and  1 is Strongly Agree')
    i=0
    t_score=0
    for question in risk_tolerance_df.index:
        score = st.slider(question, 0.0, 1.0, 0.2)
        t_score+=score
    
    st.subheader('Select one answer for each question below:')
    i=0
    c_score=0
    for question in risk_capacity:
        resp=st.radio(question.index[0], tuple(list(question)))
        score= question.loc[question.index[0],resp]
        c_score+=score

# based on the answrs calculate capacity risk and tolerance risk scores based on the answeres of the investor and generates two portfolios based on those scores:

# tolerance_score= round((score_1+score_2+score_3+score_4+score_5)/len(risk_tolerance_df.index),2)
tolerance_score=round(t_score/len(risk_tolerance_df.index),2)
tolerance=get_bucket(tolerance_score, step)
# capacity_score= round((cap_score_1+cap_score_2+cap_score_3+cap_score_4+cap_score_5)/len(risk_capacity),2)
capacity_score= round(c_score/len(risk_capacity),2)
capacity=get_bucket(capacity_score, step)

# Section 6: Display output:
# Create four tabs to display our application as per below breakdown
tab1, tab2, tab3, tab4 = st.tabs(['About','Portfolios','Past Performance','Future Projected Returns'])

# Section 6.1 Introduction: 
#tab 1 will contain an introduction:
with tab1:
    col1,col2=st.columns([1,9])
    with col1: 
        st.image('../Images/broker.png',use_column_width='Auto')
    with col2:
        st.title('Investment Advisor')

    st.header('About This Application')

    my_text = "The Investment Advisor application will assess an investor's risk tolerance and his/her's capacity to absorb risk. Based on those evaluations, two corresponding risk scores will be calculated and associated investment portfolios will be chosen from our ETFs offering. Their performance will be assessed and compared to the Benchmark portfolio of 40% Bonds 60% Stock. To increase clients' awareness of our new Crypto mix ETF, we will include the comparison performance of this fund too."

    st.write(my_text)

    with st.expander("About Us"):
        st.write("We offer our clients a tailored approach to constructing an investment portfolio based on their risk tolerance and personal cicumstances to absorb the risk arising from the investment activities.")

    with st.expander("Funds Description and Risk profile"):
        st.write("Assets in our funds range from High Growth and Crypto to Value stocks and Fixed Income securities of Long term and Short-term maturities. Each fund is constructed with the risk profile of an investor in mind. Our funds are non-diversified and may experience greater volatility than more diversified investments. To compensate for the limited diversification, we only offer Large Cap US equities and Domestic stocks and bonds to reduce volatility brought by small- and medium-cap equities and excluding foreign currency exposure. And yet, there will always be risks involved with ETFs' investments, resulting in the possible loss of money.")

# Section 6.2 - Creating a subset of portfolios for the investor's review based on the above scores.
# In addition to the capacity risk and tolerance risk based portfolios, cryptomix new etf and the benchmark fund will be added for further analysis:

#tab 2 will display the selected portfolios and their composition (an option to select a portfolio for detailed review will be given to the investor):

with tab2:
    
    col1,col2=st.columns([1,9])
    with col1: 
        st.image('../Images/pie.png',use_column_width='Auto')
    with col2:
        st.title('The scores and the corresponding selected portfolios:')
   
    st.subheader('Scores Assessment:')

    st.write(f'With the risk scores progressing from the most conservative (score 0) to the highest risk (score 1) you scored **:blue[{capacity_score}]** on your _capacity to absorb risk_ and **:blue[{tolerance_score}]** on your _risk tolerance_')
    st.write("Based on these scores, we created **:blue[Risk Capacity]** and **:blue[Risk Tolerance]** portfolios. To provide a **:blue[Benchmark]**, we included our 40/60 bonds to stocks traditional portfolio in our analysis.")
    st.write("Finally, a new Crypto enhanced portfolio **:blue[Cryptomix]** will help investors analyse how an addition of digital assets can affect the portfolio performance")

    # create two list of all portfolios for comparison (one for selecting the portfolios from the portfolios_df and one for aggregating into a new dataframe of four portfolios for further financial analysis
    # tolerace and capacity represent the buckets we received from the get_capacity_score function above
    portfolio_mix = [capacity, tolerance, 'benchmark', 'cryptomix']
    four_portfolios=['Risk Capacity', 'Risk Tolerance', 'Benchmark', 'Cryptomix']

    # create portfolio list to store selectd portfolios + benchmark + cryptomix portfolio
    portfolios_list=[portfolios_df.loc[risk_indicator,:] for risk_indicator in portfolio_mix]

    st.subheader('Selected portfolios including the new Cryptomix portfolio and the Benchmark:')

    # create dataframe to store selectd portfolios + benchmark + cryptomix portfolio
    four_portfolios_df= pd.concat(portfolios_list, axis=1, ignore_index=False)
    four_portfolios_df.columns = four_portfolios
    four_portfolios_df=four_portfolios_df.loc[(four_portfolios_df!=0).any(axis=1)]
    # st.table(four_portfolios_df)

    
    # create portfolios_info list that shores sector, industry and names breakdowns per selected portfolios
    portfolios_info= [get_sector_industry_weights(portfolio, sectors_mapping_df) for portfolio in portfolios_list]

    #create a dictionary that will store sector, industry, market cap name breakdown dataframes:
    four_portfolios_dict=dict(zip(four_portfolios, portfolios_info))
    
    #creating a plotly figure of breakdown by company/etf name for each selected portfolio and store in plotly_portfolio_figures
    plotly_portfolio_figures=[]
    for portfolio in four_portfolios:
        fig_name= 'fig_name_'+portfolio
        Name_breakdown_df = four_portfolios_dict[portfolio][sectors_mapping_df.columns.to_list().index('Name')+1].reset_index()
        fig_name=px.pie(Name_breakdown_df, names = 'Name', values='weights',title=f'<b>{portfolio} Portfolio by Company/ETF Name<b>')
        plotly_portfolio_figures.append(fig_name)
    
    #display four portfolios breakdowns by company/ETF name:

    col1,col2,col3,col4 = st.columns(4)
    
    with col1:
        st.plotly_chart(plotly_portfolio_figures[0],use_container_width=True)
    with col2:
        st.plotly_chart(plotly_portfolio_figures[1],use_container_width=True)
    with col3:
        st.plotly_chart(plotly_portfolio_figures[2],use_container_width=True)
    with col4:
        st.plotly_chart(plotly_portfolio_figures[3],use_container_width=True)
    

    portfolio_selection = st.selectbox("Select the portfolio to analyze:", tuple(four_portfolios))
    
    #get dataframes for each breakdown characteristic - sector, Industry, Name, Market Cap, based on the sectors_mapping_df (constrcuted from our mapping table) and pull data from the dictionary by the index of the breakdown identifier (i.e. Industry). Note: total breakdown by sector is located first in the portfolios_info and therefore has an index of 0:
    sector_breakdown_df = four_portfolios_dict[portfolio_selection][0]
    Industry_breakdown_df = four_portfolios_dict[portfolio_selection][sectors_mapping_df.columns.to_list().index('Industry')+1]
    Name_breakdown_df = four_portfolios_dict[portfolio_selection][sectors_mapping_df.columns.to_list().index('Name')+1]
    Market_cap_breakdown_df = four_portfolios_dict[portfolio_selection][sectors_mapping_df.columns.to_list().index('Market Cap & Style')+1]
    
    #creating plotly charts for each breakdown
    Name_breakdown_df=Name_breakdown_df.reset_index()
    fig_name_breakdown=px.pie(Name_breakdown_df, names = 'Name', values='weights',title='<b>by Company/ETF Name<b>')
    
    sector_breakdown_df=sector_breakdown_df.reset_index()
    fig_sector_breakdown=px.pie(sector_breakdown_df, names = 'Sector', values='weights',title='<b>by Sector<b>')
    
    Industry_breakdown_df=Industry_breakdown_df.reset_index()
    fig_industry_breakdown=px.pie(Industry_breakdown_df, names = 'Industry', values='weights',title='<b>by Industry<b>')
    
    Market_cap_breakdown_df=Market_cap_breakdown_df.reset_index()
    fig_market_cap_breakdown=px.pie(Market_cap_breakdown_df, names = 'Market Cap & Style', values='weights',title='<b> by Market Cap<b>')
       
    st.subheader('Portfolio Composition:')
    
    #display charts
    # st.plotly_chart(fig_name_breakdown,use_container_width=True)
    
    # st.write('**Portfolio composition by**:')
    col1, col2, col3= st.columns(3)
    with col1:
        st.plotly_chart(fig_sector_breakdown,use_container_width=True)                  
    with col2:
        st.plotly_chart(fig_industry_breakdown,use_container_width=True)
    with col3:
        st.plotly_chart(fig_market_cap_breakdown,use_container_width=True)
    # with col4:
    #     # st.write('**:blue[Market Cap & Style]**')
    #     # st.table(Market_cap_breakdown_df)
    #     st.plotly_chart(fig_name_breakdown,use_container_width=True)
   
    #select the last element in the breakdown list that contains the dataframe of all the fund characteristics:
    st.write('**Summary Table**')
    st.table(four_portfolios_dict[portfolio_selection][-1])

# Section 6.3

# Section 6.4 Monte Carlo Simulation
# inputs to Monte Carlo instance:
# portfolios df: four_portfolios_df; initial investment: initial_investment; time horizon: time_horizon 

# get_MC_input function creates a list of inputs to create a Monte Carlo class instance, where:
# Monte_Carlo_df: dataframe of prices;
# four_portfolios_df: dataframe of our selected portfolios - in the function it will be used to get weights input to Monte Carlo class;
# portfolio: we create an instance for each portfolio and also use portfolio tickers to select price data from Monte_Carlo_df
#example: first index corresponds to portfolios (0-3), second index: 0  to prices dataframe of this portfolio, 1: to weights of this portfolio
Monte_Carlo_list=[get_MC_input(api_call_df, four_portfolios_df, portfolio) for portfolio in four_portfolios]


#instantiating the class:

# capacity_cum_returns=Capacity_MC.calc_cumulative_return()

with tab3:
    
    col1,col2=st.columns([1,9])
    with col1:
        st.image('../Images/Inv_growth.png',use_column_width='Auto')
    with col2:
        st.title('Historical Performance:')

    st.write(Monte_Carlo_list[3][0].tail())
    st.write(Monte_Carlo_list[0][1])
    st.write(daily_returns_df.head())
    st.write(daily_returns_df.tail())
    st.write(four_portfolios_dict['Benchmark'][sectors_mapping_df.columns.to_list().index('Name')+1].reset_index())
    st.plotly_chart(plotly_portfolio_figures[0],use_container_width=True)

with tab4:
     
    col1,col2=st.columns([1,9])
    with col1:
        st.image('../Images/earning.png',use_column_width='Auto')
    with col2:
        st.title('Simulating future returns:')
   
    portfolio_selection_MC = st.selectbox("Select a portfolio for the simulation:", tuple(four_portfolios))
    run_simulation=st.button('Run simulation?')
    
    portfolio_index=four_portfolios.index(portfolio_selection_MC)
    MC_prices_df=Monte_Carlo_list[portfolio_index][0]
    MC_weights_df=Monte_Carlo_list[portfolio_index][1]
    num_simulation = 500
    if run_simulation:
        # initiate an instance of MCSimulation class
        with st.spinner('Simulation running...'):
            time.sleep(5)
        st.success('View the results!!')
        MC_instance=MCSimulation(portfolio_data=MC_prices_df, investment_amount=initial_investment, weights=MC_weights_df, num_simulation=num_simulation, years=time_horizon)
        
        plot = MC_instance.plot_simulation()
        distibution = MC_instance.plot_distribution()
        returns = MC_instance.return_amount()
                
        col1,col2 = st.columns(2)
        with col1:
            st.plotly_chart(plotly_portfolio_figures[portfolio_index],use_container_width=True)
        with col2:
            st.subheader(f"{portfolio_selection_MC} portfolio estimated returns on the initial investment of {initial_investment} within the next {time_horizon} year period")
            st.write(f'With a 95% confidence, your {portfolio_selection_MC} portfolio will return between USD **:blue[{returns[0]:.0f}]** and USD **:blue[{returns[1]:.0f}]** on your initial investment of USD **{initial_investment}** within a {time_horizon} year period.')
        
        col1,col2 =st.columns(2)
        with col1:
            st.subheader(f"{portfolio_selection_MC} portfolio {num_simulation} simulation runs")
            st.bokeh_chart(hv.render(plot, backend='bokeh',use_container_width=True))
            
        with col2:    
            st.subheader(f"{portfolio_selection_MC} portfolio distribution of returns based on a {time_horizon} year period and an initial investment of USD {initial_investment}")
            st.bokeh_chart(hv.render(distibution, backend='bokeh',use_container_width=True))


    
        