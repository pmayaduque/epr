# -*- coding: utf-8 -*-
"""
Created on Mon May  2 16:09:13 2022

@author: pmayaduque
"""

from pyomo.environ import *
from pyomo.opt import *


def create_model():
    # Crear modelo
    model = AbstractModel()

    # Sets
    model.ZONES = Set(ordered = False)                            # ZONES generadoras de MPA "i"
    model.COLLECTIONS = Set(ordered = False)                             # ZONES potenciales para ubicar depósitos de C & A "j"
    model.TRANSFORMERS = Set(ordered = False)                            # ZONES potenciales para ubicar depósitos de C, A & T "k"
    model.SIZES = Set(ordered = False)                         # Conjunto de tamaños según la capacidad "m"

    # Parameters
    model.genQ = Param(model.ZONES, within=NonNegativeReals)       # Cantidad real de material generado en la zona i
   
    model.te = Param(model.ZONES, within=NonNegativeReals, mutable = True)        # Tasa efectiva de recuperación sobre el genQ en la zona i
    model.tr = Param(model.ZONES, within=NonNegativeReals, mutable = True)        # Tasa de rechazo sobre el QMR en la zona i
    model.QMR = Param(model.ZONES, within=NonNegativeReals, mutable = True)         # Material con potencial de recup. en la zona i (QMR_i=genQ_i*tr_i)
    model.CAP = Param(model.SIZES, within=NonNegativeReals)        # 
    model.MA = Param(within=NonNegativeReals)                    # Cantidad mínima que el sistema debe aprovechar 
    model.ct = Param(model.COLLECTIONS, model.TRANSFORMERS, 
                    within=NonNegativeReals)        # Costo de transportar material de j hasta k
    model.TA = Param(model.COLLECTIONS, domain=Binary)                 # Binario que indica si un Acopio pertenece a la ORP o es público
    model.TT =Param(model.TRANSFORMERS, domain=Binary)                # Binario que indica si un Transformador pertenece a la ORP o es público
    model.vd = Param(within=NonNegativeReals, mutable=True)                        # Valor del depósito por unidad de producto
    model.vma = Param(within=NonNegativeReals, mutable = True)                       # Valor de una unidad de material recuperado (ahorro para la ORP)
    model.O = Param(within=PositiveReals)                         # Número máximo de COLLECTIONS a abrir
    model.P = Param(within=PositiveReals)                         # Número máximo de TRANSFORMERS a abrir
    model.rc1 = Param(model.COLLECTIONS, within=NonNegativeReals)
    model.rc2 = Param(model.TRANSFORMERS, within=NonNegativeReals)
    model.ec = Param(within=PositiveReals) 
    model.at = Param(model.SIZES, within=PositiveReals) 
    model.alfa = Param(within=NonNegativeReals, mutable = True)                    # Porcentaje para balance
    model.ft = Param(within=PositiveReals, mutable = True)                         # Factor de transformacion 

    # Definir variables
    model.y = Var(model.COLLECTIONS, model.SIZES, domain=Binary)                      # Variable de apertura y tamaño de COLLECTIONS
    model.z = Var(model.TRANSFORMERS, model.SIZES, domain=Binary)              # Variable de apertura y tamaño de TRANSFORMERS
    model.x = Var(model.ZONES, model.COLLECTIONS, model.TRANSFORMERS,
                domain=NonNegativeReals, bounds=(0,1))          # Variable de asignación ZONES - COLLECTIONS - TRANSFORMERS
    model.w = Var(model.ZONES, model.TRANSFORMERS, 
                domain=NonNegativeReals, bounds=(0,1))          # Variable de asignación ZONES - TRANSFORMERS
    model.CT = Var(domain=NonNegativeReals)                       # Costo total de transporte
    model.ES = Var(domain=NonNegativeReals)                       # Egresos del sistema desde la óptica de la ORP
    model.IS = Var(domain=NonNegativeReals)                       # Ingresos del sistema desde la óptica de la ORP
               # Ingreso del sistema para la Orp
    model.CA = Var(domain=NonNegativeReals) # Costo de apertura de instalaciones
    model.f = Var(model.COLLECTIONS, domain=NonNegativeReals)   # Costo apertura COLLECTIONS
    model.g = Var(model.TRANSFORMERS, domain=NonNegativeReals)   # Costo apertura TRANSFORMERS
    model.R = Var(model.ZONES, domain=NonNegativeReals) # Porcentaje de recuperado en cada zona
    model.Rmin = Var(domain=NonNegativeReals) # Porcentaje mínimo recuperado en cada zona
    model.Rmax = Var(domain=NonNegativeReals) # Porcentaje máximo recuperado en cada zona

    # Objective function
    def obj_rule(model):
            return (model.IS - model.ES 
                    - 0.001*sum(model.y[j,m]*model.CAP[m] for m in model.SIZES for j in model.COLLECTIONS)
                    - 0.001*sum(model.z[k,m]*model.CAP[m] for m in model.SIZES for k in model.TRANSFORMERS))
    model.obj_funct = Objective(sense=maximize, rule=obj_rule) 

    # Allocation constraint
    def allocation_rule(model, i):
        return (sum(model.w[i,k] for k in model.TRANSFORMERS) +
                sum(model.x[i,j,k] for k in model.TRANSFORMERS for j in model.COLLECTIONS)
                <= 1
                )
    model.allocation_zone = Constraint(model.ZONES, rule=allocation_rule)
    
    # Facility capacity
    def capacity_rule1(model, j):
        return (sum(model.QMR[i] * (1 - model.tr[i]) * sum(model.x[i,j,k] for k in model.TRANSFORMERS) 
                for i in model.ZONES) <= sum(model.CAP[m] * model.y[j,m] for m in model.SIZES) )
    model.capacity_depot = Constraint(model.COLLECTIONS, rule=capacity_rule1)
    
    def capacity_rule2(model, k):
        return (sum(model.QMR[i] * (1 - model.tr[i]) * model.w[i,k] for i in model.ZONES) + sum(model.QMR[i] * 
             (1 - model.tr[i]) * sum(model.x[i,j,k] 
             for j in model.COLLECTIONS) for i in model.ZONES) <= 
            sum(model.CAP[m] * model.z[k,m] for m in model.SIZES))
    model.capacity_recpl = Constraint(model.TRANSFORMERS, rule=capacity_rule2)
    
    # System recoverable goal
    def minimum_material_rule(model):
        return sum(model.QMR[i] * (1 - model.tr[i]) * (
                sum(model.w[i,k] for k in model.TRANSFORMERS) + 
                sum(model.x[i,j,k] for k in model.TRANSFORMERS for j in model.COLLECTIONS)
                ) for i in model.ZONES) >= model.MA
    model.min_material = Constraint(rule=minimum_material_rule)
    
    # Transport cost
    def transport_cost_rule(model):
        return (
                sum(model.QMR[i]* (1 - model.tr[i]) * sum(model.x[i,j,k] * model.ct[j,k] 
                                    for k in model.TRANSFORMERS 
                                    for j in model.COLLECTIONS if model.TA[j] == 1) for i in model.ZONES) + 
                sum(model.QMR[i]* (1 - model.tr[i]) * sum(model.x[i,j,k] * model.ct[j,k] * model.TT[k]
                                    for k in model.TRANSFORMERS 
                                    for j in model.COLLECTIONS if model.TA[j] == 0) for i in model.ZONES)
        ) == model.CT
    model.costs_ct = Constraint(rule=transport_cost_rule)
    
    # Infraestructure cost
    def open_cost_rule(model):
        return (sum(model.f[j]* model.TA[j] * sum(model.y[j,m] for m in model.SIZES) for j in model.COLLECTIONS) + 
                sum(model.g[k]* model.TT[k] * sum(model.z[k,m] for m in model.SIZES) for k in model.TRANSFORMERS)) == model.CA
    model.cost_or = Constraint(rule=open_cost_rule)
    
    def open_depot_capacity_rule(model, j):
        return (sum(model.y[j,m] for m in model.SIZES) <= 1)
    model.open_depot_capacity = Constraint(model.COLLECTIONS, rule=open_depot_capacity_rule)
    
    def open_recpl_capacity_rule(model, k):
        return (sum(model.z[k,m] for m in model.SIZES) <= 1) 
    model.open_recpl_capacity = Constraint(model.TRANSFORMERS, rule=open_recpl_capacity_rule)
    
    def system_costs_rule(model):
        return ((model.CT + model.CA + model.vd * sum(model.QMR[i] * ( 
            sum(model.w[i,k] for k in model.TRANSFORMERS if model.TT[k] == 1 ) + 
            sum(model.x[i,j,k] * model.TA[j] for k in model.TRANSFORMERS for j in model.COLLECTIONS)) 
            for i in model.ZONES ) + 
            sum(model.QMR[i]* (1 - model.tr[i]) * (
                    model.vma * (1 + model.ft) * (
                            sum(model.w[i,k] for k in model.TRANSFORMERS if model.TT[k] == 0) +
                            sum(model.x[i,j,k] for k in model.TRANSFORMERS if model.TT[k] == 0 
                                for j in model.COLLECTIONS if model.TA[j] == 0)) + 
                    model.vma * model.ft * (
                            sum(model.x[i,j,k] for k in model.TRANSFORMERS if model.TT[k] == 0 
                                for j in model.COLLECTIONS if model.TA[j] == 1)) +
                    model.vma * (sum(model.x[i,j,k] for k in model.TRANSFORMERS if model.TT[k] == 1 
                                for j in model.COLLECTIONS if model.TA[j] == 0))) for i in model.ZONES)) 
                    <= model.ES)
    model.costs_es = Constraint(rule=system_costs_rule)
    
    def system_income_rule(model):
        return (model.vma * (1 + model.ft) * sum(model.QMR[i] * (1 - model.tr[i]) * (
                    sum(model.w[i,k] for k in model.TRANSFORMERS) +
                    sum(model.x[i,j,k] for k in model.TRANSFORMERS 
                        for j in model.COLLECTIONS)
                    ) for i in model.ZONES) + 
                model.vd * (
                    sum((model.genQ[i] - model.QMR[i]) for i in model.ZONES) +
                    sum(model.QMR[i] * (1 - (sum(model.w[i,k] for k in model.TRANSFORMERS) +
                    sum(model.x[i,j,k] for k in model.TRANSFORMERS for j in model.COLLECTIONS))
                    ) for i in model.ZONES))) == model.IS
    model.income_is = Constraint(rule=system_income_rule)
    
    def max_depot_rule(model):
        return sum(model.y[j, m] for m in model.SIZES for j in model.COLLECTIONS) <= model.O
    model.max_depot = Constraint(rule=max_depot_rule)
    
    def max_recpl_rule(model):
        return sum(model.z[k, m] for m in model.SIZES for k in model.TRANSFORMERS)  <= model.P
    model.max_recpl = Constraint(rule=max_recpl_rule)
    
    def flow_rule1(model,i,j,k):
        return model.x[i,j,k] <= sum(model.y[j,m] for m in model.SIZES)
    model.flow1 = Constraint(model.ZONES, model.COLLECTIONS, model.TRANSFORMERS,rule = flow_rule1)
    
    def flow_rule2(model,i,j,k):
        return model.x[i,j,k] <= sum(model.z[k,m] for m in model.SIZES)
    model.flow2 = Constraint(model.ZONES, model.COLLECTIONS, model.TRANSFORMERS, rule = flow_rule2)
    
    def flow_rule3(model,i,k):
        return model.w[i,k] <= sum(model.z[k,m] for m in model.SIZES)
    model.flow3 = Constraint(model.ZONES, model.TRANSFORMERS, rule = flow_rule3)
    #New
    def open_cost_rule1(model, j):
        return (model.rc1[j] * sum(model.at[m] * model.y[j,m] for m in model.SIZES) == model.f[j])
    model.cost_or1 = Constraint(model.COLLECTIONS, rule=open_cost_rule1)
    
    def open_cost_rule2(model, k):
        return (model.ec + model.rc2[k] * sum(model.at[m]*model.z[k,m] for m in model.SIZES) == model.g[k])
    model.cost_or2 = Constraint(model.TRANSFORMERS, rule=open_cost_rule2)
    
    def rec_by_zone_rule1(model, i):
        return ((model.QMR[i]*(1 - model.tr[i])*
                 (sum(model.w[i,k] for k in model.TRANSFORMERS)+
                  sum(model.x[i,j,k] for k in model.TRANSFORMERS for j in model.COLLECTIONS))
                 ) == model.R[i]
                )
    model.rec_by_zone1 = Constraint(model.ZONES, rule = rec_by_zone_rule1)
    
    def rec_by_zone_rule2(model, i):
        return (model.Rmin <= model.R[i])
    model.rec_by_zone2 = Constraint(model.ZONES, rule = rec_by_zone_rule2)
    
    def rec_by_zone_rule3(model, i):
        return (model.Rmax >= model.R[i])
    model.rec_by_zone3 = Constraint(model.ZONES, rule = rec_by_zone_rule3)
    
    def rec_by_zone_rule4(model):
        return (model.Rmax - model.Rmin <= model.alfa * 
                sum(model.R[i] for i in model.ZONES)
                )
    model.rec_by_zone4 = Constraint(rule = rec_by_zone_rule4)
    
    
    return model