# -*- coding: utf-8 -*-
"""
Created on Mon May  2 16:20:56 2022

@author: pmayaduque
"""

import requests
import json 
import ast

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
    data_model = {None: data_read }
    #data_model[None] = data_read
    
    return data_model