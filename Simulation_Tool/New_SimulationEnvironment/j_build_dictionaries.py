import pandas as pd
import re as re

from j_paths import \
    PATHS  # TODO: Convert to setup.py or something equivalent http://docs.python-guide.org/en/latest/writing/structure/
from buildingSystem import *

paths = PATHS()

# TODO: convert this into a dataset or function so it doesnt confuse the code
lighting_control_d = {  # arbitrary, since online sources only provide ranges
    "MULTI_RES": 250.,
    "SINGLE_RES": 200.,
    "HOTEL": 300.,
    "OFFICE": 350.,
    "RETAIL": 400.,
    "FOODSTORE": 400.,
    "RESTAURANT": 250.,
    "INDUSTRIAL": 300.,
    "SCHOOL": 350.,
    "HOSPITAL": 400.,
    "GYM": 300.
}

mean_occupancy_d = {  # calculated  from the occupancy files
    "MULTI_RES": 0.014355,
    "SINGLE_RES": 0.009570,
    "HOTEL": 0.034377,
    "OFFICE": 0.009951,
    "RETAIL": 0.033507,
    "FOODSTORE": 0.055845,
    "RESTAURANT": 0.072592,
    "INDUSTRIAL": 0.030994,
    "SCHOOL": 0.010913,
    "HOSPITAL": 0.073750,
    "GYM": 0.070977,
}


