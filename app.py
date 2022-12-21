
import streamlit as st
import streamlit_authenticator as stauth
import yaml
import base64

<<<<<<< HEAD
from apps._settings import settings
from apps._load_page import load_page
from apps._front_page import front_page
from apps._projects import projects
from apps._trt import trt
from apps._bergvarmekalkulatoren import bergvarmekalkulatoren
from apps._sizing import sizing
from apps._python_programming import python_programming
from apps._geotechnics import geotechnics
from apps._energy_analysis import energy_analysis
=======
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
from src.apps.news import news_app

st.set_page_config(page_title="AV Grunnvarme", page_icon=":bar_chart:", layout="centered", initial_sidebar_state="expanded")

with open("styles/main.css") as f:
    st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)

with open('src/innlogging/config.yaml') as file:
    config = yaml.load(file, Loader=stauth.SafeLoader)
authenticator = stauth.Authenticate(config['credentials'],config['cookie']['name'],config['cookie']['key'],config['cookie']['expiry_days'])
name, authentication_status, username = authenticator.login('Asplan Viak🌱 Innlogging for grunnvarme', 'main')
>>>>>>> 92e436eb3dc053fdfe1d67bbb676f4ff1aa5dd37

NAME, authentication_status, USERNAME, authenticator = settings()

if authentication_status == False:
    st.error('Ugyldig brukernavn/passord')    
elif authentication_status == None:
    load_page()
#App start 
elif authentication_status:
    with st.sidebar:
        authenticator.logout('Logg ut', 'sidebar')
        st.title(f'Hei {NAME}!')
        options = ["Forside", "Prosjektoversikt", "TRT", "Bergvarmekalkulatoren", "Dimensjonering", "Python", "Geoteknikk", "Energianalyse"]
        selected = st.radio("Velg app", options, index=0)
        st.markdown("---")
    if selected == "Forside":
        front_page()   
    if selected == "Prosjektoversikt":
        projects(NAME)
    if selected == "TRT":
        trt()
    if selected == "Bergvarmekalkulatoren":
        bergvarmekalkulatoren()
    if selected == "Dimensjonering":
        sizing()
    if selected == "Python":
        python_programming()
    if selected == "Geoteknikk":
        geotechnics()
    if selected == "Energianalyse":
        energy_analysis()
        











