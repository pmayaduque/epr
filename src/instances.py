# -*- coding: utf-8 -*-
"""
Created on Wed Mar 24 10:46:37 2021

@author: Jesus Galarcio

En este script se incluiran algunas funciones que serán de gran utilidad para 
realizar el diseño experimental con el modelo matemático usando distintos 
parámetros de entrada.

Entre las funciones, se incluirá:
    
    1) Creación de una instancia desde un archivo de excel (OK)
    2) Resumen de resultados (OK)
    3) Función de evaluación dados los resultados de una instancia (PENDIENTE)
    

    

"""



import pandas as pd
import numpy as np


def instance_from_file(file_name):
    datos_archivo = pd.read_excel(file_name) 
    df=pd.DataFrame(datos_archivo)

    Z = set([int(i) for i in list(df["Zonas"].dropna())])
    A = set([int(i) for i in list(df["Acopios"].dropna())])
    T = set([int(i) for i in list(df["Transformadores"].dropna())])
    M = set([int(i) for i in list(df["Capacidades"].dropna())])

    output= {None: dict(
    Zonas = Z,
    Acopios = A,
    Transformadores = T,
    Capacidades = M,
    QMPM = dict(zip((Z), list(df["QMPM"].dropna()))),
    te = dict(zip((Z), list(df["te"].dropna()))),
    tr = dict(zip((Z), list(df["tr"].dropna()))),
    QMR = dict(zip((Z), list(df["QMR"].dropna()))),
    CAP = dict(zip((M), list(df["CAP"].dropna()))),
    MA = {None:df["MA"][0]},
    ct = dict(zip([(int(i),int(j)) for i in A for j in T], list(df["ct"].dropna()))),
    TA = dict(zip((A), list(df["TA"].dropna()))),
    TT = dict(zip((T), list(df["TT"].dropna()))),
    vd = {None:df["vd"][0]},
    vma = {None:df["vma"][0]},
    O = {None:df["O"][0]},
    P = {None:df["P"][0]},
    alfa = {None:df["alfa"][0]},
    rc1 = dict(zip((A), list(df["rc1"].dropna()))),
    rc2 = dict(zip((T), list(df["rc2"].dropna()))),
    ec = {None:df["ec"][0]},
    at = dict(zip((M), list(df["at"].dropna()))),
    ft = {None:df["ft"][0]}
    )}

    return output
    
