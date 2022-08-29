import streamlit as st
import requests 
import pydeck as pdk
import pandas as pd
from PIL import Image

from src.diverse.funksjoner import Location

def kart_app():
    st.header("Test av NGU sine APIer")
    with st.expander("API - test"):    
        
        location = Location() 
        lat, long = location.address_to_coordinate(location.input())
        
        lat = st.number_input('Breddegrad', value=lat, step=0.0001)
        long = st.number_input('Lengdegrad', value=long, step=0.0001)
        
        

        df = pd.DataFrame({'latitude': [lat],'longitude': [long]})

        init = pdk.Layer(
                    type='ScatterplotLayer',
                    data=df,
                    get_position='[longitude, latitude]',
                    pickable=True,
                    stroked=True,
                    radius_max_pixels=10,
                    radius_min_pixels=500,
                    filled=True,
                    line_width_scale=25,
                    line_width_max_pixels=5,
                    get_fill_color=[255, 195, 88],
                    get_line_color=[0, 0, 0])

        diff = 0.05

        x1 = long - diff
        x2 = lat - diff
        x3 = long + diff
        x4 = lat + diff

        antall = 100
        
        endpoint = f'https://ogcapitest.ngu.no/rest/services/granada/v1/collections/broennparkbroenn/items?f=json&limit={antall}&bbox={x1}%2C{x2}%2C{x3}%2C{x4}'
        r = requests.get(endpoint)
        data = r.json()
        
        st.write(data)

        geojson = pdk.Layer(
        "GeoJsonLayer",
        data,
        pickable=True,
        stroked=True,
        filled=False,
        line_width_scale=50,
        line_width_max_pixels=100,
        get_line_color=[0, 0, 255],
        extruded=True,
        wireframe=True,
        get_elevation='properties.boret_lengde_til_berg * 200')

        st.pydeck_chart(pdk.Deck(
                map_style='mapbox://styles/mapbox/streets-v11',
                initial_view_state=pdk.ViewState(
                latitude=lat,
                longitude=long,
                pitch=45,
                bearing=0
                ),
                layers=[geojson, init]))
    
    

    

    
    

