# -*- coding: utf-8 -*-
"""
Created on Wed Mar 24 11:00:03 2021

@author: Jesus Galarcio
"""
import pyomo.environ as pyo
from pyomo.opt import *


def create_model():
    # Crear modelo
    model = AbstractModel(model_name)

    # Sets
    model.ZONES = Set(ordered = False)                            # Zonas generadoras de MPA "i"
    model.COLLECTIONS = Set(ordered = False)                             # Zonas potenciales para ubicar depósitos de C & A "j"
    model.TRANSFORMERS = Set(ordered = False)                            # Zonas potenciales para ubicar depósitos de C, A & T "k"
    model.SIZES = Set(ordered = False)                         # Conjunto de tamaños según la capacidad "m"

    # Parameters
    model.zone_gen = Param(model.Zonas, within=NonNegativeReals)       # Cantidad real de material generado en la zona i
    
    return model


def create_modelT(model_name):
    # Crear modelo
    model = AbstractModel(model_name)

    # Definir conjuntos 
    model.Zonas = Set(ordered = False)                            # Zonas generadoras de MPA "i"
    model.Acopios = Set(ordered = False)                             # Zonas potenciales para ubicar depósitos de C & A "j"
    model.Transformadores = Set(ordered = False)                            # Zonas potenciales para ubicar depósitos de C, A & T "k"
    model.Capacidades = Set(ordered = False)                         # Conjunto de tamaños según la capacidad "m"

    # Definir parámetros
    model.QMPM = Param(model.Zonas, within=NonNegativeReals)       # Cantidad real de material generado en la zona i
    model.te = Param(model.Zonas, within=NonNegativeReals, mutable = True)        # Tasa efectiva de recuperación sobre el QMPM en la zona i
    model.tr = Param(model.Zonas, within=NonNegativeReals, mutable = True)        # Tasa de rechazo sobre el QMR en la zona i
    model.QMR = Param(model.Zonas, within=NonNegativeReals, mutable = True)         # Material con potencial de recup. en la zona i (QMR_i=QMPM_i*tr_i)
    model.CAP = Param(model.Capacidades, within=NonNegativeReals)        # 
    model.MA = Param(within=NonNegativeReals)                    # Cantidad mínima que el sistema debe aprovechar 
    model.ct = Param(model.Acopios, model.Transformadores, 
                    within=NonNegativeReals)        # Costo de transportar material de j hasta k
    model.TA = Param(model.Acopios, domain=Binary)                 # Binario que indica si un Acopio pertenece a la ORP o es público
    model.TT =Param(model.Transformadores, domain=Binary)                # Binario que indica si un Transformador pertenece a la ORP o es público
    model.vd = Param(within=NonNegativeReals, mutable=True)                        # Valor del depósito por unidad de producto
    model.vma = Param(within=NonNegativeReals, mutable = True)                       # Valor de una unidad de material recuperado (ahorro para la ORP)
    model.O = Param(within=PositiveReals)                         # Número máximo de Acopios a abrir
    model.P = Param(within=PositiveReals)                         # Número máximo de Transformadores a abrir
    model.rc1 = Param(model.Acopios, within=NonNegativeReals)
    model.rc2 = Param(model.Transformadores, within=NonNegativeReals)
    model.ec = Param(within=PositiveReals) 
    model.at = Param(model.Capacidades, within=PositiveReals) 
    model.alfa = Param(within=NonNegativeReals, mutable = True)                    # Porcentaje para balance
    model.ft = Param(within=PositiveReals, mutable = True)                         # Factor de transformacion 

    # Definir variables
    model.y = Var(model.Acopios, model.Capacidades, domain=Binary)                      # Variable de apertura y tamaño de Acopios
    model.z = Var(model.Transformadores, model.Capacidades, domain=Binary)              # Variable de apertura y tamaño de Transformadores
    model.x = Var(model.Zonas, model.Acopios, model.Transformadores,
                domain=NonNegativeReals, bounds=(0,1))          # Variable de asignación Zonas - Acopios - Transformadores
    model.w = Var(model.Zonas, model.Transformadores, 
                domain=NonNegativeReals, bounds=(0,1))          # Variable de asignación Zonas - Transformadores
    model.CT = Var(domain=NonNegativeReals)                       # Costo total de transporte
    model.ES = Var(domain=NonNegativeReals)                       # Egresos del sistema desde la óptica de la ORP
    model.IS = Var(domain=NonNegativeReals)                       # Ingresos del sistema desde la óptica de la ORP
    model.Z = Objective(sense=maximize, rule=obj_rule)            # Ingreso del sistema para la Orp
    model.CA = Var(domain=NonNegativeReals) # Costo de apertura de instalaciones
    model.f = Var(model.Acopios, domain=NonNegativeReals)   # Costo apertura acopios
    model.g = Var(model.Transformadores, domain=NonNegativeReals)   # Costo apertura transformadores
    model.R = Var(model.Zonas, domain=NonNegativeReals) # Porcentaje de recuperado en cada zona
    model.Rmin = Var(domain=NonNegativeReals) # Porcentaje mínimo recuperado en cada zona
    model.Rmax = Var(domain=NonNegativeReals) # Porcentaje máximo recuperado en cada zona

    # Definir restricciones
    model.allocation_zone = Constraint(model.Zonas, rule=allocation_rule)
    model.capacity_depot = Constraint(model.Acopios, rule=capacity_rule1)
    model.capacity_recpl = Constraint(model.Transformadores, rule=capacity_rule2)
    model.min_material = Constraint(rule=minimum_material_rule)
    ##New
    model.cost_or = Constraint(rule=open_cost_rule)
    
    model.costs_ct = Constraint(rule=transport_cost_rule)
    model.costs_es = Constraint(rule=system_costs_rule)
    model.income_is = Constraint(rule=system_income_rule)
    model.open_depot_capacity = Constraint(model.Acopios, rule=open_depot_capacity_rule)
    model.open_recpl_capacity = Constraint(model.Transformadores, rule=open_recpl_capacity_rule)
    model.max_depot = Constraint(rule=max_depot_rule)
    model.max_recpl = Constraint(rule=max_recpl_rule)
    model.flow1 = Constraint(model.Zonas, model.Acopios, model.Transformadores,rule = flow_rule1)
    model.flow2 = Constraint(model.Zonas, model.Acopios, model.Transformadores, rule = flow_rule2)
    model.flow3 = Constraint(model.Zonas, model.Transformadores, rule = flow_rule3)
    #New
    model.cost_or1 = Constraint(model.Acopios, rule=open_cost_rule1)
    model.cost_or2 = Constraint(model.Transformadores, rule=open_cost_rule2)
    model.rec_by_zone1 = Constraint(model.Zonas, rule = rec_by_zone_rule1)
    model.rec_by_zone2 = Constraint(model.Zonas, rule = rec_by_zone_rule2)
    model.rec_by_zone3 = Constraint(model.Zonas, rule = rec_by_zone_rule3)
    model.rec_by_zone4 = Constraint(rule = rec_by_zone_rule4)

    return model

