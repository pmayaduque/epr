# -*- coding: utf-8 -*-
"""
Created on Mon May  2 16:20:56 2022

@author: pmayaduque
"""

import requests
import json 
import ast
import binsreg
import pandas as pd

def read_data(data_path):
    
    try:
        data =  requests.get(data_path)
        data = json.loads(data.text)
    except:
        f = open(data_path)
        data = json.load(f)
    
    data_read = {}    
    for key,value in data.items():
        #print(key,value)
        if type(value) is dict:
            #[(print(ast.literal_eval(k)) if isinstance(ast.literal_eval(k), list) else print(type(ast.literal_eval(k)))) for k, v in value.items()]
            data_read[key] = {(tuple(ast.literal_eval(k)) if isinstance(ast.literal_eval(k), list) else ast.literal_eval(k)): v for k, v in value.items()}
            #try:
                #data_read[key] = {ast.literal_eval(k): v for k, v in value.items()}
            #except:
                #data_read[key] = {tuple(ast.literal_eval(k)): v for k, v in value.items()}
        else:
            data_read[key] = {None: value}    
    #compute QMR based in genQ and te
    #data_read['QMR'] = {i: data_read['genQ'][i]*data_read['te'][None] for i in data_read['ZONES'][None]}
    # Create collection and transformation subsets
    COLLECT_IN = [k for k, v in data_read['TA'].items() if v[0]==1]
    COLLECT_OUT = [k for k, v in data_read['TA'].items() if v[0]==0]
    data_read['COLLECT_IN'] = {None: COLLECT_IN} 
    data_read['COLLECT_OUT'] = {None: COLLECT_OUT} 
    TRANSF_IN = [k for k, v in data_read['TT'].items() if v[0]==1]
    TRANSF_OUT = [k for k, v in data_read['TT'].items() if v[0]==0]
    data_read['TRANSF_IN'] = {None: TRANSF_IN} 
    data_read['TRANSF_OUT'] = {None: TRANSF_OUT} 
    # Area an capacity for facilities
    data_read['CAP'] = {k : v[1] for k, v in data_read['data_inf'].items()}
    data_read['area'] = {k : v[0] for k, v in data_read['data_inf'].items()}
    # Create capacity for outsource facilities
    data_read['collect_out_cap'] = {k : v[1] for k, v in data_read['TA'].items() if v[0]==0}
    data_read['transfer_out_cap'] = {k : v[1] for k, v in data_read['TT'].items() if v[0]==0}
    
    
    data_model = {None: data_read }
    #data_model[None] = data_read
    
    return data_model

def binscatter(**kwargs):
    # Estimate binsreg
    est = binsreg.binsreg(**kwargs)
    
    # Retrieve estimates
    df_est = pd.concat([d.dots for d in est.data_plot])
    df_est = df_est.rename(columns={'x': kwargs.get("x"), 'fit': kwargs.get("y")})
    
    # Add confidence intervals
    if "ci" in kwargs:
        df_est = pd.merge(df_est, pd.concat([d.ci for d in est.data_plot]))
        df_est = df_est.drop(columns=['x'])
        df_est['ci'] = df_est['ci_r'] - df_est['ci_l']
    
    # Rename groups
    if "by" in kwargs:
        df_est['group'] = df_est['group'].astype(df[kwargs.get("by")].dtype)
        df_est = df_est.rename(columns={'group': kwargs.get("by")})

    return df_est