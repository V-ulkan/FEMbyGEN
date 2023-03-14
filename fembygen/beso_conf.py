# This is the configuration file with input parameters. It will be executed as python commands
# Written by beso_fc_gui.py at 2023-03-14 15:20:27.564097

path_calculix = 'D:/Volkanwork/FreeCAD/bin/CL34-win64/bin/ccx/calculix_2.20_4win/ccx_static.exe'
path = 'D:/Volkan/deneme/Gen4/loadCase1'
file_name = 'FEMMeshNetgen.inp'

elset_name = 'MaterialSolidSolid'
domain_optimized[elset_name] = True
domain_density[elset_name] = [7.9e-15, 7.9e-09]
domain_material[elset_name] = ['*ELASTIC\n0.21, 0.3\n*DENSITY\n7.9e-15\n*CONDUCTIVITY\n4.3e-05\n*EXPANSION\n1.2e-11\n*SPECIFIC HEAT\n590.0\n',
                               '*ELASTIC\n2.1e+05, 0.3\n*DENSITY\n7.9e-09\n*CONDUCTIVITY\n43.0\n*EXPANSION\n1.2e-05\n*SPECIFIC HEAT\n5.9e+08\n']

mass_goal_ratio = 0.4
filter_list = [['simple', "auto"],
               ]

optimization_base = 'stiffness'

mass_addition_ratio = 0.015
mass_removal_ratio = 0.03
ratio_type = 'relative'

