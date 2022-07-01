import streamlit as st
import xlsxwriter
from io import BytesIO
import numpy as np
import pandas as pd
from src.diverse.asplan_viak import Importer, Justeringer, Analyse, Plotting
import altair as alt


def kostnader_app():
    st.title('Kostnader')
    selected = st.selectbox('Velg oppløsning', options=['Timer', 'Månedlig'])
    if selected == 'Månedlig':
        monthly_data()
    if selected == 'Timer':
        hourly_data()
    file = st.file_uploader ('Last opp data', key='Kostnader')
    if file:
        with st.sidebar:
            st.title("Forutsetninger")
            price = el_price()
            invest = investment()

        calculation(file, price)

def plot(costs):
    months = ['jan', 'feb', 'mar', 'apr', 'mai', 'jun', 'jul', 'aug', 'sep', 'okt', 'nov', 'des']
    data = pd.DataFrame({'Months' : months, 'Costs' : costs })
    c = alt.Chart(data).mark_bar(color="#4a625c").encode(
        x=alt.X('Months:N', sort=months, title=None),
        y=alt.Y('Costs:Q', title="Kostnader [kr]"))
    st.altair_chart(c, use_container_width=True)

def calculation(file, price):
    df = pd.read_excel(file)
    demand = df.iloc[:,1].to_numpy()
    costs = price * demand
    plot(costs)

def el_price():
    price =  np.array(st.number_input("Velg totalpris for strøm [kr/kWh]", min_value=0.0, value = 1.1, max_value=5.0, step=0.1))
    return price 

def investment():
    invest = st.number_input("Investeringskostnad [kr]", value=250000, step=5000)
    return invest

def monthly_data():
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet()
    worksheet.write('A1', 'Måneder')
    worksheet.write('B1', 'Energibehov [kWh]')
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Des']
    worksheet.write_column('A2', months)
    workbook.close()
    st.download_button(
        label="Fyll inn data",
        data=output.getvalue(),
        file_name="Måneder.xlsx",
        mime="application/vnd.ms-excel")

def hourly_data():
    output = BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet()
    worksheet.write('A1', 'Timer [år]')
    worksheet.write('B1', 'Energibehov [kWh]')
    hours = np.arange(0,8760,1)
    worksheet.write_column('A2', hours)
    workbook.close()
    st.download_button(
        label="Fyll inn data",
        data=output.getvalue(),
        file_name="Timer.xlsx",
        mime="application/vnd.ms-excel")
