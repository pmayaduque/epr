# -*- coding: utf-8 -*-
"""
Created on Wed May  4 09:21:13 2022

@author: pmayaduque
"""

import itertools
import pandas as pd
import optimiser as opt 
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
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
            print(comb)
            n_experiment += 1
            for idx in range(len(self.factors)):  
                # identify whether the parameter is a single value or indexed  
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
        
        # Calculate extra columns
        self.df_results['goal_ratio'] = self.df_results['goal_ratio'].astype(float)
        self.df_results['%income_vd'] = (100*(self.df_results['income_vd']/self.df_results['income'])).astype(float)
        self.df_results['%income_vma'] = (100*(self.df_results['income_vma']/self.df_results['income'])).astype(float)
        
        
    def graph_goalAchiv(self, filepath=None):
        if filepath != None:
            try:
                self.df_results = pd.read_csv(filepath)
            except:
                print("There is not a file with the given path")   
        
        df = self.df_results
        
        df_grouped = df.groupby(['te', 'vd'])['goal_ratio'].mean().reset_index()
        
        df_grouped.sort_values(by=['vd'])        
        fig = px.line(df_grouped, x='vd', y='goal_ratio',  color='te',
                      color_discrete_sequence = px.colors.qualitative.Dark24,
                      title = "Goal accomplishment vs ratio between deposit and material value",
                      labels = {
                          'te': 'recovery rate',
                          'vd': 'deposit value as fraction of material value in the market',
                          'goal_ratio': 'goal accomplishment',
                          'MA':'recovery goal'})
        fig.update_layout(title_x=0.5)                
        return fig

    def graph_income(self, filepath=None):
        if filepath != None:
            try:
                self.df_results = pd.read_csv(filepath)
            except:
                print("There is not a file with the given path")
        df = self.df_results
        df_grouped = df.groupby(['te', 'MA', 'vd'])[['income', '%income_vd', '%income_vma']].mean().reset_index()
        df_grouped.sort_values(by=['vd'])     
        df_filtered = df_grouped[df_grouped['te']==0.3]
        fig = px.line(df_filtered, x='vd', y=['%income_vd','%income_vma'] , animation_frame="MA",
                      color_discrete_sequence = px.colors.qualitative.Dark24,
                      title = "Goal accomplishment vs ratio between deposit and material value",
                      labels = {
                          'te': 'recovery rate',
                          'vd': 'deposit/material value as fraction of vma',
                          'goal_ratio': '% of goal accomplishment',
                          'MA':'recovery goal'})
                        
        return fig
    
    def create_graph1(self, filepath=None):
        if filepath != None:
            try:
                self.df_results = pd.read_csv(filepath)
            except:
                print("There is not a file with the given path")
            df = self.df_results[(self.df_results['vma']==250000) & (self.df_results['tr']==0.15)]
            print(df.shape)
        fig = sns.barplot(data= df, x="vd", y="OF_value", hue ='te', )
        
        return fig


# Describes a set of predifined experiments                
def EDA_graph(instance, 
              results_path = None):
    
    if results_path != None:
        try:
            df1 = pd.read_csv(results_path)
        except:
            print("There is not a file with the given path")
    else:
        exp_design= {'vma' :[i for i in range(250000, 500001, 50000)],
                     'vd' : [i/100 for i in range(0, 101, 10)],
                     'MA' : [0.10, 0.15, 0.20],
                     'te' : [0.15, 0.20, 0.30],
                     'alfa' : [0.20, 0.30, 0.50],
                     'ft' : [0.15, 0.30, 0.45]
                }
        experiment1 = Experiment(instance, exp_design)
        df1 = experiment1.df_results            
            
    # Create vars for the graph   
    dict_varX = {'vma': "Material value", 
                 'vd': "Deposit Value", 
                 'MA': "Recovery goal", 
                 'te': "recovery rate"}
    plot_varX = list(dict_varX.keys())

    dict_varY = {'OF_value': 'System profit', 
                 'goal_ratio': "Goal Achivement"}
    plot_varY = list(dict_varY.keys())

    # Creates subplots container
    fig = make_subplots(rows=len(plot_varY), cols=len(plot_varX))
    
    # Creates each subplot
    for i in range(len(plot_varY)):
        for j in range(len(plot_varX)):
            subfig = go.Box(x=df1[plot_varX[j]], y=df1[plot_varY[i]],
                                name=plot_varX[j])
            fig.append_trace(subfig, i+1, j+1)
    # Remove legends         
    fig.update(layout_showlegend=False)

    # set axis labels
    for i in range(len(plot_varY)):
        for j in range(len(plot_varX)):        
            fig.update_xaxes(title_text=dict_varX[plot_varX[j]], row = i+1, col = j+1)
            if j == 0:
                fig.update_yaxes(title_text=dict_varY[plot_varY[i]], row = i+1, col = 1)
    
    return fig 
        
           