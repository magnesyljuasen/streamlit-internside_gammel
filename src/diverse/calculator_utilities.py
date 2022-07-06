from bz2 import compress
import streamlit as st
import numpy as np
import pandas as pd
import altair as alt
from shapely.geometry import Point, shape
import json
#from annotated_text import annotated_text
import pydeck as pdk
import xlsxwriter
from io import BytesIO
from datetime import date


def hour_to_month (hourly_array):
    monthly_array = []
    summert = 0
    for i in range(0, len(hourly_array)):
        verdi = hourly_array[i]
        if np.isnan(verdi):
            verdi = 0
        summert = verdi + summert
        if i == 744 or i == 1416 or i == 2160 or i == 2880 \
                or i == 3624 or i == 4344 or i == 5088 or i == 5832 \
                or i == 6552 or i == 7296 or i == 8016 or i == 8759:
            monthly_array.append(int(summert))
            summert = 0
    return monthly_array  


class Prerequisites:
    def __init__(self):
        pass

    def show(self, address, energy):
        st.title("Resultater")
        st.write(f"📍{address} | ⚡Estimert oppvarmingsbehov: {round(energy, -1)} kWh")

    def disclaimer(self):
        st.markdown(""" **Resultatene fra bergvarmekalkulatoren er 
        estimater, og skal ikke brukes for endelig 
        dimensjonering av energibrønn med varmepumpe.** """)

        st.markdown(""" *_Trykk på boksene under for å se resultatene. 
        Du kan endre forutsetningene for beregningene i menyen til venstre._* """)
        
      
class Electricity:
    def __init__(self):
        self.region = str
        self.elspot_arr = np.array(0)
        self.elspot_average = float
        self.year = str
    
    def update(self):
        self.elspot_average = np.average(self.elspot_arr) 

    def import_file(self):
        with open('src/csv/regioner.geojson') as f:
            js = json.load(f)
        f.close()
        return js

    def find_region(self, lat, long):
        punkt = Point(long, lat)
        js = self.import_file()
        region = 'NO 1'
        for feature in js['features']:
            polygon = shape(feature['geometry'])
            if polygon.contains(punkt):
                region = feature['properties']['ElSpotOmr']
                if region == 'NO 1':
                    region = 'Sørøst-Norge (NO1)'
                if region == 'NO 2':
                    region = 'Sørvest-Norge (NO2)'
                if region == 'NO 3':
                    region = 'Midt-Norge (NO3)'
                if region == 'NO 4':
                    region = 'Nord-Norge (NO4)'
                if region == 'NO 5':
                    region = 'Vest-Norge (NO5)'
        self.region = region

    def input(self):
        with st.form("3"):
            self.elprice_average = st.number_input("Gjennomsnittlig strømpris (inkl. nettleie og andre avgifter) [kr/kWh]", 
            value = 1.1, min_value = 0.1, step = 0.1)
        
            submitted = st.form_submit_button("Oppdater")

    def calculation(self):
        diff = self.elprice_average - self.elspot_average
        if diff > 0:
            self.elprice_hourly = self.elspot_hourly + diff
        if diff < 0:
            self.elprice_hourly = self.elspot_hourly - diff
        if diff == 0:
            self.elprice_hourly = self.elspot_hourly

    def plot(self):
        x = np.arange(8760)
        source = pd.DataFrame({
        'x': x,
        'y': self.elprice_hourly})

        c = alt.Chart(source).mark_line().encode(
            x=alt.X('x', scale=alt.Scale(domain=[0,8760]), title=None),
            y=alt.Y('y', scale=alt.Scale(domain=[0,7]), title="Pris på strøm (kr/kWh)"),
            color = alt.value("#1d3c34"))
        st.altair_chart(c, use_container_width=True)


class Geology:
    def __init__(self):
        self.depth_to_bedrock = int
        self.lat = 5
        self.long = 10

    def adjust(self):
        self.depth_to_bedrock = st.number_input("Oppgi dybde til fjell [m]", min_value= 0, value=0, max_value=150, 
        help = "Dybde til fjell har stor lokal variasjon og bør sjekkes opp mot NGU sine databaser for grunnvannsbrønner og grunnundersøkelser.")