# Definir función objetivo
def obj_rule(model):
        return (model.IS - model.ES 
                - 0.001*sum(model.y[j,m]*model.CAP[m] for m in model.Capacidades for j in model.Acopios)
                - 0.001*sum(model.z[k,m]*model.CAP[m] for m in model.Capacidades for k in model.Transformadores))
 ##- 0.001*sum(model.y[i,m] for m in model.Capacidades for i in model.Zonas))

## Cada zona GMPA puede ser asignada a una DCA, a una DCAT o a ambas

def allocation_rule(model, i):
    return (sum(model.w[i,k] for k in model.Transformadores) +
            sum(model.x[i,j,k] for k in model.Transformadores for j in model.Acopios)
            <= 1
            )

## Capacidad de los Acopios

def capacity_rule1(model, j):
    return (sum(model.QMR[i] * (1 - model.tr[i]) * sum(model.x[i,j,k] for k in model.Transformadores) 
            for i in model.Zonas) <= sum(model.CAP[m] * model.y[j,m] for m in model.Capacidades) )

## Capacidad de los Transformadores

def capacity_rule2(model, k):
    return (sum(model.QMR[i] * (1 - model.tr[i]) * model.w[i,k] for i in model.Zonas) + sum(model.QMR[i] * 
         (1 - model.tr[i]) * sum(model.x[i,j,k] 
         for j in model.Acopios) for i in model.Zonas) <= 
        sum(model.CAP[m] * model.z[k,m] for m in model.Capacidades))

## Cantidad mínima de material aprovechado

def minimum_material_rule(model):
    return sum(model.QMR[i] * (1 - model.tr[i]) * (
            sum(model.w[i,k] for k in model.Transformadores) + 
            sum(model.x[i,j,k] for k in model.Transformadores for j in model.Acopios)
            ) for i in model.Zonas) >= model.MA

## Costo total de transporte

def transport_cost_rule(model):
    return (
            sum(model.QMR[i]* (1 - model.tr[i]) * sum(model.x[i,j,k] * model.ct[j,k] 
                                for k in model.Transformadores 
                                for j in model.Acopios if model.TA[j] == 1) for i in model.Zonas) + 
            sum(model.QMR[i]* (1 - model.tr[i]) * sum(model.x[i,j,k] * model.ct[j,k] * model.TT[k]
                                for k in model.Transformadores 
                                for j in model.Acopios if model.TA[j] == 0) for i in model.Zonas)
    ) == model.CT

## Costo de apertura(New)
            
