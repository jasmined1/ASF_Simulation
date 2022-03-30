"""
=========================================
main file for hourly simulation of the ASF
=========================================
"""


"""
@author: Mauro Luzzatto 
@credits: Prageeth Jayathissa, Jerimias Schmidli

02.11.2016
"""

"""
Edited by Jasmine de Riedmatten
25.03.2022
"""


"""
Description of the code 


HOW TO USE:
- Open the mainHourly.GH file in Grasshopper
- Set both red framed boolean toggles to true 
- Set all needed values for evaluation at the beginning of the mainSimulationHourly.py script

if LadyBug once has calculated all the radiation data, they will be stored in the folder with the corresponding DataName. 
Also the Data of the PV producation and radiation hitting the window will be saved and can be loaded again, with the same DataName.


Calculation without the ASF: 
    set XANGLES and YANGLES equal [0], set numberHorizontal and numberVertical to 0 in the PanelData settings


VARIABLE DEFINITION

    SimulationPeriod: 

    FromMonth = start month
    ToMonth = end month (for example to select only january, FromMonth = 1, Tomonth = 1)
    FromDay =  start day within a month
    ToDay = end day within a month (15. day of a month, FromDay = 15, ToDay = 15)
    FromHour': start hour of a day
    ToHour': end hour of a day (last hour is not included)

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
   human_heat_emissions = heat emitted by a human body per hour. Source: HVAC Engineers Handbook, F. 

"""


import os, sys

import numpy as np
import pandas as pd
from buildingSystem import *  
from SimulationClassHourly_Static import ASF_Simulation

sys.path.insert(0, os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), '5R1C_ISO_simulator'))    
    
from buildingPhysics import Building #Importing Building Class
from supplySystem import *  
from emissionSystem import *
    
SimulationPeriod = {
'FromMonth': 7, #7, #1,
'ToMonth': 7,#7, #1,
'FromDay': 6, #6, #8,
'ToDay': 6, #8,
'FromHour': 5,#5
'ToHour': 20}#20



#Set simulation data 
SimulationData= {
'optimizationTypes' : ['E_total', 'Cooling'], 
'DataFolderName' : 'ZH13test_static', 
'FileName' : 'ZH13test_static',
'geoLocation' : 'Zuerich_Kloten_2013', 
'EPWfile': 'Zuerich_Kloten_2013.epw',
'Save' : True, 
'ShowFig': True
}   


BlindData = {
    "PERCENT_HEIGHT" : [0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
    "TILT_ANGLE": [0, 45, 90],
    "slat_height" : 100,
    "slat_thickness" : 2,
    "BlindOffset": 150,
}

#Set Building Parameters in [mm]
BuildingData={
"room_width": 4900,     
"room_height":3100,
"room_depth":7000,
"glazing_percentage_w": 0.92,
"glazing_percentage_h": 0.97,
"WindowGridSize" : 200,
"BuildingOrientation" : 0,
"panelHeight":1200,
"panelGridSize" : 25} 

##@Michael: This will need to be modified to fit your model
BuildingProperties={
"glass_solar_transmittance" : 0.691 ,
"glass_light_transmittance" : 0.744 ,
"lighting_load" : 11.74 ,
"lighting_control" : 300,
"Lighting_Utilisation_Factor" :  0.45, # 0.75
"Lighting_Maintenance_Factor" : 0.9,
"U_em" : 0.2, 
"U_w" : 1.1,
"ACH_vent" : 1.5,
"ACH_infl" : 0.5,
"ventilation_efficiency" : 0.6,
"c_m_A_f" : 165 * 10**3,
"theta_int_h_set" : 22,
"theta_int_c_set" : 26,
"phi_c_max_A_f": -np.inf,
"phi_h_max_A_f":np.inf,
"heatingSupplySystem" : COP3Heater,
"coolingSupplySystem" : COP3Cooler,
"heatingEmissionSystem" : AirConditioning,
"coolingEmissionSystem" : AirConditioning,}
#
#Set simulation Properties
SimulationOptions= {
'setBackTempH' : 4.,
'setBackTempC' : 4.,
'Occupancy' : 'Occupancy_COM.csv',
'ActuationEnergy' : False,
'Temp_start' : 22,
'human_heat_emission' : 0.12} #[kWh] heat emitted by a human body per hour. Source: HVAC Engineers Handbook, F. Porges
   
if __name__=='__main__':
    
    ASFtest = ASF_Simulation(SimulationPeriod = SimulationPeriod, 
                             SimulationData = SimulationData, 
                             BlindData = BlindData,
                             BuildingData = BuildingData,
                             BuildingProperties = BuildingProperties, 
                             SimulationOptions = SimulationOptions)
    ASFtest.SolveASF()
    print ASFtest.TotalHourlyData
        
        