class Input:
    def __init__(self):
        self.lat = float
        self.long = float
        self.name = str
        self.area = int
        self.selected_zipcode = []
        self.zipcode()
        
    @st.cache
    def import_zipcode(self):
        zipcode_df = pd.read_csv('src/adresse/alle_postnummer.csv', sep=',', low_memory=False)
        return zipcode_df.iloc[:,1].to_numpy()

    def zipcode(self):
        zipcode_list = self.import_zipcode()
        zipcode_list = np.sort(zipcode_list)
        self.selected_zipcode = st.multiselect('📍 Skriv inn postnummer eller poststed', zipcode_list, 
        help=""" Adressen brukes til å hente inn nøyaktige temperaturdata 
        og nærliggende energibrønner. """)
        
    def process(self):
        selected = self.selected_zipcode
        if len(selected) > 1:
            st.error('Du må velge ett postnummer')
            st.stop()
        if selected:
            self.selected = selected[0] 
            self.find_address()
            if self.lat != float:      
                self.set_area()         

    @st.cache
    def import_address(self):
        filename = 'src/adresse/' + self.selected + '.csv'
        address_df = pd.read_csv(filename, sep=',', low_memory=False)
        return address_df, address_df.iloc[:,1].to_numpy()

    def find_address(self):
        address_df, address_list = self.import_address()
        address_list = np.sort(address_list)
        selected = st.multiselect('📍 Finn adresse', address_list, 
        help=""" Adressen brukes til å hente inn nøyaktige temperaturdata 
        og nærliggende energibrønner. """)
        if len(selected) > 1:
            st.error('Du må velge en adresse')
            st.stop()
        if len(selected) == 1:
            i=address_df[address_df['Navn']==selected[0]]
            self.long, self.lat, self.name = i.iat[0,3], i.iat[0,2], selected[0]

    def set_area(self):
        area_list = np.arange(100, 1000, 1, dtype=int)
        area_list_str = np.char.mod('%d m\u00b2', area_list)
        selected = st.multiselect('🏠 Tast inn oppvarmet boligareal', area_list_str, 
        help=""" Oppvarmet bruksareal er den delen av 
        bruksarealet (BRA) som tilføres varme fra bygnings varmesystem. """)
        if len(selected) > 1:
            st.error('Du må velge ett areal')
            st.stop()
        if len(selected) == 1:
            self.area = int(selected[0].split()[0])

        #self.area = st.number_input('Oppgi oppvarmet areal [m\u00b2]', min_value=100, value=150, max_value=1000, step=10, 
        #help='Oppvarmet bruksareal er den delen av bruksarealet (BRA) som tilføres varme fra bygnings varmesystem')


