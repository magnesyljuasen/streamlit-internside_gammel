import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image

from scripts._profet import EnergyDemand
from scripts._utils import Plotting
from scripts._energy_coverage import EnergyCoverage
from scripts._costs import Costs
from scripts._ghetool import GheTool
from scripts._utils import hour_to_month
from scripts._peakshaving import peakshaving

def energy_analysis():
    st.button("Refresh")
    st.title("Energianalyse")
    st.header("Last opp fil")
    with st.expander("Hvordan skal filen se ut?"):
        st.write("Det kan kun importeres **excel ark** med maks 5 timeserier på formatet som under. Det er at rekkefølgen er lik som under (og med overskrift).")
        image = Image.open("src/data/img/example_input_energy_analysis.PNG")
        st.image(image)  
    uploaded_array = st.file_uploader("Last opp timeserier [kW]")
    if uploaded_array:
        df = pd.read_excel(uploaded_array)
        electric_array = df.iloc[:,0].to_numpy()
        space_heating_array = df.iloc[:,1].to_numpy()
        dhw_array = df.iloc[:,2].to_numpy()
        solar_array = df.iloc[:,3].to_numpy()
        thermal_array = df.iloc[:,4].to_numpy()
        Plotting().hourly_plot(electric_array, "Elspesifikt behov", Plotting().GRASS_BLUE)
        Plotting().hourly_plot(np.sort(electric_array)[::-1], "Elspesifikt behov", Plotting().GRASS_BLUE)

        Plotting().hourly_plot(space_heating_array, "Romoppvarmingsbehov", Plotting().FOREST_BROWN)
        Plotting().hourly_plot(np.sort(space_heating_array)[::-1], "Romoppvarmingsbehov", Plotting().FOREST_BROWN)

        Plotting().hourly_plot(dhw_array, "Tappevannsbehov", Plotting().FOREST_PURPLE)
        Plotting().hourly_plot(np.sort(dhw_array)[::-1], "Tappevannsbehov", Plotting().FOREST_PURPLE)

        Plotting().hourly_plot(thermal_array, "Termisk (romoppvarming + tappevann)", Plotting().FOREST_DARK_BROWN)
        Plotting().hourly_plot(np.sort(thermal_array)[::-1], "Termisk (romoppvarming + tappevann)", Plotting().FOREST_DARK_BROWN)

        Plotting().hourly_plot(solar_array, "Produsert solenergi", Plotting().SUN_YELLOW)
        Plotting().hourly_plot(np.sort(solar_array)[::-1], "Produsert solenergi", Plotting().SUN_YELLOW)

    else:
        st.stop()
    st.markdown("---")
    #--
    #st.header("Kjølebehov")
    #annual_cooling_demand = st.number_input("Legg inn årlig kjølebehov [kWh]", min_value=0, value=0, step=1000)
    #cooling_effect = st.number_input("Legg inn kjøleeffekt [kW]", min_value=0, value=0, step=100)
    #cooling_per_month = annual_cooling_demand * np.array([0.025, 0.05, 0.05, .05, .075, .1, .2, .2, .1, .075, .05, .025])
    #months = ["jan", "feb", "mar", "apr", "mai", "jun", "jul", "aug", "sep", "okt", "nov", "des"]
    #Plotting().xy_plot_bar(months, "Måneder", cooling_per_month, 0, max(cooling_per_month) + max(cooling_per_month)/10, "Effekt [W]", Plotting().GRASS_GREEN)
    #st.markdown("---")
    #--
    st.header("Fjernvarme og solenergi")
    st.subheader("Dekningsgrad")
    energy_coverage = EnergyCoverage(thermal_array)
    energy_coverage.COVERAGE = st.number_input("Velg energidekningsgrad [%]", min_value=50, value=90, max_value=100, step=2, key="fjernvarmedekning")    
    energy_coverage._coverage_calculation()
    Plotting().hourly_stack_plot(energy_coverage.covered_arr, energy_coverage.non_covered_arr, "Fjernvarmedekning", "Spisslast", Plotting().FOREST_GREEN, Plotting().GRASS_BLUE)
    Plotting().hourly_stack_plot(np.sort(energy_coverage.covered_arr)[::-1], np.sort(energy_coverage.non_covered_arr)[::-1], "Fjernvarmedekning", "Spisslast", Plotting().FOREST_GREEN, Plotting().GRASS_BLUE)

    st.subheader("Gjenstående elektrisk behov")
    Plotting().hourly_plot(electric_array + energy_coverage.non_covered_arr, "Totalt elektrisk behov; uten solproduksjon", Plotting().GRASS_BLUE)
    Plotting().hourly_plot(np.sort(electric_array + energy_coverage.non_covered_arr)[::-1], "Totalt elektrisk behov; uten solproduksjon", Plotting().GRASS_BLUE)

    Plotting().hourly_plot(electric_array + energy_coverage.non_covered_arr - solar_array, "Totalt elektrisk behov; med solproduksjon", Plotting().GRASS_BLUE)
    Plotting().hourly_plot(np.sort(electric_array + energy_coverage.non_covered_arr - solar_array)[::-1], "Totalt elektrisk behov; med solproduksjon", Plotting().GRASS_BLUE)
    st.markdown("---")
    #--
    st.header("Grunnvarme og solenergi")
    st.subheader("Dekningsgrad")
    energy_coverage = EnergyCoverage(thermal_array)
    energy_coverage.COVERAGE = st.number_input("Velg energidekningsgrad [%]", min_value=50, value=90, max_value=100, step=2, key="grunnvarmedekning")    
    energy_coverage._coverage_calculation()
    Plotting().hourly_stack_plot(energy_coverage.covered_arr, energy_coverage.non_covered_arr, "Grunnvarmedekning", "Spisslast", Plotting().SPRING_GREEN, Plotting().SPRING_BLUE)
    Plotting().hourly_stack_plot(np.sort(energy_coverage.covered_arr)[::-1], np.sort(energy_coverage.non_covered_arr)[::-1], "Grunnvarmedekning", "Spisslast", Plotting().SPRING_GREEN, Plotting().SPRING_BLUE)
    st.subheader("Årsvarmefaktor")
    energy_coverage.COP = st.number_input("Velg COP", min_value=1.0, value=3.5, max_value=5.0, step=0.2)
    energy_coverage._geoenergy_cop_calculation()
    Plotting().hourly_triple_stack_plot(energy_coverage.gshp_compressor_arr, energy_coverage.gshp_delivered_arr, energy_coverage.non_covered_arr, "Kompressor", "Levert fra brønn(er)", "Spisslast", Plotting().GRASS_BLUE, Plotting().GRASS_GREEN, Plotting().SPRING_BLUE)
    Plotting().hourly_triple_stack_plot(np.sort(energy_coverage.gshp_compressor_arr)[::-1], np.sort(energy_coverage.gshp_delivered_arr)[::-1], np.sort(energy_coverage.non_covered_arr)[::-1], "Kompressor", "Levert fra brønn(er)", "Spisslast", Plotting().GRASS_BLUE, Plotting().GRASS_GREEN, Plotting().SPRING_BLUE)
    st.subheader("Gjenstående elektrisk behov")
    Plotting().hourly_plot(electric_array + energy_coverage.non_covered_arr + energy_coverage.gshp_compressor_arr, "Totalt elektrisk behov; uten solproduksjon", Plotting().GRASS_BLUE)
    Plotting().hourly_plot(np.sort(electric_array + energy_coverage.non_covered_arr + energy_coverage.gshp_compressor_arr)[::-1], "Totalt elektrisk behov; uten solproduksjon", Plotting().GRASS_BLUE)

    Plotting().hourly_plot(electric_array + energy_coverage.non_covered_arr + energy_coverage.gshp_compressor_arr - solar_array, "Totalt elektrisk behov; med solproduksjon", Plotting().GRASS_BLUE)
    Plotting().hourly_plot(np.sort(electric_array + energy_coverage.non_covered_arr + energy_coverage.gshp_compressor_arr - solar_array)[::-1], "Totalt elektrisk behov; med solproduksjon", Plotting().GRASS_BLUE)
    st.markdown("---")
    #--
    st.header("Alternativer for spisslast - Akkumuleringstank")
    max_effect_noncovered = max(energy_coverage.non_covered_arr)
    st.write("**Før akkumulering**")
    Plotting().hourly_plot(energy_coverage.non_covered_arr, "Spisslast", Plotting().SPRING_BLUE, 0, 1.1*max_effect_noncovered, max_effect_noncovered)
    Plotting().hourly_plot(np.sort(energy_coverage.non_covered_arr)[::-1], "Spisslast", Plotting().SPRING_BLUE, 0, 1.1*max_effect_noncovered, max_effect_noncovered)
    #Plotting().hourly_plot(energy_coverage.non_covered_arr, "Spisslast", Plotting().SUN_YELLOW, 0, 1.1*max_effect_noncovered, max_effect_noncovered, winterweek=True)
    st.write("**Etter akkumulering**")
    effect_reduction = st.number_input("Ønsket effektreduksjon [kW]", value=int(round(max_effect_noncovered/10,0)), step=10)
    if effect_reduction > max_effect_noncovered:
        st.warning("Effektreduksjon kan ikke være høyere enn effekttopp")
        st.stop()
    TO_TEMP = st.number_input("Turtemperatur [°C]", value = 60)
    FROM_TEMP = st.number_input("Returtemperatur [°C]", value = 40)
    peakshaving_arr, peakshaving_effect = peakshaving(energy_coverage.non_covered_arr, effect_reduction, TO_TEMP, FROM_TEMP)
    Plotting().hourly_plot(peakshaving_arr, "Spisslast", Plotting().SPRING_BLUE, 0, 1.1*max_effect_noncovered, peakshaving_effect)
    Plotting().hourly_plot(np.sort(peakshaving_arr)[::-1], "Spisslast", Plotting().SPRING_BLUE, 0, 1.1*max_effect_noncovered, peakshaving_effect)
    #Plotting().hourly_plot(energy_coverage.non_covered_arr, "Spisslast", Plotting().SUN_YELLOW, 0, 1.1*max_effect_noncovered, max_effect_noncovered, winterweek=True)
    st.markdown("---")
    #--
    st.header("Fjernvarme/grunnvarme/solenergi")
    st.subheader("Dekningsgrad, grunnvarme/romoppvarming")
    energy_coverage = EnergyCoverage(space_heating_array)
    energy_coverage.COVERAGE = st.number_input("Velg energidekningsgrad for romoppvarming [%]", min_value=50, value=90, max_value=100, step=2, key="fjernvarme/grunnvarme/solenergi")    
    energy_coverage._coverage_calculation()
    Plotting().hourly_stack_plot(energy_coverage.covered_arr, energy_coverage.non_covered_arr, "Grunnvarmedekning", "Spisslast", Plotting().FOREST_BROWN, Plotting().SPRING_BLUE)
    Plotting().hourly_stack_plot(np.sort(energy_coverage.covered_arr)[::-1], np.sort(energy_coverage.non_covered_arr)[::-1], "Grunnvarmedekning", "Spisslast", Plotting().FOREST_BROWN, Plotting().SPRING_BLUE)
    st.subheader("Årsvarmefaktor, grunnvarme/romoppvarming")
    energy_coverage.COP = st.number_input("Velg COP", min_value=1.0, value=3.5, max_value=5.0, step=0.2, key="fjernvarme/grunnvarme/solenergi-cop")
    energy_coverage._geoenergy_cop_calculation()
    Plotting().hourly_triple_stack_plot(energy_coverage.gshp_compressor_arr, energy_coverage.gshp_delivered_arr, energy_coverage.non_covered_arr, "Kompressor", "Levert fra brønn(er)", "Spisslast", Plotting().GRASS_BLUE, Plotting().GRASS_GREEN, Plotting().SPRING_BLUE)
    Plotting().hourly_triple_stack_plot(np.sort(energy_coverage.gshp_compressor_arr)[::-1], np.sort(energy_coverage.gshp_delivered_arr)[::-1], np.sort(energy_coverage.non_covered_arr)[::-1], "Kompressor", "Levert fra brønn(er)", "Spisslast", Plotting().GRASS_BLUE, Plotting().GRASS_GREEN, Plotting().SPRING_BLUE)
    st.subheader("Konsept")
    Plotting().hourly_triple_stack_plot(dhw_array, energy_coverage.covered_arr, energy_coverage.non_covered_arr, "Tappevann(fjernvarme)", "Romoppvarming(grunnvarme)", "Romoppvarmingsspisslast(fjernvarme)", 
    Plotting().FOREST_PURPLE, Plotting().SPRING_GREEN, Plotting().SPRING_BLUE)
    Plotting().hourly_quad_stack_plot(dhw_array, energy_coverage.gshp_compressor_arr, energy_coverage.gshp_delivered_arr, energy_coverage.non_covered_arr, "Tappevann(fjernvarme)", "Kompressor(grunnvarme)", "Levert fra brønner(grunnvarme)", "Romoppvarmingspisslast(fjernvarme)", 
    Plotting().FOREST_PURPLE, Plotting().GRASS_BLUE, Plotting().GRASS_GREEN, Plotting().SPRING_BLUE)
    Plotting().hourly_quad_stack_plot(np.sort(dhw_array)[::-1], np.sort(energy_coverage.gshp_compressor_arr)[::-1], np.sort(energy_coverage.gshp_delivered_arr)[::-1], np.sort(energy_coverage.non_covered_arr)[::-1], "Tappevann(fjernvarme)", "Kompressor(grunnvarme)", "Levert fra brønner(grunnvarme)", "Romoppvarmingspisslast(fjernvarme)", 
    Plotting().FOREST_PURPLE, Plotting().GRASS_BLUE, Plotting().GRASS_GREEN, Plotting().SPRING_BLUE)
    st.subheader("Gjenstående elektrisk behov")
    Plotting().hourly_plot(electric_array + energy_coverage.gshp_compressor_arr, "Totalt elektrisk behov; uten solproduksjon", Plotting().GRASS_BLUE)
    Plotting().hourly_plot(electric_array + energy_coverage.gshp_compressor_arr - solar_array, "Totalt elektrisk behov; med solproduksjon", Plotting().GRASS_BLUE)
    st.markdown("---")
    #--
