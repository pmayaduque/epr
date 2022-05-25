# -*- coding: utf-8 -*-
"""
Created on Mon May  2 16:08:29 2022

@author: pmayaduque
"""

import optimiser as opt ##Modelo normal
from  pyomo.environ import *
from utilities import read_data
#from experiments import Experiment, EDA_graph, overview_dv_mva, graph_case_dv_vma
import experiments
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
import pandas as pd


# read data from file
data_filepath = "../data/data.json" # data path
data = read_data(data_filepath)
    
model = opt.create_model()
instance = model.create_instance(data)

exp_design= {'vma' :[250000, 400000, 550000],
                    'vd' : [10, 20, 30],
                    'MA' : [0.10, 0.15, 0.20],
                    'te' : [0.15, 0.20, 0.30],
                    'alfa' : [0.50],
                    'ft' : [0.15, 0.30, 0.45],
                    "ind_income" : [0, 0.5, 1],
}
experiment1 = Experiment(instance, exp_design)
df1 = experiment1.df_results  
'''
# Run instance from json data
results, termination = opt.solve_instance(instance, 
                       optimizer = 'gurobi',
                       mipgap = 0.002,
                       tee = True)

model_results = opt.Results(instance, termination) 

# Print results
print(model_results.solution)


 
        
# Exploratory Analysis
fig = experiments.EDAv2_graph(instance, r"../output_files/EDA1.csv")
pio.write_html(fig, file='temp.html')
'''
# General overview
fig = experiments.overview_dv_mva(instance, r"../output_files/EDA_large.csv")
pio.write_html(fig, file='temp.html')  




# A particular case vd vs vma
fig = experiments.graph_case_dv_vma(instance, r"../output_files/vma_vd.csv")
pio.write_html(fig, file='temp.html')  
'''

experiment1 = Experiment(instance, exp_design)
df1 = experiment1.df_results  

# Experiments capacity

exp_design= {'vma' :[500000],
             'vd' : [0.30],
             'MA' : [0.20],
             'te' : [0.30],
             'ind_income' : [i/100 for i in range(0, 101, 1)],
             'CAP' : [{"1": 0.38, "2": 0.76, "3": 1.14, "4": 1.52, "5": 1.90, "6": 2.28}]
                }




df1["scaled_profit"] = (df1["OF_value"] - df1["OF_value"].min()) /(df1["OF_value"].max() -df1["OF_value"].min())
fig = px.line(df1, x='ind_income', y ="scaled_profit")
pio.write_html(fig, file='temp.html') 
 
'''