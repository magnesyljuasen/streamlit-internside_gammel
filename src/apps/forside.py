import streamlit as st
from PIL import Image


def forside_app():
    col1, col2, col3 = st.columns(3)
    with col1:
        image = Image.open('src/bilder/logo.png')
        st.image(image)  
    with col2:
        st.title("Grunnvarme")
        st.write('Internside')