class Demand:
    def __init__(self):
        self.space_heating_arr = np.zeros(8760)
        self.dhw_arr = np.zeros(8760)
        self.energy_arr = np.zeros(8760)
        self.space_heating_sum = int
        self.dhw_sum = int
        self.energy_sum = int
    
    def update(self):
        self.space_heating_sum = int(np.sum(self.space_heating_arr))
        self.dhw_sum = int(np.sum(self.dhw_arr))
        self.energy_sum = int(np.sum(self.energy_arr))

    def from_file(self, area, weather_station_id):
        factor = 1
        dhw = 'src/database/' + 'SN180' + '_dhw.csv'
        space_heating = 'src/temperature/_' + weather_station_id + '_romoppvarming.csv'
        self.dhw_arr = (pd.read_csv(dhw, sep=',', on_bad_lines='skip').to_numpy() * area) * factor
        self.space_heating_arr = (pd.read_csv(space_heating, sep=',', on_bad_lines='skip').to_numpy() * area) * factor
        self.energy_arr = self.dhw_arr + self.space_heating_arr

    def plot(self):
        dhw_arr = hour_to_month (self.dhw_arr)
        romoppvarming_arr = hour_to_month (self.space_heating_arr)
        months = ['jan', 'feb', 'mar', 'apr', 'mai', 'jun', 'jul', 'aug', 'sep', 'okt', 'nov', 'des']
        data = pd.DataFrame({'Måneder' : months, 'Romoppvarmingsbehov' : romoppvarming_arr, 'Varmtvannsbehov' : dhw_arr, })
        c = alt.Chart(data).transform_fold(
            ['Romoppvarmingsbehov', 'Varmtvannsbehov'],
            as_=['Forklaring', 'Oppvarmingsbehov (kWh)']).mark_bar().encode(
            x=alt.X('Måneder:N', sort=months, title=None),
            y='Oppvarmingsbehov (kWh):Q',
            color=alt.Color('Forklaring:N', scale=alt.Scale(domain=['Romoppvarmingsbehov', 'Varmtvannsbehov'], 
            range=['#4a625c', '#8e9d99']), legend=alt.Legend(orient='top', direction='vertical', title=None)))
        st.altair_chart(c, use_container_width=True)

    def adjust(self):
        with st.form('1'):
            dhw_sum = self.dhw_sum
            dhw_sum_new = st.number_input('Varmtvann [kWh]', min_value = int(round(dhw_sum - dhw_sum/2, -1)), 
            max_value = int(round(dhw_sum + dhw_sum/2, -1)), value = round(dhw_sum, -1), step = int(500), help="""
            Erfaring viser at varmtvannsbehovet er avhengig av antall forbrukere og bør justeres etter dette. 
            Bor det mange i boligen bør det altså justeres opp. """)

            space_heating_sum = self.space_heating_sum
            space_heating_sum_new = st.number_input('Romoppvarming [kWh]', min_value = int(round(space_heating_sum - space_heating_sum/2, -1)), 
            max_value = int(round(space_heating_sum + space_heating_sum/2, -1)), value = round(space_heating_sum, -1), step = int(500), help= """
            Romoppvarmingsbehovet er beregnet basert på oppgitt oppvarmet areal og temperaturdata fra nærmeste værstasjon
            for de 30 siste år. """)
            dhew_percentage = dhw_sum_new / dhw_sum
            romoppvarming_prosent = space_heating_sum_new / space_heating_sum

            self.dhw_arr = (self.dhw_arr * dhew_percentage).flatten()
            self.space_heating_arr = (self.space_heating_arr * romoppvarming_prosent).flatten()
            self.energy_arr = (self.dhw_arr + self.space_heating_arr).flatten()
            submitted = st.form_submit_button("Oppdater")
    #---


