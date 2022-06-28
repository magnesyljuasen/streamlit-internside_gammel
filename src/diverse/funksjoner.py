import requests
from streamlit_lottie import st_lottie
import streamlit as st 
from PIL import Image
from geopy.geocoders import Nominatim
import pydeck as pdk
import pandas as pd


def load_lottie(url: str):
    r = requests.get(url)
    if r.status_code!= 200:
        return None
    return r.json()

#--
def load_page():
    lott = load_lottie('https://assets3.lottiefiles.com/packages/lf20_szeieqx5.json')
    st_lottie(lott)

def title_page():
    col1, col2, col3 = st.columns(3)
    with col1:
        image = Image.open('src/bilder/logo.png')
        st.image(image)  
    with col2:
        st.title("Grunnvarme")
        st.write('Internside')


class Location:
    def __init__(self):
        pass

    def address_to_coordinate (self, adresse):
        geolocator = Nominatim(user_agent="my_request")
        location = geolocator.geocode(adresse, timeout=None)
        if location is None:
            st.error ('Finner ikke adresse. Prøv igjen!')
            st.stop()
        lat = location.latitude
        long = location.longitude
        return lat, long

    def input(self):
         address = st.text_input('Oppgi adresse (det kan være lurt å inkludere kommune)', value='Karl Johans Gate 22, Oslo')
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
