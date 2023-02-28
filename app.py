
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
from apps._electricity_data import power_grid
from apps._undisturbed_temperature import undisturbed_temperature
from apps._elprice import elprice

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
            options = ["Forside", "Prosjektoversikt", "Termisk responstest", "Bergvarmekalkulatoren", "Tidligfasedimensjonering", "Energianalyse", "Python", "Geoteknisk vurdering", "ΔT", "Uforstyrret temperatur", "Tensio", "Strømpriser"]
            selected = st.radio("Velg app", options, index=0)
            st.markdown("---")
    if NAME == None:
        early_phase()
    else:
        if selected == "Forside":
            front_page()   
        if selected == "Prosjektoversikt":
            projects(NAME)
        if selected == "Termisk responstest":
            trt()
        if selected == "Bergvarmekalkulatoren":
            bergvarmekalkulatoren()
        if selected == "Tidligfasedimensjonering":
            early_phase()
        if selected == "Energianalyse":
            energy_analysis()
        if selected == "Python":
            python_programming()
        if selected == "Geoteknisk vurdering":
            geotechnics()
        if selected == "ΔT":
            delta_t()
        if selected == "Uforstyrret temperatur":
            undisturbed_temperature()
        if selected == "Strømpriser":
            elprice()
        if selected == "Tensio":
            if NAME == "Randi" or NAME == "Magne" or NAME == "Henrik":
                power_grid()
            else:
                st.write("**Konfidensielle data - be om tilgang**")
            



    
        