class Groundsource:
    def __init__(self):
        self.coverage = int
        self.cop = float
        self.energy_gshp_arr = np.array(0)
        self.energy_gshp_sum = int
        self.heat_pump_size = float
    
    def update(self):
        self.energy_sum = int(np.sum(self.energy_arr))

    def adjust(self):
        with st.form("2"):    
            self.coverage = st.number_input("Energidekningsgrad for bergvarme [%]", 
            value=100, min_value=80, max_value=100, step = 1, 
            help="""Vanligvis settes dekningsgraden til 100% 
            som betyr at bergvarmeanlegget skal dekke hele energibehovet. 
            Dersom dekningsgraden er mindre enn dette skal energikilder 
            som vedfyring eller strøm dekke behovet de kaldeste dagene.""")
            
            self.cop = st.number_input("Årsvarmefaktor (SCOP) til varmepumpen", 
            value=3.0, min_value=2.0, max_value=4.0, step = 0.1, 
            help="""Årsvarmefaktoren avgjør hvor mye energi du sparer 
            med et varmepumpeanlegg; den uttrykker hvor mye varmeenergi 
            anlegget leverer i forhold til hvor mye elektrisk energi 
            det bruker i løpet av et år.""")

            submitted = st.form_submit_button("Oppdater")

    def demands(self, energy_arr):
        self.energy_arr = energy_arr
        self.update()

    def temperature(self, undisturbed_temperature):
        self.undisturbed_temperature = undisturbed_temperature

    def calculation(self):
        self.energy_gshp_arr, self.energy_gshp_sum, self.heat_pump_size = self.coverage_calculation()
        self.heat_pump_size_adjustment()
        self.energy_gshp_delivered_arr, self.energy_gshp_compressor_arr, self.energy_gshp_peak_arr, \
        self.energy_gshp_delivered_sum, self.energy_gshp_compressor_sum, self.energy_gshp_peak_sum = self.cop_calculation()
        self.meter = self.meter_calculation()
        self.number_of_wells = self.wellnumber_calculation()

    @st.cache
    def coverage_calculation(self):
        coverage = self.coverage
        energy_arr = self.energy_arr
        energy_sum = self.energy_sum
        heat_pump_size = max(energy_arr)
        calculated_coverage = 100.5
        if coverage == 100:
            return np.array(energy_arr), int(np.sum(energy_arr)), float("{:.1f}".format(heat_pump_size))

        while (calculated_coverage / coverage) > 1:
            tmp_list = np.zeros (8760)
            for i, effect in enumerate (energy_arr):
                if effect > heat_pump_size:
                    tmp_list[i] = heat_pump_size
                else:
                    tmp_list[i] = effect
            
            calculated_coverage = (sum (tmp_list) / energy_sum) * 100
            heat_pump_size -= 0.05

        return np.array(tmp_list), int(np.sum(tmp_list)), float("{:.1f}".format(heat_pump_size))

    def cop_calculation(self):
        cop = self.cop
        energy_arr = self.energy_arr
        energy_gshp_arr = self.energy_gshp_arr
        energy_gshp_delivered_arr = energy_gshp_arr - energy_gshp_arr / cop
        energy_gshp_compressor_arr = energy_gshp_arr - energy_gshp_delivered_arr
        energy_gshp_peak_arr = energy_arr - energy_gshp_arr

        energy_gshp_delivered_sum = int(np.sum(energy_gshp_delivered_arr))
        energy_gshp_compressor_sum = int(np.sum(energy_gshp_compressor_arr))
        energy_gshp_peak_sum = int(np.sum(energy_gshp_peak_arr))

        return energy_gshp_delivered_arr, energy_gshp_compressor_arr, energy_gshp_peak_arr, energy_gshp_delivered_sum, energy_gshp_compressor_sum, energy_gshp_peak_sum

    def meter_calculation(self):
        temperature = self.undisturbed_temperature
        kWh_per_meter = 0.0011*temperature**4 - 0.0537*temperature**3 + 1.0318*temperature**2 + 6.2816*temperature + 36.192
        upper_limit = 110
        lower_limit = 70
        if kWh_per_meter > upper_limit:
            kWh_per_meter = upper_limit
        if kWh_per_meter < lower_limit:
            kWh_per_meter = lower_limit
        self.kWh_per_meter = kWh_per_meter
        return int(self.energy_gshp_delivered_sum / kWh_per_meter)

    def wellnumber_calculation(self):
        meters = self.meter
        bronnlengde = 0
        for i in range(1,10):
            bronnlengde += 350
            if meters <= bronnlengde:
                return i

    def heat_pump_size_adjustment(self):
        heat_pump_size = self.heat_pump_size

        if heat_pump_size > 0 and heat_pump_size < 6:
            heat_pump_size = 6
        if heat_pump_size > 6 and heat_pump_size < 8:
            heat_pump_size = 8
        if heat_pump_size > 8 and heat_pump_size < 10:
            heat_pump_size = 10
        if heat_pump_size > 10 and heat_pump_size < 12:
            heat_pump_size = 12
        if heat_pump_size > 12 and heat_pump_size < 15:
            heat_pump_size = 15
        if heat_pump_size > 14 and heat_pump_size > 17:
            heat_pump_size = 17

        self.heat_pump_size = heat_pump_size

    def diagram(self):
        wide_form = pd.DataFrame({
            'Varighet (timer)' : np.array(range(0, len(self.energy_arr))),
            'Spisslast (ikke bergvarme)' : np.sort(self.energy_arr)[::-1], 
            'Levert energi fra brønn(er)' : np.sort(self.energy_gshp_arr)[::-1],
            'Strømforbruk varmepumpe' : np.sort(self.energy_gshp_compressor_arr)[::-1]
            })

        c = alt.Chart(wide_form).transform_fold(
            ['Spisslast (ikke bergvarme)', 'Levert energi fra brønn(er)', 'Strømforbruk varmepumpe'],
            as_=['key', 'Effekt (kW)']).mark_area().encode(
                x=alt.X('Varighet (timer):Q', scale=alt.Scale(domain=[0, 8760])),
                y='Effekt (kW):Q',
                color=alt.Color('key:N', scale=alt.Scale(domain=['Spisslast (ikke bergvarme)', 'Levert energi fra brønn(er)', 'Strømforbruk varmepumpe'], 
                range=['#ffdb9a', '#48a23f', '#1d3c34']), legend=alt.Legend(orient='top', direction='vertical', title=None))
            )

        st.altair_chart(c, use_container_width=True)

    def show_results(self):
        st.subheader("Dimensjonering")
        number_of_wells = self.number_of_wells
        meters = self.meter
        heat_pump_size = self.heat_pump_size
        text = " brønn"
        text1 = " energibrønn"
        text2 = "dybde"
        if number_of_wells > 1:
            text = " brønner" 
            text1 = " energibrønner"
            text2 = "total dybde"

        st.write(f""" Vi har beregnet et bergvarmeanlegg for din bolig. Et bergvarmeanlegg består av en
        energibrønn og varmepumpe. """)

        st.write(""" *Den største usikkerheten i beregningen er oppvarmingsbehovet. Du kan justere
        dette i menyen til venstre f.eks. ut ifra målt strømforbruk til oppvarming i din bolig. Endelig
        dimensjonering av energibrønn og varmepumpe skal utføres av leverandør basert 
        på reellt oppvarmingsbehov og stedlige geologiske forhold.* """)

        
        column_1, column_2, column_3 = st.columns(3)
        with column_1:
            st.metric(label="Brønndybde", value=str(meters) + " m")
        with column_2:
            st.metric(label='Antall energibrønner', value = str(number_of_wells) + text)
        with column_3:
            st.metric(label="Varmepumpestørrelse", value=str(heat_pump_size) + " kW")

