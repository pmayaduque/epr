# -*- coding: utf-8 -*-
"""
Created on Wed May  4 09:21:13 2022

@author: pmayaduque
"""

import itertools
import pandas as pd
import optimiser as opt 
import plotly.express as px
import plotly.io as pio
from plotly.offline import plot
pio.renderers.default='browser'

import seaborn as sns

class Experiment:
    def __init__(self, instance, exp_design):
        self.exp_design = exp_design
        self.factors = list(exp_design.keys())
        # get all combinations all experimentation levels 
        self.levels = [l for l in exp_design.values()]
        self.combinations = list(itertools.product(*self.levels))
        self.df_results = pd.DataFrame()
        n_experiment = 0
        for comb in self.combinations:
            n_experiment += 1
            for idx in range(len(self.factors)):  
                len_attr = len(getattr(instance, self.factors[idx]))
                if len_attr == 1:
                    query = "instance.{}={}".format(self.factors[idx], comb[idx])
                    exec(query)
                else:
                    for k,v in comb[idx].items():                        
                        query = "instance.{}[{}]={}".format(self.factors[idx], k, v)
                        exec(query)
            print("solving {} out of {}".format(n_experiment, len(self.combinations)))            
            results, termination = opt.solve_instance(instance, 
                                       optimizer = 'gurobi',
                                       mipgap = 0.002,
                                       tee = False)           
            model_results = opt.Results(instance, termination) 
            
            # get results in dataframe
            dict_results = {**model_results.instance_data, **model_results.solution}
            if len(self.df_results) == 0:   
                self.df_results = pd.DataFrame(columns = list(dict_results.keys()))
                self.df_results = self.df_results. append(dict_results, ignore_index = True)
            else: 
                self.df_results = self.df_results.append(dict_results, ignore_index = True)


    def create_graph(self, filepath=None):
        if filepath != None:
            try:
                self.df_results = pd.read_csv(filepath)
            except:
                print("There is not a file with the given path")
        # df = self.df_results[self.df_results["vma"]==250000]        
        df = self.df_results
        print(df.shape)
        #df = df["vma_vd"] = df["vma"].apply(lambda x: x[1])
        fig = px.box(df, x="vd", y="OF_value")
        fig.show()
    
    def create_graph1(self, filepath=None):
        if filepath != None:
            try:
                self.df_results = pd.read_csv(filepath)
            except:
                print("There is not a file with the given path")
            df = self.df_results[(self.df_results['vma']==250000) & (self.df_results['tr']==0.15)]
            print(df.shape)
        fig = sns.barplot(data= df, x="vd", y="OF_value", hue ='te' )
        fig.show()
                
            
           