# -*- coding: utf-8 -*-
"""
Created on Mon May  2 16:08:29 2022

@author: pmayaduque
"""

import optimiser as opt ##Modelo normal
from  pyomo.environ import *
from utilities import read_data
from experiments import Experiment, EDA_graph, overview_dv_mva, graph_case_dv_vma
import experiments
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
import pandas as pd
import statsmodels.api as sm
from statsmodels.formula.api import ols
from sklearn.preprocessing import StandardScaler, MinMaxScaler


# read data from file
data_filepath = "../data/data.json" # data path
data = read_data(data_filepath)
    
model = opt.create_model()
instance = model.create_instance(data)

 
'''
# Run instance from json data
results, termination = opt.solve_instance(instance, 
                       optimizer = 'gurobi',
                       mipgap = 0.002,
                       tee = True)

model_results = opt.Results(instance, termination) 

# Print results
print(model_results.solution)
'''

# Run DOE for parameter significance 
exp_design= {'vma' :[250000, 400000, 550000],
             'vd' : [0.25, 0.50, 0.75],
             'ind_income' : [0, 0.5, 1],
             'MA' : [0.10, 0.20, 0.30],
             'te' : [0.15, 0.25, 0.35],
             'alfa' : [0.50],
             'ft' : [0.20, 0.25, 0.30],
             "fop":  [0.40, 0.60, 0.80]
             }
experiment1 = Experiment(instance, exp_design)
df1 = experiment1.df_results  
#df1.to_csv("DOE.csv" ,index=False)
          
df1 = pd.read_csv(r"../output_files/DOE.csv")
df1 = df1[df1['temination']!="no-optimal"]


scaler_maxmin = MinMaxScaler()
columns = ['vma', 'vd', 'MA', 'te', 'ft', 'fop', 'ind_income']
for col in columns:    
    df1['maxmin_'+col] = scaler_maxmin.fit_transform(df1[[col]])
model1 = ols("goal_ratio ~ C(maxmin_vma, Sum) + C(maxmin_vd, Sum) + C(maxmin_MA, Sum) + C(maxmin_te, Sum) + C(maxmin_ft, Sum) + C(maxmin_fop, Sum) +C(maxmin_ind_income, Sum) + C(maxmin_ft, Sum)*C(maxmin_fop, Sum)", data=df1).fit()
model1_aov_table = sm.stats.anova_lm(model1, typ=3)
model1_aov_table
model2 = ols("std_profit ~ C(maxmin_vma, Sum) + C(maxmin_vd, Sum) + C(maxmin_MA, Sum) + C(maxmin_te, Sum) + C(maxmin_ft, Sum) + C(maxmin_fop, Sum) +C(maxmin_ind_income, Sum) + C(maxmin_vd, Sum)*C(maxmin_te, Sum) +  + C(maxmin_ft, Sum)*C(maxmin_fop, Sum)" , data=df1).fit()
model2_aov_table = sm.stats.anova_lm(model2, typ=3)
model2_aov_table

# Run experiment for ind_income
exp_design= {'vma' :[550000],
             'vd' : [0.25],
             'ind_income' : [i/100 for i in range(0, 101, 1)],
             'MA' : [0.20],
             'te' : [0.30],
             'alfa' : [0.50],
             'ft' : [0.25],
             "fop":  [0.60]
             }
experiment1 = Experiment(instance, exp_design)
df1 = experiment1.df_results  
df1 = pd.read_csv(r"../output_files/exp_ind_income.csv")
df1 = df1[df1['temination']!="no-optimal"]

# Run experiment for alpha
exp_design= {'vma' :[550000],
             'vd' : [0.25],
             'alfa' : [i/100 for i in range(0, 101, 1)],
             'MA' : [0.20],
             'te' : [0.30],
             'ind_income' : [0.75],
             'ft' : [0.25],
             "fop":  [0.60]
             }
experiment1 = Experiment(instance, exp_design)
df1 = experiment1.df_results  
df1 = pd.read_csv(r"../output_files/exp_ind_income.csv")
df1 = df1[df1['temination']!="no-optimal"]

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
 