# TODO: Rename to BuildArchetypeDatafame
def ArchT_build_df(BuildingData={'room_width': 4900, 'room_height': 3100, 'room_depth': 7000,
                                 'glazing_percentage_w': 0.92, 'glazing_percentage_h': 0.97}):
    """
    Reads the CEA database excel sheet and extracts necessary information to conduct and archetype evaluation
    :param BuildingData: A dictionary containing the necessary room dimension
    :return: A dataframe with archetype data for ASF evaluation
    """
    # read thermal properties for RC model
    arch = pd.read_excel(paths['Archetypes_properties'], sheetname='THERMAL')
    r = re.compile("([a-zA-Z_]+)")  # generate regular expression of letters to strip numbers

    # Strip numbers off the building archetypes for matching later on
    arch["code1"] = pd.DataFrame([r.match(string).groups() for string in arch.Code])
    arch.set_index(['code1'], inplace=True)

    # Delete uneeded archetypes and
    arch.drop(['SERVERROOM', 'PARKING', 'SWIMMING', 'COOLROOM'], inplace=True)
    arch.reset_index(drop=False, inplace=True)
    arch.drop('Es', axis=1, inplace=True)  # Ratio of floor area that has electricity not needed
    arch.drop('Hs', axis=1, inplace=True)  # ratio of gross floor area heated or cooled not needed
    arch.drop('U_roof', axis=1, inplace=True)  # roof u value not needed, assume only facade loss
    arch.drop('U_base', axis=1, inplace=True)  # heat transfer through basement not needed

    # read internal loads for RC model from CEA excel sheet and keep necessary loads
    int_loads = pd.read_excel(paths['Archetypes_properties'], sheetname='INTERNAL_LOADS')
    int_loads = int_loads[['Code', 'Qs_Wp', 'Ea_Wm2', 'El_Wm2']]

    # read thermal set points and ventilation rates
    thermal_setpoint_ventelation = pd.read_excel(paths['Archetypes_properties'], sheetname='INDOOR_COMFORT')

    # Combine everything into a single dataframe
    b_props = arch.merge(int_loads, how='left', left_on='code1', right_on='Code')
    b_props = b_props.merge(thermal_setpoint_ventelation, how='left', left_on='code1', right_on='Code')
    b_props = b_props.drop(['Code_y', 'Code'], axis=1)

    # Create set back temperature definition to match with the ASF_Simulation
    b_props['setBackTempC'] = b_props['Tcs_setb_C'] - b_props['Tcs_set_C']
    b_props['setBackTempH'] = b_props['Ths_set_C'] - b_props['Ths_setb_C']

    volume = (BuildingData['room_width'] / 1000) * (BuildingData['room_depth'] / 1000) * (
        BuildingData['room_height'] / 1000)
    area = (BuildingData['room_width'] / 1000) * (BuildingData['room_depth'] / 1000)

    b_props['ACH_vent_p'] = b_props['Ve_lps'] * 3.6 / volume

    # Assign values for Cm from ISO13790:2008, Table 12, based on archetypes
    c_m = []
    for i in range(0, len(b_props['th_mass'])):
        # c_m.append(165.0*10**3) just testing default value
        if b_props['th_mass'][i] == "T1":
            c_m.append(110.0 * 10 ** 3)  # Light
        elif b_props['th_mass'][i] == "T2":
            c_m.append(165.0 * 10 ** 3)  # Medium
        elif b_props['th_mass'][i] == "T3":
            c_m.append(260.0 * 10 ** 3)  # Heavy
    b_props['c_m_A_f'] = pd.DataFrame(c_m)

    # declare variables
    occupancy = []
    lighting_control = []
    mean_occupancy = []
    # declare constants
    glass_solar_transmitance = []
    glass_light_transmitance = []
    Lighting_Utilisation_Factor = []
    Lighting_MaintenanceFactor = []
    ACH_vent = []
    ACH_infl = []
    ventilation_efficiency = []
    phi_c_max_A_f = []
    phi_h_max_A_f = []
    heatingSystem = []
    coolingSystem = []
    heatingEfficiency = []
    coolingEfficiency = []
    ActuationEnergy = []
    COP_H = []
    COP_C = []

    for code in b_props['code1']:
        # variables
        occupancy.append('schedules_occ_%s.csv' % code)
        lighting_control.append(lighting_control_d.get(code))
        mean_occupancy.append(mean_occupancy_d.get(code))
        glass_solar_transmitance.append(0.687)
        glass_light_transmitance.append(0.744)
        Lighting_Utilisation_Factor.append(0.45)
        Lighting_MaintenanceFactor.append(0.9)
        ACH_vent.append(1.5)  # TODO: Shoudlnt this be a variable
        ACH_infl.append(0.5)
        ventilation_efficiency.append(0.6)
        phi_c_max_A_f.append(-np.inf)
        phi_h_max_A_f.append(np.inf)
        heatingSystem.append(DirectHeater)  # DirectHeater, #ResistiveHeater #HeatPumpHeater
        coolingSystem.append(DirectCooler)  # DirectCooler, #HeatPumpCooler
        heatingEfficiency.append(1.0)
        coolingEfficiency.append(1.0)
        ActuationEnergy.append(False)
        COP_H.append(1.0)
        COP_C.append(1.0)

    b_props['lighting_control'] = lighting_control
    b_props['mean_occupancy'] = mean_occupancy
    b_props['Qs_Wm2'] = b_props['mean_occupancy'] * b_props['Qs_Wp']  # occupancy: p/m2, qs_wp: W/p
    b_props['Occupancy'] = occupancy
    b_props['ActuationEnergy'] = ActuationEnergy
    b_props['glass_solar_transmitance'] = glass_solar_transmitance
    b_props['glass_light_transmitance'] = glass_light_transmitance
    b_props['Lighting_Utilisation_Factor'] = Lighting_Utilisation_Factor
    b_props['Lighting_MaintenanceFactor'] = Lighting_MaintenanceFactor
    b_props['ACH_vent'] = ACH_vent
    b_props['ACH_infl'] = ACH_infl
    b_props['ventilation_efficiency'] = ventilation_efficiency
    b_props['phi_c_max_A_f'] = phi_c_max_A_f
    b_props['phi_h_max_A_f'] = phi_h_max_A_f
    b_props['heatingSystem'] = heatingSystem
    b_props['coolingSystem'] = coolingSystem
    b_props['heatingEfficiency'] = heatingEfficiency
    b_props['coolingEfficiency'] = coolingEfficiency
    b_props['COP_H'] = COP_H
    b_props['COP_C'] = COP_C

    #convert possible intergers to floats
    b_props[['Tcs_set_C']]=b_props[['Tcs_set_C']].apply(pd.to_numeric)
    b_props[['Ths_set_C']]=b_props[['Ths_set_C']].apply(pd.to_numeric)

    BuildingPropertiesDF = pd.DataFrame({'Code': []})
    BuildingPropertiesDF['Code'] = b_props.loc[:, 'Code_x']
    BuildingPropertiesDF.loc[:, 'lighting_load'] = b_props.loc[:, 'El_Wm2']
    BuildingPropertiesDF.loc[:, 'lighting_control'] = lighting_control
    BuildingPropertiesDF.loc[:, 'U_em'] = b_props.loc[:, 'U_wall']
    BuildingPropertiesDF.loc[:, 'U_w', ] = b_props.loc[:, 'U_win']
    BuildingPropertiesDF.loc[:, 'theta_int_h_set'] = b_props.loc[:, 'Ths_set_C']
    BuildingPropertiesDF.loc[:, 'theta_int_c_set'] = b_props.loc[:, 'Tcs_set_C']
    BuildingPropertiesDF.loc[:, 'c_m_A_f'] = b_props.loc[:, 'c_m_A_f']
    BuildingPropertiesDF.loc[:, 'Qs_Wp'] = b_props.loc[:, 'Qs_Wp']
    BuildingPropertiesDF.loc[:, 'Ea_Wm2'] = b_props.loc[:, 'Ea_Wm2']
    BuildingPropertiesDF.loc[:, 'glass_solar_transmitance'] = glass_solar_transmitance
    BuildingPropertiesDF.loc[:, 'glass_light_transmitance'] = glass_light_transmitance
    BuildingPropertiesDF.loc[:, 'Lighting_Utilisation_Factor'] = Lighting_Utilisation_Factor
    BuildingPropertiesDF.loc[:, 'Lighting_MaintenanceFactor'] = Lighting_MaintenanceFactor
    BuildingPropertiesDF.loc[:, 'ACH_vent'] = ACH_vent
    BuildingPropertiesDF.loc[:, 'ACH_infl'] = ACH_infl
    BuildingPropertiesDF.loc[:, 'ventilation_efficiency'] = ventilation_efficiency
    BuildingPropertiesDF.loc[:, 'phi_c_max_A_f'] = phi_c_max_A_f
    BuildingPropertiesDF.loc[:, 'phi_h_max_A_f'] = phi_h_max_A_f
    BuildingPropertiesDF.loc[:, 'heatingSystem'] = heatingSystem
    BuildingPropertiesDF.loc[:, 'coolingSystem'] = coolingSystem
    BuildingPropertiesDF.loc[:, 'heatingEfficiency'] = heatingEfficiency
    BuildingPropertiesDF.loc[:, 'coolingEfficiency'] = coolingEfficiency
    BuildingPropertiesDF.loc[:, 'COP_H'] = COP_H
    BuildingPropertiesDF.loc[:, 'COP_C'] = COP_C
    BuildingPropertiesDF.set_index(['Code'], inplace=True)

    SimulationOptionsDF = b_props[['Code_x', 'setBackTempC', 'setBackTempH', 'Occupancy', 'ActuationEnergy']]
    SimulationOptionsDF.set_index(['Code_x'], inplace=True)

    SimulationOptionsDF = SimulationOptionsDF[0:2]
    BuildingPropertiesDF=BuildingPropertiesDF[0:2]

    SimulationOptions = SimulationOptionsDF.to_dict(orient='index')
    BuildingProperties = BuildingPropertiesDF.to_dict(orient='index')

    return BuildingProperties, SimulationOptions


