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
    prize_zone_array = []
    for i, zone in enumerate(zones):
        r = requests.get(f"{url}/?zone={zone}&date={today}&key=b0235f2e-7ddc-4bf1-a054-5dffb4ec037a")
        if r.status_code == 200:
            price_array = []
            for i in range(0, 24):
                NOK_per_kWh = list(r.json().values())[i]["NOK_per_kWh"]
                price_array.append(NOK_per_kWh)
            prize_zone_array.append(price_array)


    if st.checkbox("NO1", value=True):
        chart_data = pd.DataFrame({
            'NO1': prize_zone_array[0],
            })
    if st.checkbox("NO2"):
        chart_data = pd.DataFrame({
            'NO2': prize_zone_array[1],
            })
    if st.checkbox("NO3"):
        chart_data = pd.DataFrame({
            'NO3': prize_zone_array[2],
            })
    if st.checkbox("NO4"):
        chart_data = pd.DataFrame({
            'NO4': prize_zone_array[3],
            })
    if st.checkbox("NO5"):
        chart_data = pd.DataFrame({
            'NO5': prize_zone_array[4],
            })


    st.line_chart(chart_data)

    st.header(f"Strømpris i dag, {today}")
    st.metric(label = "Gjennomsnittlig strømpris", value = f"{round(np.mean(price_array), 2)} kr")

    
    

        















