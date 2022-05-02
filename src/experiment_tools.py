# -*- coding: utf-8 -*-
"""
Created on Sun Jun  6 16:56:51 2021

@author: Jesus Galarcio
"""

import pandas as pd


def create_dataframe_base():
    #Esta función crea la base de datos que se usará para almacenar los 
    #parámetros y los resultados de los experimentos
    col_names = ['Instance','Zonas','Acopios','Transformadores','Capacidades',
                 'QMPM','te','tr','QMR','CAP','MA','ct',
                 'TA','TT','vd','vma','O','P','rc1','rc2','alfa','ec',
                 'at','ft','y','z','x','w','R','Rmin','Rmax','f','g','CT','CA',
                 'ES','IS','Z', "1.1.1 Ingresos x depositos no redimidos - COP",
                "1.1.2 Ingresos x depositos no redimidos - Ton",
                "1.2.1 Ingresos x venta de material en el mercado - COP",
                "1.2.2 Ingresos x venta de material en el mercado - Ton",
                "2.1.1 Costo de transporte entre Acopios de la ORP y cualquier transformador",
                "2.1.2 Costo de transporte entre Acopios de entes externos y Transformadores de la ORP",
                "2.2.1 Costo de apertura de Acopios",
                "2.2.2 Costo de apertura de Transformadores",
                "2.3.1 Pago x depositos (COP)",
                "2.3.2 Pago x depositos (Ton)",
                "2.4 Costo de adquisición de material transformado por EE",
                "2.5 Costo de usar instalaciones de EE para transformar material",
                "2.6 Costo de adquisición de material sin transformar clasificado por EE",
                "Capacidad instalada"]
    df = pd.DataFrame(columns = col_names)
    return df


def new_row(df, data, Instance):
    #Con esta función, se crea un registro en el dataframe. Si la instancia 
    #no tiene solución, se registrarán los parámetros y las variables irán 
    #con un NA
    
    dict_row = {'Instance' : Instance,
            'Zonas' : str(data[None]["Zonas"]),
            'Acopios' : str(data[None]["Acopios"]),
            'Transformadores' : str(data[None]["Transformadores"]),
            'Capacidades' : str(data[None]["Capacidades"]),
            'QMPM' : str(data[None]["QMPM"]),
            'te' : str(data[None]["te"]),
            'tr' : str(data[None]["tr"]),
            'QMR' : str(data[None]["QMR"]),
            'CAP' : str(data[None]["CAP"]),
            'MA' : data[None]["MA"][None],
            'ct' : str(data[None]["ct"]),
            'TA' : str(data[None]["TA"]),
            'TT' : str(data[None]["TT"]),
            'vd' : data[None]["vd"][None],
            'vma' : data[None]["vma"][None],
            'O' : data[None]["O"][None],
            'P' : data[None]["P"][None],
            'rc1' : str(data[None]["rc1"]),
            'rc2' : str(data[None]["rc2"]),
            'alfa' : data[None]["alfa"][None],
            'ec' : data[None]["ec"][None],
            'at' : str(data[None]["at"]),
            'ft' : data[None]["ft"][None],
            'y' : "NA",
            'z' : "NA",
            'x' : "NA",
            'w' : "NA",
            'R' : "NA",
            'Rmin' : "NA",
            'Rmax' : "NA",
            'f' : "NA",
            'g' : "NA",
            'CT' : "NA",
            'CA' : "NA",
            'ES' : "NA",
            'IS' : "NA",
            'Z' : "NA",
            "1.1.1 Ingresos x depositos no redimidos - COP":"NA",
            "1.1.2 Ingresos x depositos no redimidos - Ton":"NA",
            "1.2.1 Ingresos x venta de material en el mercado - COP":"NA",
            "1.2.2 Ingresos x venta de material en el mercado - Ton":"NA",
            "2.1.1 Costo de transporte entre Acopios de la ORP y cualquier transformador":"NA",
            "2.1.2 Costo de transporte entre Acopios de entes externos y Transformadores de la ORP":"NA",
            "2.2.1 Costo de apertura de Acopios":"NA",
            "2.2.2 Costo de apertura de Transformadores":"NA",
            "2.3.1 Pago x depositos (COP)":"NA",
            "2.3.2 Pago x depositos (Ton)":"NA",
            "2.4 Costo de adquisición de material transformado por EE":"NA",
            "2.5 Costo de usar instalaciones de EE para transformar material":"NA",
            "2.6 Costo de adquisición de material sin transformar clasificado por EE":"NA",
            "Capacidad instalada":"NA"
            }
    
    df = df.append(dict_row, ignore_index = True)
    
    return df

