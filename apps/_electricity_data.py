import streamlit as st
import pandas as pd
import folium
from folium.plugins import HeatMap, HeatMapWithTime
from streamlit_folium import st_folium
import random
import numpy as np
import geopandas as gpd
from shapely.geometry import Polygon

@st.cache()
def upload_data(number_of_points):
    df1 = pd.read_excel("src/data/input/el_nett_trondheim.xlsx", sheet_name=0)
    df2 = pd.read_excel("src/data/input/el_nett_trondheim.xlsx", sheet_name=1)
    df1 = df1.head(number_of_points)
    trafo_list = df1["trafo"].unique()
    return df1, df2, trafo_list

@st.cache()
def color_generator(trafo_list):
    color_list = []
    for i in range(0, len(trafo_list)):
        color = "#%06x" % random.randint(0, 0xFFFFFF)
        color_list.append(color)
    return color_list

def power_grid():
    st.button("Refresh")
    st.title("Data fra Tensio")
    st.caption("Det er 115 118 adressepunkter i datasettet. Det tar lang tid å vise alle på kart (særlig for *adresser*)")
    number_of_points = st.number_input("Antall punkter", value = 100, max_value=115118, step = 100)
    #--
    st.markdown("*Velg type kartvisning*")
    c1, c2 = st.columns(2)
    with c1:
        address_display = st.checkbox("Adresser", value=True)
    with c2:
        address_trafo_display = st.checkbox("Adresser tilknyttet samme trafo", value=True)
    df1, df2, trafo_list = upload_data(number_of_points)
    color_list = color_generator(trafo_list)
    with st.expander("Data"):
        st.write(df1)
        st.write(df2)
    #--
    m = folium.Map(location=[63.446827, 10.421906], zoom_start=11)
    for i in range(0, len(trafo_list)):
        df_plot = df1.loc[df1['trafo'] == trafo_list[i]]
        lat_point_list= df_plot["lat"]
        lng_point_list = df_plot["lng"]
        if len(lat_point_list) > 4:
            trafo_name = df_plot["trafo"].iloc[0]
            df2_row = df2.loc[df2["trafo"] == trafo_name]
            polygon_geom = Polygon(zip(lng_point_list, lat_point_list))
            polygon_geom2 = polygon_geom.convex_hull
            #--
            text = f""" 
            Trafo: <strong>{trafo_name}</strong></br> \
            Nettstasjon: <strong>{df2_row["grid_station"].iloc[0]}</strong></br> \ 
            Antall energimålere (AV | TRD): <strong>{len(lat_point_list)} | {df2_row["energimålere"].iloc[0]}</strong></br> \
            Kapasitet (TRD): <strong>{round(df2_row["performance (kW)"].iloc[0] * 10/1000, 2)} GW</strong></br> \   
            """
            #--
            if address_trafo_display:
                folium.GeoJson(polygon_geom2, style_function=lambda x: {'fillColor': 'orange'}, tooltip=text).add_to(m)
            if address_display:
                df_plot.apply(lambda row:folium.CircleMarker(location=[row["lat"], row["lng"]], radius=5, tooltip=row["trafo"], color=color_list[i]).add_to(m), axis=1)
    st_folium(m, width=725, returned_objects=[])
    st.markdown("---")
    st.caption("- Knytte trafo til kapasitet")
    st.caption("- Knytte trafo til nettstasjon")
    st.caption("- Heat map(?)")


    #--
    #df2 = pd.read_excel("src/data/input/el_nett_trondheim.xlsx", sheet_name=1)
    #st.write(df2)
    #st.write(df1["trafo"].unique())









