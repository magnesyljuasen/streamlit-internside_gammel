import streamlit as st
import pandas as pd
import numpy as np
import xlwings as xw
import win32com.client as win32
import requests
import csv
import os
import timeit

from src.diverse.funksjoner import Location

class Temperatur:
    def __init__ (self):
        self.klient_id = '248d45de-6fc1-4e3b-a4b0-e2932420605e'
        
    def stasjons_liste (self): 
        endpoint = 'https://frost.met.no/sources/v0.jsonld?country=NO&types=SensorSystem'
        r = requests.get(endpoint, auth=(self.klient_id,''))
        klimadata = r.json()['data']

        distanseListe = []
        IDListe = []
        iListe = []
        koordinatListe = []

        i = -1
        for stasjon in range (0,len(klimadata)):
            i += 1
            stasjonID = klimadata[stasjon]['id']
            try: 
                stasjonKoordinater = klimadata[stasjon]['geometry']['coordinates']
            except:
                stasjonKoordinater = [0,0]

            stasjonX = stasjonKoordinater [0]
            stasjonY = stasjonKoordinater [1]

            IDListe.append (stasjonID)
            iListe.append (i)
            koordinatListe.append (stasjonKoordinater)

        klimadataFrame = {'ID': iListe, 'stasjonID': IDListe, 'koordinat': koordinatListe}

        stasjonsListe = pd.DataFrame (klimadataFrame)
        
        return stasjonsListe
    
    def temperatur_data (self, stasjon):
        endpoint = 'https://frost.met.no/observations/v0.jsonld'
        intervaller = ['2021-01-01/2022-01-01', '2020-01-01/2021-01-01', '2019-01-01/2020-01-01', 
        '2018-01-01/2019-01-01', '2017-01-01/2018-01-01', '2016-01-01/2016-01-01', 
        '2015-01-01/2016-01-01', '2014-01-01/2015-01-01', '2013-01-01/2014-01-01', 
        '2012-01-01/2013-01-01', '2011-01-01/2012-01-01']
        
        intervaller = ['2021-01-01/2022-01-01', '2020-01-01/2021-01-01', '2019-01-01/2020-01-01', 
        '2018-01-01/2019-01-01', '2017-01-01/2018-01-01', '2016-01-01/2016-01-01', 
        '2015-01-01/2016-01-01', '2014-01-01/2015-01-01', '2013-01-01/2014-01-01', 
        '2012-01-01/2013-01-01', '2011-01-01/2012-01-01', '2010-01-01/2011-01-01', 
        '2009-01-01/2010-01-01', '2008-01-01/2009-01-01', '2007-01-01/2008-01-01', 
        '2006-01-01/2007-01-01', '2005-01-01/2006-01-01', '2004-01-01/2005-01-01', 
        '2003-01-01/2004-01-01', '2002-01-01/2003-01-01', '2001-01-01/2002-01-01', 
        '2000-01-01/2001-01-01', '1999-01-01/2000-01-01', '1998-01-01/1999-01-01', 
        '1997-01-01/1998-01-01', '1996-01-01/1997-01-01', '1995-01-01/1996-01-01', 
        '1994-01-01/1995-01-01', '1993-01-01/1994-01-01', '1992-01-01/1993-01-01', 
        '1991-01-01/1992-01-01']

        luftTemperaturSummert = 0
        teller = 0
        for intervall in intervaller: 
            try: 
                parameters = {
                    'sources' : stasjon,
                    'referencetime' : intervall,
                    'elements' : 'air_temperature',
                    'timeoffsets': 'PT0H',
                    'timeresolutions' : 'PT1H'}
                r = requests.get(endpoint, parameters, auth=(self.klient_id,''))
                temperaturData = r.json()['data']

                luftTemperatur = np.zeros (8760)
                for i, registrertData in enumerate (temperaturData):
                    if i == 8760: 
                        break
                    tidspunkt = registrertData['referenceTime']
                    if (tidspunkt [11] + tidspunkt [12] + ':00') == (tidspunkt [11] + tidspunkt [12] + tidspunkt [13] + tidspunkt [14] + tidspunkt [15]):
                        luftTemperatur [i] = (registrertData['observations'][0]['value'])     
                luftTemperatur = np.array (luftTemperatur) 
                luftTemperaturSummert += luftTemperatur
                teller += 1
                print ('Data')

            except:
                print ('Ingen data')
                continue
                
        if teller > 0:
            luftTemperatur = luftTemperaturSummert / teller
            gjennomsnittsTemperatur = sum (luftTemperatur) / 8760
        else:
            luftTemperatur = np.array ([0, 0])
            gjennomsnittsTemperatur = np.array ([0, 0])
        
        return luftTemperatur, gjennomsnittsTemperatur

