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
import hvplot


sys.path.append('.\\Brian\\')
sys.path.append('.\\Adam\\')
sys.path.append('.\\Boris\\')

# import math
from Score_calculator.questionnaire_st import get_bucket
from Sector_name.sector_industry import get_sector_industry_weights
from Portfolio_analysis.historical_analysis import get_historical_analysis
from Static_data.static_data import step, capacity_questions, n_days, timeframe, num_sim, trading_days
from Monte_Carlo.monte_carlo_input import get_MC_input
# from API_calls.API_calls import get_api_data
from MonteCarlo.MonteCarloEdited import MCSimulation

#create internet page name
st.set_page_config(page_title="Investment Advisor", layout='wide')

# Section 1: establishing connections for getting data

# Section 1.1: establishing connections for getting DB stored position data (questionnaires and risk weights, portfolios, sector/industry mappings)

# 1) Create Database connection string to a database where questionnaires, weights, portfolios and securitiy deail tables are stored (position data)
database_connection_string = 'sqlite:///Resources/investor.db'

# 2) Create an engine to interact with the database
engine = sqlalchemy.create_engine(database_connection_string)

# Section 1.2: establishing connections for getting market data (prices of the underlying scurities)

#Create a set up for ALPACA API Calls:
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
    
    #resetting the index for merging with crypto later in the function:
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
    
    #resetting the index for merging with stocks/bonds later in the function:
    crypto_df.index=crypto_df.index.date
    
    # merge non-crypto and crypto parts to generate df that will be used for Monte Carlo simulation:
    total_df=prices_Monte_Carlo_df.merge(crypto_df, how='inner', left_index=True, right_index=True)
    total_df=total_df.dropna()
    total_df = total_df.drop_duplicates()
    
    # Create an empty DataFrame for holding the closing prices
    closing_prices_df = pd.DataFrame()
    for ticker in tickers:
        closing_prices_df[ticker] = total_df[ticker]['close']
    
    #construct daily returns that will be used in the historical analysiss:
    daily_returns_df=closing_prices_df.pct_change().dropna()
    
    return (total_df, daily_returns_df)

# Section 2: Upload position data (relevant tables to dataframes for further analysis), and market data(prices of the securities):

# Section 2.1: Uploading position data from DB tables:

# the function below transforms db tables to dataframes for further processing:
def read_table_to_df(table, engine):
    return pd.read_sql_table(table, con=engine)

# creating a list of dataframes to store risk capacity related dataframes:
capacity_tables=capacity_questions
risk_capacity=[]
for table in capacity_tables:
    pd_name= table+"_df"
    pd_name = read_table_to_df(table, engine)
    pd_name=pd_name.set_index('Questions')
    risk_capacity.append(pd_name)
         
# read risk tolerance questionnaire into a dataframes risk_tolerance:
risk_tolerance_df =  read_table_to_df('risk_tolerance_questions', engine)
risk_tolerance_df=risk_tolerance_df.set_index('Questions')

# read portfolios into a portfolios_df dataframe:
portfolios_df =  read_table_to_df('portfolios', engine)
portfolios_df=portfolios_df.set_index('Risk_tolerance')

# read sectors/industry/investment style mappings into a sectors_mapping_df dataframe:
sectors_mapping_df =  read_table_to_df('sector_mapping', engine)
sectors_mapping_df=sectors_mapping_df.set_index('Sector')

# Section 2.2: market data upload - create an API call and store Monte Carlo input data and daily returns data for the set of our portfolios
tickers_api_call = portfolios_df.columns.to_list()
api_call_df, daily_returns_df=get_api_data(tickers_api_call, n_days, timeframe)


# Section 3 Calculating risk scores:

# Section 3.1: Gatheering data from an investor - questionnaires are displaied by using Streamlit software for interacting with the user

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

# Section 3.2: Generating risk scores (capacity score and tolerance score based on the answers to the questionnaires:

# tolerance_score= round((score_1+score_2+score_3+score_4+score_5)/len(risk_tolerance_df.index),2)
tolerance_score=round(t_score/len(risk_tolerance_df.index),2)
tolerance=get_bucket(tolerance_score, step)
# capacity_score= round((cap_score_1+cap_score_2+cap_score_3+cap_score_4+cap_score_5)/len(risk_capacity),2)
capacity_score= round(c_score/len(risk_capacity),2)
capacity=get_bucket(capacity_score, step)

