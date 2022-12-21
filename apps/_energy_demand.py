
import streamlit as st
import numpy as np

from scripts._profet import EnergyDemand
from scripts._utils import Plotting
from scripts._energy_coverage import EnergyCoverage
from scripts._costs import Costs

def energy_demand():
    st.title("Energibehov")
    selected_input_option = st.radio("Velg inputform", options=["PROFet", "Last opp fil"], horizontal=True)
    if selected_input_option == "PROFet":
        st.header("PROFet")
        st.caption("Foreløpig begrenset til Trondheimsklima")
        energy_demand = EnergyDemand()
        demand_array, selected_array = energy_demand.get_thermal_arrays_from_input()
    if selected_input_option == "Last opp fil":
        st.header("Filopplasting")
        st.caption("Under arbeid...")
        demand_array = st.file_uploader("Last opp fil")
    Plotting().hourly_plot(demand_array, selected_array, Plotting().FOREST_GREEN)
    Plotting().hourly_plot(np.sort(demand_array)[::-1], selected_array, Plotting().FOREST_GREEN)
    st.markdown("---")
    #--
    st.header("Dekningsgrad")
    energy_coverage = EnergyCoverage(demand_array)
    energy_coverage.COVERAGE = st.number_input("Velg energidekningsgrad [%]", min_value=50, value=90, max_value=100, step=2)    
    energy_coverage._coverage_calculation()
    Plotting().hourly_stack_plot(energy_coverage.covered_arr, energy_coverage.non_covered_arr, "Grunnvarmedekning", "Spisslast", Plotting().FOREST_GREEN, Plotting().SUN_YELLOW)
    #--
    st.header("Årsvarmefaktor")
    energy_coverage.COP = st.number_input("Velg COP", min_value=1.0, value=3.5, max_value=5.0, step=0.2)
    energy_coverage._geoenergy_cop_calculation()
    Plotting().hourly_triple_stack_plot(energy_coverage.gshp_compressor_arr, energy_coverage.gshp_delivered_arr, 
    energy_coverage.non_covered_arr, "Kompressor", "Levert fra brønn(er)", "Spisslast", Plotting().FOREST_GREEN, Plotting().GRASS_GREEN, Plotting().SUN_YELLOW)
    Plotting().hourly_triple_stack_plot(np.sort(energy_coverage.gshp_compressor_arr)[::-1], np.sort(energy_coverage.gshp_delivered_arr)[::-1], 
    np.sort(energy_coverage.non_covered_arr)[::-1], "Kompressor", "Levert fra brønn(er)", "Spisslast", Plotting().FOREST_GREEN, Plotting().GRASS_GREEN, Plotting().SUN_YELLOW)

    st.markdown("---")
    #--
    st.title("Brønnpark")
    st.header("Design")
    c1, c2 = st.columns(2)
    with c1:
        kWh_per_meter = st.number_input("Velg kWh/m", min_value=60, value=80, max_value=120, step=5)
    with c2:
        watt_per_meter = st.number_input("Velg W/m", min_value=10, value=25, max_value=50) /1000
    meters_1 = (np.sum(energy_coverage.gshp_delivered_arr)/kWh_per_meter)
    meters_2 = max(energy_coverage.covered_arr)/watt_per_meter
    if meters_1 > meters_2:
        meters = meters_1
    else:
        meters = meters_2
    meters = st.number_input("Velg totalt antall brønnmeter [m] - standardverdi er basert på kWh/m og W/m", value=int(meters), step=10)
    st.header("Dybde til fjell")
    depth_to_bedrock = st.number_input("Oppgi dybde til fjell [m]", min_value = 0, value=10, max_value=250, step=1)
    st.markdown("---")
    st.title("Kostnader")
    st.caption("Under arbeid")
    costs = Costs()
    costs.calculate_investment(energy_coverage.heat_pump_size, meters, 5)
    costs.adjust()
    tab1, tab2 = st.tabs(["Direkte kjøp", "Lånefinansiert"])
    with tab1:
        costs.calculate_monthly_costs(demand_array, energy_coverage.gshp_compressor_arr, energy_coverage.non_covered_arr, costs.elprice, 0, 0)
        costs.operation_show_after()
        costs.plot("Driftskostnad")
        costs.profitibality_operation()

    with tab2:
        costs.calculate_monthly_costs(demand_array, energy_coverage.gshp_compressor_arr, energy_coverage.non_covered_arr, costs.elprice, costs.investment, costs.payment_time)

        costs.operation_and_investment_show()

        costs.plot("Totalkostnad")
        costs.profitibality_operation_and_investment()
    