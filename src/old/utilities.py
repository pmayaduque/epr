# -*- coding: utf-8 -*-
"""
Created on Mon May  2 14:55:39 2022

@author: pmayaduque
"""

import requests
import json
import ast



def read_data(data_path):
    
    try:
        data = json.loads(data.text)
    except:
        f = open(data_path)
        data = json.load(f)
    

        
    return data_read