class Costs:
    def __init__(self):
        pass

    def calculate_investment (self, heat_pump_size, meter, depth_to_bedrock):
        heat_pump_price = 141000
        
        if heat_pump_size > 12:
            heat_pump_price = int(heat_pump_price + (heat_pump_size - 12) * 10000)
        
        graving_pris = 30000
        rigg_pris = 15000
        etablering_pris = 3500
        odex_sko_pris = 575
        bunnlodd_pris = 1000
        lokk_pris = 700
        odex_i_losmasser_pris = 700  # per meter
        fjellboring_pris = 170  # per meter
        kollektor_pris = 90  # per meter

        kollektor = (meter - 1) * kollektor_pris
        boring = ((meter - depth_to_bedrock) * fjellboring_pris) + (depth_to_bedrock * odex_i_losmasser_pris)
        boring_faste_kostnader = etablering_pris + odex_sko_pris + bunnlodd_pris + lokk_pris + rigg_pris + graving_pris

        energibronn_pris = int(kollektor) + int(boring) + int(boring_faste_kostnader)
        komplett_pris = energibronn_pris + heat_pump_price
        self.investment = int(komplett_pris)

    def adjust(self):
        with st.form("5"):
            investment = self.investment
            self.investment = st.number_input("Juster investeringskostnad [kr]", 
            min_value = 10000, value = int(round(investment,-1)), 
            max_value = 1000000, step = 5000)
            self.interest = st.number_input("Juster effektiv rente [%]", value = 2.44, min_value = 1.0, max_value = 20.0)
            submitted = st.form_submit_button("Oppdater")

    def calculate_monthly_costs(self, energy_arr, compressor_arr, peak_arr, elprice_arr, investment, repayment_period):
        instalment = 0
        if investment != 0:
            monthly_antall = repayment_period * 12
            monthly_rente = (self.interest/100) / 12
            instalment = investment / ((1 - (1 / (1 + monthly_rente) ** monthly_antall)) / monthly_rente)

        el_cost_hourly = energy_arr * elprice_arr
        gshp_cost_hourly = (compressor_arr + peak_arr) * elprice_arr

        self.el_cost_monthly = np.array(hour_to_month(el_cost_hourly))
        self.gshp_cost_monthly = np.array(hour_to_month(gshp_cost_hourly)) + instalment

        self.el_cost_sum = np.sum(self.el_cost_monthly)
        self.gshp_cost_sum = np.sum(self.gshp_cost_monthly)
        self.savings_sum = self.el_cost_sum - self.gshp_cost_sum

    def plot(self, kostnad):
        gshp_text_1 = "Bergvarme"        
        gshp_text_2 = f"{kostnad}: " + str(int(round(self.gshp_cost_sum, -1))) + " kr/år"
        el_text_1 = "Elektrisk oppvarming"
        el_text_2 = f"{kostnad}: " + str(int(round(self.el_cost_sum, -1))) + " kr/år"
        
        months = ['jan', 'feb', 'mar', 'apr', 'mai', 'jun', 'jul', 'aug', 'sep', 'okt', 'nov', 'des']
        wide_form = pd.DataFrame({
            'Måneder' : months,
            gshp_text_1 : self.gshp_cost_monthly, 
            el_text_1 : self.el_cost_monthly})

        c1 = alt.Chart(wide_form).transform_fold(
            [gshp_text_1, el_text_1],
            as_=['key', 'Kostnader (kr)']).mark_bar(opacity=1).encode(
                x=alt.X('Måneder:N', sort=months, title=None),
                y=alt.Y('Kostnader (kr):Q',stack=None),
                color=alt.Color('key:N', scale=alt.Scale(domain=[gshp_text_1], 
                range=['#48a23f']), legend=alt.Legend(orient='top', 
                direction='vertical', title=gshp_text_2))).configure_view(strokeWidth=0)

        c2 = alt.Chart(wide_form).transform_fold(
            [gshp_text_1, el_text_1],
            as_=['key', 'Kostnader (kr)']).mark_bar(opacity=1).encode(
                x=alt.X('Måneder:N', sort=months, title=None),
                y=alt.Y('Kostnader (kr):Q',stack=None, title=None),
                color=alt.Color('key:N', scale=alt.Scale(domain=[el_text_1], 
                range=['#880808']), legend=alt.Legend(orient='top', 
                direction='vertical', title=el_text_2))).configure_view(strokeWidth=0)

        col1, col2 = st.columns(2)
        with col1:
            st.altair_chart(c1, use_container_width=True)  
        with col2:
            st.altair_chart(c2, use_container_width=True) 

    def operation_show(self):
        st.subheader("Drift") 
        st.write("""Figuren under viser årlige driftskostnader 
        med bergvarme kontra elektrisk oppvarming. I dette regnestykket er 
        ikke investeringskostnaden inkludert. Bergvarme gir en god strømbesparelse 
        som reduserer din månedlige strømregning. """)

    def operation_show_after(self):
        value=(round(self.savings_sum, -1))
        st.metric(label="Driftsbesparelse med bergvarme", value=(str(int(round(self.savings_sum, -1))) + " kr/år"))        
        #annotated_text("Driftsbesparelse med bergvarme: ", 
        #(f"{value} kr", "per år", "#b7dc8f"))


    def operation_and_investment_show(self):
        st.subheader("Investering og drift over 20 år")
        st.write(f""" Figuren under viser årlige kostnader til oppvarming inkl. investeringskostnad. 
        Det er forutsatt at investeringen nedbetales i løpet av 20 år med en effektiv rente på {round(self.interest,2)} %.""")

    def operation_and_investment_after(self):
        if self.profitibality() == False:
            text1 = "Besparelse med bergvarme: "
            savings1 = int(round(self.savings_sum, -1))
            text2 = "Akkumulert besparelse med bergvarme etter 20 år"
            savings2 = int(round(self.savings_sum*20, -1))

            #annotated_text(text1,
            #(f"{savings1} kr", "per år", "#d0e8b6"), "   ", 
            #(f"{savings2} kr", "etter 20 år", "#b7dc8f"))

            
            
            st.metric(label=text1, value=(str(int(round(self.savings_sum, -1))) + " kr/år"))
            st.metric(label=text2, value=(str(int(round(self.savings_sum * 20, -1))) + " kr"))

    def investment_show(self):
        st.subheader("Investeringskostnad") 
        st.write(""" Investeringskostnaden omfatter en komplett installsjon av 
        bergvarme inkl. varmepumpe, montering og energibrønn. 
        Merk at dette er et estimat, og endelig pris må fastsettes av leverandør. """)
        st.metric(label="Investeringskostnad", value=(str(int(round(self.investment, -1))) + " kr"))

    def profitibality(self):
        if self.savings_sum < 0:
            st.warning("Bergvarme er ikke lønnsomt etter 20 år med oppgitte forutsetninger.")
            return True 
        return False 