def new_solution_to_row(df, data, Instance, instance):
    #df = df.set_index('Instance')
    
    _sol = {'y' : str(instance.y.get_values()),
     'z' : str(instance.z.get_values()),
     'x' : str(instance.x.get_values()),
     'w' : str(instance.w.get_values()),
     'R' : str(instance.R.get_values()),
     'Rmin' : instance.Rmin(),
     'Rmax' : instance.Rmax(),
     'f' : str(instance.f.get_values()),
     'g' : str(instance.g.get_values()),
     'CT' : instance.CT(),
     'CA' : instance.CA(),
     'ES' : instance.ES(),
     'IS' : instance.IS(),
     'Z' : instance.Z()}
        
    df.loc[[Instance],['y','z','x','w','R','Rmin','Rmax','f','g','CT','CA','ES','IS','Z']] = list(_sol.values())
    
    _aditional_calcs = solution_summary_extended(df = df, instance_name = Instance)

    df.loc[[Instance],list(_aditional_calcs.keys())] = list(_aditional_calcs.values())
    
    return df


# dat1.to_excel('myDataFrame.xlsx')
       
def solution_summary_extended(df, instance_name):
    
    #Variables adicionales para el cálculo
    _QMR = eval(df.loc[instance_name]["QMR"])
    _tr = eval(df.loc[instance_name]["tr"])
    _zonas =eval(df.loc[instance_name]["Zonas"])
    _R = eval(df.loc[instance_name]["R"])
    _y = eval(df.loc[instance_name]["y"])
    _cap = eval(df.loc[instance_name]["CAP"])
    _cap_set = eval(df.loc[instance_name]["Capacidades"])
    _acopios = eval(df.loc[instance_name]["Acopios"])    
    _z = eval(df.loc[instance_name]["z"])
    _transf = eval(df.loc[instance_name]["Transformadores"])
    _w = eval(df.loc[instance_name]["w"])
    _x = eval(df.loc[instance_name]["x"])
    _f = eval(df.loc[instance_name]["f"])
    _g = eval(df.loc[instance_name]["g"])
    _TA = eval(df.loc[instance_name]["TA"])
    _TT = eval(df.loc[instance_name]["TT"])
    _ct = eval(df.loc[instance_name]["ct"])
    _vd = df.loc[instance_name]["vd"]
    _vma = df.loc[instance_name]["vma"]
    _QMPM = eval(df.loc[instance_name]["QMPM"])
    _ft = df.loc[instance_name]["ft"]
    
    # Obtener variables de decisión
    res5 = df.loc[instance_name]["IS"]
    res511 = sum([(_QMPM[i] - _QMR[i]) for i in _zonas])
    res512 = sum([_QMR[i] * (1 - (sum([_w[i,k] for k in _transf]) + sum([_x[i,j,k] 
    for k in _transf for j in _acopios]))) for i in _zonas])
    res51 = _vd*(res511+res512)
    res52 = _vma*(1+_ft)*sum([_QMR[i] * (1 - _tr[i]) * sum([sum([_w[i,k] for k in _transf]) + 
                      sum([_x[i,j,k] for k in _transf for j in _acopios])
            ]) for i in _zonas
            ])    
        
    #Hasta aqui vamos good xDDDD
    res6 = df.loc[instance_name]["ES"]  

    res61 = df.loc[instance_name]["CT"]

    res611 = sum([sum([_x[i,j,k]*_ct[j,k] for k in _transf for j in _acopios if _TA[j] == 1]) * _QMR[i] * (1 - _tr[i]) for i in _zonas])
    res612 = sum([sum([_x[i,j,k]*_ct[j,k] for k in _transf if _TT[k] == 1 for j in _acopios if _TA[j] == 0]) * _QMR[i] * (1 - _tr[i]) for i in _zonas])
    
    
    #El costo de apertura está funcionando bien.
    res62 = df.loc[instance_name]["CA"]
    res621 = sum([sum([_y[j,m] for m in _cap_set])*_f[j]*_TA[j] for j in _acopios]) 
    res622 = sum([sum([_z[k,m] for m in _cap_set])*_g[k]*_TT[k] for k in _transf])
    
    
    res63 = _vd*sum([(sum([_w[i,k]*_TT[k] for k in _transf]) + sum([_x[i,j,k]*_TA[j] 
    for k in _transf for j in _acopios])) * _QMR[i] for i in _zonas])
        
        
    
    res64 = _vma*(1 + _ft) * sum([_QMR[i] * (1 - _tr[i]) * sum([sum([_w[i,k] for k in _transf if _TT[k] == 0]) + 
                      sum([_x[i,j,k] for k in _transf if _TT[k] == 0 for j in _acopios if _TA[j] == 0])
            ]) for i in _zonas])
    
    res65 = _vma* _ft * sum([_QMR[i] * (1 - _tr[i]) * sum([ 
                      sum([_x[i,j,k] for k in _transf if _TT[k] == 0 for j in _acopios if _TA[j] == 1])
            ]) for i in _zonas])
    
    res66 = _vma*  sum([_QMR[i] * (1 - _tr[i]) * sum([ 
                      sum([_x[i,j,k] for k in _transf if _TT[k] == 1 for j in _acopios if _TA[j] == 0])
            ]) for i in _zonas])
        
    # Obtener función objetivo
    obj_val = df.loc[instance_name]["Z"]
    res7 = [_QMR[i] for i in _zonas]
    res8 = [_QMR[i]*(1 - _tr[i]) for i in _zonas]
    res9 = _R.values()
    res10 = [sum([_cap[m]*_y[j,m] for m in _cap_set]) for j in _acopios]
    res11 = [sum([_cap[m]*_z[k,m] for m in _cap_set]) for k in _transf]
    
    Cap_inst = sum([_z[k,m]*_cap[m] for m in _cap_set 
    for k in _transf]) + sum([_y[j,m]*_cap[m] for m 
             in _cap_set for j in _acopios])
        
    print("")
    res1 = _w
    print("w(i,k)")
    for key, value in res1.items():
      if value > 0:
        print("Asignación", key, ":", value)

    print("")
    
    res2 = _x
    print("x(i,j,k)")
    for key, value in res2.items():
      if value > 0:
        print("Asignación", key, ":", value)
    
    print("")
    
    res3 = _y
    print("y(j,m)")
    for key, value in res3.items():
      if value > 0:
        print("Centro acopio", key, ":", value)
    
    print("")
    
    res4 = _z
    print("z(k,m)")
    for key, value in res4.items():
      if value > 0:
        print("Centro transformación", key, ":", value)
    
    print("")

    return {"1.1.1 Ingresos x depositos no redimidos - COP":res51,
            "1.1.2 Ingresos x depositos no redimidos - Ton":res51/_vd,
            "1.2.1 Ingresos x venta de material en el mercado - COP":res52,
            "1.2.2 Ingresos x venta de material en el mercado - Ton":res52/(_vma*(1 + _ft)),
            "2.1.1 Costo de transporte entre Acopios de la ORP y cualquier transformador":res611,
            "2.1.2 Costo de transporte entre Acopios de entes externos y Transformadores de la ORP":res612,
            "2.2.1 Costo de apertura de Acopios":res621,
            "2.2.2 Costo de apertura de Transformadores":res622,
            "2.3.1 Pago x depositos (COP)":res63,
            "2.3.2 Pago x depositos (Ton)":res63/_vd,
            "2.4 Costo de adquisición de material transformado por EE":res64,
            "2.5 Costo de usar instalaciones de EE para transformar material":res65,
            "2.6 Costo de adquisición de material sin transformar clasificado por EE":res66,
            "Capacidad instalada":Cap_inst
            }
    
    