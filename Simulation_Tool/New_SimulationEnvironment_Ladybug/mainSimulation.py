"""
=========================================
main file for the annual ASF simulation
=========================================
"""


"""
@author: Mauro Luzzatto 
@credits: Prageeth Jayathissa, Jerimias Schmidli

02.11.2016
"""


"""
Description of the code 


HOW TO USE:
- Open the mainNew.GH file in Grasshopper
- Set both red framed boolean toggles to true 
- Set all needed values for evaluation at the beginning of the main.py script
- start simulation, for a new loaction an error with ..SunPosition.csv not found, just wait 1 min for GH to create it, then start simulation again
- after all radiation files are calculated (radiaion_results and radtion_wall) - the number should be equal comb*hour_in_month - close GH to avoid interaction with it 

When LadyBug once has calculated all the radiation data (ASF and Window), they will be stored in the folder with the corresponding 'DataFolderName'. 
The PV porduction is saved with the corresponding 'filename', this makes it possible to use the same radiaiton data for different combination analysis.

Calculation without the ASF: 

- set XANGLES and YANGLES equal [0], set numberHorizontal and numberVertical to 0 in the PanelData settings


VARIABLE DEFINITION

    SimulationData:
   
   optimization_Types = Decide for which energy demand type, you want to do the optimisation for, multiple options are possible.  ['E_total', 'Cooling', 'Heating', 'SolarEnergy', 'Lighting', 'E_HCL'] 
                       If all otpimization types are chosen, the azimuth and altitude angle plots are created as well. 
   
   DataFolderName = choose the name of the stored data, those only effects the radiaiton results generated by ladybug
   FileName = used for the PV results, enables to use same radiaiton data but with different configuration
   
   geoLocation = set the location which should be evaluated, make sure the correspoding .epw file is saved in the WeatherData folder
   EPWfile = use same file name as used in geolocation, but this is used for the ladybug calculation, same name and ending ".epw" is needed
   
   ShowFig = decide if you want to create (True) or not create (False) the figures
   Save =  decide if you want to save (True) or not save (False) the results
   
   PanelData:
   
   XANGLES = set the X-Angles of the ASF = [0, 15, 30, 45, 60, 75, 90] , 0 = closed, 90 = open
   YANGLES = set the Y-Angles of the ASF = [-45, -30,-15,0, 15, 30, 45] 
   NoClusters = option for using different multiple clusters
   numberHorizontal = number of panels in horizontal direction (columns)
   numberVertical = number of panels in vertical direction (rows)
   panelOffset = 
   panelSize = size of PV panel [mm]
   panelSpacing = diagonal distance betwee panels [mm]
   panelGridSize = grid size on panel surface used for the solar radiaiton analysis with ladybug [mm]
   
   
   BuildingData:
   
   room_width, room_height, room_depth = room dimensons in mm
   glazing_percentage_w = perecentage of glazing of the total room width [%]
   glazing_percentage_h =  perecentage of glazing of the total room height [%]
   BuildingOrientation = building orientation of 0 corresponds to south facing, 90 is east facing, -90 is west facing
   WindowGridSize = select grid Size for the solar irradiation on the window surface calculated with ladybug [mm]
	
   
   BuildingProperties:
   
   glass_solar_transmitance: Fraction of Radiation transmitting through the window []
   glass_light_transmitance: Fraction of visible light (luminance) transmitting through the window []
   lighting_load: Lighting Load [W/m2] 
   lighting_control: Lux threshold at which the lights turn on [Lx]
   U_em: U value of opaque surfaces  [W/m2K]
   U_w: U value of glazed surfaces [W/m2K]
   ACH_vent: Air changes per hour through ventilation [Air Changes Per Hour]
   ACH_infl: Air changes per hour through infiltration [Air Changes Per Hour]
   ventilation_efficiency: The efficiency of the heat recovery system for ventilation. Set to 0 if there is no heat recovery []
   c_m_A_f: Thermal capacitance of the room per floor area [J/m2K] #capcitance of the building dependent on building type: medium = 165'000, heavy = 260'000, light = 110'000, very heavy = 370'000
   theta_int_h_set : Thermal heating set point [C]
   theta_int_c_set: Thermal cooling set point [C]
   phi_c_max_A_f: Maximum cooling load. Set to -np.inf for unresctricted cooling [C]
   phi_h_max_A_f: Maximum heating load. Set to no.inf for unrestricted heating [C]
   COP_H = heating cop
   COP_C = cooling cop

   
   SimulationOptions
   
   setBackTempH' = chose a setBackTemperature, it determines to what extend the building can heat up, when no people are in the building [C]
   setBackTempC' = chose a setBackTemperature, it determines to what extend the building can cool down, when no people are in the building [C]
   Occupancy'  = select occupancy profile file, 'Occupancy_COM.csv'
   ActuationEnergy = choose whether you want to include the the needed actuation energy for the ASF adjustment
   Temp_start = simulation starting Temperature [C] 
   human_heat_emissions = heat emitted by a human body per hour. Source: HVAC Engineers Handbook, F. Porges # 0.12 [kWh]


"""



