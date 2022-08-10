from logging.handlers import RotatingFileHandler
from click import option
import streamlit as st
import re 
import requests
from geopy.geocoders import Nominatim
import pydeck as pdk
import pandas as pd
from datetime import date
import src.diverse.prosjektdatabase as db


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

    def map1(self, lat, long):
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

    def map2(self, df, color_pick):
        init = pdk.Layer(
        type='ScatterplotLayer',
        data=df,
        get_position='[Longitude, Latitude]',
        pickable=True,
        stroked=True,
        radius_max_pixels=10,
        radius_min_pixels=500,
        filled=True,
        line_width_scale=25,
        line_width_max_pixels=5,
        get_fill_color=color_pick,
        get_line_color=[0, 0, 0])

        st.pydeck_chart(pdk.Deck(
        map_style='mapbox://styles/mapbox/streets-v11',
        initial_view_state=pdk.ViewState(
        latitude=64.01487,
        longitude=11.49537,
        pitch=0,
        bearing=0,
        zoom = 3.1
        ),
        layers=[init], tooltip={
        'html': '<b>{key}</b> <br> ID: {Oppdragsnummer} <br> {Type} <br> <i>Registrert av {Innsender}</i>',
        'style': {'color': 'white'}}))

def new_entry(name):
    dato = date.today().strftime("%d/%m/%Y")
    st.header("Registrer nytt oppdrag")
    c1, c2 = st.columns(2)
    with c1: 
        projectname = st.text_input("*Prosjektnavn")
        id = st.text_input("*Oppdragsnummer")
    with c2:
        project_type = st.multiselect("*Oppdragstype", ["TRT", "TRT & Dimensjonering", "Annet", "Større oppdrag"])
        if len(project_type) > 0:
            project_type = project_type[0]
        project_status = st.multiselect("*Oppdragsstatus", ["Pågår", "Fullført", "Avventer", "Kommer"])
        if len(project_status) > 0:
            project_status = project_status[0]

    if len(projectname) > 0 and len(id) > 0 and len(project_type) > 0 and len(project_status) > 0: 
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
            location.map1(lat, long)
            db.insert_data(projectname, id, project_type, project_status, lat, long, name, dato)

def change_entry():
    ds = db.fetch_all_data()
    df = pd.DataFrame(ds)
    arr = df["key"].to_numpy()
    selected = st.radio("Valg", ["Slett oppdrag", "Oppdater status"])
    key = st.multiselect("Velg oppdrag", arr)
    if len(key) > 0:
        if selected == "Slett oppdrag":
            db.remove_data(key[0])
        if selected == "Oppdater status":
            list = db.get_data(key[0])
            db.remove_data(key[0])
            projectname = st.text_input("Endre navn", list["key"])

            id = list["Oppdragsnummer"]
            project_type = list["Type"]
            project_status = list["Status"]
            if project_status == "Pågår":
                index = 0
            if project_status == "Fullført":
                index = 1
            if project_status == "Avventer":
                index = 2
            if project_status == "Kommer":
                index = 3
            project_status = st.selectbox("Status", ["Pågår", "Fullført", "Avventer", "Kommer"])
            lat = list["Latitude"]
            long = list["Longitude"]
            name = list["Innsender"]
            dato = list["Dato"]
            db.insert_data(projectname, id, project_type, project_status, lat, long, name, dato)

def prosjekter_app(name):
    st.title("Prosjekter")
    new_entry(name)

    st.markdown("""---""")
    st.header("Oppdragsoversikt")
    ds = db.fetch_all_data()
    if len(ds) == 0:
        st.warning("Ingen data")
        st.stop()
    df = pd.DataFrame(ds)
    
    with st.expander("Oppdater status / Feilført"):
        change_entry()
    with st.expander("Tabellform"):
        st.write(df)
    location = Location()
    st.subheader("Aktive oppdrag")
    location.map2(df.loc[df['Status'] == 'Pågår'], [255, 195, 88])

    with st.expander("Andre"):
        st.subheader("Fremtidige oppdrag")
        location.map2(df.loc[df['Status'] == 'Kommer'], [183, 220, 143])
        
        st.subheader("Fullførte oppdrag")
        location.map2(df.loc[df['Status'] == 'Fullført'], [29, 60, 52])
    
    
