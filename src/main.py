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
# set parameters to change and the given values

exp_design= {'tr' : [0.15],
             'te' : [0.15],#, [0.15, 0.20, 0.25, 0.3], #[0.30, 0.50],
             'vma' :[250000],#[i for i in range(250000, 1000001, 50000)],
             'vd' : [200000],#[i for i in range(50000, 1000001, 50000)],
             'MA' : [0.15]#,[i/100 for i in range(10, 17, 2)]
        }
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
# Run the experiment
experiment1 = Experiment(instance, exp_design)

# Create graphs
fig = experiment1.create_graph(r"../output_files/Experiment1.csv")
fig.show()
