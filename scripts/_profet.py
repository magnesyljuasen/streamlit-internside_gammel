import streamlit as st
import pandas as pd
import numpy as np

class EnergyDemand:
    def __init__(self):
        self.profet_data = pd.read_csv('src\data\csv\effect_profiles.csv', sep=';')
            
    def get_thermal_arrays_from_input(self):
        building_types = ['House', 'Apartment', 'Office', 
        'Shop', 'Hotel','Kindergarten',' School', 
        'University','Culture_Sport', 'Nursing_Home', 
        'Hospital','Other']
        building_standard = ['Regular', 'Efficient', 'Very efficient']
        arrays = ["Thermal", "DHW", "Space_heating"]
        c1, c2 = st.columns(2)
        with c1:
            selected_area = st.number_input("Areal", min_value=1, value=1000, max_value=100000, step = 250)
            selected_building_type = st.selectbox("Bygningstype", options=building_types)
        with c2:
            selected_building_standard = st.selectbox("Bygningsstandard", options=building_standard)
            selected_array = st.selectbox("Behovsprofil", options=arrays)
        if selected_array == "Thermal":
            return selected_area * (np.array(self.profet_data[selected_building_type + selected_building_standard + "Space_heating"]) + np.array(self.profet_data[selected_building_type + selected_building_standard + "DHW"])).flatten(), selected_array
        else:
            return selected_area * np.array(self.profet_data[selected_building_type + selected_building_standard + selected_array]).flatten(), selected_array
