# -*- coding: utf-8 -*-
"""
Created on Mon May  2 16:08:29 2022

@author: pmayaduque
"""

import optimiser as opt ##Modelo normal
from  pyomo.environ import *
from utilities import read_data
from experiments import Experiment
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

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



# Exploratory analysis

exp_design= {'vma' :[i for i in range(250000, 500001, 50000)],
             'vd' : [i/100 for i in range(0, 101, 10)],
             'MA' : [0.10, 0.15, 0.20],
             'te' : [0.15, 0.20, 0.30],
             'alfa' : [0.20, 0.30, 0.50],
             'ft' : [0.15, 0.30, 0.45]
        }
experiment1 = Experiment(instance, exp_design)
fig = experiment1.graph_goalAchiv()#r"../output_files/Experiment1.csv")
pio.write_html(fig, file='temp.html')

df1 = experiment1.df_results
dict_varX = {'vma': "Material value", 
             'vd': "Deposit Value", 
             'MA': "Recovery goal", 
             'te': "recovery rate"}
plot_varX = list(dict_varX.keys())

dict_varY = {'OF_value': 'System profit', 
             'goal_ratio': "Goal Achivement"}
plot_varY = list(dict_varY.keys())

fig = make_subplots(rows=len(plot_varY), cols=len(plot_varX),                    
                    row_titles = plot_varY)

for i in range(len(plot_varY)):
    for j in range(len(plot_varX)):
        subfig = go.Box(x=df1[plot_varX[j]], y=df1[plot_varY[i]],
                            name=plot_varX[j])
        fig.append_trace(subfig, i+1, j+1)
        
fig.update(layout_showlegend=False)

# set axis labels
for i in range(len(plot_varY)):
    for j in range(len(plot_varX)):        
        fig.update_xaxes(title_text=dict_varX[plot_varX[j]], row = i+1, col = j+1)
        if j == 0:
            fig.update_yaxes(title_text=dict_varY[plot_varY[i]], row = i+1, col = 1)

fig = EDA_graph(instance, r"../output_files/EDA.csv")
pio.write_html(fig, file='temp.html')


