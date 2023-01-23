import sys
from pathlib import Path
import numpy as np
import pandas as pd

import fire
import questionary
import math

def get_capacity_score(risk_capacity):
    number_questions = len(risk_capacity)
    score = 0
    
    zero_df=[]
    for df in risk_capacity:
        n_rows=len(df.axes[0])
        n_cols=len(df.axes[1])
        df_zero = pd.DataFrame(np.zeros((n_rows, n_cols)), index =df.index, columns =df.columns)
        zero_df.append(df)
        
    
    for num in range(number_questions):  
        questions=list(zero_df[num].index)
        responses = list(zero_df[num].columns)
        for question in questions:

            selection=questionary.select(
        question, choices=responses
    ).ask()
            print(question)
            print(selection)
            score+=risk_capacity[num].loc[question,selection]
    
    capacity_score=score/number_questions
    if capacity_score == 1:
        lower=0.9
    else:
        lower = math.floor(capacity_score*10)/10
    higher=round(lower+0.1,1)
    bucket = str(lower)+'-'+str(higher)
    
    # lower = math.floor(capacity_score*10)/10
    # higher=math.ceil(capacity_score*10)/10
    # if lower==higher:
    #     higher=lower+0.1
    # bucket = str(lower)+'-'+str(higher)
    return (round(capacity_score,3), bucket)


def get_tolerance_score(risk_tolerance_df):
    n_rows=len(risk_tolerance_df.axes[0])
    n_cols=len(risk_tolerance_df.axes[1])
    
    df_zero = pd.DataFrame(np.zeros((n_rows, n_cols)), index =risk_tolerance_df.index, columns =risk_tolerance_df.columns)
    questions=list(df_zero.index)
    responses = list(df_zero.columns)
    
    for question in questions:
        
        selection=questionary.select(
    question, choices=responses
).ask()

        df_zero.loc[question,selection]=risk_tolerance_df.loc[question,selection]
    score = df_zero.values.sum()/n_rows
    if score == 1:
        lower=0.9
    else:
        lower = math.floor(score*10)/10
    higher=round(lower+0.1,1)
    bucket = str(lower)+'-'+str(higher)    
    
    # lower = math.floor(score*10)/10
    # higher=math.ceil(score*10)/10
    # if lower==higher:
    #     higher=lower+0.1
    # bucket = str(lower)+'-'+str(higher)
    return (round(score,3), bucket)
