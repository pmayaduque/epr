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



# Exploratory analysis

exp_design= {'vma' :[i for i in range(250000, 500001, 50000)],
             'vd' : [i/100 for i in range(0, 101, 1)],
             'MA' : [0.10, 0.15, 0.20],
             'te' : [0.15, 0.20, 0.30],
             'alfa' : [0.20, 0.30, 0.50],
             'ft' : [0.15, 0.30, 0.45]
        }
experiment1 = Experiment(instance, exp_design)


# Exploratory Analysis
fig = EDA_graph(instance, r"../output_files/EDA.csv")
pio.write_html(fig2, file='temp.html')

# Goal Achivemente
fig = experiment1.graph_goalAchiv()
pio.write_html(fig, file='temp.html')


df1 = pd.read_csv(r"../output_files/EDA_large.csv")
df_grouped = df1.groupby(['vma', 'vd'])['goal_ratio'].mean().reset_index()
df_grouped.sort_values(by=['vd'])        
fig1 = px.line(df_grouped, x='vd', y='goal_ratio',  color='vma',
                      color_discrete_sequence = px.colors.qualitative.Dark24,
                      title = "Goal accomplishment vs ratio between deposit and material value",
                      labels = {
                          'te': 'recovery rate',
                          'vd': 'deposit value as fraction of material value in the market',
                          'goal_ratio': 'goal accomplishment',
                          'MA':'recovery goal'})
df_grouped = df1.groupby(['te', 'vd'])['goal_ratio'].mean().reset_index()
fig2 = px.line(df_grouped, x='vd', y='goal_ratio',  color='te',
                      color_discrete_sequence = px.colors.qualitative.Dark24,
                      title = "Goal accomplishment vs ratio between deposit and material value",
                      labels = {
                          'te': 'recovery rate',
                          'vd': 'deposit value as fraction of material value in the market',
                          'goal_ratio': 'goal accomplishment',
                          'MA':'recovery goal'})

          
fig = make_subplots(rows=2, cols=1, 
                    shared_xaxes='columns',
                    vertical_spacing=0.05)

n1_traces = len(fig1['data'])
n2_traces = len(fig2['data'])
#vma = df_grouped['vma'].unique()
#income_txt = ["Deposit", "Material"]
for i in range(n1_traces):        
    trace = fig1['data'][i]    
    #trace.name = "vma:"+ str(vma[i])
    trace.legendgroup = "1"
    fig.append_trace(trace, 1, 1)
for i in range(n2_traces):
    trace = fig2['data'][i]
    #trace.name =  income_txt[i]
    trace.legendgroup = "2"
    fig.append_trace(trace, 2, 1)

fig.update_traces(legendgroup = '1',row=1)
fig.update_traces(legendgroup = '2',row=2)



fig.update_layout(
    legend_tracegroupgap = 180
)
fig.update_xaxes(dtick=0.1, tickformat=".1f")
fig.update_xaxes(title_text="Deposit as a fration of material value", row = 2, col = 1)
fig.update_yaxes(dtick=0.05, tickformat=".2f")
fig.update_annotations(dict(font_size=8))
for col in [1]:
    fig.add_annotation(dict(x=col / 2 - 0.4, y=0.8, xref="paper", yref="paper", 
                            text='trace %d' %col, showarrow=False))


pio.write_html(fig, file='temp.html')          

