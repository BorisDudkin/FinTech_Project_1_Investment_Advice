import numpy as np
import pandas as pd
import sqlalchemy
import streamlit as st
import sys
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
sys.path.append('..\\Brian\\')
sys.path.append('..\\Adam\\')

# import math
from Score_calculator.questionnaire_st import get_bucket
from Sector_name.sector_industry import get_sector_industry_weights
from Static_data.static_data import step, capacity_questions
from MonteCarlo.monte_carlo_input import get_MC_input
from API_calls.API_calls import get_api_data

#create internet page name
st.set_page_config(page_title="Investment Advisor 💲")

#create four tabs to display data as per below breakdown
tab1, tab2, tab3, tab4 = st.tabs(['About','Portfolios','Past Performance','Future Returns'])

#tab 1 will contain introduction
with tab1:

    st.title('Investment Advisor 💰')

    # DATE_COLUMN = 'date/time'

    st.header('About This Application')

    my_text = "The Investment Advisor application will assess an investor's risk tolerance and his/her's capacity to absorbe risk. Based on those evaluations, two corresponding risk scores will be calculated and associated investment portfolios will be chosen from our ETFs offering. Their performance will be assessed and compared to the Benchmark portfolio of 40% Bonds 60% Stock. To increase clients' awareness of our new Crypto mix ETF, we will include the comparison performance of this fund too."

    st.write(my_text)

    with st.expander("About Us"):
        st.write("We offer our clients a tailored approach to constructing an investment portfolio based on their risk tolerance and personal cicumstances to absorbe the risk arising from the investment activities.")

    with st.expander("Funds Description and Risk profile"):
        st.write("Assets in our funds range from High Growth and Crypto to Value stocks and Fixed Income securities of Long term and Short-term maturities. Each fund is constructed with the risk profile of an investor in mind. Our funds are non-diversified and may experience greater volatility than more diversified investments. To compensate for the limited diversification, we only offer Large Cap US equities and Domestic stocks and bonds to reduce volatility brought by small- and medium-cap equities and excluding foreign currency exposure. And yet, there will always be risks involved with ETFs' investments, resulting in the possible loss of money")

# #Retrieve historical data:
# csvpath = Path("./Resources/historical_data.csv")
# historical_data_df = pd.read_csv(csvpath, index_col="index", parse_dates=True, infer_datetime_format=True)

#Section below will create a connection to our database and upload relevant tables to dataframes for further analysis

# Database connection string to the clean NYSE database
database_connection_string = 'sqlite:///Resources/investor.db'

# Create an engine to interact with the database
engine = sqlalchemy.create_engine(database_connection_string)

capacity_tables=capacity_questions
risk_capacity=[]
for table in capacity_tables:
    pd_name= table+"_df"
    pd_name = pd.read_sql_table(table, con=engine)
    pd_name=pd_name.set_index('Questions')
    risk_capacity.append(pd_name)
         
# read tolerance questionnaire into a dataframes risk_tolerance:
risk_tolerance_df =  pd.read_sql_table('risk_tolerance_questions', con=engine)
risk_tolerance_df=risk_tolerance_df.set_index('Questions')

# read portfolios into a portfolios_df dataframe:
portfolios_df =  pd.read_sql_table('portfolios', con=engine)
portfolios_df=portfolios_df.set_index('Risk_tolerance')

    
# read sectors into a sectors_mapping_df dataframe:
sectors_mapping_df =  pd.read_sql_table('sector_mapping', con=engine)
sectors_mapping_df=sectors_mapping_df.set_index('Sector')

#Subheader will display the questionnaire to determine the risk tolearance and risk capacity profiles of an investor:

with st.sidebar:
    
    st.header('Questionnaire:')
    
    st.subheader('Initial investment')
    initial_investment = st.number_input('How much money would you like to invest (in USD)?')

    st.subheader('Investment time horizon')
    time_horizon = st.number_input('What is your planned investment time horizon (in years)?')
    
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

# Section below calculates capacity risk and tolerance risk scores based on the answeres of the investor and generates two portfolios based on those scores:

# tolerance_score= round((score_1+score_2+score_3+score_4+score_5)/len(risk_tolerance_df.index),2)
tolerance_score=round(t_score/len(risk_tolerance_df.index),2)
tolerance=get_bucket(tolerance_score, step)
# capacity_score= round((cap_score_1+cap_score_2+cap_score_3+cap_score_4+cap_score_5)/len(risk_capacity),2)
capacity_score= round(c_score/len(risk_capacity),2)
capacity=get_bucket(capacity_score, step)

# In addition to the capacity risk and tolerance risk based portfolios, cryptomix new etf and the benchmark fund will be added for further analysis:

#tab 2 will display the selected portfolios and their composition (an option to select a portfolio for detailed review will be given to the investor):

with tab2:

    st.header('Assessment of the scores and corresponding selected portfolios:')

    st.subheader('Scores Assessment:')

    st.write(f'With the risk scores progressing from the most conservative (score 0) to the highest risk (score 1) you scored **:blue[{capacity_score}]** on your _capacity to absorbe risk_ and **:blue[{tolerance_score}]** on your _risk tolerance_')

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
    st.table(four_portfolios_df)

    st.subheader('Portfolios Characterisitcs:')
    # create portfolios_info list that shores sector, industry and names breakdowns per selected portfolios
    portfolios_info= [get_sector_industry_weights(portfolio, sectors_mapping_df) for portfolio in portfolios_list]

    #create a dictionary that will store sector, industry, market cap name breakdown dataframes:
    four_portfolios_dict=dict(zip(four_portfolios, portfolios_info))

    portfolio_selection = st.selectbox("Select the portfolio to analyze:", tuple(four_portfolios))
    
    #get dataframes for each breakdown characteristic - sector, Industry, Name, Market Cap, based on the sectors_mapping_df (constrcuted from our mapping table):
    sector_breakdown_df = four_portfolios_dict[portfolio_selection][0]
    Industry_breakdown_df = four_portfolios_dict[portfolio_selection][sectors_mapping_df.columns.to_list().index('Industry')+1]
    Name_breakdown_df = four_portfolios_dict[portfolio_selection][sectors_mapping_df.columns.to_list().index('Name')+1]
    Market_cap_breakdown_df = four_portfolios_dict[portfolio_selection][sectors_mapping_df.columns.to_list().index('Market Cap & Style')+1]
    

    st.markdown('**Portfolio composition by**:')
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write('**:blue[Sector]**')
        st.table(sector_breakdown_df)
    with col2:
        st.write('**:blue[Industry]**')
        st.table(Industry_breakdown_df)
    with col3:
        st.write('**:blue[Market Cap & Style]**')
        st.table(Market_cap_breakdown_df)
   
    #select the last element in the breakdown list that contains the dataframe of all the fund characteristics:
    st.write('**:blue[Summary Table]**')
    st.table(four_portfolios_dict[portfolio_selection][-1])

# This section coveres getting ready and making an API call to extract the pricing data for our selected portfolios (API call function accepts the dictionary of tickers and returns prices in the format needed for Monte carlo simulation and daily returns needed for past performance analysis):

# #create a dictionary of tickers based on the index of the four_portfolios_df dataframe:
# tickers = list(four_portfolios_df.index)
# portfolios_dict={}
# for ticker in tickers:
#     portfolios_dict[ticker]=1/len(tickers)


# #get an input for Monte Carlo simulation (note: price data per portfolio will be created at a later stage):
# Monte_Carlo_df=API_call['Historical prices']

# #get daily pct changes for historical performance analysis:
# daily_returns_df=API_call['Daily returns']


# create an API call and store data
tickers = list(four_portfolios_df.index)
n_days=10
timeframe='1Day'
api_call_df=get_api_data(tickers, n_days, timeframe)

# inputs to Monte Carlo instance:
# portfolios df: four_portfolios_df; initial investment: initial_investment; time horizon: time_horizon 

# get_MC_input function creates a list of inputs to create a Monte Carlo class instance, where:
# Monte_Carlo_df: dataframe of prices;
# four_portfolios_df: dataframe of our selected portfolios - in the function it will be used to get weights input to Monte Carlo class;
# portfolio: we create an instance for each portfolio and also use portfolio tickers to select price data from Monte_Carlo_df
Monte_Carlo__list=[get_MC_input(api_call_df, four_portfolios_df, portfolio, initial_investment, time_horizon) for portfolio in four_portfolios]


with tab3:
    st.write(Monte_Carlo__list[3][1])
