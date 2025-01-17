# -*- coding: utf-8 -*-
"""
Created on Wed Feb 17 11:26:40 2016

Calculate hour of the year based on date input

@author: Jeremias
"""

import numpy as np


month = 1
day = 2
hour = 24  #hour of the day (i.e between 0:00 and 1:00 corresponds to value 1)

def calcHOY(month, day, hour):
    
    daysPerMonth=np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
    if daysPerMonth[month-1]<day:
        raise ValueError("month " + str(month) + " has less than " + str(day) +" days")
    HOY = 0
    for i in range(month-1):
        HOY += daysPerMonth[i]*24
    HOY +=(day-1)*24+hour
    return HOY
    
#HOY = calcHOY(month, day, hour)

#print HOY
#    