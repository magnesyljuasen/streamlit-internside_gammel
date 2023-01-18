
import streamlit as st
import streamlit_authenticator as stauth
import yaml
import base64

from apps._settings import settings
from apps._load_page import load_page
from apps._front_page import front_page
from apps._projects import projects
from apps._trt import trt
from apps._bergvarmekalkulatoren import bergvarmekalkulatoren
from apps._sizing import sizing
from apps._python_programming import python_programming
from apps._geotechnics import geotechnics
from old._energy_analysis_old import energy_analysis_old
from apps._energy_analysis import energy_analysis
from apps._early_phase import early_phase
from apps._delta_t import delta_t

from scripts._ghetool import main_functionalities


NAME, authentication_status, USERNAME, authenticator = settings()

if authentication_status == False:
    st.error('Ugyldig brukernavn/passord')    
elif authentication_status == None:
    load_page()
#App start 
elif authentication_status:
    with st.sidebar:
        authenticator.logout('Logg ut', 'sidebar')
        if NAME != None:
            st.title(f'Hei {NAME}!')
            options = ["Forside", "Prosjektoversikt", "TRT", "Bergvarmekalkulatoren", "Tidligfasedimensjonering", "Energianalyse", "Python", "Geoteknikk", "ΔT",]
            selected = st.radio("Velg app", options, index=0)
            st.markdown("---")
    if NAME == None:
        early_phase()
    else:
        if selected == "Forside":
            front_page()   
        if selected == "Prosjektoversikt":
            projects(NAME)
        if selected == "TRT":
            trt()
        if selected == "Bergvarmekalkulatoren":
            bergvarmekalkulatoren()
        if selected == "Tidligfasedimensjonering":
            early_phase()
        if selected == "Energianalyse":
            energy_analysis()
        if selected == "Python":
            python_programming()
        if selected == "Geoteknikk":
            geotechnics()
        if selected == "ΔT":
            delta_t()
            



    
        











