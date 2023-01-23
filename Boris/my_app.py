import numpy as np
import pandas as pd
import sqlalchemy
import streamlit as st

import math
from Score_calculator.questionnaire_st import get_bucket
from Sector_name.sector_industry import get_sector_industry_weights


st.set_page_config(page_title="Investment Advisor 💲")


st.title('Investment Advisor 💰')

DATE_COLUMN = 'date/time'

st.header('About This Application')

my_text = "The Investment Advisor application will assess an investor's risk tolerance and his/her's capacity to absorbe risk. Based on those evaluations, two corresponding risk scores will be calculated and associated investment portfolios will be chosen from our ETFs offering. Their performance will be assessed and compared to the Benchmark portfolio of 40% Bonds 60% Stock. To increase clients' awareness of our new Crypto mix ETF, we will include the comparison performance of this fund too."

st.write(my_text)

with st.expander("About Us"):
    st.write("We offer our clients a tailored approach to constructing an investment portfolio based on their risk tolerance and personal cicumstances to absorbe the risk arising from the investment activities.")
    
with st.expander("Funds Description and Risk profile"):
    st.write("Assets in our funds range from High Growth and Crypto to Value stocks and Fixed Income securities of Long term and Short-term maturities. Each fund is constructed with the risk profile of an investor in mind. Our funds are non-diversified and may experience greater volatility than more diversified investments. To compensate for the limited diversification, we only offer Large Cap US equities and Domestic stocks and bonds to reduce volatility brought by small- and medium-cap equities and excluding foreign currency exposure. And yet, there will always be risks involved with ETFs' investments, resulting in the possible loss of money")

# Database connection string to the clean NYSE database
database_connection_string = 'sqlite:///Resources/investor.db'

# Create an engine to interact with the database
engine = sqlalchemy.create_engine(database_connection_string)

capacity_tables=['Q1_Capacity','Q2_Capacity','Q3_Capacity','Q4_Capacity','Q5_Capacity']
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


with st.sidebar:
    st.header('Questionnaire:')
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
    
# tolerance_score= round((score_1+score_2+score_3+score_4+score_5)/len(risk_tolerance_df.index),2)
tolerance_score=round(t_score/len(risk_tolerance_df.index),2)
tolerance=get_bucket(tolerance_score)
# capacity_score= round((cap_score_1+cap_score_2+cap_score_3+cap_score_4+cap_score_5)/len(risk_capacity),2)
capacity_score= round(c_score/len(risk_capacity),2)
capacity=get_bucket(capacity_score)

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
st.dataframe(four_portfolios_df)

st.subheader('Portfolios Characterisitcs:')
 # create portfolios_info list that stores sector, industry and names breakdowns per selected portfolios
portfolios_info= [get_sector_industry_weights(portfolio, sectors_mapping_df) for portfolio in portfolios_list]
i=0
for portfolio in portfolios_info:
    st.write(f"{four_portfolios[i]} Portfolio Breakdown:")
    for breakdown in portfolio:
            st.write(breakdown)
    i+=1
    
st.bar_chart(portfolios_info[0][3])