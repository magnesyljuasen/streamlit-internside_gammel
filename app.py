
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from src.apps.geoteknikk import geoteknikk_app

from src.diverse.funksjoner import load_page
from src.apps.forside import forside_app
from src.apps.trt import trt_app
from src.apps.prosjekter import prosjekter_app
from src.apps.bergvarmekalkulatoren import bergvarmekalkulatoren_app
from src.apps.kostnader import kostnader_app
from src.apps.kart import kart_app
from src.apps.profet import profet_app
from src.apps.maler import maler_app
from src.apps.strompris import strompris_app
from src.apps.programmering import programmering_app
from src.apps.pygfunction import pygfunction_app

st.set_page_config(page_title="AV Grunnvarme", page_icon=":bar_chart:", layout="centered")

with open("styles/main.css") as f:
    st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)

with open('src/innlogging/config.yaml') as file:
    config = yaml.load(file, Loader=stauth.SafeLoader)
authenticator = stauth.Authenticate(config['credentials'],config['cookie']['name'],config['cookie']['key'],config['cookie']['expiry_days'])
name, authentication_status, username = authenticator.login('Asplan Viak🌱 Innlogging for grunnvarme', 'main')

if authentication_status == False:
    st.error('Ugyldig brukernavn/passord')
    
elif authentication_status == None:
    load_page()

#App start 
elif authentication_status:
    with st.sidebar:
        authenticator.logout('Logg ut', 'sidebar')
        st.title(f'Hei {name}!')

        options = ["Forside", "Prosjekter", "TRT", "Dimensjonering", "Økonomi", "PROFet", "Strømpris", "Bergvarmekalkulatoren", "Kart", "Geoteknikk", "Maler", "Programmering"]
        selected = st.radio("Velg app", options, index=0)
        st.markdown("---")

    if selected == "Forside":
        forside_app()

    if selected == "Prosjekter":
        prosjekter_app(name)

    if selected == "TRT":
        trt_app()

    if selected == "Dimensjonering":
        pygfunction_app()

    if selected == "Økonomi":
        kostnader_app()

    if selected == "PROFet":
        profet_app()

    if selected == "Strømpris":
        strompris_app()

    if selected == "Bergvarmekalkulatoren":
        bergvarmekalkulatoren_app()

    if selected == "Kart":
        kart_app() 

    if selected == "Geoteknikk":
        geoteknikk_app()

    if selected == "Maler":
        maler_app()

    if selected == "Programmering":
        programmering_app()

   
        
        











