from pyrsistent import m
import streamlit as st
from calculator_utilities import Groundsource, Input, Temperature, Geology, Demand, Electricity, Prerequisites, Temperature, Costs, Environment, Gis, download_report
import numpy as np
#from annotated_text import annotated_text
from bokeh.models.widgets import Div
from datetime import date


def main_calculation():
    demand = Demand()
    electricity = Electricity()
    geology = Geology()
    
    with st.sidebar:
        st.title("Forutsetninger")
        with st.expander("Oppvarmingsbehov"):
            demand.adjust()
            demand.update()
            demand.plot()

        with st.expander("Årsvarmefaktor (SCOP) og dekningsgrad"):
            groundsource = Groundsource()
            groundsource.adjust()
            groundsource.demands(demand.energy_arr)
            groundsource.update()
            groundsource.calculation()
            groundsource.diagram()

        with st.expander("Strømpris"):
            electricity.input()
            electricity.calculation()
            electricity.plot()

        with st.expander("Dybde til fjell"):
            geology.adjust()

        with st.expander("Kostnader"):     
            costs = Costs()
            costs.calculate_investment(groundsource.heat_pump_size, groundsource.meter, geology.depth_to_bedrock)
            costs.adjust()

        with st.expander("Klimagassutslipp"):
            environment = Environment()
            environment.adjust()
            environment.calculate_emissions(demand.energy_arr, 
            groundsource.energy_gshp_compressor_arr, groundsource.energy_gshp_peak_arr)
                     

    with st.expander("Kostnader"):
        costs.calculate_monthly_costs(demand.energy_arr, 
        groundsource.energy_gshp_compressor_arr, groundsource.energy_gshp_peak_arr, electricity.elprice_hourly, 0, 0)
        costs.operation_show()
        costs.plot("Driftskostnad")
        costs.operation_show_after()
        costs.calculate_monthly_costs(demand.energy_arr, 
        groundsource.energy_gshp_compressor_arr, groundsource.energy_gshp_peak_arr, electricity.elprice_hourly, costs.investment, 20)
        costs.operation_and_investment_show()
        costs.plot("Totalkostnad")
        costs.operation_and_investment_after()
        costs.investment_show()            

    with st.expander("Klimagassutslipp"):
        environment.text_before()
        environment.plot()
        environment.text_after()

  





           