class Environment:
    def __init__(self):
        self.co2_per_kwh = float 

    def adjust(self):
        options = ['Norsk energimiks', 'Norsk-europeisk energimiks', 'Europeisk energimiks ']
        selected = st.selectbox('Velg energimiks for produksjon av strøm', options, index=1) 
        if selected == options[0]:
            self.co2_per_kwh = 16.2
        elif selected == options[1]:
            self.co2_per_kwh = 116.93
        elif selected == options[2]:
            self.co2_per_kwh = 123

        st.write(f"{round(self.co2_per_kwh, 1)} gram CO\u2082-ekvivalenter per kWh")

    #i kilogram 
    def calculate_emissions(self, energy_arr, compressor_arr, peak_arr):
        co2_constant = self.co2_per_kwh/1000
        el_co2_hourly = energy_arr * co2_constant
        gshp_co2_hourly = (compressor_arr + peak_arr) * co2_constant

        self.el_co2_monthly = np.array(hour_to_month(el_co2_hourly))
        self.gshp_co2_monthly = np.array(hour_to_month(gshp_co2_hourly))

        self.el_co2_sum = np.sum(self.el_co2_monthly) * 20
        self.gshp_co2_sum = np.sum(self.gshp_co2_monthly) * 20
        self.savings_co2_sum = (self.el_co2_sum - self.gshp_co2_sum)
    
    def plot(self):
        gshp = round(self.gshp_co2_sum/1000)
        el = round(self.el_co2_sum/1000)
        savings = round(self.savings_co2_sum/1000)

        #--1
        source = pd.DataFrame({"label" : [f'Utslipp: {gshp} tonn CO\u2082', f'Grønn energi'], 
        "value": [gshp, savings]})
        c1 = alt.Chart(source).mark_arc(innerRadius=35).encode(
            theta=alt.Theta(field="value", type="quantitative"),
            color=alt.Color(field="label", type="nominal", scale=alt.Scale(range=['#48a23f', '#a23f47']), 
            legend=alt.Legend(orient='top', direction='vertical', title=f'Bergvarme'))).configure_view(strokeWidth=0)
            
        #--2
        source = pd.DataFrame({"label" : [f'Utslipp: {el} CO\u2082'], 
        "value": [el]})
        c2 = alt.Chart(source).mark_arc(innerRadius=35).encode(
            theta=alt.Theta(field="value", type="quantitative"),
            color=alt.Color(field="label", type="nominal", scale=alt.Scale(range=['#a23f47']), 
            legend=alt.Legend(orient='top', direction='vertical', title='Elektrisk oppvarming'))).configure_view(strokeWidth=0)
        
        col1, col2 = st.columns(2)
        with col1:
            st.altair_chart(c1, use_container_width=True)
        with col2:
            st.altair_chart(c2, use_container_width=True) 
        
    def text_before(self):
        savings = round(self.savings_co2_sum/1000)
        flights = round(savings/(103/1000))

        st.subheader("Klimagassutslipp etter 20 år")
        st.write(f""" Vi har beregnet klimagassutslipp for bergvarme sammenlignet med elektrisk oppvarming. 
        Figuren under viser at du i løpet av 20 år sparer {savings} tonn CO\u2082. 
        Dette tilsvarer **{flights} flyreiser** mellom Oslo - Trondheim. """) 

    def text_after(self):
        savings = round(self.savings_co2_sum/1000)
        #st.markdown(f"Besparelse med bergvarme: **{savings} tonn CO\u2082**")
        #annotated_text("Utslippskutt med bergvarme: ", (f"{savings} tonn CO\u2082", "etter 20 år", "#b7dc8f"))
        #'#ffdb9a', '#48a23f', '#1d3c34'
        st.metric(label="Utslippskutt med bergvarme etter 20 år", value=str(savings) + " tonn CO\u2082")