#    st.title("Brønnpark")
#    simulation_obj = GheTool()
#    simulation_obj.monthly_load_heating = hour_to_month(energy_coverage.gshp_delivered_arr)
#    simulation_obj.monthly_load_cooling = cooling_per_month
#    simulation_obj.peak_heating = energy_coverage.heat_pump_size
#    simulation_obj.peak_cooling = cooling_effect
#    well_guess = int(round(np.sum(energy_coverage.gshp_delivered_arr)/80/300,2))
#    st.markdown(f"Estimert ca. **{well_guess}** brønner a 300 m ")
#    verdi = 5
#    with st.form("Inndata"):
#        c1, c2 = st.columns(2)
#        with c1:
#            simulation_obj.K_S = st.number_input("Varmledningsevne", min_value=1.0, value=3.5, max_value=10.0, step=1.0) 
#            simulation_obj.T_G = st.number_input("Uforstyrret temperatur", min_value=1.0, value=8.0, max_value=20.0, step=1.0)
#            simulation_obj.R_B = st.number_input("Målt borehullsmotstand", min_value=0.0, value=0.08, max_value=2.0, step=0.01) + 0.02
#            simulation_obj.N_1= st.number_input("Antall brønner (X)", value=well_guess, step=1) 
#            simulation_obj.N_2= st.number_input("Antall brønner (Y)", value=1, step=1) 
#        with c2:
#            H = st.number_input("Brønndybde [m]", min_value=100, value=300, max_value=500, step=10)
#            GWT = st.number_input("Grunnvannsstand [m]", min_value=0, value=5, max_value=100, step=1)
#            simulation_obj.H = H - GWT
#            simulation_obj.B = st.number_input("Avstand mellom brønner", min_value=1, value=15, max_value=30, step=1)
#            simulation_obj.RADIUS = st.number_input("Brønndiameter [mm]", min_value = 80, value=115, max_value=300, step=1) / 2000
#        st.form_submit_button("Kjør simulering")
#        simulation_obj._run_simulation()

    #st.title("Kostnader")
    #st.caption("Under arbeid")
    #tab1, tab2 = st.tabs(["Direkte kjøp", "Lånefinansiert"])
    #with tab1:
    #    costs_operation = Costs(meters)
    #    costs_operation._calculate_monthly_costs(demand_array, energy_coverage.gshp_compressor_arr, energy_coverage.non_covered_arr, costs_operation.INVESTMENT)
    #    costs_operation._show_operation_costs(costs_operation.INVESTMENT)
        #costs.operation_show_after()
        #costs.plot("Driftskostnad")
        #costs.profitibality_operation()
    #with tab2:
    #    costs_operation_and_investment = Costs(meters)
    #    costs_operation_and_investment._calculate_monthly_costs(demand_array, energy_coverage.gshp_compressor_arr, energy_coverage.non_covered_arr, 0)
    #    costs_operation_and_investment._show_operation_costs(0)
        #costs.operation_and_investment_show()
        #costs.plot("Totalkostnad")
        #costs.profitibality_operation_and_investment()
    