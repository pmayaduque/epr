# -*- coding: utf-8 -*-
"""
Created on Mon May  2 16:09:13 2022

@author: pmayaduque
"""

from pyomo.environ import *
from pyomo.opt import *
from pyomo.core import value
import time


def create_model():
    # Crear modelo
    model = AbstractModel()

    # Sets
    model.ZONES = Set(ordered = False)                            # ZONES generadoras de MPA "i"
    model.COLLECTIONS = Set(ordered = False)                             # ZONES potenciales para ubicar depósitos de C & A "j"
    model.TRANSFORMERS = Set(ordered = False)                            # ZONES potenciales para ubicar depósitos de C, A & T "k"
    model.SIZES = Set(ordered = False)                         # Conjunto de tamaños según la capacidad "m"

    # Parameters
    model.genQ = Param(model.ZONES, within=NonNegativeReals, mutable = True)       # Cantidad real de material generado en la zona i
   
    model.te = Param(model.ZONES, within=NonNegativeReals, mutable = True)        # Tasa efectiva de recuperación sobre el genQ en la zona i
    model.tr = Param(model.ZONES, within=NonNegativeReals, mutable = True)        # Tasa de rechazo sobre el QMR en la zona i
    model.QMR = Param(model.ZONES, within=NonNegativeReals, mutable = True)         # Material con potencial de recup. en la zona i (QMR_i=genQ_i*tr_i)
    model.CAP = Param(model.SIZES, within=NonNegativeReals, mutable = True)        # 
    model.MA = Param(within=NonNegativeReals, mutable = True)                    # Cantidad mínima que el sistema debe aprovechar 
    model.ct = Param(model.COLLECTIONS, model.TRANSFORMERS, within=NonNegativeReals)        # Costo de transportar material de j hasta k
    model.TA = Param(model.COLLECTIONS, domain=Binary)                 # Binario que indica si un Acopio pertenece a la ORP o es público
    model.TT =Param(model.TRANSFORMERS, domain=Binary)                # Binario que indica si un Transformador pertenece a la ORP o es público
    model.vd = Param(within=NonNegativeReals, mutable=True)                        # Valor del depósito por unidad de producto
    model.vma = Param(within=NonNegativeReals, mutable = True)                       # Valor de una unidad de material recuperado (ahorro para la ORP)
    model.O = Param(within=PositiveReals, mutable=True)                         # Número máximo de COLLECTIONS a abrir
    model.P = Param(within=PositiveReals, mutable=True)                         # Número máximo de TRANSFORMERS a abrir
    model.r_cc = Param(model.COLLECTIONS, within=NonNegativeReals, mutable=True)
    model.r_tp = Param(model.TRANSFORMERS, within=NonNegativeReals, mutable=True)
    model.ec = Param(within=PositiveReals) 
    # TODO: is there a single set of areas for both cc and tp
    model.area = Param(model.SIZES, within=PositiveReals) 
    model.alfa = Param(within=NonNegativeReals, mutable = True)                    # Porcentaje para balance
    model.ft = Param(within=PositiveReals, mutable = True)                         # Factor de transformacion 
    model.fop= Param(within=PositiveReals, mutable = True)  # percentage of the valorization ft that is expend in transformation  
    model.ind_income = Param(within=Binary, initialize = 1, mutable = True)
    # Definir variables
    model.y = Var(model.COLLECTIONS, model.SIZES, domain=Binary)                      # Variable de apertura y tamaño de COLLECTIONS
    model.z = Var(model.TRANSFORMERS, model.SIZES, domain=Binary)              # Variable de apertura y tamaño de TRANSFORMERS
    model.x = Var(model.ZONES, model.COLLECTIONS, model.TRANSFORMERS,
                domain=NonNegativeReals, bounds=(0,1))          # Variable de asignación ZONES - COLLECTIONS - TRANSFORMERS
    model.w = Var(model.ZONES, model.TRANSFORMERS, 
                domain=NonNegativeReals, bounds=(0,1))          # Variable de asignación ZONES - TRANSFORMERS
    model.R = Var(model.ZONES, domain=NonNegativeReals) # Porcentaje de recuperado en cada zona
    model.Rmin = Var(domain=NonNegativeReals) # Porcentaje mínimo recuperado en cada zona
    model.Rmax = Var(domain=NonNegativeReals) # Porcentaje máximo recuperado en cada zona

    model.InfrasCost = Var(domain=NonNegativeReals) # Costo de apertura de instalaciones
    model.TranspCost = Var(domain=NonNegativeReals)                       # Costo total de transporte
    model.AcquisCost = Var(domain=NonNegativeReals)
    model.TransfCost = Var(domain=NonNegativeReals) # Transformation cost
    model.Income = Var(domain=NonNegativeReals)                       # Ingresos del sistema desde la óptica de la ORP
    
    
    
    # Objective function
    def obj_rule(model):
            return (model.Income - (model.InfrasCost + model.TranspCost + model.AcquisCost) 
                    - 0.001*sum(model.y[j,m]*model.CAP[m] for m in model.SIZES for j in model.COLLECTIONS)
                    - 0.001*sum(model.z[k,m]*model.CAP[m] for m in model.SIZES for k in model.TRANSFORMERS))
    model.obj_funct = Objective(sense=maximize, rule=obj_rule) 
    
    # System income
    def system_income_rule(model):
        return (model.vma * (1 + model.ft) * sum(model.QMR[i] * (1 - model.tr[i]) * (
                    sum(model.w[i,k] for k in model.TRANSFORMERS) +
                    sum(model.x[i,j,k] for k in model.TRANSFORMERS for j in model.COLLECTIONS)
                    ) for i in model.ZONES) + 
                model.vd * (
                    sum(model.genQ[i] for i in model.ZONES) -
                    sum(model.QMR[i] * (sum(model.w[i,k] for k in model.TRANSFORMERS) +
                    (sum(model.x[i,j,k] for k in model.TRANSFORMERS for j in model.COLLECTIONS))
                    ) for i in model.ZONES))) == model.Income
    model.ct_income = Constraint(rule=system_income_rule)
    
    # Infraestructure cost
    def open_cost_rule(model):
        return (sum(model.r_cc[j]*model.TA[j]*sum(model.area[s]*model.y[j,s] for s in model.SIZES) for j in model.COLLECTIONS) + 
                sum(model.r_tp[k]*model.TT[k]*sum(model.area[s]*model.z[k,s] for s in model.SIZES) for k in model.TRANSFORMERS)
                + model.ec) == model.InfrasCost
    model.cost_or = Constraint(rule=open_cost_rule)
    
    # Transport cost
    def transport_cost_rule(model):
        return (
                sum(model.QMR[i]* (1 - model.tr[i]) * sum(model.x[i,j,k] * model.ct[j,k] 
                                    for k in model.TRANSFORMERS 
                                    for j in model.COLLECTIONS if model.TA[j] == 1) for i in model.ZONES) + 
                sum(model.QMR[i]* (1 - model.tr[i]) * sum(model.x[i,j,k] * model.ct[j,k] * model.TT[k]
                                    for k in model.TRANSFORMERS 
                                    for j in model.COLLECTIONS if model.TA[j] == 0) for i in model.ZONES)
        ) == model.TranspCost
    model.ct_tranportCost = Constraint(rule=transport_cost_rule)
    
    # Acquisition cost 
    def acquisition_costs_rule(model):
        return (model.vd*(sum(model.x[i,j,k] for i in model.ZONES  for j in model.COLLECTIONS if model.TA[j]==1 for k in model.TRANSFORMERS if model.TT[k]==0))+
                model.vma*(sum(model.x[i,j,k] for i in model.ZONES  for j in model.COLLECTIONS if model.TA[j]==0 for k in model.TRANSFORMERS if model.TT[k]==1))+
                model.vd*(sum(model.x[i,j,k] for i in model.ZONES  for j in model.COLLECTIONS if model.TA[j]==1 for k in model.TRANSFORMERS if model.TT[k]==1))+
                model.vma*(1+model.ft)*(sum(model.x[i,j,k] for i in model.ZONES  for j in model.COLLECTIONS if model.TA[j]==0 for k in model.TRANSFORMERS if model.TT[k]==0))+
                model.vd*(sum(model.w[i,k] for i in model.ZONES for k in model.TRANSFORMERS if model.TT[k]==1))+
                model.vma*(1+model.ft)*(sum(model.w[i,k] for i in model.ZONES for k in model.TRANSFORMERS if model.TT[k]==0))
                == model.AcquisCost)
    model.ct_AcquisCost = Constraint(rule=acquisition_costs_rule)
    
    # Constraints
    
    # At most one facility in each location
    def open_depot_capacity_rule(model, j):
        return (sum(model.y[j,m] for m in model.SIZES) <= 1)
    model.open_depot_capacity = Constraint(model.COLLECTIONS, rule=open_depot_capacity_rule)
    
    def open_recpl_capacity_rule(model, k):
        return (sum(model.z[k,m] for m in model.SIZES) <= 1) 
    model.open_recpl_capacity = Constraint(model.TRANSFORMERS, rule=open_recpl_capacity_rule)
    
    # Maximum number of each facility
    def max_depot_rule(model):
        return sum(model.y[j, m] for m in model.SIZES for j in model.COLLECTIONS) <= model.O
    model.max_depot = Constraint(rule=max_depot_rule)
    
    def max_recpl_rule(model):
        return sum(model.z[k, m] for m in model.SIZES for k in model.TRANSFORMERS)  <= model.P
    model.max_recpl = Constraint(rule=max_recpl_rule)    
    
    # Binary relation between opened facilities 
    def flow_rule1(model,i,j,k):
        return model.x[i,j,k] <= sum(model.y[j,m] for m in model.SIZES)
    model.flow1 = Constraint(model.ZONES, model.COLLECTIONS, model.TRANSFORMERS,rule = flow_rule1)
    
    def flow_rule2(model,i,j,k):
        return model.x[i,j,k] <= sum(model.z[k,m] for m in model.SIZES)
    model.flow2 = Constraint(model.ZONES, model.COLLECTIONS, model.TRANSFORMERS, rule = flow_rule2)
    
    def flow_rule3(model,i,k):
        return model.w[i,k] <= sum(model.z[k,m] for m in model.SIZES)
    model.flow3 = Constraint(model.ZONES, model.TRANSFORMERS, rule = flow_rule3)
        
    # Maximum flow allowed (do not exced the generated capacity)
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
    
    # Balance between zones    
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