class Gis:
    def __init__(self):
        pass

    def kart(self, stasjon_lat, adresse_lat, energibronn_lat, stasjon_long, adresse_long, energibronn_long):
        df1 = pd.DataFrame({'latitude': [stasjon_lat],'longitude': [stasjon_long]})
        df2 = pd.DataFrame({'latitude': [adresse_lat],'longitude': [adresse_long]})
        df3 = pd.DataFrame({'latitude': [energibronn_lat],'longitude': [energibronn_long]})
    
        st.pydeck_chart(pdk.Deck(
            map_style='mapbox://styles/mapbox/streets-v11',
            initial_view_state=pdk.ViewState(
                latitude=adresse_lat,
                longitude=adresse_long,
                pitch=0,
            ),
            layers=[
                pdk.Layer(
                    type='ScatterplotLayer',
                    data=df1,
                    get_position='[longitude, latitude]',
                    pickable=True,
                    stroked=True,
                    radius_max_pixels=10,
                    radius_min_pixels=500,
                    filled=True,
                    line_width_scale=25,
                    line_width_max_pixels=5,
                    get_fill_color=[255, 195, 88],
                    get_line_color=[0, 0, 0]
                ),
                pdk.Layer(
                    type='ScatterplotLayer',
                    data=df2,
                    get_position='[longitude, latitude]',
                    pickable=True,
                    stroked=True,
                    radius_max_pixels=20,
                    radius_min_pixels=500,
                    filled=True,
                    line_width_scale=25,
                    line_width_max_pixels=5,
                    get_fill_color=[29, 60, 52],
                    get_line_color=[29, 60, 52],
                ),
                pdk.Layer(
                    type='ScatterplotLayer',
                    data=df3,
                    get_position='[longitude, latitude]',
                    pickable=True,
                    stroked=True,
                    radius_max_pixels=10,
                    radius_min_pixels=500,
                    filled=True,
                    line_width_scale=25,
                    line_width_max_pixels=5,
                    get_fill_color=[183, 220, 143],
                    get_line_color=[0, 0, 0]
                ),
            ],
        ))