# Display output - main bodies split into four tabs for easy visualization:
# Create four tabs to display our application as per below breakdown
tab1, tab2, tab3, tab4 = st.tabs(['About','Portfolios','Past Performance','Future Projected Returns'])

# Tab 1: About: 
#tab 1 will contain an introduction (information about the company, about the app and about the investment practices):

with tab1:
    col1,col2=st.columns([1,9])
    with col1: 
        st.image('../Images/broker.png',width=85)
    with col2:
        st.title('Investment Advisor Application')

    st.header('About This Application:')

    my_text = "The Investment Advisor application will assess an investor's risk tolerance and their capacity to absorbe risk. Based on those evaluations, two corresponding risk scores will be calculated, and associated investment portfolios will be chosen from our ETFs offering. Their performance will be assessed and compared to the Benchmark portfolio with a 40/60 bond to stock ratio. To increase clients' awareness of our new Cryptomix ETF, we will include the comparison performance of this fund as well."

    st.write(my_text)

    with st.expander("About Us"):
        st.write("We offer our clients a tailored approach to constructing an investment portfolio based on their risk tolerance and personal cicumstances to absorbe the risk arising from the investment activities.")

    with st.expander("Funds Description and Risk profile"):
        st.write("Assets in our funds range from High Growth and Crypto to Value Stocks and Fixed Income securities of long-term and short-term maturities. Each fund is constructed with the risk profile of an investor in mind. Our funds are non-diversified and may experience greater volatility than more diversified investments. To compensate for the limited diversification, we only offer Large Cap US equities and Domestic stocks and bonds to reduce volatility brought by small- and medium-cap equities, excluding foreign currency exposure. And yet, there will always be risks involved with ETFs' investments, resulting in the possible loss of money.")

# Section 4 - Defining two portfolios based on the risk capacity and risk tolerance scores respectively and adding crypto enhanced and benchmark portfolios:

# Tab 2: Portfolios: 
#tab 2 will display the selected portfolios and their composition (an option to select a portfolio for detailed review will be given to the investor):

with tab2:
    
    col1,col2=st.columns([1,9])
    with col1: 
        st.image('../Images/pie.png', width=85)
    with col2:
        st.title('The Scores and their Corresponding Selected Portfolios')
   
    st.header('Scores Assessment:')

    st.write(f'With the risk scores progressing from the most conservative (score 0) to the highest risk (score 1) you scored **:blue[{capacity_score}]** on your _capacity to absorbe risk_ and **:blue[{tolerance_score}]** on your _risk tolerance_.')
    st.write("Based on these scores, we created **:blue[Risk Capacity]** and **:blue[Risk Tolerance]** portfolios. To provide a **:blue[Benchmark]**, we included our 40/60 bonds to stocks traditional portfolio in our analysis.")
    st.write("Finally, a new Crypto enhanced portfolio **:blue[Cryptomix]** will help investors analyze how an addition of digital assets can affect portfolio performance.")

    # create two list of all portfolios for comparison (one for selecting the portfolios from the portfolios_df and one for aggregating into a new dataframe of four portfolios for further financial analysis
    # tolerace and capacity represent the buckets we received from the get_capacity_score function above
    portfolio_mix = [capacity, tolerance, 'benchmark', 'cryptomix']
    four_portfolios=['Risk Capacity', 'Risk Tolerance', 'Benchmark', 'Cryptomix']

    # create portfolio list to store selectd portfolios + benchmark + cryptomix portfolio
    portfolios_list=[portfolios_df.loc[risk_indicator,:] for risk_indicator in portfolio_mix]

    st.subheader('Selected portfolios including the Cryptomix and Benchmark:')

    # create dataframe four_portfolios_df to store selectd portfolios + benchmark + cryptomix portfolio
    four_portfolios_df= pd.concat(portfolios_list, axis=1, ignore_index=False)
    four_portfolios_df.columns = four_portfolios
    four_portfolios_df=four_portfolios_df.loc[(four_portfolios_df!=0).any(axis=1)]
    # st.table(four_portfolios_df)

    
    # create portfolios_info list that stores sector, industry and names breakdowns per selected portfolios - function get_sector_industry_weights concatenates portfolio with sector/industry mapping table on tickers and generates relevant breakdowns for each portfolio.
    portfolios_info= [get_sector_industry_weights(portfolio, sectors_mapping_df) for portfolio in portfolios_list]

    #create a dictionary that will store sector, industry, market cap name breakdown dataframes by zipping portfolios list and the breakdowns list from above
    four_portfolios_dict=dict(zip(four_portfolios, portfolios_info))
    
    #creating a plotly figure of breakdown by company/etf name for each selected portfolio and store in plotly_portfolio_figures
    plotly_portfolio_figures=[]
    for portfolio in four_portfolios:
        fig_name= 'fig_name_'+portfolio
        Name_breakdown_df = four_portfolios_dict[portfolio][sectors_mapping_df.columns.to_list().index('Name')+1].reset_index()
        fig_name=px.pie(Name_breakdown_df, names = 'Name', values='weights',title=f'<b>{portfolio} Portfolio by Company/ETF Name<b>')
        plotly_portfolio_figures.append(fig_name)
    
    #display four portfolios breakdowns by company/ETF name:

    col1,col2,col3,col4 = st.columns(4, gap='large')
    
    with col1:
        st.plotly_chart(plotly_portfolio_figures[0],use_container_width=True)
    with col2:
        st.plotly_chart(plotly_portfolio_figures[1],use_container_width=True)
    with col3:
        st.plotly_chart(plotly_portfolio_figures[2],use_container_width=True)
    with col4:
        st.plotly_chart(plotly_portfolio_figures[3],use_container_width=True)
    

    portfolio_selection = st.selectbox("Select the portfolio to analyze:", tuple(four_portfolios))
    
    # get dataframes for each breakdown characteristic - sector, Industry, Name, Market Cap, based on the sectors_mapping_df (constrcuted from our mapping table) and pull data from the dictionary by the index of the breakdown identifier (i.e. Industry). Note: total breakdown by sector is located first in the portfolios_info and therefore has an index of 0:
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
    
    # st.write('**Portfolio composition by**:')
    col1, col2, col3= st.columns(3, gap='large')
    with col1:
        st.plotly_chart(fig_sector_breakdown,use_container_width=True)                  
    with col2:
        st.plotly_chart(fig_industry_breakdown,use_container_width=True)
    with col3:
        st.plotly_chart(fig_market_cap_breakdown,use_container_width=True)

   
    #select the last element in the breakdown list that contains the dataframe of all the fund characteristics:
    st.write('**Summary Table**')
    st.table(four_portfolios_dict[portfolio_selection][-1])

