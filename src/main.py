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





exp_design= {'vma' :[i for i in range(250000, 1000000, 50000)],
             'vd' : [i/100 for i in range(0, 100, 2)],
             'MA' : [0.1],
             'te' : [0.15, 0.2, 0.3]
        }
experiment1 = Experiment(instance, exp_design)
fig = experiment1.graph_goalAchiv()#r"../output_files/Experiment1.csv")
pio.write_html(fig, file='temp.html')





