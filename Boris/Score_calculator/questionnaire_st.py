
import math


def get_bucket(score, step):
    """Determines the bucket for selecting a portfolio based on the risk scores from questionnaires

    Args:
        score (float): risk score from the questionnaires
        step (float): determines size of a bucket between 0 and 1. i.e. a step of 0.1 will create buckets of 0-0.1, 0.1-0.2 etc

    Returns:
        a string containing a bucket between 0 and 1 in a srep of step parameter

    """


    # get the lower boundary of a bucket:
    if score == 1:
        lower=0.9
    else:
        lower = math.floor(score*10)/10
    #get a higher boundary of a bucket
    higher=round(lower+step,1)
    # create a bucket
    bucket = str(lower)+'-'+str(higher)   
    return bucket

