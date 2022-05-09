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

# MODEL VALIDATION

# Cero deposit and not goal: when  vma makes worth to collect?
exp_design= {'vd' : [0],
             'vma' :[i for i in range(245000, 300000, 500)],
             'MA': [0]}
experiment1 = Experiment(instance, exp_design)
df = experiment1.df_results[['vma', 'OF_value', 'income', 'Q_coll']]
df['cost'] = df['OF_value'] - df['income']
fig = px.line(df, x='vma', y=['OF_value', 'income', 'cost'])
pio.write_html(fig, file='temp.html')

# Capacity sets a limit for collection
exp_design= {'vd' : [0],
             'vma' :[i for i in range(245000, 300000, 500)],
             'MA': [0]}
experiment1 = Experiment(instance, exp_design)
df = experiment1.df_results[['vma', 'OF_value', 'income', 'Q_coll']]
fig= px.line(df, x='vma', y='Q_coll')
pio.write_html(fig, file='temp.html')

# without capacity the model collects all the generation
exp_design= {'vd' : [0],
             'vma' :[i for i in range(20000, 5000000, 100000)],
             'MA': [0], 
             'CAP': [{1: 1000, 2: 1000, 3: 1000, 4: 1000, 5: 1000, 6:1000}]
             }
experiment1 = Experiment(instance, exp_design)
df = experiment1.df_results[['vma', 'OF_value', 'income', 'Q_coll', 'x']]
fig= px.line(df, x='vma', y='Q_coll')
pio.write_html(fig, file='temp.html')



# Large set of runs to show importance of vd/vma ratio 
exp_design= {'tr' : [0.15],
             'te' : [0.15, 0.2, 0.3],#, [0.15, 0.20, 0.25, 0.3], #[0.30, 0.50],
             'vma' :[i for i in range(250000, 750001, 50000)],
             'vd' : [i for i in range(50000, 750001, 50000)],
             'MA' : [i/100 for i in range(10, 31, 2)], 
             'CAP': [{1: 1000, 2: 1000, 3: 1000, 4: 1000, 5: 1000, 6:1000}]
        }
# Run the experiment
experiment1 = Experiment(instance, exp_design)

# Create graphs
fig = experiment1.graph_income(r"../output_files/Experiment1.csv")
pio.write_html(fig, file='temp.html')
'''
exp_design= {'tr' : [{1: 0.15, 2: 0.15, 3: 0.15, 4: 0.15}],
             'te' : [{1: i/100, 2: i/100, 3: i/100, 4: i/100} for i in range(15, 100, 20)],
             'vd' : [i for i in range(0, 500001, 50000)]
        }


#Example:
exp_design= {'te' : [{1: 0.25, 2: 0.25, 3: 0.25, 4: 0.25}, {1: 0.5, 2: 0.5, 3: 0.5, 4: 0.5}],
                 'tr' : [{1: 0.1, 2: 0.1, 3: 0.1, 4: 0.1}, {1: 0.2, 2: 0.2, 3: 0.2, 4: 0.2}],
                 'vd' : [6, 7]
        }


exp_design= {'te' : [{1: i/100, 2: i/100, 3: i/100, 4: i/100} for i in range(15, 100, 20)],
             'tr' : [{1: i/100, 2: i/100, 3: i/100, 4: i/100} for i in range(0, 26, 5)],
             'vd' : [i for i in range(0, 500001, 50000)],
             'vma': [100000, 250000, 400000], #[i for i in range(0, 500001, 50000)],
             'ft': [0.25, 0.50, 0.75],
    }


'''


