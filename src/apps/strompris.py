import streamlit as st
import requests
from datetime import date
import numpy as np
import pandas as pd

def strompris_app():
    
    st.title("Strømpriser API")
    #url = "https://norway-power.ffail.win/" 
    url = "https://playground-norway-power.ffail.win" #bruk denne for testing

    today = date.today()
    zones = ["NO1", "NO2", "NO3", "NO4", "NO5"]
    for i, zone in enumerate(zones):
        r = requests.get(f"{url}/?zone={zone}&date={today}&key=b0235f2e-7ddc-4bf1-a054-5dffb4ec037a")
        if r.status_code == 200:
            price_array = []
            for i in range(0, 24):
                NOK_per_kWh = list(r.json().values())[i]["NOK_per_kWh"]
                price_array.append(NOK_per_kWh)

            chart_data = pd.DataFrame({
                'NO1': price_array,
                'NO2': price_array,
                'NO3': price_array,
                'NO4': price_array,
                'NO5': price_array
                })

        st.line_chart(chart_data)

    st.header(f"Strømpris i dag, {today}")
    st.metric(label = "Gjennomsnittlig strømpris", value = f"{round(np.mean(price_array), 2)} kr")

    
    

        