# # Section 5  Historical Analysis:

# Call historical_analysis function to get 1-3y returns and Sharpe Ratio, Cumulative rturns per asset and per portfolio:

summary_df, cum_returns_portfolios_df, cum_returns_assets_df, n_years=get_historical_analysis(daily_returns_df, four_portfolios_df, trading_days)
summary_df = summary_df.applymap("{0:.2f}".format)

# create plotly plots for assets and portfolios cummulative returns:

fig_returns_portfolio=px.line(cum_returns_portfolios_df, y= cum_returns_portfolios_df.columns,title=f'<b>{n_years}-Year Cumulative Returns by Portfolio</b>')
fig_returns_portfolio.update_xaxes(rangeslider_visible=True)
fig_returns_portfolio.update_layout(xaxis_range=[list(cum_returns_portfolios_df.index)[0],list(cum_returns_portfolios_df.index)[-1]], showlegend=True, title={'x' : 0.5}, yaxis_title="Cumulative Returns")

fig_returns_assets=px.line(cum_returns_assets_df, y= cum_returns_assets_df.columns,title=f'<b>{n_years}-Year Cumulative Returns by Underlying Asset</b>')
fig_returns_assets.update_xaxes(rangeslider_visible=True)
fig_returns_assets.update_layout(xaxis_range=[list(cum_returns_assets_df.index)[0],list(cum_returns_assets_df.index)[-1]], showlegend=True, title={'x' : 0.5}, yaxis_title="Cumulative Returns", legend=dict(orientation="h",))

#Tab 3: Past Performance: will display the results of the historical performance

with tab3:
    
    col1,col2=st.columns([1,9])
    with col1:
        st.image('../Images/Inv_growth.png', width=85)
    with col2:
        st.title('Historical Performance')
        
