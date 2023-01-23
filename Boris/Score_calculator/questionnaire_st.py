
import math

def get_bucket(score):
    if score == 1:
        lower=0.9
    else:
        lower = math.floor(score*10)/10
    higher=round(lower+0.1,1)
    bucket = str(lower)+'-'+str(higher)   
    return bucket

