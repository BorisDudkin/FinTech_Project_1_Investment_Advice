from dotenv import load_dotenv
import os
import http.client
import json
import pandas as pd
from yahoo_api import dataframe_maker

btc_prices=dataframe_maker(weights={'BTC-USD':0.5,'ETH-USD':0.5})
print(btc_prices['Historical close prices'])