class Profet:
    def __init__ (self, luft_temperatur):
        self.filplassering = "profet.xlsm"
        self.luft_temperatur = luft_temperatur
        self.profet_df = self.beregning ()
        
    def beregning (self):
        app = xw.App(visible=False)
        workBook = xw.Book (self.filplassering)
        sht = workBook.sheets [1]
        
        sht.range ('E4').value = [[self.luft_temperatur[i]] for i in range(0, len(self.luft_temperatur))]
        
        sht.range ('W4').value = 1
        
        makro = workBook.macro ("module1.main")
        makro()
        
        profet_df = sht.range ('A3').expand().options(pd.DataFrame).value
        
        workBook.close ()
        
        return profet_df
    
    def space_heating (self):
        return self.profet_df ['Space heating hourly [kW]'].to_numpy()
    
    def dhw (self):
        return self.profet_df ['DHW hourly [kW]'].to_numpy()

def frost_profet_beregning ():
    temp = Temperatur ()
    stasjonsliste = temp.stasjons_liste()
    df = pd.DataFrame(columns = ['Stasjon ID', 'Lat', 'Long', 'Temperatur per time', 'Gjennomsnittstemperatur', 'DHW per time', 'Space heating per time'])
    j = 0
    
    for i in range (11,500):
        stasjon_id = stasjonsliste.iat [i,1]
        stasjon_long = stasjonsliste.iat [i,2][0]
        stasjon_lat = stasjonsliste.iat [i,2][1]
        
        luft_temp, gjsnittstemp = temp.temperatur_data (stasjon_id)
        
        if sum (luft_temp) > 0:
            prof = Profet (luft_temp)
            space_heating = prof.space_heating ()
            dhw = prof.dhw ()
            
            df.loc[j] = [stasjon_id, stasjon_lat, stasjon_long, luft_temp, gjsnittstemp, dhw, space_heating]
            j += 1
        
    return df  


def to_csv (df):
    for i in range (0, len (df)):
        stasjon_id = df.iat [i,0]
        stasjon_lat = df.iat [i,1]
        stasjon_long = df.iat [i,2]
        temperatur_per_time = df.iat [i,3]
        dhw_per_time = df.iat [i,5]
        space_heating_per_time = df.iat [i,6]
        np.savetxt((r"C:\Users\magne.syljuasen\Progg\temperaturer\Filer\_" + stasjon_id + '_temperatur.csv'), temperatur_per_time, delimiter=',', fmt='%f', header='Data')
        #np.savetxt((r"C:\Users\magne.syljuasen\Progg\temperaturer\Filer\_" + stasjon_id + '_dhw.csv'), dhw_per_time, delimiter=',', fmt='%f', header='Data')
        np.savetxt((r"C:\Users\magne.syljuasen\Progg\temperaturer\Filer\_" + stasjon_id + '_romoppvarming.csv' ), space_heating_per_time, delimiter=',', fmt='%f', header='Data')
        
        with open('Stasjoner.csv', 'a') as f:
            f.write(stasjon_id + ',' + str (stasjon_lat) + ',' + str (stasjon_long) + '\n')
        
    f.close ()
    
def main ():
    df = frost_profet_beregning ()
    to_csv (df)

main()

def profet_app():
    st.title("PROFet")

    location = Location() 
    lat, long = location.address_to_coordinate(location.input())
    with st.expander("Juster posisjon"):
        lat = st.number_input('Breddegrad', value=lat, step=0.0001)
        long = st.number_input('Lengdegrad', value=long, step=0.0001)

    location.map(lat, long)
    st.markdown("---")


