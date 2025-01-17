# -*- coding: utf-8 -*-
"""
Created on Wed Nov 09 11:53:33 2016

@author: Mauro
"""
import unittest
import sys,os
import numpy as np
from buildingSystem import *  
from SimulationClassHourly import ASF_Simulation

#sys.path.insert(0, os.path.abspath(os.path.dirname(sys.argv[0])))        
#from mainSimulation import MainCalculateASF



class TestMainSimulation(unittest.TestCase):
	


    def test_WinterStandard(self):
        print 'Standard Test: Sunny Winter Day'
        SimulationPeriod = {
        'FromMonth': 1, #7, #1,
        'ToMonth': 1,#7, #1,
        'FromDay': 8, #6, #8,
        'ToDay': 8, #8,
        'FromHour': 5,#5
        'ToHour': 20}#20
        
        
        #Set simulation data 
        SimulationData= {
        'optimizationTypes' : ['E_total'], 
        'DataFolderName' : 'ZH13_49comb_WinterSunnyDay', 
        'FileName' : 'ZH13_49comb_WinterSunnyDay',
        'geoLocation' : 'Zuerich_Kloten_2013', 
        'EPWfile': 'Zuerich_Kloten_2013.epw',
        'Save' : False, 
        'ShowFig': False, 
        'timePeriod': None} # asf_electricity_function  
         
        PanelData = {
        "XANGLES": [0, 15, 30, 45, 60, 75, 90],
        "YANGLES" : [-45, -30,-15,0, 15, 30, 45],
        "NoClusters":1,
        "numberHorizontal":6,
        "numberVertical":9,
        "panelOffset":400,
        "panelSize":400,
        "panelSpacing":500, 
        "panelGridSize" : 25}
        
        #Set Building Parameters in [mm]
        BuildingData={
        "room_width": 4900,     
        "room_height":3100,
        "room_depth":7000,
        "glazing_percentage_w": 0.92,
        "glazing_percentage_h": 0.97,
        "WindowGridSize" : 200,
        "BuildingOrientation" : 0} #building orientation of 0 corresponds to south facing, 90 is east facing, -90 is west facing
        
        
        BuildingProperties={
        "glass_solar_transmitance" : 0.691 ,
        "glass_light_transmitance" : 0.744 ,
        "lighting_load" : 11.74 ,
        "lighting_control" : 300,
        "Lighting_Utilisation_Factor" :  0.45, # 0.75
        "Lighting_MaintenanceFactor" : 0.9,
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
        "heatingSystem" : DirectHeater, #DirectHeater, #DirectHeater, #ResistiveHeater #HeatPumpHeater
        "coolingSystem" : DirectCooler, #DirectCooler, #DirectCooler, #HeatPumpCooler
        "heatingEfficiency" : 1,
        "coolingEfficiency" :1,
        'COP_H': 3,
        'COP_C':3}
        #
        #Set simulation Properties
        SimulationOptions= {
        'setBackTempH' : 4.,
        'setBackTempC' : 4.,
        'Occupancy' : 'Occupancy_COM.csv',
        'ActuationEnergy' : False,
        'Temp_start' : 18,
        'human_heat_emission' : 0.12} #[kWh] heat emitted by a human body per hour. Source: HVAC Engineers Handbook, F. Porges
		
		
        ASFtest=ASF_Simulation( SimulationPeriod =  SimulationPeriod, SimulationData = SimulationData, PanelData = PanelData, BuildingData = BuildingData, BuildingProperties = BuildingProperties, SimulationOptions = SimulationOptions)
        ASFtest.SolveASF()
        		
        self.assertEqual(round(ASFtest.TotalHourlyData['E_total']['E'],2), 1.81)
        self.assertEqual(round(ASFtest.TotalHourlyData['E_total']['PV'],2), -2.93)
        self.assertEqual(ASFtest.ResultsBuildingSimulation['E_total']['BestCombKey'][180],9)
        
		
    def test_SummerStandard(self):
        print 'Standard Test: Sunny Summer Day'
        SimulationPeriod = {
        'FromMonth': 7,
        'ToMonth': 7,
        'FromDay': 6,
        'ToDay': 6, 
        'FromHour': 5,
        'ToHour': 20}
        
        
        #Set simulation data 
        SimulationData= {
        'optimizationTypes' : ['E_total'], 
        'DataFolderName' : 'ZH13_49comb_Notcloudy_6_7', 
        'FileName' : 'ZH13_49comb_Notcloudy_6_7',
        'geoLocation' : 'Zuerich_Kloten_2013', 
        'EPWfile': 'Zuerich_Kloten_2013.epw',
        'Save' : False, 
        'ShowFig': True, 
        'timePeriod': None} # asf_electricity_function  
    
         
        PanelData = {
        "XANGLES": [0, 15, 30, 45, 60, 75, 90],
        "YANGLES" : [-45, -30,-15,0, 15, 30, 45],
        "NoClusters":1,
        "numberHorizontal":6,
        "numberVertical":9,
        "panelOffset":400,
        "panelSize":400,
        "panelSpacing":500, 
        "panelGridSize" : 25}
        
        #Set Building Parameters in [mm]
        BuildingData={
        "room_width": 4900,     
        "room_height":3100,
        "room_depth":7000,
        "glazing_percentage_w": 0.92,
        "glazing_percentage_h": 0.97,
        "WindowGridSize" : 200,
        "BuildingOrientation" : 0} #building orientation of 0 corresponds to south facing, 90 is east facing, -90 is west facing
        
        
        BuildingProperties={
        "glass_solar_transmitance" : 0.691 ,
        "glass_light_transmitance" : 0.744 ,
        "lighting_load" : 11.74 ,
        "lighting_control" : 300,
        "Lighting_Utilisation_Factor" :  0.45, # 0.75
        "Lighting_MaintenanceFactor" : 0.9,
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
        "heatingSystem" : DirectHeater, #DirectHeater, #DirectHeater, #ResistiveHeater #HeatPumpHeater
        "coolingSystem" : DirectCooler, #DirectCooler, #DirectCooler, #HeatPumpCooler
        "heatingEfficiency" : 1,
        "coolingEfficiency" :1,
        'COP_H': 3,
        'COP_C':3}
        #
        #Set simulation Properties
        SimulationOptions= {
        'setBackTempH' : 4.,
        'setBackTempC' : 4.,
        'Occupancy' : 'Occupancy_COM.csv',
        'ActuationEnergy' : False,
        'Temp_start' : 22,
        'human_heat_emission' : 0.12} #[kWh] heat emitted by a human body per hour. Source: HVAC Engineers Handbook, F. Porges
		
		
        ASFtest=ASF_Simulation( SimulationPeriod =  SimulationPeriod, SimulationData = SimulationData, PanelData = PanelData, BuildingData = BuildingData, BuildingProperties = BuildingProperties, SimulationOptions = SimulationOptions)
        ASFtest.SolveASF()
        		
        self.assertEqual(round(ASFtest.TotalHourlyData['E_total']['E'],2), -1.89)
        self.assertEqual(round(ASFtest.TotalHourlyData['E_total']['PV'],2), -3.77)
        self.assertEqual(ASFtest.ResultsBuildingSimulation['E_total']['BestCombKey'][4475],25)		

  

if __name__ == '__main__':
	unittest.main()