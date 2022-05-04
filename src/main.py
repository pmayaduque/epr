# -*- coding: utf-8 -*-
"""
Created on Mon May  2 16:08:29 2022

@author: pmayaduque
"""

import optimiser as opt ##Modelo normal
from  pyomo.environ import *
from utilities import read_data
from experiments import Experiment

#from model_deposit_no_income import create_model  ## Modelo cuando el dopósito no es un ingreso
#from instances import test_instance, instance_from_file, solution_summary, eval_instance, solution_to_file, solution_from_file
#from experiment_tools import *
#from experimento_1 import doe0, doe1, doe2


# read data from file
data_filepath = "../data/data.json" # data path
data = read_data(data_filepath)
    
model = opt.create_model()
instance = model.create_instance(data)

results, termination = opt.solve_instance(instance, 
                       optimizer = 'gurobi',
                       mipgap = 0.002,
                       tee = True)

model_results = opt.Results(instance, termination) 

# Print results
print(model_results.solution)


# Runing experiments

#exp_design= {'te' : [{1: 0.25, 2: 0.25, 3: 0.25, 4: 0.25}, {1: 0.5, 2: 0.5, 3: 0.5, 4: 0.5}],
#             'tr' : [{1: 0.1, 2: 0.1, 3: 0.1, 4: 0.1}, {1: 0.2, 2: 0.2, 3: 0.2, 4: 0.2}],
#             'vd' : [6, 7]
#    }

exp_design= {'te' : [{1: i/100, 2: i/100, 3: i/100, 4: i/100} for i in range(15, 100, 20)],
             'tr' : [{1: i/100, 2: i/100, 3: i/100, 4: i/100} for i in range(0, 26, 5)],
             'vd' : [i for i in range(0, 500001, 50000)],
             'vma': [i for i in range(0, 500001, 50000)],
    }
experiment1 = Experiment(instance, exp_design)