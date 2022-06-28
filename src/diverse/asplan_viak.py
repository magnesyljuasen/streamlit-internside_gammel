import pandas as pd
import numpy as np
import streamlit as st
import altair as alt

class Importer:
    def __init__(self, fil) :
        self.fil = fil
        self.df = self.les_data()

    def les_data(self):
        df = pd.read_csv (self.fil, sep = ',', skiprows = 3)
        #df[['Dato', 'Klokkeslett']] = df['Unnamed: 0'].str.split(' ', expand=True)
        df = df.iloc[:, [0,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,25,26,28]]
        df = df.rename(columns={
            'Unnamed: 0':'Tidspunkt',
            'Smp.3' :'Panel pipe length',
            'Smp.4' : 'RA_temp(1), Tr_bPump',
            'Smp.5' : 'RA_temp(2), Tr_aPump',
            'Smp.6' : 'RA_temp(3), Theat',
            'Smp.7' : 'RA_temp(4), T_in',
            'Smp.8' : 'RA_temp(5), T_air',
            'Smp.9' : 'Flow',
            'Smp.10' : 'Pump speed',
            'Smp.11' : 'Panel heat',
            'Smp.12' : 'Test_Run',
            'Smp.13' : 'Test_Done',
            'Smp.14' : 'Purge',
            'Smp.15' : 'Purge_Done',
            'Smp.16' : 'Heating',
            'Smp.17' : 'Heating_Done',
            'Smp.18' : 'Cooling',
            'Smp.19' : 'Cooling_Done',
            'Smp.20' : 'Heat_Enabled',
            'Smp.21' : 'Pump_Enabled',
            'Smp.23' : 'Pause_Mode',
            'Smp.24' : 'Mains_Fail',
            'Smp.26' : 'E_Stop',
            })
        df['Tidspunkt'] = pd.to_datetime(df['Tidspunkt'], format = '%Y-%m-%d %H:%M:%S')
        return df

    def test_data(self, dato):
        for i in range (self.df.shape[0]-1, 0, -1):
            delta = (self.df.iat[i,0] - dato)
            delta_dager = int(str(delta).split(' ')[0])
            if delta_dager < 0:
                df = self.df.tail(self.df.shape[0] - i)
                df = df.iloc[1:,:]
                return df

class Justeringer:
    def __init__(self):
        pass

    def sirkulasjon(self, df):
        #Start sirkulasjon 
        for index, value in enumerate (df['Purge']):
            if value == -1:
                df = df.iloc[index:]
                break
        #Slutt sirkulasjon
        for index, value in enumerate (df['Purge']):
            if value == 0:
                df = df.iloc[:index]
                return df

    def varme(self, df):
        #Start sirkulasjon 
        for index, value in enumerate (df['Purge']):
            if value == -1:
                df = df.iloc[index:]
                break
        #Start test
        for index, value in enumerate (df['Heat_Enabled']):
            if value == -1:
                df = df.iloc[index:]
                break
        #Slutt test
        for index, value in enumerate (df['Heating']):
            if value == 0:
                df = df.iloc[:index]
                return df          

class Analyse:
    def __init__(self,df):
        self.df = df

    def gjennomsnittsverdi(self):
        arr = (self.df['RA_temp(1), Tr_bPump'] + self.df['RA_temp(3), Theat']) / 2
        return "{:.2f}".format(np.mean(arr))


class Plotting:
    def __init__(self) -> None:
        pass

    def enkel_graf(self, df):
        c = alt.Chart(df).mark_line(color='#1D3C34').encode(
            x=alt.X('Tidspunkt:T', axis=alt.Axis(format='%H:%M:%S', title='Klokkeslett')),
            y=alt.Y('RA_temp(3), Theat:Q', title='Temperatur (°C)'),
            ).configure_axis(grid=False).configure_view(strokeWidth=0)
        st.altair_chart(c, use_container_width=True)






    







    