
import streamlit as st
import numpy as np
import pandas as pd

from scripts._profet import EnergyDemand
from scripts._utils import Plotting
from scripts._energy_coverage import EnergyCoverage
from scripts._costs import Costs
from scripts._ghetool import GheTool
from scripts._utils import hour_to_month
from scripts._peakshaving import peakshaving

def early_phase():
    st.warning("Under utvikling")
    st.title("Tidligfasedimensjonering av energibrønnpark")
    #---
    st.header("Ⅰ) Energibehov")
    selected_input = st.radio("Hvordan vil du legge inn input?", options=["PROFet", "Last opp"])
    if selected_input == "PROFet":
        st.subheader("Termisk behov fra PROFet")
        st.caption("Foreløpig begrenset til Trondheimsklima")
        energy_demand = EnergyDemand()
        demand_array, selected_array = energy_demand.get_thermal_arrays_from_input()
        Plotting().hourly_plot(demand_array, selected_array, Plotting().FOREST_GREEN)
        Plotting().hourly_duration_plot(demand_array, selected_array, Plotting().FOREST_GREEN)
        #--
        st.subheader("Elspesifikt behov fra PROFet")
        with st.expander("Elspesifikt behov"):
            electric_array, selected_array = energy_demand.get_electric_array_()
            Plotting().hourly_plot(electric_array, selected_array, Plotting().SUN_YELLOW)
            Plotting().hourly_duration_plot(electric_array, selected_array, Plotting().SUN_YELLOW)
    else:
        st.subheader("Last opp fil")
        uploaded_array = st.file_uploader("Last opp timeserie i kW")
        if uploaded_array:
            df = pd.read_excel(uploaded_array, header=None)
            demand_array = df.iloc[:,0].to_numpy()
            Plotting().hourly_plot(demand_array, "Energibehov", Plotting().FOREST_GREEN)
            Plotting().hourly_duration_plot(demand_array, "Energibehov", Plotting().FOREST_GREEN)
        else:
            st.stop()
    st.markdown("---")
    #--
    st.subheader("Kjølebehov")
    annual_cooling_demand = st.number_input("Legg inn årlig kjølebehov [kWh]", min_value=0, value=0, step=1000)
    cooling_effect = st.number_input("Legg inn kjøleeffekt [kW]", min_value=0, value=0, step=100)
    cooling_per_month = annual_cooling_demand * np.array([0.025, 0.05, 0.05, .05, .075, .1, .2, .2, .1, .075, .05, .025])
    months = ["jan", "feb", "mar", "apr", "mai", "jun", "jul", "aug", "sep", "okt", "nov", "des"]
    Plotting().xy_plot_bar(months, "Måneder", cooling_per_month, 0, max(cooling_per_month) + max(cooling_per_month)/10, "Energibehov [kWh]", Plotting().GRASS_GREEN)
    st.markdown("---")
    #--
    st.subheader("Dekningsgrad")
    energy_coverage = EnergyCoverage(demand_array)
    energy_coverage.COVERAGE = st.number_input("Velg energidekningsgrad [%]", min_value=50, value=90, max_value=100, step=2)    
    energy_coverage._coverage_calculation()
    st.caption(f"**Effektdekningsgrad: {int(round((energy_coverage.heat_pump_size/np.max(demand_array))*100,0))} %**")
    Plotting().hourly_stack_plot(energy_coverage.covered_arr, energy_coverage.non_covered_arr, "Grunnvarmedekning", "Spisslast", Plotting().FOREST_GREEN, Plotting().SUN_YELLOW)
    Plotting().hourly_stack_plot(np.sort(energy_coverage.covered_arr)[::-1], np.sort(energy_coverage.non_covered_arr)[::-1], "Grunnvarmedekning", "Spisslast", Plotting().FOREST_GREEN, Plotting().SUN_YELLOW)
    #--
    st.subheader("Årsvarmefaktor")
    energy_coverage.COP = st.number_input("Velg COP", min_value=1.0, value=3.5, max_value=5.0, step=0.2)
    energy_coverage._geoenergy_cop_calculation()
    Plotting().hourly_triple_stack_plot(energy_coverage.gshp_compressor_arr, energy_coverage.gshp_delivered_arr, 
    energy_coverage.non_covered_arr, "Kompressor", "Levert fra brønn(er)", "Spisslast", Plotting().FOREST_GREEN, Plotting().GRASS_GREEN, Plotting().SUN_YELLOW)
    Plotting().hourly_triple_stack_plot(np.sort(energy_coverage.gshp_compressor_arr)[::-1], np.sort(energy_coverage.gshp_delivered_arr)[::-1], 
    np.sort(energy_coverage.non_covered_arr)[::-1], "Kompressor", "Levert fra brønn(er)", "Spisslast", Plotting().FOREST_GREEN, Plotting().GRASS_GREEN, Plotting().SUN_YELLOW)
    st.markdown("---")
    #--
