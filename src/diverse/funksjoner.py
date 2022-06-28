import requests
from streamlit_lottie import st_lottie
import streamlit as st 
from PIL import Image


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
