import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image

from scripts._utils import Plotting


def undisturbed_temperature():
    st.title("Uforstyrret temperatur")
    uploaded_file = st.file_uploader("Last opp fil (excel)")
    with st.expander("Hvordan skal filen se ut?"):
        image = Image.open("src/data/img/uforstyrretTemperaturInput.PNG")
        st.image(image)  
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        st.header("Rådata")
        Plotting().xy_plot_reversed(df["Temperatur"], df["Dybde"])
        st.header("Analyse")
        groundwater_table = st.number_input("Grunnvannstand [m]", value=5, min_value=0, max_value=100, step=1)
        df_filtered = df[df["Dybde"] >= groundwater_table]
        mean_value = df_filtered["Temperatur"].mean()
        positive_deviation = 0
        negative_deviation = 0
        st.write(f"*Gjettet: {round(float(mean_value),2)} °C*")
        mean_value = st.slider("Velg verdi", value = float(mean_value), min_value=float(mean_value) - 3, max_value=float(mean_value) + 3)
        #--
        for i in range(0, len(df_filtered)-1):
            if df_filtered["Temperatur"].iloc[i] > mean_value:
                x1 = df_filtered["Temperatur"].iloc[i] - mean_value
                x2 = df_filtered["Temperatur"].iloc[i+1] - mean_value
                delta_y = df_filtered["Dybde"].iloc[i+1] - df_filtered["Dybde"].iloc[i]
                areal_trekant = delta_y*abs(x1-x2)/2
                if x1 > x2:
                    langside = x1 - abs(x1-x2)
                elif x2 < x1:
                    langside = x2 - abs(x1-x2)
                else:
                    langside = x1
                areal_rektangel = delta_y*langside
                totalt_areal = areal_rektangel + areal_trekant
                positive_deviation += totalt_areal
            elif df_filtered["Temperatur"].iloc[i] < mean_value:
                x1 = mean_value - df_filtered["Temperatur"].iloc[i] 
                x2 = mean_value - df_filtered["Temperatur"].iloc[i+1] 
                delta_y = df_filtered["Dybde"].iloc[i+1] - df_filtered["Dybde"].iloc[i]
                areal_trekant = delta_y*abs(x1-x2)/2
                if x1 > x2:
                    langside = x1 - abs(x1-x2)
                elif x2 < x1:
                    langside = x2 - abs(x1-x2)
                else:
                    langside = x1
                areal_rektangel = delta_y*langside
                totalt_areal = areal_rektangel + areal_trekant
                negative_deviation += totalt_areal
        st.write(f"Denne verdien skal bli 1,00; **{round(float(positive_deviation/negative_deviation),2)}**")
        st.write(f"**Uforstyrret temperatur: {round(float(mean_value),2)} °C**")
        Plotting().xy_plot_reversed(df_filtered["Temperatur"], df_filtered["Dybde"], groundwater_table, mean_value)

