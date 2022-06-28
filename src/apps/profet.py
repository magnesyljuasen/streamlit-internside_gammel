import streamlit as st

from src.diverse.funksjoner import Location


def profet_app():
    st.title("PROFet")

    location = Location() 
    lat, long = location.address_to_coordinate(location.input())
    with st.expander("Juster posisjon"):
        lat = st.number_input('Breddegrad', value=lat, step=0.0001)
        long = st.number_input('Lengdegrad', value=long, step=0.0001)

    location.map(lat, long)
    st.markdown("---")