# Create dictionaries for Archetypes:
# TODO: Rename to BuildDictsFromDF
def MakeDicts(b_props):
    bp_df = b_props[['Code_x',
                     'El_Wm2',
                     'lighting_control',
                     'U_wall',
                     'U_win',
                     'Ths_set_C',
                     'Tcs_set_C',
                     'c_m_A_f',
                     'Qs_Wp',  # Sensible heat gain due to occupancy [W/p]
                     'Ea_Wm2',  # Maximum electrical consumption due to appliances per unit of gross floor area [W/m2]
                     'glass_solar_transmitance',
                     'glass_light_transmitance',
                     'Lighting_Utilisation_Factor',
                     'Lighting_MaintenanceFactor',
                     'ACH_vent',
                     'ACH_infl',
                     'ventilation_efficiency',
                     'phi_c_max_A_f',
                     'phi_h_max_A_f',
                     'heatingSystem',
                     'coolingSystem',
                     'heatingEfficiency',
                     'coolingEfficiency',
                     'COP_H',
                     'COP_C']]

    bp_df = bp_df.rename(index=str, columns={'Code_x': 'Code',
                                             'El_Wm2': 'lighting_load',
                                             'U_win': 'U_w',
                                             'c_m_A_f': 'c_m_A_f',
                                             'U_wall': 'U_em',
                                             'Ths_set_C': 'theta_int_h_set',
                                             'Tcs_set_C': 'theta_int_c_set',
                                             })
    bp_df = bp_df.set_index(['Code'])
    BP_dict = bp_df.to_dict(orient='index')

    so_df = b_props[['Code_x', 'setBackTempC', 'setBackTempH', 'Occupancy', 'ActuationEnergy']]
    so_df = so_df.set_index(['Code_x'])

    SO_dict = so_df.to_dict(orient='index')

    return BP_dict, SO_dict


# TODO: Rename to SortDicts (check if necessary)
def sort_dicts(to_sort, sorted):
    newdict = {}
    for key in sorted:
        newdict[key] = to_sort[key]
    return newdict


if __name__ == '__main__':
    BuildingData = {
        "room_width": 4900,
        "room_height": 3100,
        "room_depth": 7000,
        "glazing_percentage_w": 0.92,
        "glazing_percentage_h": 0.97}

    b_data = ArchT_build_df(BuildingData)