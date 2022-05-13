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






# Exploratory Analysis
fig = experiments.EDA_graph(instance, r"../output_files/EDA.csv")
pio.write_html(fig, file='temp.html')

# General overview
fig = experiments.overview_dv_mva(instance, r"../output_files/EDA_large.csv")
pio.write_html(fig, file='temp.html')  

# A particular case vd vs vma
fig = experiments.graph_case_dv_vma(instance, r"../output_files/vma_vd.csv")
pio.write_html(fig, file='temp.html')  

'''
# Experiments capacity
exp_design= {'vma' :[500000],
             'vd' : [0.4],
             'MA' : [0.15],
             'te' : [0.20],
             'alfa' : [0.1]
                }
experiment1 = experiments.Experiment(instance, exp_design)
df1 = experiment1.df_results 
df1.to_csv("alfa_ft.csv", index=False)


 