#     st.header(f'{n_years}-year underlying securities cumulative returns')
#     st.line_chart(cum_returns_assets_df)
    st.header('Performance of Underlying Assets:')
    st.plotly_chart(fig_returns_assets,use_container_width=True)
    
    st.subheader('Selected Portfolios Overview:')
    col1,col2,col3,col4 = st.columns(4, gap='large')
    
    with col1:
        st.plotly_chart(plotly_portfolio_figures[0],use_container_width=True)
    with col2:
        st.plotly_chart(plotly_portfolio_figures[1],use_container_width=True)
    with col3:
        st.plotly_chart(plotly_portfolio_figures[2],use_container_width=True)
    with col4:
        st.plotly_chart(plotly_portfolio_figures[3],use_container_width=True)
        
        
    st.subheader('Yearly Returns and Sharpe-Ratio by Portfolio:') 
    st.title('\n')  

    st.dataframe(summary_df.style.highlight_max(color='lightblue', axis=0),use_container_width=True)
    st.title('\n')
    st.title('\n')
    
    st.subheader('Portfolio Performance:')
    st.plotly_chart(fig_returns_portfolio,use_container_width=True)
                                                

# Section 6: Monte Carlo Simulation

# inputs to Monte Carlo instance:
# portfolios df: four_portfolios_df; initial investment: initial_investment; time horizon: time_horizon 

# get_MC_input function creates a list of inputs to create a Monte Carlo class instance, where:
# Monte_Carlo_df: dataframe of prices;
# four_portfolios_df: dataframe of our selected portfolios - in the function it will be used to get weights input to Monte Carlo class;
# portfolio: we create an instance for each portfolio and also use portfolio tickers to select price data from Monte_Carlo_df
#example: first index corresponds to portfolios (0-3), second index: 0  to prices dataframe of this portfolio, 1: to weights of this portfolio
Monte_Carlo_list=[get_MC_input(api_call_df, four_portfolios_df, portfolio) for portfolio in four_portfolios]

# Tab 4: Future Projected Returns:
# tab 4 will display Monte Carlo simulation results for a sected by user portfolio:

with tab4:
     
    col1,col2=st.columns([1,9])
    with col1:
        st.image('../Images/earning.png', width=85)
    with col2:
        st.title('Simulating Future Returns')

    st.header(f"Monte Carlo {time_horizon} Year Portfolio Analysis:")

    st.write(f"**With the utilization of a financial simulation known as 'Monte Carlo', your portfolios were analyzed for their estimated future returns using an intial invesment of :blue[${initial_investment:.2f}] over the span of :blue[{time_horizon:.0f}] years.**")

    st.write("**The following were the outcomes...**")

    st.caption("_**Disclaimer:** These results are not guaranteed but rather an estimate based on the assumption of normal distribution, which quantifies risk and return by the mean for returns and standard deviation for risk. Outcome is based on random number algorithm and may not render consistent results._")
   
    #select portfolio:
    portfolio_selection_MC = st.selectbox("Select a portfolio for the simulation:", tuple(four_portfolios))
    run_simulation=st.button('Run simulation?')
    
    portfolio_index=four_portfolios.index(portfolio_selection_MC)
    MC_prices_df=Monte_Carlo_list[portfolio_index][0]
    MC_weights_df=Monte_Carlo_list[portfolio_index][1]
    num_simulation = num_sim
    if run_simulation:
        # initiate an instance of MCSimulation class
        with st.spinner('Simulation running...'):
            time.sleep(7)
        st.success('View the results!')
        MC_instance=MCSimulation(portfolio_data=MC_prices_df, investment_amount=initial_investment, weights=MC_weights_df, num_simulation=num_simulation, years=time_horizon)
        
        #Calling the functions from Monte Carlo
        plot = MC_instance.plot_simulation()
        distibution = MC_instance.plot_distribution()
        returns = MC_instance.return_amount()
                
        bycompany,description = st.columns([1,2], gap='large')
        with bycompany:
            st.plotly_chart(plotly_portfolio_figures[portfolio_index],use_container_width=True)
        with description:
            st.subheader(f"{portfolio_selection_MC} Estimated Returns:")
            st.subheader(f'With a 95% confidence, an initial investment of _${initial_investment}_ over the course of _{time_horizon} years_ will result in your {portfolio_selection_MC} having an estimated return value between **:blue[{returns[0]:.2f}]** and **:blue[{returns[1]:.2f}]** USD.')
        col1,col2 =st.columns(2)
        with col1:
            st.subheader(f"{portfolio_selection_MC} Portfolio based on {num_simulation} Simulations:")
            st.bokeh_chart(hv.render(plot, backend='bokeh',use_container_width=True))
            
        with col2:    
            st.subheader(f"{portfolio_selection_MC} Portfolio Distribution of Returns:")
            st.bokeh_chart(hv.render(distibution, backend='bokeh',use_container_width=True))


    
        