class PDF(FPDF):
        def header(self):
            # Logo
            self.image('src/bilder/egen_logo3.PNG', 10, 8, 33)
            # Arial bold 15
            self.set_font('Arial', 'B', 15)
            # Move to the right
            self.cell(80)
            # Title
            self.cell(30, 10, 'Resultater', 0, 0)
            # Line break
            self.ln(20)

        # Page footer
        def footer(self):
            # Position at 1.5 cm from bottom
            self.set_y(-15)
            # Arial italic 8
            self.set_font('Arial', 'I', 8)
            # Page number
            self.cell(0, 10, 'Side ' + str(self.page_no()) + '/{nb}', 0, 0, 'C')

def download_report(average_temperature, weather_station_id, space_heating_sum, 
dhw_sum, kWh_per_meter, energy_gshp_delivered_sum, energy_gshp_compressor_sum, 
energy_gshp_peak_sum, cop, coverage, region, elprice_average):
    
    # Instantiation of inherited class
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('Times', '', 12)
    lines = [
    f"Innhentet fra kart",
    f"- Årsmiddeltemperatur: {average_temperature} °C (år 1991 - 2020 fra værstasjon {weather_station_id})",
    f"- Strømregion: {region}",
    f"- Energi fra grunnen: {int(kWh_per_meter)} kWh per meter brønn "
    f"",
    f"Estimert energibehov",
    f"- Romoppvarming: {int(space_heating_sum)} kWh ",
    f"- Varmtvann: {int(dhw_sum)} kWh ",
    f"- Totalt energibehov: {int(space_heating_sum + dhw_sum)} kWh",
    f"",
    f"Ditt bergvarmeanlegg",
    f"- Årsvarmefaktor (SCOP): {float((cop))}",
    f"- Energidekningsgrad for bergvarme: {int(coverage)} %",
    f"- Levert energi fra grunnen: {energy_gshp_delivered_sum} kWh",
    f"- Strømforbruk varmepumpe: {energy_gshp_compressor_sum} kWh",
    f"- Spisslast (dekkes ikke av bergvarme): {energy_gshp_peak_sum} kWh",
    

    f"- Totalkostnad for strøm: {float(elprice_average)} kr/kWh"
    ]

    for index, value in enumerate(lines):
        pdf.cell(0, 10, str(value), 0, 1)


    st.download_button(
        "📈 Last ned resultater (PDF)",
        data=pdf.output(dest='S').encode('latin-1'),
        file_name="Resultater.pdf",
    )

        