def open_cost_rule(model):
    return (sum(model.f[j]* model.TA[j] * sum(model.y[j,m] for m in model.Capacidades) for j in model.Acopios) + 
            sum(model.g[k]* model.TT[k] * sum(model.z[k,m] for m in model.Capacidades) for k in model.Transformadores)) == model.CA

def open_cost_rule1(model, j):
    return (model.rc1[j] * sum(model.at[m] * model.y[j,m] for m in model.Capacidades) == model.f[j])

def open_cost_rule2(model, k):
    return (model.ec + model.rc2[k] * sum(model.at[m]*model.z[k,m] for m in model.Capacidades) == model.g[k])


## Egresos operativos del sistema de reembolso de depósito para la ORP:
# - Suma los depósitos pagados por el ingreso de material al sistema
# - El valor que, eventualmente, se le pagaría las instalaciones públicas 
#  de tipo DCAT por la certificación de aprovechamiento de material gestionado
#  a través de su infraestructura

def system_costs_rule(model):
    return ((model.CT + model.CA + model.vd * sum(model.QMR[i] * ( 
        sum(model.w[i,k] for k in model.Transformadores if model.TT[k] == 1 ) + 
        sum(model.x[i,j,k] * model.TA[j] for k in model.Transformadores for j in model.Acopios)) 
        for i in model.Zonas ) + 
        sum(model.QMR[i]* (1 - model.tr[i]) * (
                model.vma * (1 + model.ft) * (
                        sum(model.w[i,k] for k in model.Transformadores if model.TT[k] == 0) +
                        sum(model.x[i,j,k] for k in model.Transformadores if model.TT[k] == 0 
                            for j in model.Acopios if model.TA[j] == 0)) + 
                model.vma * model.ft * (
                        sum(model.x[i,j,k] for k in model.Transformadores if model.TT[k] == 0 
                            for j in model.Acopios if model.TA[j] == 1)) +
                model.vma * (sum(model.x[i,j,k] for k in model.Transformadores if model.TT[k] == 1 
                            for j in model.Acopios if model.TA[j] == 0))) for i in model.Zonas)) 
                <= model.ES)

## Ingresos operativos del sistema de reembolso de depósit para la ORP

def system_income_rule(model):
    return (model.vma * (1 + model.ft) * sum(model.QMR[i] * (1 - model.tr[i]) * (
                sum(model.w[i,k] for k in model.Transformadores) +
                sum(model.x[i,j,k] for k in model.Transformadores 
                    for j in model.Acopios)
                ) for i in model.Zonas) + 
            model.vd * (
                sum((model.QMPM[i] - model.QMR[i]) for i in model.Zonas) +
                sum(model.QMR[i] * (1 - (sum(model.w[i,k] for k in model.Transformadores) +
                sum(model.x[i,j,k] for k in model.Transformadores for j in model.Acopios))
                ) for i in model.Zonas))) == model.IS

## Asignación de capacidades a Acopios *

def open_depot_capacity_rule(model, j):
    return (sum(model.y[j,m] for m in model.Capacidades) <= 1)

## Asignación de capacidades a Transformadores

def open_recpl_capacity_rule(model, k):
    return (sum(model.z[k,m] for m in model.Capacidades) <= 1) 

## Número máximo de Acopios a abrir

def max_depot_rule(model):
    return sum(model.y[j, m] for m in model.Capacidades for j in model.Acopios) <= model.O

## Número máximo de Transformadores a abrir

def max_recpl_rule(model):
    return sum(model.z[k, m] for m in model.Capacidades for k in model.Transformadores)  <= model.P

## No se pueden asignar Zonas a Acopios cerrados

def flow_rule1(model,i,j,k):
    return model.x[i,j,k] <= sum(model.y[j,m] for m in model.Capacidades)

## No se pueden asignar Zonas a Transformadores cerrados aunque pase por un DCA abierto

def flow_rule2(model,i,j,k):
    return model.x[i,j,k] <= sum(model.z[k,m] for m in model.Capacidades)

## No se pueden asignar Zonas directamente a Transformadores cerrados
def flow_rule3(model,i,k):
    return model.w[i,k] <= sum(model.z[k,m] for m in model.Capacidades)

## Porcentaje recuperado por zona
def rec_by_zone_rule1(model, i):
    return ((model.QMR[i]*(1 - model.tr[i])*
             (sum(model.w[i,k] for k in model.Transformadores)+
              sum(model.x[i,j,k] for k in model.Transformadores for j in model.Acopios))
             ) == model.R[i]
            )

def rec_by_zone_rule2(model, i):
    return (model.Rmin <= model.R[i])

def rec_by_zone_rule3(model, i):
    return (model.Rmax >= model.R[i])

def rec_by_zone_rule4(model):
    return (model.Rmax - model.Rmin <= model.alfa * 
            sum(model.R[i] for i in model.Zonas)
            )
