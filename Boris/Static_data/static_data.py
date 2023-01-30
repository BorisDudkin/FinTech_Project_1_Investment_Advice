#this is a length of the risk bucket for portfolio selection (for example the bucket of 0.3-0.4 will correspond to the step of 0.1
step = 0.1

#this is a list of dbs that contain risk capacity related questions. If new questions are added and the corresponding dbs created, this list has to be updated
capacity_questions=['Q1_Capacity','Q2_Capacity','Q3_Capacity','Q4_Capacity','Q5_Capacity']

#timeframe and number of days for historical data API retrieval:
n_days=1200
timeframe='1Day'

#number of Monte Carlo simulations 
num_sim = 500

#number of trading days i a year
trading_days=252