def solve_instance(instance,
                optimizer='gurobi',
                mipgap=0.02,
                tee=True):
    solver = SolverFactory(optimizer)
    solver.options['MIPGap'] = mipgap
    timea = time.time()
    results = solver.solve(instance, tee = tee)
    term_cond = results.solver.termination_condition
    #s_status = results.solver.status
    term = {}
    # TODO: Check which other termination conditions may be interesting for us 
    # http://www.pyomo.org/blog/2015/1/8/accessing-solver
    #status {aborted, unknown}, Termination Condition {maxTimeLimit (put), locallyOptimal, maxEvaluations, licesingProblem}
    if term_cond != TerminationCondition.optimal:
          term['Temination Condition'] = format(term_cond)
          execution_time = time.time() - timea
          term['Execution time'] = execution_time
          raise RuntimeError("Optimization failed.")

    else: 
          term['Temination Condition'] = format(term_cond)
          execution_time = time.time() - timea
          term['Execution time'] = execution_time    
    return results, term


class Results():
    def __init__(self, instance, termination):
        # general descriptives        
        self.instance_data = {}
        self.instance_data['ind_income'] = value(instance.ind_income)
        self.instance_data['genQ'] = [(k, value(v)) for k, v in instance.genQ.items()]
        self.instance_data['te'] = [(k, value(v)) for k, v in instance.te.items()]
        self.instance_data['tr'] = [(k, value(v)) for k, v in instance.tr.items()]
        self.instance_data['QMR'] = [(k, value(v)) for k, v in instance.QMR.items()]
        self.instance_data['CAP'] = [(k, value(v)) for k, v in instance.CAP.items()]
        self.instance_data['MA'] = value(instance.MA)
        self.instance_data['vd'] = value(instance.vd)
        self.instance_data['vma'] = value(instance.vma)
        self.instance_data['O'] = value(instance.O)
        self.instance_data['P'] = value(instance.P)
        self.instance_data['alfa'] = value(instance.alfa)
        self.instance_data['ft'] = value(instance.ft)
        self.instance_data['ec'] = value(instance.ec)
        self.instance_data['r_cc'] = [(k, value(v)) for k, v in instance.r_cc.items()]
        self.instance_data['r_tp'] = [(k, value(v)) for k, v in instance.r_tp.items()]
        self.instance_data['area'] = [(k, value(v)) for k, v in instance.area.items()]
      
        self.solution = {}
        if termination['Temination Condition'] == 'optimal':
            self.solution['temination'] = 'optimal'
            self.solution['OF_value'] = instance.obj_funct.expr()
            self.solution['cost_infraest'] = value(instance.InfrasCost)
            self.solution['cost_transport'] = value(instance.TranspCost)
            self.solution['cost_acquis'] = value(instance.AcquisCost)
            self.solution['y'] = [(key, value) for key, value in instance.y.get_values().items() if value > 0]
            self.solution['z'] = [(key, value) for key, value in instance.z.get_values().items() if value > 0]
            self.solution['x'] = [(key, value) for key, value in instance.x.get_values().items() if value > 0]
            self.solution['w'] = [(key, value) for key, value in instance.w.get_values().items() if value > 0]
            self.solution['R_total'] = sum(instance.R.get_values().values()) 
            self.solution['Rmax'] = value(instance.Rmax) 
            self.solution['Rmim'] = value(instance.Rmin) 
        else:
            self.solution['temination'] = 'no-optimal'
            self.solution['OF_value'] = None
            self.solution['R_total'] = sum(instance.R.get_values().values()) 
            self.solution['cost_infraest'] = None
            self.solution['cost_transport'] = None
            self.solution['cost_acquis'] = None
            self.solution['y'] = None
            self.solution['z'] = None
            self.solution['x'] = None
            self.solution['w'] = None
            self.solution['Rmax'] = None
            self.solution['Rmim'] = None

    
    
        