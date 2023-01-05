import numpy as np
import streamlit as st
import scipy

def peakshaving(energy_arr, REDUCTION, TO_TEMP, FROM_TEMP):
    RHO, HEAT_CAPACITY = 0.96, 4.2
    NEW_MAX_EFFECT = max(energy_arr) - REDUCTION
    
    #Finne topper
    peakshaving_arr = energy_arr
    max_effect_arr = np.zeros(len(energy_arr))
    for i in range(0, len(energy_arr)):
        effect = energy_arr[i]
        if effect > NEW_MAX_EFFECT:
            max_effect_arr[i] = effect - NEW_MAX_EFFECT
    
    #Lade tanken før topper, og ta bort topper
    day = 12
    peakshave_accumulated = 0
    peakshave_arr = []
    for i in range(0, len(energy_arr)-day):
        peakshave = max_effect_arr[i+day]
        peakshave_arr.append(peakshave)
        peakshave_accumulated += peakshave
        if peakshave > 0:
            peakshaving_arr[i+day] -= peakshave
            peakshaving_arr[i] += peakshave/6
            peakshaving_arr[i+1] += peakshave/6
            peakshaving_arr[i+2] += peakshave/6
            peakshaving_arr[i+3] += peakshave/6
            peakshaving_arr[i+4] += peakshave/6
            peakshaving_arr[i+5] += peakshave/6

    #Totalenergi
    tank_size = round(max(peakshave_arr)*3600/(RHO*HEAT_CAPACITY*(TO_TEMP-FROM_TEMP))/1000,1)
    #tank_size = round(peakshave_accumulated*3600/(RHO*HEAT_CAPACITY*(TO_TEMP-FROM_TEMP))/1000,1)
    st.write(f"Tankstørrelse {tank_size} m3")
    with st.expander("Mulige tanker", expanded=True):
        diameter_list = [1, 2, 3, 4, 5]
        for i in range(0, len(diameter_list)):
            diameter = diameter_list[i]
            height = round(4*tank_size/(scipy.pi*diameter**2),1)
            st.write(f"{i}) Diameter: {diameter} m | Høyde: {height} m")
    return peakshaving_arr, max(peakshaving_arr)