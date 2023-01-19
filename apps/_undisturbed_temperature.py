import streamlit as st
import pandas as pd
import numpy as np

from scripts._utils import Plotting


def undisturbed_temperature():
    st.button("Refresh")
    st.title("Uforstyrret temperatur")
    df = pd.read_excel("src/data/input/uforstyrret_temperatur.xlsx")
    st.header("Rådata")
    Plotting().xy_plot_reversed(df["Temperatur"], df["Dybde"])
    st.header("Analyse")
    groundwater_table = st.number_input("Grunnvannstand [m]", value=5, min_value=0, max_value=100, step=1)
    df_filtered = df[df["Dybde"] >= groundwater_table]
    Plotting().xy_plot_reversed(df_filtered["Temperatur"], df_filtered["Dybde"])
    mean_value = df_filtered["Temperatur"].mean()
    positive_deviation = 0
    negative_deviation = 0
    st.write(f"**Opprinnelig gjennomsnitt: {round(float(mean_value),2)}**")
    mean_value = st.slider("Uforstyrret temperatur", value=float(mean_value), min_value=float(mean_value) - 3, max_value=float(mean_value) + 3)
    for i in range(0, len(df_filtered)-1):
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
        if totalt_areal > 0:
            positive_deviation += totalt_areal
        if totalt_areal < 0:
            negative_deviation += totalt_areal

    st.write(f"Denne skal bli 0: **{int(positive_deviation) + int(negative_deviation)}**")
    

