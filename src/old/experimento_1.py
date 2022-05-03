# -*- coding: utf-8 -*-
"""
Created on Wed Aug 25 18:40:35 2021

@author: Jesus Galarcio
"""
import pandas as pd
from experiment_tools import *
from pyomo.environ import *
from pyomo.opt import *
from model import create_model
from instances import solution_summary


def doe0(data, model, opt):
    #Caso de estudio
    instance_base = model.create_instance(data)
    df = create_dataframe_base()
    
    df= new_row(df, data = data, Instance = "Base")
    df = df.set_index('Instance')
    
    results = opt.solve(instance_base)
    
    
    if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
        print ("this is feasible and optimal")
        df = new_solution_to_row(df, data = data , Instance= "Base", instance = instance_base)
        solution_summary(instance_base)
        
    elif results.solver.termination_condition == TerminationCondition.infeasible:
        print ("do something about it? or exit?")
    else:
        # something else is wrong
        print (str(results.solver))
    
    return df



def doe1(data, model, opt):

    #Ingresar los datos en una variable
    exp_1 = data
    #Crear un dataframe para el experimento
    df_1 = create_dataframe_base()
    
    ### Experimento real utilizado en la tesis
    
#    _vma = [ 250000*(i/100) for i in range(0,201,20)]
#    _vd = [ 250000*(i/100) for i in range(0,201,20)]
#    _te_i = [ (i/100) for i in range(15,101,20)]
#    _tr_i = [ (i/100) for i in range(0,26,5)]
    
    
    ### Experimento Ajuste capacidad
    
#    _vma = [250000]
#    _vd = [ 250000*(i/100) for i in range(0,201,20)]
#    _te_i = [ (i/100) for i in range(15,101,20)]
#    _tr_i = [ (i/100) for i in range(0,26,5)]
    
    
    ### Experimento para encontrar el punto de equilibrio

    _vma = [250000]
    _vd = [ 200000,
            202500,
            205000,
            207500,
            210000,
            212500,
            215000,
            217500,
            220000,
            222500,
            225000,
            227500,
            230000,
            232500,
            235000,
            237500,
            240000,
            242500,
            245000,
            247500,
            250000
            ]
    _te_i = [ (i/100) for i in range(15,101,20)]
    _tr_i = [0.45]

    
    n_experimentos = len(_vma)*len(_te_i)*len(_vd)*len(_tr_i)
    
    exp_1_instances = []
    exp_1_data = []
    cont=0
    
    for factor_1 in _vma:
        for factor_2 in _vd:
            for factor_3 in _te_i:
                for factor_4 in _tr_i:
                    cont = cont + 1
                    name = "Exp_1_vma_" + str(round(factor_1)) + "_vd_" + str(round(factor_2)) + "_te_" + str(round(factor_3,2)) + "_tr_"+str(round(factor_4,2)) 
                    print("Creando los experimentos. Estado: {} de {}. {}% completado...".format(cont,n_experimentos,(cont/n_experimentos)*100))
                    exp_1[None]["vma"][None] = factor_1
                    exp_1[None]["vd"][None] = factor_2
                    exp_1[None]["te"] = {1: factor_3, 2: factor_3, 3: factor_3, 4: factor_3}
                    exp_1[None]["tr"] = {1: factor_4, 2: factor_4, 3: factor_4, 4: factor_4}
                    for j in range(1,5):
                        exp_1[None]["QMR"][j] = exp_1[None]["QMPM"][j] * exp_1[None]["te"][j]
                    
                    exp_1_data.append(exp_1)
                    exp_1_instances.append(model.create_instance(exp_1))
                    df_1= new_row(df_1, data = exp_1, Instance = name)

    df_1 = df_1.set_index('Instance')
    print(df_1)

    df_1.to_excel("Experimento_MG.xlsx")

    instance_names = list(df_1.index)
    for i in range(n_experimentos):
        print("Solving instance: ",instance_names[i],". Progress: ",i+1," of ",n_experimentos)
        results = opt.solve(exp_1_instances[i])
        if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
            print ("this is feasible and optimal")
    
            df_1 = new_solution_to_row(df_1, data = exp_1_data[i] , Instance= instance_names[i], instance = exp_1_instances[i])
            
        elif results.solver.termination_condition == TerminationCondition.infeasible:
            print ("do something about it? or exit?")
        else:
            # something else is wrong
            print (str(results.solver))
    #
    #df_1.to_excel("./output_files/E1_results_2.xlsx")
    return df_1


def doe2(data, model, opt):
    #Ingresar los datos en una variable
    exp_2 = data
    #Crear un dataframe para el experimento
    df_2 = create_dataframe_base() 
    
    _MAp = [0.68,
            0.82,
            0.96,
            1.1,
            1.23,
            1.37,
            1.51,
            1.64,
            1.85,
            2.05
            ]
    
    _te_i = [ (i/100) for i in range(15,101,20)]
    
    n_experimentos = len(_MAp)*len(_te_i)
    
    exp_2_instances = []
    exp_2_data = []
    
    cont=0  
    for factor_1 in _MAp:
        for factor_2 in _te_i:
            cont = cont + 1
            name = "Exp_2_MA_" + str(round(factor_1,2)) + "_te_i_" + str(round(factor_2,2)) 
            print("Creando los experimentos. Estado: {} de {}. {}% completado...".format(cont,n_experimentos,(cont/n_experimentos)*100))
            exp_2[None]["MA"][None] = factor_1
            exp_2[None]["te"] = {1: factor_2, 2: factor_2, 3: factor_2, 4: factor_2}
            for j in range(1,5):
                exp_2[None]["QMR"][j] = exp_2[None]["QMPM"][j] * exp_2[None]["te"][j]
            
            exp_2_data.append(exp_2)
            exp_2_instances.append(model.create_instance(exp_2))
            df_2= new_row(df_2, data = exp_2, Instance = name)

    df_2 = df_2.set_index('Instance')
    print(df_2)

    df_2.to_excel("Exp_Evolution.xlsx")    
    
    instance_names = list(df_2.index)
    for i in range(n_experimentos):
        print("Solving instance: ",instance_names[i],". Progress: ",i+1," of ",n_experimentos)
        results = opt.solve(exp_2_instances[i])
        if (results.solver.status == SolverStatus.ok) and (results.solver.termination_condition == TerminationCondition.optimal):
            print ("this is feasible and optimal")
    
            df_2 = new_solution_to_row(df_2, data = exp_2_data[i] , Instance= instance_names[i], instance = exp_2_instances[i])
            
        elif results.solver.termination_condition == TerminationCondition.infeasible:
            print ("do something about it? or exit?")
        else:
            # something else is wrong
            print (str(results.solver))          
    
    return df_2



