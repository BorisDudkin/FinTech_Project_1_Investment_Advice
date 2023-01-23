# A Database CLI Application

# Import modules
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import sqlalchemy

import fire
import questionary
import math
from Score_calculator.questionnaire import get_capacity_score, get_tolerance_score
from Sector_name.sector_industry import get_sector_industry_weights

def investment_advice(risk_capacity, risk_tolerance_df, portfolios_df, sectors_mapping_df):

    print("----------------------------Questionnaire---------------------------\n")
    # calculate investor's tolerance score based on the tolerance questionnaire
    tolerance_score, tolerance = get_tolerance_score(risk_tolerance_df)
    
    # calculate investor's ability to abosrbe risk score based on the capacity questionnaires:
    capacity_score, capacity = get_capacity_score(risk_capacity)
    
    print("------------------------Assessment Results--------------------------\n")
    
    print(f'With the risk scores progressing from the most conservative (score 0) to the highest risk (score 1) you scored {capacity_score} on your capacity to absorbe risk and {tolerance_score} on your risk tolerance\n')
    
    # create two list of all portfolios for comparison (one for selecting the portfolios from the portfolios_df and one for aggregating into a new dataframe of four portfolios for further financial analysis
    # tolerace and capacity represent the buckets we received from the get_capacity_score function above
    portfolio_mix = [capacity, tolerance, 'benchmark', 'cryptomix']
    four_portfolios=['Risk Capacity', 'Risk Tolerance', 'Benchmark', 'Cryptomix']
    
    # create portfolio list to store selectd portfolios + benchmark + cryptomix portfolio
    portfolios_list=[portfolios_df.loc[risk_indicator,:] for risk_indicator in portfolio_mix]
    print("Selected Portfolios based on your answers, including the Pylot Crypto enhanced Portfolio and the Benchmark\n")
    # create dataframe to store selectd portfolios + benchmark + cryptomix portfolio
    four_portfolios_df= pd.concat(portfolios_list, axis=1, ignore_index=False)
    four_portfolios_df.columns = four_portfolios
    four_portfolios_df=four_portfolios_df.loc[(four_portfolios_df!=0).any(axis=1)]
    print(four_portfolios_df)
    print("----------------------Portfolios Characterisitcs------------------------\n")
    # create portfolios_info list that stores sector, industry and names breakdowns per selected portfolios
    portfolios_info= [get_sector_industry_weights(portfolio, sectors_mapping_df) for portfolio in portfolios_list]
    i=0
    for portfolio in portfolios_info:
        print(f"{four_portfolios[i]} Portfolio Breakdown:\n")
       
        for breakdown in portfolio:
              print(breakdown)
        i+=1
        print("----------------------------------------------\n")
              
    results ="Would you like to make a new assessment?"

#     # Using the `results` statement created above,
#     # prompt the user to run the report again (`y`) or exit the program (`n`).
    continue_running = questionary.select(results, choices=['y', 'n']).ask()

    # Return the `continue_running` variable from the `sector_report` function
    return continue_running


# The `__main__` loop of the application.
# It is the entry point for the program.
if __name__ == "__main__":
    
    # Print a welcome message for the application
    print("\n---------------------------About Us-----------------------------\n")
    print("We offer our clients a tailored approach to constructing an investment portfolio based on their risk tolerance\n")
    print("and personal cicumstances to absorbe the risk arising from the investment activities.\n")

    print("\n---------------Funds Description and Risk profile----------------\n")
    print("Assets in our funds range from High Growth and Crypto to Value stocks\n")
    print("and Fixed Income securities of Long term and Short-term maturities.\n")
    print("Each fund is constructed with the risk profile of an investor in mind.\n")
    print("Our funds are non-diversified and may experience greater volatility than more diversified investments.\n")
    print("To compensate for the limited diversification, we only offer Large Cap US equities and Domestic stocks and bonds\n")       
    print("to reduce volatility brought by small- and medium-cap equities and excluding foreign currency exposure\n")
    print("Still, there will always be risks involved with ETFs' investments, resulting in the possible loss of money\n")
    print("\n-------------------------About This Application------------------------\n")                
    print("The application will assess an investor's risk tolerance and his/her's capacity to absorbe risk.\n")
    print("Based on those evaluations, two corresponding risk scores will be calculated and associated investment portfolios will be chosen from our ETFs offering.\n")
    print("Their performance will be assessed and compared to the Benchmark portfolio of 40% Bonds 60% Stock.\n To increase clients' awareness of our new Crypto mix ETF, we will include the comparison performance of this fund too.\n")

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
    
#   Alternatively, read from csv:
# read capacity questionnaires into a list of dataframes risk_capacity:
#     my_questionnaires=['Q1_Capacity.csv','Q2_Capacity.csv','Q3_Capacity.csv','Q4_Capacity.csv','Q5_Capacity.csv']
#     risk_capacity=[]

#     for quest in my_questionnaires:
#         csvpath = Path("./Resources/"+quest)
#         pd_name= quest+"_df"
#         pd_name = pd.read_csv(csvpath)
#         pd_name=pd_name.set_index('Questions')
#         risk_capacity.append(pd_name)

#     # read tolerance questionnaire into a dataframes risk_tolerance:
#     csvpath = Path("./Resources/Q_Tolerance.csv")
#     risk_tolerance_df = pd.read_csv(csvpath)
#     risk_tolerance_df=risk_tolerance_df.set_index('Questions')

#     # read portfolios into a portfolios_df dataframe:
#     csvpath = Path("./Resources/Portfolios.csv")
#     portfolios_df = pd.read_csv(csvpath)
#     portfolios_df=portfolios_df.set_index('Risk_tolerance')

#     # read sectors into a sectors_mapping_df dataframe:
#     csvpath = Path("./Resources/Sector_mapping.csv")
#     sectors_mapping_df = pd.read_csv(csvpath)
#     sectors_mapping_df=sectors_mapping_df.set_index('Sector')

    # Create a variable named running and set it to True
    running = True

    # While running is `True` call the `sector_report` function.
    # Pass the `nyse_df` DataFrame `sectors` and the database `engine` as parameters.
    while running:
        continue_running = investment_advice(risk_capacity, risk_tolerance_df, portfolios_df, sectors_mapping_df)
        if continue_running == 'y':
            running = True
        else:
            running = False
            print("Thank you for using our services!")
