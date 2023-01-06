import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from scipy.constants import pi
import pygfunction as gt
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib as mpl
from cycler import cycler
import numpy as np
from scipy.constants import pi
import altair as alt
import pygfunction as gt
import pandas as pd
from scripts._utils import Plotting
from datetime import datetime
import matplotlib.dates as mdates
plt.rcParams["figure.figsize"] = (10,5)
from scripts._pygfunction import Simulation

class EnergyAnalysis:
    def __init__(self):
        st.button("Refresh")
        self._import_dataframe()
        #self._plot_arr("Romoppvarmingsbehov", self.space_heating_arr, Plotting().FOREST_GREEN)
        #self._plot_arr("Tappevannsbehov", self.dhw_arr, '#607670')
        #self._plot_arr("Termisk energibehov", self.thermal_arr, Plotting().FOREST_GREEN)
        #self._plot_arr("Elektrisk energibehov", self.electric_arr, Plotting().SUN_YELLOW)
        ##self._plot_thermal_arr()
        ##self._plot_space_heating_arr()
        ##self._plot_dhw_arr()
        ##self._plot_electric_arr()
        st.markdown("---")
        self._plot_geoenergy()
        ##self._plot_solar_production()
        ##self._plot_geoenergy_solar()
        ##self._plot_district_heating()
        
        #self._plot_geoenergy_coverage()
        #self._plot_effect_diagram()
        #self._plot_arr("Grunnvarmeproduksjon", self.coverage_arr, Plotting().FOREST_GREEN)
        #self._plot_arr("Solenergiproduksjon", self.solar_arr, Plotting().SUN_YELLOW)
        #self._plot_solar_geoenergy()
        #self._plot_arr("Sammenstilt elektrisk energibehov inkl. grunnvarme", self.electric_arr + self.compressor_arr + self.peak_arr, Plotting().SUN_YELLOW)
        #self._plot_arr("Sammenstilt elektrisk energibehov inkl. grunnvarme og solcelleproduksjon", self.electric_arr + self.compressor_arr + self.peak_arr - self.solar_arr, Plotting().SUN_YELLOW)
        #self._plot_arr("Spisslast", self.peak_arr, Plotting().FOREST_GREEN)
        #self._plot_arr("Spisslastreduksjon med solceller", self.peak_arr - self.solar_arr, Plotting().FOREST_GREEN)
        self._peakshaving()
        self._plot_peakshaving_arr()
        #self._winterweek(self.thermal_arr)
        ##self._plot_distric_heating_and_geoenergy()

    def _import_dataframe(self):
        df = pd.read_csv("src\data\input\yrkesskolevegen.csv", sep=";")
        self.electric_arr = df["Elektrisk"]
        self.space_heating_arr = df["Romoppvarming"]
        self.dhw_arr = df["Tappevann"]
        self.thermal_arr = self.space_heating_arr + self.dhw_arr
        self.solar_arr = df["Solenergi"]

    def _plot_peakshaving_arr(self):

        date_1, date_2 = np.datetime64("2021-01-01T00"), np.datetime64("2022-01-01T00")
        #--
        x = np.arange(date_1, date_2, dtype='datetime64')
        y1 = self.peak_arr

        mpl.rcParams['axes.prop_cycle'] = cycler(color=['#1d3c34'])
        plt.stackplot(x,y1, labels=[f'Spisslast: {int(np.sum(y1)):,} kWh | {int(max(y1)):,} kW'.replace(',', ' ')])
        plt.legend(loc='best')
        myFmt = mdates.DateFormatter('%d.%m')
        plt.gca().xaxis.set_major_formatter(myFmt)
        plt.xlabel("Timer i ett år")
        plt.ylabel("Effekt [kW]")
        plt.grid(color='black', linestyle='--', linewidth=0.1)
        plt.xlim([date_1, date_2])
        st.pyplot(plt)
        plt.close()
        
        #--

        x = np.arange(date_1, date_2, dtype='datetime64')
        y1 = self.peakshaving_arr

        mpl.rcParams['axes.prop_cycle'] = cycler(color=['#1d3c34'])
        plt.stackplot(x,y1, labels=[f'Spisslast: {int(np.sum(y1)):,} kWh | {int(max(y1)):,} kW'.replace(',', ' ')])
        plt.legend(loc='best')
        myFmt = mdates.DateFormatter('%d.%m')
        plt.gca().xaxis.set_major_formatter(myFmt)
        plt.xlabel("Timer i ett år")
        plt.ylabel("Effekt [kW]")
        plt.grid(color='black', linestyle='--', linewidth=0.1)
        plt.xlim([date_1, date_2])
        st.pyplot(plt)
        plt.close()

    def _plot_thermal_arr(self):
        date_1, date_2 = np.datetime64("2021-01-01T00"), np.datetime64("2022-01-01T00")

        x = np.arange(date_1, date_2, dtype='datetime64')
        y1, y2 = self.dhw_arr, self.space_heating_arr

        mpl.rcParams['axes.prop_cycle'] = cycler(color=['#778a85', '#1d3c34'])
        plt.stackplot(x,y1, y2, labels=[f'Tappevann: {int(np.sum(y1)):,} kWh | {int(max(y1)):,} kW'.replace(',', ' '),f'Romoppvarming: {int(np.sum(y2)):,} kWh | {int(max(y2)):,} kW'.replace(',', ' ')])
        plt.legend(loc='best')
        myFmt = mdates.DateFormatter('%d.%m')
        plt.gca().xaxis.set_major_formatter(myFmt)
        plt.xlabel("Timer i ett år")
        plt.ylabel("Effekt [kW]")
        plt.grid(color='black', linestyle='--', linewidth=0.1)
        
        plt.xlim([date_1, date_2])
        st.pyplot(plt)
        plt.close()

    def _plot_space_heating_arr(self):
        date_1, date_2 = np.datetime64("2021-01-01T00"), np.datetime64("2022-01-01T00")

        x = np.arange(date_1, date_2, dtype='datetime64')
        y1 = self.space_heating_arr

        mpl.rcParams['axes.prop_cycle'] = cycler(color=['#1d3c34'])
        plt.stackplot(x,y1, labels=[f'Romoppvarming: {int(np.sum(y1)):,} kWh | {int(max(y1)):,} kW'.replace(',', ' ')])
        plt.legend(loc='best')
        myFmt = mdates.DateFormatter('%d.%m')
        plt.gca().xaxis.set_major_formatter(myFmt)
        plt.xlabel("Timer i ett år")
        plt.ylabel("Effekt [kW]")
        plt.grid(color='black', linestyle='--', linewidth=0.1)
        plt.xlim([date_1, date_2])
        st.pyplot(plt)
        plt.close()

    def _plot_dhw_arr(self):
        date_1, date_2 = np.datetime64("2021-01-01T00"), np.datetime64("2022-01-01T00")

        x = np.arange(date_1, date_2, dtype='datetime64')
        y1 = self.dhw_arr

        mpl.rcParams['axes.prop_cycle'] = cycler(color=['#778a85'])
        plt.stackplot(x,y1, labels=[f'Tappevann: {int(np.sum(y1)):,} kWh | {int(max(y1)):,} kW'.replace(',', ' ')])
        plt.legend(loc='best')
        myFmt = mdates.DateFormatter('%d.%m')
        plt.gca().xaxis.set_major_formatter(myFmt)
        plt.xlabel("Timer i ett år")
        plt.ylabel("Effekt [kW]")
        plt.grid(color='black', linestyle='--', linewidth=0.1)
        plt.xlim([date_1, date_2])
        st.pyplot(plt)
        plt.close()

    def _plot_electric_arr(self):
        date_1, date_2 = np.datetime64("2021-01-01T00"), np.datetime64("2022-01-01T00")

        x = np.arange(date_1, date_2, dtype='datetime64')
        y1 = self.electric_arr

        mpl.rcParams['axes.prop_cycle'] = cycler(color=['#664e23'])
        plt.stackplot(x,y1, labels=[f'Elspesifikt: {int(np.sum(y1)):,} kWh | {int(max(y1)):,} kW'.replace(',', ' ')])
        plt.legend(loc='best')
        myFmt = mdates.DateFormatter('%d.%m')
        plt.gca().xaxis.set_major_formatter(myFmt)
        plt.xlabel("Timer i ett år")
        plt.ylabel("Effekt [kW]")
        plt.grid(color='black', linestyle='--', linewidth=0.1)
        plt.xlim([date_1, date_2])
        st.pyplot(plt)
        plt.close()

    def _plot_geoenergy(self):
        energy_arr = self.thermal_arr
        COP = 3.5
        COVERAGE = 90
        energy_sum = np.sum(energy_arr)
        heat_pump_size = max(energy_arr)
        reduction = heat_pump_size / 600
        calculated_coverage = 100.5
        if COVERAGE == 100:
            return np.array(energy_arr), int(np.sum(energy_arr)), float("{:.1f}".format(heat_pump_size))
        while (calculated_coverage / COVERAGE) > 1:
            tmp_list = np.zeros (8760)
            for i, effect in enumerate (energy_arr):
                if effect > heat_pump_size:
                    tmp_list[i] = heat_pump_size
                else:
                    tmp_list[i] = effect
            calculated_coverage = (sum (tmp_list) / energy_sum) * 100
            heat_pump_size -= reduction
        self.coverage_arr = np.array(tmp_list)
        self.heat_pump_size = float("{:.1f}".format(heat_pump_size))

        self.delivered_from_wells_arr = self.coverage_arr - self.coverage_arr / COP
        #np.savetxt('to_simulation.csv', self.delivered_from_wells_arr, delimiter=',')
        self.compressor_arr = self.coverage_arr - self.delivered_from_wells_arr
        self.peak_arr = energy_arr - self.coverage_arr
        #--
        date_1, date_2 = np.datetime64("2021-01-01T00"), np.datetime64("2022-01-01T00")

        x = np.arange(date_1, date_2, dtype='datetime64')
        y1 = self.compressor_arr
        y2 = self.delivered_from_wells_arr
        y3 = self.peak_arr

        mpl.rcParams['axes.prop_cycle'] = cycler(color=['#997534', '#48a23f', '#cc9c46'])
        plt.stackplot(x,y1,y2,y3, labels=[f'Kompressor: {int(np.sum(y1)):,} kWh | {int(max(y1)):,} kW'.replace(',', ' '), f'Levert fra brønner: {int(np.sum(y2)):,} kWh | {int(max(y2)):,} kW'.replace(',', ' '), f'Spisslast: {int(np.sum(y3)):,} kWh | {int(max(y3)):,} kW'.replace(',', ' ')])
        plt.legend(loc='best')
        myFmt = mdates.DateFormatter('%d.%m')
        plt.gca().xaxis.set_major_formatter(myFmt)
        plt.xlabel("Timer i ett år")
        plt.ylabel("Effekt [kW]")
        plt.grid(color='black', linestyle='--', linewidth=0.1)
        plt.xlim([date_1, date_2])
        st.pyplot(plt)
        plt.close()
        #--
        date_1, date_2 = np.datetime64("2021-01-01T00"), np.datetime64("2022-01-01T00")
        x = np.arange(date_1, date_2, dtype='datetime64')
        y1, y2 = self.coverage_arr, self.peak_arr

        mpl.rcParams['axes.prop_cycle'] = cycler(color=['#b7dc8f', '#cc9c46'])
        plt.stackplot(x,y1, y2, labels=[f'Grunnvarme: {int(np.sum(y1)):,} kWh | {int(max(y1)):,} kW'.replace(',', ' '),f'Spisslast: {int(np.sum(y2)):,} kWh | {int(max(y2)):,} kW'.replace(',', ' ')])
        plt.legend(loc='best')
        myFmt = mdates.DateFormatter('%d.%m')
        plt.gca().xaxis.set_major_formatter(myFmt)
        plt.xlabel("Timer i ett år")
        plt.ylabel("Effekt [kW]")
        plt.grid(color='black', linestyle='--', linewidth=0.1)
        plt.xlim([date_1, date_2])
        st.pyplot(plt)
        plt.close()

    def _plot_solar_production(self):
        date_1, date_2 = np.datetime64("2021-01-01T00"), np.datetime64("2022-01-01T00")

        x = np.arange(date_1, date_2, dtype='datetime64')
        y1 = self.solar_arr

        mpl.rcParams['axes.prop_cycle'] = cycler(color=['#ffc358'])
        plt.stackplot(x,y1, labels=[f'Solenergiproduksjon: {int(np.sum(y1)):,} kWh | {int(max(y1)):,} kW'.replace(',', ' ')])
        plt.legend(loc='best')
        myFmt = mdates.DateFormatter('%d.%m')
        plt.gca().xaxis.set_major_formatter(myFmt)
        plt.xlabel("Timer i ett år")
        plt.ylabel("Effekt [kW]")
        plt.grid(color='black', linestyle='--', linewidth=0.1)
        plt.xlim([date_1, date_2])
        st.pyplot(plt)
        plt.close()

    def _plot_geoenergy_solar(self):
        date_1, date_2 = np.datetime64("2021-01-01T00"), np.datetime64("2022-01-01T00")

        x = np.arange(date_1, date_2, dtype='datetime64')
        y1 = self.compressor_arr
        y2 = self.electric_arr
        y3 = self.peak_arr

        mpl.rcParams['axes.prop_cycle'] = cycler(color=['#997534', '#664e23', '#cc9c46'])
        plt.stackplot(x,y1,y2,y3, labels=[f'Kompressor: {int(np.sum(y1)):,} kWh | {int(max(y1)):,} kW'.replace(',', ' '), f'Elspesifikt: {int(np.sum(y2)):,} kWh | {int(max(y2)):,} kW'.replace(',', ' '), f'Spisslast: {int(np.sum(y3)):,} kWh | {int(max(y3)):,} kW'.replace(',', ' ')])
        plt.legend(loc='best')
        myFmt = mdates.DateFormatter('%d.%m')
        plt.gca().xaxis.set_major_formatter(myFmt)
        plt.xlabel("Timer i ett år")
        plt.ylabel("Effekt [kW]")
        plt.grid(color='black', linestyle='--', linewidth=0.1)
        plt.xlim([date_1, date_2])
        st.pyplot(plt)
        plt.close()
        #--
        mpl.rcParams['axes.prop_cycle'] = cycler(color=['#664e23', '#664e23'])
        y1 = self.compressor_arr + self.electric_arr + self.peak_arr
        y2 = self.compressor_arr + self.electric_arr + self.peak_arr - self.solar_arr
        fig, (ax1, ax2) = plt.subplots(1, 2)
        fig.tight_layout()
        myFmt = mdates.DateFormatter('%d.%m')
        ax1.xaxis.set_major_formatter(myFmt)
        ax1.set_ylabel("Effekt (kW)")
        ax1.set_xlabel("Timer i ett år")
        ax1.set_xlim([date_1, date_2])
        ax1.stackplot(x, y1, labels=[f'{int(np.sum(y1)):,} kWh | {int(max(y1)):,} kW'.replace(',', ' ')])
        ax1.set_ylim([-200,800])
        ax1.set_title("Uten solproduksjon")
        ax1.legend()
        ax1.grid(color='black', linestyle='--', linewidth=0.1)
        ax2.stackplot(x, y2, labels=[f'{int(np.sum(y2)):,} kWh | {int(max(y2)):,} kW'.replace(',', ' ')])
        ax2.xaxis.set_major_formatter(myFmt)
        ax2.set_ylim([-200,800])
        ax2.set_xlabel("Timer i ett år")
        ax2.set_xlim([date_1, date_2])
        ax2.set_title(f'Med solproduksjon. Overskudd: {int(-np.where(y2<0,y2,0).sum(0)):,} kWh'.replace(',', ' '))
        ax2.legend()
        ax2.grid(color='black', linestyle='--', linewidth=0.1)
        st.pyplot(fig)
        
        plt.close()

    def _plot_district_heating(self):
        energy_arr = self.thermal_arr
        COVERAGE = 90
        energy_sum = np.sum(energy_arr)
        district_heating_effect = max(energy_arr)
        reduction = district_heating_effect / 600
        calculated_coverage = 100.5
        if COVERAGE == 100:
            return np.array(energy_arr), int(np.sum(energy_arr)), float("{:.1f}".format(district_heating_effect))
        while (calculated_coverage / COVERAGE) > 1:
            tmp_list = np.zeros (8760)
            for i, effect in enumerate (energy_arr):
                if effect > district_heating_effect:
                    tmp_list[i] = district_heating_effect
                else:
                    tmp_list[i] = effect
            calculated_coverage = (sum (tmp_list) / energy_sum) * 100
            district_heating_effect -= reduction
        self.district_heating_coverage_arr = np.array(tmp_list)
        self.district_heating_effect = float("{:.1f}".format(district_heating_effect))
        self.district_heating_peak_arr = energy_arr - self.district_heating_coverage_arr

        #--
        date_1, date_2 = np.datetime64("2021-01-01T00"), np.datetime64("2022-01-01T00")
        x = np.arange(date_1, date_2, dtype='datetime64')
        y1, y2 = self.district_heating_coverage_arr, self.district_heating_peak_arr

        mpl.rcParams['axes.prop_cycle'] = cycler(color=['#232927', '#cc9c46'])
        plt.stackplot(x,y1, y2, labels=[f'Fjernvarme: {int(np.sum(y1)):,} kWh | {int(max(y1)):,} kW'.replace(',', ' '),f'Spisslast: {int(np.sum(y2)):,} kWh | {int(max(y2)):,} kW'.replace(',', ' ')])
        plt.legend(loc='best')
        myFmt = mdates.DateFormatter('%d.%m')
        plt.gca().xaxis.set_major_formatter(myFmt)
        plt.xlabel("Timer i ett år")
        plt.ylabel("Effekt [kW]")
        plt.grid(color='black', linestyle='--', linewidth=0.1)
        plt.xlim([date_1, date_2])
        st.pyplot(plt)
        plt.close()

        #--
        mpl.rcParams['axes.prop_cycle'] = cycler(color=['#664e23', '#664e23'])
        y1 = self.district_heating_peak_arr + self.electric_arr
        y2 = self.district_heating_peak_arr + self.electric_arr - self.solar_arr
        fig, (ax1, ax2) = plt.subplots(1, 2)
        fig.tight_layout()
        myFmt = mdates.DateFormatter('%d.%m')
        ax1.xaxis.set_major_formatter(myFmt)
        ax1.set_ylabel("Effekt (kW)")
        ax1.set_xlabel("Timer i ett år")
        ax1.set_xlim([date_1, date_2])
        ax1.stackplot(x, y1, labels=[f'{int(np.sum(y1)):,} kWh | {int(max(y1)):,} kW'.replace(',', ' ')])
        ax1.set_ylim([-200,800])
        ax1.set_title("Uten solproduksjon")
        ax1.legend()
        ax1.grid(color='black', linestyle='--', linewidth=0.1)
        ax2.stackplot(x, y2, labels=[f'{int(np.sum(y2)):,} kWh | {int(max(y2)):,} kW'.replace(',', ' ')])
        ax2.xaxis.set_major_formatter(myFmt)
        ax2.set_ylim([-200,800])
        ax2.set_xlabel("Timer i ett år")
        ax2.set_xlim([date_1, date_2])
        ax2.set_title(f'Med solproduksjon. Overskudd: {int(-np.where(y2<0,y2,0).sum(0)):,} kWh'.replace(',', ' '))
        ax2.legend()
        ax2.grid(color='black', linestyle='--', linewidth=0.1)
        st.pyplot(fig)
        plt.close()

    def _plot_distric_heating_and_geoenergy(self):
        date_1, date_2 = np.datetime64("2021-01-01T00"), np.datetime64("2022-01-01T00")

        x = np.arange(date_1, date_2, dtype='datetime64')
        y1 = self.dhw_arr
        y2 = self.space_heating_arr - self.peak_arr
        y3 = self.peak_arr

        mpl.rcParams['axes.prop_cycle'] = cycler(color=['#232927', '#1d3c34', '#232927'])
        plt.stackplot(x,y1,y2,y3, labels=[f'Tappevann (fjernvarme): {int(np.sum(y1)):,} kWh | {int(max(y1)):,} kW'.replace(',', ' '), f'Romoppvarming (grunnvarme): {int(np.sum(y2)):,} kWh | {int(max(y2)):,} kW'.replace(',', ' '),  f'Spisslast (fjernvarme): {int(np.sum(y3)):,} kWh | {int(max(y3)):,} kW'.replace(',', ' ')])
        plt.legend(loc='best')
        myFmt = mdates.DateFormatter('%d.%m')
        plt.gca().xaxis.set_major_formatter(myFmt)
        plt.xlabel("Timer i ett år")
        plt.ylabel("Effekt [kW]")
        plt.grid(color='black', linestyle='--', linewidth=0.1)
        plt.xlim([date_1, date_2])
        st.pyplot(plt)
        plt.close()
    




        
    def _plot_arr(self, name, array, COLOR):
        plot = Plotting()
        plot.hourly_plot(array, COLOR, name)
    
    

    def _peakshaving(self):
        energy_arr = self.peak_arr
        REDUCTION = 150
        RHO, HEAT_CAPACITY = 0.96, 4.2
        NEW_MAX_EFFECT = max(energy_arr) - REDUCTION
        
        #Finne topper
        peakshaving_arr = np.zeros(len(energy_arr))
        for i in range(0, len(energy_arr)):
            peakshaving_arr[i] = energy_arr[i]

        max_effect_arr = np.zeros(len(energy_arr))
        for i in range(0, len(energy_arr)):
            effect = energy_arr[i]
            if effect > NEW_MAX_EFFECT:
                max_effect_arr[i] = effect - NEW_MAX_EFFECT
        
        #Lade tanken før topper, og ta bort topper
        day = 12
        for i in range(0, len(energy_arr)-day):
            peakshave = max_effect_arr[i+day]
            if peakshave > 0:
                peakshaving_arr[i+day] -= peakshave
                peakshaving_arr[i] += peakshave/6
                peakshaving_arr[i+1] += peakshave/6
                peakshaving_arr[i+2] += peakshave/6
                peakshaving_arr[i+3] += peakshave/6
                peakshaving_arr[i+4] += peakshave/6
                peakshaving_arr[i+5] += peakshave/6
            
        self.peakshaving_arr = peakshaving_arr







    def _winterweek(self, energy_arr):
        size = 100
        max_index = np.argmax(energy_arr)
        new_energy_arr = energy_arr[max_index - size : max_index + size]

        REDUCTION = 200
        RHO, HEAT_CAPACITY = 0.96, 4.2
        NEW_MAX_EFFECT = max(energy_arr) - REDUCTION
        #st.line_chart(energy_arr)
        #st.write(np.sum(energy_arr))

        tank = 0
        for i in range(0, len(energy_arr)):
            effect = energy_arr[i]
            if effect > NEW_MAX_EFFECT:
                charging = effect - NEW_MAX_EFFECT
                energy_arr[i] = effect - charging
                tank = tank + charging

        st.line_chart(new_energy_arr)

    def _plot_effect_diagram(self):
        wide_form = pd.DataFrame({
        'Varighet (timer)' : np.array(range(0, len(self.thermal_arr))),
        'Spisslast (ikke bergvarme)' : np.sort(self.thermal_arr)[::-1], 
        'Levert energi fra brønner' : np.sort(self.coverage_arr)[::-1],
        'Strømforbruk varmepumpe' : np.sort(self.compressor_arr)[::-1]
        })

        c = alt.Chart(wide_form).transform_fold(
            ['Spisslast (ikke bergvarme)', 'Levert energi fra brønner', 'Strømforbruk varmepumpe'],
            as_=['key', 'Effekt (kW)']).mark_bar(width=2, opacity=0.5).encode(
                x=alt.X('Varighet (timer):Q', scale=alt.Scale(domain=[0, 8760])),
                y=alt.Y('Effekt (kW):Q', scale=alt.Scale(zero=False)) ,
                color=alt.Color('key:N', scale=alt.Scale(domain=['Spisslast (ikke bergvarme)', 'Levert energi fra brønner', 'Strømforbruk varmepumpe'], 
                range=['#FFC358', '#48a23f', '#1d3c34']), legend=alt.Legend(orient='top', direction='vertical', title=None))
            )

        st.altair_chart(c, use_container_width=True)


    def _plot_geoenergy_coverage(self):
        wide_form = pd.DataFrame({
        'Timer i ett år' : np.array(range(0, len(self.thermal_arr))),
        'Spisslast (ikke bergvarme)' : self.thermal_arr, 
        'Levert energi fra brønner' : self.coverage_arr,
        'Strømforbruk varmepumpe' : self.compressor_arr
        })

        c = alt.Chart(wide_form).transform_fold(
            ['Spisslast (ikke bergvarme)', 'Levert energi fra brønner', 'Strømforbruk varmepumpe'],
            as_=['key', 'Effekt (kW)']).mark_bar(width=2, opacity=0.5).encode(
                x=alt.X('Timer i ett år:Q', scale=alt.Scale(domain=[0, 8760])),
                y='Effekt (kW):Q',
                color=alt.Color('key:N', scale=alt.Scale(domain=['Spisslast (ikke bergvarme)', 'Levert energi fra brønner', 'Strømforbruk varmepumpe'], 
                range=['#ffdb9a', '#48a23f', '#ffc358']), legend=alt.Legend(orient='top', direction='vertical', title=None))
            )

        st.altair_chart(c, use_container_width=True)

    def _plot_solar_geoenergy(self):
        wide_form = pd.DataFrame({
        'Timer i ett år' : np.array(range(0, len(self.electric_arr))),
        'Spisslast' : self.compressor_arr + self.peak_arr + self.electric_arr,
        'Kompressor' : self.compressor_arr + self.electric_arr,
        'Elspesifikt' : self.electric_arr, 
        })

        c = alt.Chart(wide_form).transform_fold(
            ['Spisslast', 'Kompressor', 'Elspesifikt'],
            as_=['key', 'Effekt (kW)']).mark_bar(width=2, opacity=0.5).encode(
                x=alt.X('Timer i ett år:Q', scale=alt.Scale(domain=[0, 8760])),
                y='Effekt (kW):Q',
                color=alt.Color('key:N', scale=alt.Scale(domain=['Spisslast', 'Kompressor', 'Elspesifikt'], 
                range=['#ffc358', '#b2883d' , '#664e23']), legend=alt.Legend(orient='top', direction='vertical', title=None))
            )

        st.altair_chart(c, use_container_width=True)

        wide_form = pd.DataFrame({
        'Timer i ett år' : np.array(range(0, len(self.electric_arr))),
        'Spisslast' : np.sort(self.compressor_arr + self.peak_arr + self.electric_arr)[::-1],
        'Kompressor' : np.sort(self.compressor_arr + self.electric_arr)[::-1],
        'Elspesifikt' : np.sort(self.electric_arr)[::-1], 
        })

        c = alt.Chart(wide_form).transform_fold(
            ['Spisslast', 'Kompressor', 'Elspesifikt'],
            as_=['key', 'Effekt (kW)']).mark_bar(width=2).encode(
                x=alt.X('Timer i ett år:Q', scale=alt.Scale(domain=[0, 8760])),
                y='Effekt (kW):Q',
                color=alt.Color('key:N', scale=alt.Scale(domain=['Spisslast', 'Kompressor', 'Elspesifikt'], 
                range=['#1d3c34', '#607670' , '#a4b1ad']), legend=alt.Legend(orient='top', direction='vertical', title=None))
            )

        st.altair_chart(c, use_container_width=True)

        wide_form = pd.DataFrame({
        'Timer i ett år' : np.array(range(0, len(self.electric_arr))),
        'Spisslast' : self.compressor_arr + self.peak_arr + self.electric_arr - self.solar_arr,
        'Kompressor' : self.compressor_arr + self.electric_arr - self.solar_arr,
        'Elspesifikt' : self.electric_arr - self.solar_arr, 
        })

        c = alt.Chart(wide_form).transform_fold(
            ['Spisslast', 'Kompressor', 'Elspesifikt'],
            as_=['key', 'Effekt (kW)']).mark_bar(width=2, opacity=0.5).encode(
                x=alt.X('Timer i ett år:Q', scale=alt.Scale(domain=[0, 8760])),
                y=alt.Y('Effekt (kW):Q', scale=alt.Scale(domain=[0,800])),
                color=alt.Color('key:N', scale=alt.Scale(domain=['Spisslast', 'Kompressor', 'Elspesifikt'], 
                range=['#1d3c34', '#607670' , '#a4b1ad']), legend=alt.Legend(orient='top', direction='vertical', title=None))
            )

        st.altair_chart(c, use_container_width=True)


    




def energy_analysis_old():
    energy_analysis_obj = EnergyAnalysis()




