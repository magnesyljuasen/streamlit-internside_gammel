import streamlit as st
from datetime import datetime
import pandas as pd

from src.diverse.asplan_viak import Importer, Justeringer, Analyse, Plotting

def trt_app():
    st.title('TRT Analyse')
    with st.sidebar:
        st.title("Sjekkliste for analyse")
        st.write("- Bilde av strømmåler før / etter test")
        st.write("- Temperaturprofilmålinger før / etter test")
        st.write("- Kollektorvæske")
        st.write("- Kollektortype")
        st.write("- Grunnvannstand")
        st.write("- Borelogg")
           

    fil = st.file_uploader ('Last opp testdata', key='TRT')
    if fil is not None:
        plotting = Plotting()
        test_type = st.selectbox('Hvilken type test?', ('Asplan Viak', 'Seabrokers', 'Båsum', 'Vestnorsk'))
        #Asplan Viak
        if test_type == 'Asplan Viak':
            fil.name = 'AV.csv'
            importer = Importer(fil)
            df = importer.df

            dato = pd.Timestamp(st.date_input('Velg datoen testen ble startet:'))
            df = importer.test_data(dato)
            if df.shape[0] != 1:
                st.markdown("---")
                st.header('Rådata')
                plotting.enkel_graf(df)
                with st.expander('Data'):
                    st.write(df)

                st.header('Sirkulasjon')
                juster_data = Justeringer()
                df_sirkulasjon = juster_data.sirkulasjon(df)
                plotting.enkel_graf(df_sirkulasjon)
                with st.expander('Data'):
                    st.write (df_sirkulasjon)
                analyse_sirkulasjon = Analyse(df_sirkulasjon)
                st.metric('Uforstyrret temperatur fra sirkulasjon', str(analyse_sirkulasjon.gjennomsnittsverdi()) + ' °C')
                
                st.header('Varme')
                df_varme = juster_data.varme(df)
                plotting.enkel_graf(df_varme)
                with st.expander('Data'):
                    st.write (df_varme)

        #-----
        if test_type == 'Seabrokers':
            st.write("Kommer...") 
        
        if test_type == 'Båsum':
            st.write("Kommer...") 


        if test_type == 'Vestnorsk':
            st.write("Kommer...") 