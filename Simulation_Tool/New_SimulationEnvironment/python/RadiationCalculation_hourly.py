# -*- coding: utf-8 -*-
"""
Created on Wed Nov 02 08:30:45 2016

@author: Mauro
"""
import sys, os
import time
import json
import csv
import numpy as np

def CalculateRadiationData(SimulationPeriode, XANGLES, YANGLES, paths, DataNamePV, DataNameWin):

                   
    if not os.path.isfile(os.path.join(paths['PV'], 'HourlyPV_electricity_results_' + DataNamePV + '.npy')) or not os.path.isfile(os.path.join(paths['PV'], 'HourlyBuildingRadiationData_' + DataNameWin + '.npy')):    
        if not os.path.isdir(paths['PV']):
            os.makedirs(paths['PV'])
    
        # create dicitionary to save optimal angles:
        BuilRadData = {}
        
        resultsdetected=0
        
        print '\nStart radiation calculation with ladybug'
        print 'Time: ' + time.strftime("%Y_%m_%d %H.%M.%S", time.localtime())
    
        tic = time.time()
        
    
    
        for monthi in range(SimulationPeriode['FromMonth'], SimulationPeriode['ToMonth']+1): #month:
            
            BuilRadData[monthi]= {}
            
            for day in range(SimulationPeriode['FromDay'], SimulationPeriode['ToDay'] + 1):      
    
                BuilRadData[monthi][day] = {}
                
                for hour in range(SimulationPeriode['FromHour'], SimulationPeriode['ToHour'] + 1):
                    
                    BuildingRadiationData = np.array([])
                    
                    for x_angle in XANGLES:
                        for y_angle in YANGLES:
                            
                            comb_data={"x_angle":x_angle,
                                       "y_angle":y_angle,
                                       "Hour":hour,
                                       "Day": day,
                                       "Month":monthi
                                       }
                                       
                            #create json file with the set combination of x-angle,y-angle and HOY
                            with open('comb.json','w') as f:
                                f.write(json.dumps(comb_data))
                                
                                print hour, day, monthi, x_angle, y_angle, resultsdetected
                                toc = time.time() - tic
                                print 'time passed (min): ' + str(toc/60.)
                            
            #                #write ASFangles for Clusters
            #                with open('outputASFangles.json','w') as f:
            #                    f.write(json.dumps(ASFangles[index]))
            #                    print "index:", index
            #                      
                            #Wait until the radiation_results were created    
                            while not os.path.exists(os.path.join(paths['radiation_results'],'RadiationResults' +'_' +  str(hour) + '_' + str(day) + '_' + str(monthi)  + '_' + str(x_angle) + '_' + str(y_angle)+ '.csv')):
                                time.sleep(1)
                            
                            #paths['radiation_results']+'\\RadiationResults' +'_Index_'+ str(index) + '_NoCluster_' + str(NoClusters) + '_'  + str(HOD) + '_' + str(monthi)  + '_' + str(x_angle) + '_' + str(y_angle)+ '.csv'                
                            
                            else:
                                print 'next step'
                                resultsdetected += 1
                                                                                                
                                #read total radition on wall and save it in BuildingRadiationData              
                                while not os.path.exists(os.path.join(paths['radiation_wall'], 'RadiationWall' + '_' + str(hour) + '_' + str(day) + '_'+ str(monthi) + '_' + str(x_angle) + '_' + str(y_angle) + '.csv')):
                                    time.sleep(1)
                                else:
                                    with open(os.path.join(paths['radiation_wall'], 'RadiationWall' + '_' + str(hour) + '_' + str(day) + '_' + str(monthi) + '_' + str(x_angle) + '_' + str(y_angle) + '.csv'), 'r') as csvfile:
                                        reader = csv.reader(csvfile)
                                        for idx,line in enumerate(reader):
                                            if idx == 1:
                                                BuildingRadiationData = np.append(BuildingRadiationData, [float(line[0])])
                                                break
                                    
                                                       
                    
                   
                        #Radiation data is calculated for all days per month, so the data is divided through the amount of days per month
                        BuilRadData[monthi][day][hour]= BuildingRadiationData *1000. #W/h
                        
    
        np.save(os.path.join(paths['save_results_path'],'HourlyBuildingRadiationData_' + DataNameWin + '.npy'), BuilRadData)
        print "\nEnd of radiation calculation: " + time.strftime("%Y_%m_%d %H.%M.%S", time.localtime())

    else:
        BuilRadData = np.load(os.path.join(paths['PV'], 'HourlyBuildingRadiationData_' + DataNameWin + '.npy')).item()
        print '\nLadyBug data loaded from Folder:'
        print 'radiation_wall_'+ DataNameWin   
    
    return BuilRadData