def eval_instance(data, instance, solution_from = 1):
    # En esta función la idea es tener cada parámero de una instancia como variable 
    # privada para reaizar el cálculo de la función objetivo y de otras variables 
    # por fuera de pyomo. 
    # Para esto, emplearemos, ya sea la solución óptima entregada por el algoritmo
    # o una solución dada por usuario.

    #Si la solución viene de Pyomo, solution_from = 1 && solution == instance
    #Si la solución viene de un archivo de excel, entonces solution_from = 2 &
    # solution = archivo de excel
    
    if solution_from == 1:
        #Variables from model
        x = instance.x.get_values()
        y = instance.y.get_values()
        z = instance.z.get_values()
        w = instance.w.get_values()
    else:
        #Variables from excel
        x = instance["x"]
        y = instance["y"]
        z = instance["z"]
        w = instance["w"]      
        
        
        
    #Parámetros
    _Z = data[None]["Zonas"]
    _A = data[None]["Acopios"]
    _T = data[None]["Transformadores"]
    _M = data[None]["Capacidades"]
    _QMPM = data[None]["QMPM"]
    _te = data[None]["te"]
    _tr = data[None]["tr"]
    _QMR = data[None]["QMR"]
    _CAP = data[None]["CAP"]    
    _MA = data[None]["MA"][None]    
    _ct1 = data[None]["ct1"]
    _ct2 = data[None]["ct2"]
    _ct3 = data[None]["ct3"]
    _TA = data[None]["TA"]
    _TT = data[None]["TT"]
    _vd = data[None]["vd"][None]
    _vma = data[None]["vma"][None]
    _O = data[None]["O"][None]
    _P = data[None]["P"][None]
    _alfa = data[None]["alfa"][None]
    _rc1 = data[None]["rc1"]
    _rc2 = data[None]["rc2"]
    _ec = data[None]["ec"][None]
    _at = data[None]["at"]
    
    
    
    #Variables a calcular
    
    #fj y gk
    _f={}
    _g={}
    
    for j in _A:
        _aux = sum([_at[m]*y[j,m] for m in _M])
        _f[j] = _rc1[j]*_aux
    
    for k in _T:
        _aux = sum([_at[m]*z[k,m] for m in _M])
        _g[k] = _ec + _rc2[k]*_aux
    
    #CA
    
    _aux1 = sum([_f[j]* _TA[j]* sum([y[j,m] for m in _M]) for j in _A])
    _aux2 = sum([_g[k]* _TT[k]* sum([z[k,m] for m in _M]) for k in _T])
    
    _CA = _aux1 + _aux2
    
    
    
    
    #_CT
    _CT1 = 0
    _CT2 = 0
    _CT3 = 0
    for i in _Z:
        aux1 = 0
        aux2 = 0
        aux3 = 0
        for j in _A:     
            for k in _T:
               aux1 = x[i,j,k] * _ct1[i,j] + aux1
               aux2 = x[i,j,k] * _ct2[j,k] + aux2
        for k in _T:
            aux3 = w[i,k] * _ct3[i,k] + aux3
        _CT1 = _QMR[i]*aux1 + _CT1
        _CT2 = _QMR[i]*(1 - _tr[i]) * aux2 + _CT2
        _CT3 = _QMR[i]*aux3 + _CT3
    
    _CT = _CT1 + _CT2 + _CT3
    
    
    
    #_ES
    _ES1 = 0
    _ES2 = 0
    for i in _Z:
        aux1 = 0
        aux2 = 0
        for k in _T:
            aux1 = w[i,k] * _TT[k] + aux1
            aux2 = w[i,k] * (1 - _TT[k]) + aux2
        for j in _A:
            for k in _T:
                aux1 = x[i,j,k] * _TA[j] + aux1
                aux2 = x[i,j,k] * (1 - _TA[j]) + aux2
        _ES1 = _QMR[i]*aux1 + _ES1
        _ES2 = _QMR[i] * (1 - _tr[i]) * aux2 + _ES2
    _ES = _vd*_ES1 + _vma*_ES2 + _CT + _CA
    
    #_IS
    _IS1 = 0
    _IS2 = 0
    aux3 = sum([(_QMPM[i] - _QMR[i]) for i in _Z])
    for i in _Z:
        aux1 = 0
        aux2 = 0
        for k in _T:
            aux1 = w[i,k]*_TT[k] + aux1
            aux2 = w[i,k] + aux2
        for j in _A:
            for k in _T:
                aux1 = x[i,j,k]*_TA[j] + aux1
                aux2 = x[i,j,k] + aux2
        _IS1 = _QMR[i] * (1 - _tr[i]) * aux1 + _IS1
        _IS2 = _QMR[i] *(1 - aux2) + _IS2
    _IS = _vma*_IS1 + _vd*(aux3 + _IS2)
    
    #Z
    Z = _IS - _ES
    
    if solution_from == 1:
        # Comprobaciones
        assert(instance.CT.get_values()[None] == _CT)
        assert(instance.ES.get_values()[None] == _ES)
        assert(instance.IS.get_values()[None] - _IS < 0.001)
        assert(Z - instance.Z.expr() < 0.00001)
        
        print("Comprobación exitosa")
    else:
        print("Calculos realizados sin comprobación")
        
    return {"Costo de transporte":_CT, "Ingresos del sistema" : _IS, "Egresos del sistema": _ES, "Utilidad": Z}

