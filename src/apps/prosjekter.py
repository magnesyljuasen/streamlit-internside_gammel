from click import option
import streamlit as st
import re 
import requests
from geopy.geocoders import Nominatim
import pydeck as pdk
import pandas as pd


class Location:
    def __init__(self):
        pass

    def address_to_coordinate (self, adresse):
        geolocator = Nominatim(user_agent="my_request")
        location = geolocator.geocode(adresse, timeout=None, country_codes="NO")
        if location is None:
            lat = 0
            long = 0
        else:
            lat = location.latitude
            long = location.longitude
        return lat, long

    def input(self):
         address = st.text_input('Skriv inn adresse hvis den ikke finner riktig sted (det kan være lurt å inkludere kommune)', placeholder='Karl Johans Gate 22, Oslo')
         return address

    def map(self, lat, long):
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

        st.pydeck_chart(pdk.Deck(
                map_style='mapbox://styles/mapbox/streets-v11',
                initial_view_state=pdk.ViewState(
                latitude=lat,
                longitude=long,
                pitch=45,
                bearing=0
                ),
                layers=[init]))


def prosjekter_app():
    st.title("Oppdragsoversikt")
    st.header("Registrer nytt oppdrag")
    c1, c2 = st.columns(2)
    with c1: 
        projectname = st.text_input("*Prosjektnavn")
        id = st.text_input("*Oppdragsnummer")
        
    with c2:
        project_type = st.multiselect("*Oppdragstype", ["TRT", "TRT & Dimensjonering", "Annet", "Større oppdrag"])
        status = st.multiselect("*Oppdragsstatus", ["Pågår", "Fullført", "Avventer", "Kommer"])
        
    lat, long = 0, 0
    res = re.findall(r'\w+', projectname)
    location = Location()
    for index, value in enumerate(res):
        lat, long = location.address_to_coordinate(value)
        if lat or long > 0:
            break
    with st.expander("Hvis posisjon er feil"):
        adjusted_address = location.input()
    if len(adjusted_address) > 0:
        lat, long = location.address_to_coordinate(adjusted_address)
    if lat != 0:
        location.map(lat, long)

    st.header("Aktive oppdrag")
    st.write("Kart")
    st.write("Liste")

    st.header("Fullførte oppdrag")
    st.write("Kart")
    st.write("Liste")

