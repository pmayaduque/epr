# -*- coding: utf-8 -*-
"""
Created on Mon May  2 16:08:29 2022

@author: pmayaduque
"""

import optimiser as opt ##Modelo normal
from  pyomo.environ import *
from utilities import read_data, binscatter
from experiments import Experiment, overview_dv_mva
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
import pandas as pd



#from model_deposit_no_income import create_model  ## Modelo cuando el dopósito no es un ingreso
#from instances import test_instance, instance_from_file, solution_summary, eval_instance, solution_to_file, solution_from_file
#from experiment_tools import *
#from experimento_1 import doe0, doe1, doe2


# read data from file
data_filepath = "../data/data.json" # data path
data = read_data(data_filepath)
    
model = opt.create_model()
instance = model.create_instance(data)

# Run instance from json data
'''
results, termination = opt.solve_instance(instance, 
                       optimizer = 'gurobi',
                       mipgap = 0.002,
                       tee = True)

model_results = opt.Results(instance, termination) 

# Print results
print(model_results.solution)



'''




# Exploratory Analysis
fig = EDA_graph(instance, r"../output_files/EDA.csv")
pio.write_html(fig2, file='temp.html')

# General overview
fig = overview_dv_mva(instance, r"../output_files/EDA_large.csv")
pio.write_html(fig, file='temp.html')  




exp_design= {'ind_income': [0, 1],
            'vma' :[500000],
             'vd' : [0],
             'MA' : [0.10],
             'te' : [0.15],
             'alfa' : [1],
             'ft' : [0.30]
              }
experiment1 = Experiment(instance, exp_design)


df1 = experiment1.df_results
df1["scaled_profit"] = (df1["OF_value"] - df1["OF_value"].min()) /(df1["OF_value"].max() -df1["OF_value"].min())


fig = px.line(df1, x='vd', y='goal_ratio', color='ind_income')
pio.write_html(fig, file='temp.html')  