import numpy as np
import sys,os
from SimulationClass import ASF_Simulation


sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), '5R1C_ISO_simulator'))    
from buildingPhysics import Building #Importing Building Class
from supplySystem import *
from emissionSystem import *


#SimulationData = {
#'optimizationTypes' : ['E_total', 'Cooling', 'Heating', 'SolarEnergy', 'Lighting', 'E_HCL'],
#'DataFolderName' : 'ZH13_49comb', #'ZH13_49comb',
#'FileName': 'ZH13_49comb',
#'geoLocation' : 'Zuerich_Kloten_2013',
#'EPWfile': 'Zuerich_Kloten_2013.epw',
#'Save' : True,
#'ShowFig': True}


SimulationData = {
'optimizationTypes' : ['E_total'], #, 'Cooling', 'Heating', 'SolarEnergy', 'Lighting', 'E_HCL'
'DataFolderName' : 'ZH_49comb_HiLo', #'ZH13_49comb',
'FileName': 'ZH_49comb_HiLo',
'geoLocation' : 'Zuerich_Kloten_2013',
'EPWfile': 'Zuerich_Kloten_2013.epw',
'Save' : True,
'ShowFig': True,
'timePeriod': None,
'total_pv_combinations': 49}



PanelData = {
"XANGLES": [0, 15, 30, 45, 60, 75, 90],
"YANGLES" : [-45, -30,-15,0, 15, 30, 45],
"NoClusters":1,
"numberHorizontal":5,
"numberVertical":6,
"panelOffset":400,
"panelSize":425,
"panelSpacing":510, 
"panelGridSize" : 25}

# PanelData = {
# "XANGLES": [45],
# "YANGLES" : [0],
# "NoClusters":1,
# "numberHorizontal":5,
# "numberVertical":6,
# "panelOffset":400,
# "panelSize":425,
# "panelSpacing":510, 
# "panelGridSize" : 25}
            
BuildingData = {
"room_width": 3000, 
"room_height":2100, 
"room_depth":4000, 
"glazing_percentage_w": 0.92,
"glazing_percentage_h": 0.97, 
"WindowGridSize": 200, 
"BuildingOrientation" : 0}
            
# SimulationData = {
#     'optimizationTypes' : ['E_total'], #, 'Cooling', 'Heating', 'SolarEnergy', 'Lighting', 'E_HCL'
#     'DataFolderName' : 'ZH13_49comb_static_45_0', #'ZH13_49comb_static_45_0',
#     'FileName': 'ZH13_49comb_static_45_0',
#     'geoLocation' : 'Zuerich_Kloten_2013',
#     'EPWfile': 'Zuerich_Kloten_2013.epw',
#     'Save' : False,
#     'ShowFig': False}






##Set building properties for RC-Model simulator
##>@Michael: This will need to be modified to match your code
BuildingProperties={
"glass_solar_transmittance" : 0.6 ,
"glass_light_transmittance" : 0.6 ,#0.68
"lighting_load" : 2.79 ,
"lighting_control" : 300,
"Lighting_Utilisation_Factor" : 0.6,# 0.75,
"Lighting_Maintenance_Factor" : 0.9,
"U_em" : 0.17, 
"U_w" : 0.75,
"ACH_vent" : 1.5,
"ACH_infl" : 0.5,
"ventilation_efficiency" : 0.6 ,#0.6
"c_m_A_f" : 165 * 10**3,
"theta_int_h_set" : 21.0,
"theta_int_c_set" : 26.0,
"phi_c_max_A_f": -np.inf,
"phi_h_max_A_f":np.inf,
"heatingSupplySystem" : COP42Heater,
"coolingSupplySystem" : COP81Cooler,
"heatingEmissionSystem" : FloorHeating,
"coolingEmissionSystem" : FloorHeating,
}

#
#Set simulation Properties
SimulationOptions= {
'setBackTempH' : 4.0,
'setBackTempC' : 4.0,
'Occupancy' : 'schedules_occ_SINGLE_RES.csv',
'ActuationEnergy' : True,
'human_heat_emission' : 0.12,
'Temp_start' : 20.0} 

	
if __name__=='__main__':
    
    ASF = ASF_Simulation(SimulationData = SimulationData, BuildingProperties = BuildingProperties, SimulationOptions = SimulationOptions, PanelData=PanelData)
    ASF.SolveASF()
    yearlyData = ASF.yearlyData
    Results = ASF.ResultsBuildingSimulation

    print ASF.yearlyData

    
   
