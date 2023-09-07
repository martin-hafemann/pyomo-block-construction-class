import pandas as pd

from pyomo.environ import *
from pyomo.opt import SolverFactory

import blocks.chp as chp

PATH_PRICES = 'data/prices/'
PATH_OUT = 'data/output/'

opt = SolverFactory('gurobi')

data = DataPortal()

data.load(
        filename=PATH_PRICES + '/gas_price.csv',
        index='t',
        param='gas_price'
)
data.load(
        filename=PATH_PRICES + '/power_price.csv',
        index='t',
        param='power_price'
)

# Get input parameters for the chp
chp1_data = pd.read_csv(
    'data/assets/chp1.csv',
    index_col=0
)
chp2_data = pd.read_csv(
    'data/assets/chp2.csv',
    index_col=0
)

# Create chp instances with different construction rules.
chp1_obj = chp.Chp(chp1_data, forced_operation_time=10)
chp2_obj = chp.Chp(chp2_data)

# Create abstract model
m = AbstractModel()

# Define sets
m.t = Set(ordered=True)

# Define parameter components
m.gas_price = Param(m.t)
m.power_price = Param(m.t)

# Define block components
m.chp1 = Block(rule=chp1_obj.chp_block_rule)
m.chp2 = Block(rule=chp2_obj.chp_block_rule)


def obj_expression(m):
    """ Objective Function """
    return (quicksum((m.chp1.gas[t] + m.chp2.gas[t]) * m.gas_price[t] for t in m.t) -
            quicksum((m.chp1.power[t] + m.chp2.power[t]) * m.power_price[t] for t in m.t))


m.obj = Objective(
    rule=obj_expression,
    sense=minimize
    )

# Create instanz
instance = m.create_instance(data)

# Solve the optimization problem
results = opt.solve(
    instance,
    symbolic_solver_labels=True,
    tee=True,
    logfile='data/output/solver.log',
    load_solutions=True)

# Write Results
results.write()

df_variables = pd.DataFrame()
df_parameters = pd.DataFrame()
df_output = pd.DataFrame()

for parameter in instance.component_objects(Param, active=True):
    name = parameter.name
    df_parameters[name] = [value(parameter[t]) for t in instance.t]

for variable in instance.component_objects(Var, active=True):
    name = variable.name
    df_variables[name] = [value(variable[t]) for t in instance.t]

df_output = pd.concat([df_parameters, df_variables], axis=1)
df_output.to_csv('data/output/output_time_series.csv')