#    st.subheader("Alternativer for spisslast")
#    with st.expander("Akkumuleringstank"):
#        max_effect_noncovered = max(energy_coverage.non_covered_arr)
#        st.write("**Før akkumulering**")
#        Plotting().hourly_plot(energy_coverage.non_covered_arr, "Spisslast", Plotting().SUN_YELLOW, 0, 1.1*max_effect_noncovered, max_effect_noncovered)
#        #Plotting().hourly_plot(energy_coverage.non_covered_arr, "Spisslast", Plotting().SUN_YELLOW, 0, 1.1*max_effect_noncovered, max_effect_noncovered, winterweek=True)
#        st.write("**Etter akkumulering**")
#        effect_reduction = st.number_input("Ønsket effektreduksjon [kW]", value=int(round(max_effect_noncovered/10,0)), step=10)
#        if effect_reduction > max_effect_noncovered:
#            st.warning("Effektreduksjon kan ikke være høyere enn effekttopp")
#            st.stop()
#        TO_TEMP = st.number_input("Turtemperatur [°C]", value = 60)
#        FROM_TEMP = st.number_input("Returtemperatur [°C]", value = 40)
#        peakshaving_arr, peakshaving_effect = peakshaving(energy_coverage.non_covered_arr, effect_reduction, TO_TEMP, FROM_TEMP)
#        Plotting().hourly_plot(peakshaving_arr, "Spisslast", Plotting().SUN_YELLOW, 0, 1.1*max_effect_noncovered, peakshaving_effect)
#        #Plotting().hourly_plot(energy_coverage.non_covered_arr, "Spisslast", Plotting().SUN_YELLOW, 0, 1.1*max_effect_noncovered, max_effect_noncovered, winterweek=True)
#    st.markdown("---")
    st.subheader("Oppsummert")
    st.write(f"Totalt energibehov: {int(round(np.sum(demand_array),0)):,} kWh | {int(round(np.max(demand_array),0)):,} kW".replace(',', ' '))
    st.write(f"- Dekkes av grunnvarmeanlegget: {int(round(np.sum(energy_coverage.covered_arr),0)):,} kWh | **{int(round(np.max(energy_coverage.covered_arr),0)):,}** kW".replace(',', ' '))
    st.write(f"- - Kompressor: {int(round(np.sum(energy_coverage.gshp_compressor_arr),0)):,} kWh | {int(round(np.max(energy_coverage.gshp_compressor_arr),0)):,} kW".replace(',', ' '))
    st.write(f"- - Levert fra brønn(er): {int(round(np.sum(energy_coverage.gshp_delivered_arr),0)):,} kWh | {int(round(np.max(energy_coverage.gshp_delivered_arr),0)):,} kW".replace(',', ' '))
    st.write(f"- Spisslast: {int(round(np.sum(energy_coverage.non_covered_arr),0)):,} kWh | {int(round(np.max(energy_coverage.non_covered_arr),0)):,} kW".replace(',', ' '))
    st.markdown("---")
    #---
    st.header("Ⅱ) Dimensjonering av brønnpark")
    simulation_obj = GheTool()
    simulation_obj.monthly_load_heating = hour_to_month(energy_coverage.gshp_delivered_arr)
    simulation_obj.monthly_load_cooling = cooling_per_month
    simulation_obj.peak_cooling = cooling_effect
    well_guess = int(round(np.sum(energy_coverage.gshp_delivered_arr)/80/300,2))
    if well_guess == 0:
        well_guess = 1
    st.markdown(f"Estimert ca. **{well_guess}** brønn(er) á 300 m ")
    with st.form("Inndata"):
        c1, c2 = st.columns(2)
        with c1:
            simulation_obj.K_S = st.number_input("Effektiv varmledningsevne [W/m∙K]", min_value=1.0, value=3.5, max_value=10.0, step=1.0) 
            simulation_obj.T_G = st.number_input("Uforstyrret temperatur [°C]", min_value=1.0, value=8.0, max_value=20.0, step=1.0)
            simulation_obj.R_B = st.number_input("Borehullsmotstand [m∙K/W]", min_value=0.0, value=0.08, max_value=2.0, step=0.01)
            simulation_obj.N_1= st.number_input("Antall brønner (X)", value=well_guess, step=1) 
            simulation_obj.N_2= st.number_input("Antall brønner (Y)", value=1, step=1)
            #--
            simulation_obj.COP = energy_coverage.COP
            heat_carrier_fluid_types = ["HX24", "HX35", "Kilfrost GEO 24%", "Kilfrost GEO 32%", "Kilfrost GEO 35%"]    
            heat_carrier_fluid = st.selectbox("Type kollektorvæske", options=list(range(len(heat_carrier_fluid_types))), format_func=lambda x: heat_carrier_fluid_types[x])
            simulation_obj.FLOW = st.number_input("Flow [l/min]", value=0.5, step=0.1)
        with c2:
            H = st.number_input("Brønndybde [m]", min_value=100, value=300, max_value=500, step=10)
            GWT = st.number_input("Grunnvannsstand [m]", min_value=0, value=5, max_value=100, step=1)
            simulation_obj.H = H - GWT
            simulation_obj.B = st.number_input("Avstand mellom brønner", min_value=1, value=15, max_value=30, step=1)
            simulation_obj.RADIUS = st.number_input("Brønndiameter [mm]", min_value = 80, value=115, max_value=300, step=1) / 2000
            simulation_obj.peak_heating = st.number_input("Varmepumpe [kW]", value = int(round(energy_coverage.heat_pump_size,0)), step=10)
        st.form_submit_button("Kjør simulering")
        heat_carrier_fluid_densities = [970.5, 955, 1105.5, 1136.2, 1150.6]
        heat_carrier_fluid_capacities = [4.298, 4.061, 3.455, 3.251, 3.156]
        simulation_obj.DENSITY = heat_carrier_fluid_densities[heat_carrier_fluid]
        simulation_obj.HEAT_CAPACITY = heat_carrier_fluid_capacities[heat_carrier_fluid]
        simulation_obj._run_simulation()
    #--
    st.header("Ⅲ) Kostnader")
    costs_obj = Costs()
    #-- input
    costs_obj.ELPRICE = st.number_input("Strømpris inkl. alt [kr/kWh]", min_value=0.0, value=1.0, max_value=10.0, step=1.0)
    costs_obj.LIFETIME = st.number_input("Levetid [år]", min_value=1, value=25, max_value=100, step=5)
    costs_obj.DISKONTERINGSRENTE = st.number_input("Diskonteringsrente [%]", min_value=1, value=6, max_value=100, step=2) / 100
    costs_obj.METERS = (simulation_obj.N_1 * simulation_obj.N_2) * simulation_obj.H
    costs_obj.gshp_compressor_arr = energy_coverage.gshp_compressor_arr
    costs_obj.non_covered_arr = energy_coverage.non_covered_arr
    costs_obj.demand_array = demand_array
    costs_obj.heat_pump_size = energy_coverage.heat_pump_size
    #--
    costs_obj._run_cost_calculation()
    st.subheader("Resultater")
    st.write(f" - Investeringskostnad: {costs_obj.investment_cost:,} kr".replace(',', ' '))
    st.write(f" - Driftskostnad (strøm): {costs_obj.operation_cost:,} kr/år".replace(',', ' '))
    st.write(f" - Vedlikeholdskostnad: {costs_obj.maintenance_cost:,} kr/år".replace(',', ' '))
    st.write(f" - LCOE: {costs_obj.LCOE:,} kr/kWh".replace(',', ' '))
