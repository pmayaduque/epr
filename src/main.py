from pyomo.environ import *
from pyomo.opt import *
from model import create_model ##Modelo normal
#from model_deposit_no_income import create_model  ## Modelo cuando el dopósito no es un ingreso
from instances import test_instance, instance_from_file, solution_summary, eval_instance, solution_to_file, solution_from_file
from experiment_tools import *
from experimento_1 import doe0, doe1, doe2

# Crear el modelo
print ("Creating model...")

model = create_model("REP_EE_ORP")

print ("Model created successfully!!")

# Crear instancia del modelo abtsracto
print ("Creating instance...")
data = instance_from_file("./data/instancia_new.xls")

print(data)

opt = SolverFactory('gurobi')

### Correr instancia base

#df = doe0(data, model, opt)
#df.to_excel("./output_files_2.0/B.xlsx")


### Correr experimento completo

#La idea es probar con todas las combinaciones y pasarlo por R para encontrar la interacción entre las variables

df_1 = doe1(data, model, opt)
df_1.to_excel("./output_files_2.0/MG_PINF7.xlsx")

#df_1 = doe1(data, model, opt)
#df_1.to_excel("./output_files/R_DOE_model_alternativo.xlsx")


### Correr experimento de MA - Te_i

#df_1 = doe2(data, model, opt)
#df_1.to_excel("./output_files_2.0/DOE_model_evolution_modif.xlsx")






#Otra idea es incrementar el valor de la meta de forma gradual, manteniendo fijos los demás parámetros.

## Creación del campo "Capacidad instalada"
#def cap_inst(R):
#    R = eval(R)
#    return sum(R.values())
#
    
#df_1["Capacidad instalada"] = df_1["R"].apply(cap_inst)
#
#datos_archivo = pd.read_excel("./output_files_2.0/Validation.xlsx", engine='openpyxl')
#df=pd.DataFrame(datos_archivo)
#df = df.set_index('Instance')
#solution_summary_extended(df, "Base")