def test_instance():
    data_init= {None: dict(
        Zonas = {1, 2, 3, 4},
        Acopios = {1, 2, 3},
        Transformadores = {1, 2, 3},
        Capacidades = {1,2,3},
        QMPM = {1:10, 2:15, 3:30, 4:25},
        te = {1:0.2, 2:0.1, 3:0.1, 4:0.1},
        tr = {1:0.1, 2:0.1, 3:0.1, 4:0.1},
        QMR = {1:2, 2:1.5, 3:3, 4:2.5},
        CAP = {1:4, 2:5, 3:6},
        MA = {None:8},
        ct1 = {
            (1,1):300,
            (1,2):325,
            (1,3):350,
            (2,1):300,
            (2,2):325,
            (2,3):350,
            (3,1):300,
            (3,2):325,
            (3,3):350,
            (4,1):300,
            (4,2):325,
            (4,3):350
        },
        ct2 = {            
            (1,1):300,
            (1,2):325,
            (1,3):350,
            (2,1):300,
            (2,2):325,
            (2,3):350,
            (3,1):300,
            (3,2):325,
            (3,3):350,
        },
        ct3 = {
            (1,1):300,
            (1,2):325,
            (1,3):350,
            (2,1):300,
            (2,2):325,
            (2,3):350,
            (3,1):300,
            (3,2):325,
            (3,3):350,
            (4,1):300,
            (4,2):325,
            (4,3):350
        },
        TA = {1:0, 2:1, 3:0},
        TT = {1:0, 2:1, 3:0},
        vd = {None:20000000},
        vma = {None:15000000},
        O = {None:3},
        P = {None:3}
        )}
    return data_init

def solution_summary(instance):
    sources = []
    targets = []
    weights = []
    
    # Obtener variables de decisión
    print("")
    res1 = instance.w.get_values()
    print("w(i,k)")
    for key, value in res1.items():
      if value > 0:
        print("Asignación", key, ":", value)
        sources.append(key[0])
        targets.append(key[1])
        weights.append(value)
    
    print("")
    
    res2 = instance.x.get_values()
    print("x(i,j,k)")
    for key, value in res2.items():
      if value > 0:
        print("Asignación", key, ":", value)
        sources.append(key[0])
        targets.append(key[1])
        weights.append(value)
    
        sources.append(key[0])
        targets.append(key[1])
        weights.append(value)
    
    print("")
    
    res3 = instance.y.get_values()
    print("y(j,m)")
    for key, value in res3.items():
      if value > 0:
        print("Centro acopio", key, ":", value)
    
    print("")
    
    res4 = instance.z.get_values()
    print("z(k,m)")
    for key, value in res4.items():
      if value > 0:
        print("Centro transformación", key, ":", value)
    
    print("")
    
    res5 = instance.IS.get_values()[None]
    print("Ingreso del sistema: ",res5)
    
    print("")
    
    res6 = instance.ES.get_values()[None]
    print("Egresos del sistema: ",res6)
    
    print("")
    
    # Obtener función objetivo
    obj_val = instance.Z.expr()
    print("Utilidad del sistema", ":", obj_val)
#df = instance_from_file("./data/i_0.xls")
#names = list(df.columns)


def solution_from_file(file_name):
    variables = ['x', 'y', 'z', 'w']
    
    for sheet in variables:
        df = pd.read_excel(file_name+".xlsx", sheet_name = sheet, engine='openpyxl')
        sol = {}
        for i in range(len(df)):
            sol[eval(df.iloc[i,0])] = df.iloc[i,1]
        globals()[sheet] = sol
        
    sol = {'x':x,'y':y, 'z':z, 'w':w }
        
    
    #La idea es que pueda leer desde el arhivo de excel las modificaciones
    
    return sol


def solution_to_file(instance, file_name):
    _x_ = instance.x.get_values()
    _y_ = instance.y.get_values()
    _z_ = instance.z.get_values()
    _w_ = instance.w.get_values()
    
    variables = ['x', 'y', 'z', 'w']
    column_names = {'x':['(i,j,k)', 'x'], 'y':['(j,m)', 'y'], 'z': ['(k,m)', 'z'], 'w':['(i,k)', 'w']}
    
    writer = pd.ExcelWriter("{}.xlsx".format(file_name))
    
    for v in variables:
        keys = [i for i in eval("_" + v + "_").keys()]
        values = [i for i in eval("_" + v + "_").values()]
        
        df = pd.DataFrame(list(zip(keys, values)), columns =column_names[v])
        
        df.to_excel(writer, sheet_name = v, index=False)
        
    writer.save()
    writer.close()