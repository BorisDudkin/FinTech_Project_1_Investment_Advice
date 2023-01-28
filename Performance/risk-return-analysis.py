import pandas as pd
from pathlib import Path
import numpy as np
from yahoo_api import yahoo_api_call


# %matplotlib inline

# Import the data by reading in the CSV file and setting the DatetimeIndex 
# Review the first 5 rows of the DataFrame
# YOUR CODE HERE
# 'BTC-USD', 'ETH-USD', 'T', 'XOM', 'AAPL', 'MSFT', 'SQ', 'AGG', 'SPY'
yahoo_api_call("BTC-USD","1D" )