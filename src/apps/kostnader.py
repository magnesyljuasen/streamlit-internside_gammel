import streamlit as st
import xlsxwriter
from io import BytesIO
import numpy as np
import pandas as pd
from src.diverse.asplan_viak import Importer, Justeringer, Analyse, Plotting


def kostnader_app():
    st.title('Kostnader')
    
    valg = st.selectbox('Velg oppløsning', options=['Timer', 'Månedlig'])
    if valg == 'Månedlig':
        monthly_data()
    if valg == 'Timer':
        hourly_data()
    fil = st.file_uploader ('Last opp data', key='Kostnader')
    if fil:
        st.write(type(fil))
        st.dataframe(fil)


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
