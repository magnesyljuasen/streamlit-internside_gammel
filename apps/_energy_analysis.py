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
from scripts._utils import negative_sum

def energy_analysis():
    st.button("Refresh")
    st.title("Energianalyse")
    st.header("Last opp fil")
    with st.expander("Hvordan skal filen se ut?"):
        st.write("Det kan kun importeres **excel ark** med maks 5 timeserier på formatet som under. Det er at rekkefølgen er lik som under (og med overskrift).")
        image = Image.open("src/data/img/example_input_energy_analysis.PNG")
        st.image(image)  
    uploaded_array = st.file_uploader("Last opp timeserier [kW]")
    st.markdown("---")
    ELPRICE = st.number_input("Velg total strømpris [kr/kwh]", min_value=0.0, value=1.0, max_value=10.0, step=0.5)
    DISTRICTHEATING_PRICE = st.number_input("Velg total fjernvarmepris [kr/kwh]", min_value=0.0, value=1.0, max_value=10.0, step=0.5)
    MAX_VALUE = st.number_input("Maksverdi for plotting", min_value=0, value=1000000, max_value=10000000)
    st.markdown("---")
    if uploaded_array:
        df = pd.read_excel(uploaded_array)
        electric_array = df.iloc[:,0].to_numpy()
        space_heating_array = df.iloc[:,1].to_numpy()
        dhw_array = df.iloc[:,2].to_numpy()
        solar_array = df.iloc[:,3].to_numpy()
        thermal_array = df.iloc[:,4].to_numpy()
        Plotting().hourly_plot(electric_array, "Elspesifikt behov", Plotting().GRASS_BLUE)
        df = pd.DataFrame({"Elspesifikt behov" : electric_array})
        #np.savetxt('src/data/output/Elspesifikt.csv', electric_array, delimiter=',')
        with st.expander("Varighetskurve"):
            Plotting().hourly_duration_plot(electric_array, "Elspesifikt behov", Plotting().GRASS_BLUE)

        Plotting().hourly_plot(space_heating_array, "Romoppvarmingsbehov", Plotting().FOREST_BROWN)
        df["Romoppvarmingsbehov"] = space_heating_array
        with st.expander("Varighetskurve"):
            Plotting().hourly_duration_plot(space_heating_array, "Romoppvarmingsbehov", Plotting().FOREST_BROWN)

        df["Tappevannsbehov"] = dhw_array
        Plotting().hourly_plot(dhw_array, "Tappevannsbehov", Plotting().FOREST_PURPLE)
        with st.expander("Varighetskurve"):
            Plotting().hourly_duration_plot(dhw_array, "Tappevannsbehov", Plotting().FOREST_PURPLE)
        
        df["Termisk behov"] = thermal_array
        Plotting().hourly_plot(thermal_array, "Termisk (romoppvarming + tappevann)", Plotting().FOREST_DARK_BROWN)
        with st.expander("Varighetskurve"):
            Plotting().hourly_duration_plot(thermal_array, "Termisk (romoppvarming + tappevann)", Plotting().FOREST_DARK_BROWN)

        df["Solenergi"] = solar_array
        Plotting().hourly_plot(solar_array, "Produsert solenergi", Plotting().SUN_YELLOW)
        #np.savetxt('src/data/output/Produsert solenergi.csv', solar_array, delimiter=',')
        with st.expander("Varighetskurve"):
            Plotting().hourly_duration_plot(solar_array, "Produsert solenergi", Plotting().SUN_YELLOW)
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
    energy_coverage.COVERAGE = st.number_input("Velg energidekningsgrad [%]", min_value=50, value=100, max_value=100, step=2, key="fjernvarmedekning")    
    energy_coverage._coverage_calculation()
    df["S1 - Fjernvarmedekning"] = energy_coverage.covered_arr
    df["S1 - Spisslast"] = energy_coverage.non_covered_arr
    Plotting().hourly_plot(energy_coverage.covered_arr, "Fjernvarmedekning", Plotting().FOREST_GREEN)
    #Plotting().hourly_stack_plot(energy_coverage.covered_arr, energy_coverage.non_covered_arr, "Fjernvarmedekning", "Spisslast", Plotting().FOREST_GREEN, Plotting().GRASS_BLUE)
    #np.savetxt('src/data/output/Fjernvarmedekning.csv', energy_coverage.covered_arr, delimiter=',')
    #np.savetxt('src/data/output/Spisslast.csv', energy_coverage.non_covered_arr, delimiter=',')
    with st.expander("Varighetskurve"):
        Plotting().hourly_stack_plot(np.sort(energy_coverage.covered_arr)[::-1], np.sort(energy_coverage.non_covered_arr)[::-1], "Fjernvarmedekning", "Spisslast", Plotting().FOREST_GREEN, Plotting().GRASS_BLUE)
    st.subheader("Gjenstående elektrisk behov")
    df["S1 - Totalt elektrisk behov"] = electric_array + energy_coverage.non_covered_arr
    Plotting().hourly_plot(electric_array + energy_coverage.non_covered_arr, "Totalt elektrisk behov; uten solproduksjon", Plotting().GRASS_BLUE)
    with st.expander("Varighetskurve"):
        Plotting().hourly_plot(np.sort(electric_array + energy_coverage.non_covered_arr)[::-1], "Totalt elektrisk behov; uten solproduksjon", Plotting().GRASS_BLUE)
    df["S1 - Totalt elektrisk behov med solproduksjon"] = electric_array + energy_coverage.non_covered_arr - solar_array
    Plotting().hourly_negative_plot(electric_array + energy_coverage.non_covered_arr - solar_array, "Totalt elektrisk behov; med solproduksjon", Plotting().GRASS_BLUE)
    with st.expander("Varighetskurve"):
        Plotting().hourly_negative_plot(np.sort(electric_array + energy_coverage.non_covered_arr - solar_array)[::-1], "Totalt elektrisk behov; med solproduksjon", Plotting().GRASS_BLUE)
    with st.expander("Kostnader"):
        months = ["jan", "feb", "mar", "apr", "mai", "jun", "jul", "aug", "sep", "okt", "nov", "des"]
        cost_per_month_el = hour_to_month(ELPRICE*(electric_array + energy_coverage.non_covered_arr - solar_array))
        cost_per_month_districtheating = hour_to_month(DISTRICTHEATING_PRICE*(energy_coverage.covered_arr))
        Plotting().xy_plot_bar_stacked(months, "Måneder i ett år", cost_per_month_el, cost_per_month_districtheating, f"Strøm: {int(round(np.sum(cost_per_month_el),0)):,} kr/år".replace(",", " "), f"Fjernvarme: {int(round(np.sum(cost_per_month_districtheating),0)):,} kr/år".replace(",", " "), 0, MAX_VALUE, "Kostnad [kr]", Plotting().GRASS_BLUE, Plotting().FOREST_GREEN)
        st.write(f"**Sum: {int(round(np.sum(cost_per_month_districtheating) + np.sum(cost_per_month_el),0)):,} kr**".replace(",", " "))
        df1 = pd.DataFrame({"Strøm" : cost_per_month_el, "Fjernvarme" : cost_per_month_districtheating})
    st.markdown("---")
    #--
    st.header("Grunnvarme og solenergi")
    st.subheader("Dekningsgrad")
    energy_coverage = EnergyCoverage(thermal_array)
    energy_coverage.COVERAGE = st.number_input("Velg energidekningsgrad [%]", min_value=50, value=90, max_value=100, step=2, key="grunnvarmedekning")    
    energy_coverage._coverage_calculation()
    df["S2 - Grunnvarmedekning"] = energy_coverage.covered_arr
    df["S2 - Spisslast"] = energy_coverage.non_covered_arr
    Plotting().hourly_stack_plot(energy_coverage.covered_arr, energy_coverage.non_covered_arr, "Grunnvarmedekning", "Spisslast", Plotting().SPRING_GREEN, Plotting().SPRING_BLUE)
    #np.savetxt('src/data/output/Grunnvarmedekning.csv', energy_coverage.covered_arr, delimiter=',')
    #np.savetxt('src/data/output/Spisslast.csv', energy_coverage.non_covered_arr, delimiter=',')
    with st.expander("Varighetskurve"):
        Plotting().hourly_stack_plot(np.sort(energy_coverage.covered_arr)[::-1], np.sort(energy_coverage.non_covered_arr)[::-1], "Grunnvarmedekning", "Spisslast", Plotting().SPRING_GREEN, Plotting().SPRING_BLUE)
    st.subheader("Årsvarmefaktor")
    energy_coverage.COP = st.number_input("Velg COP", min_value=1.0, value=3.5, max_value=5.0, step=0.2)
    energy_coverage._geoenergy_cop_calculation()
    df["S2 - Kompressor"] = energy_coverage.gshp_compressor_arr
    df["S2 - Levert energi fra brønner"] = energy_coverage.gshp_delivered_arr
    Plotting().hourly_triple_stack_plot(energy_coverage.gshp_compressor_arr, energy_coverage.gshp_delivered_arr, energy_coverage.non_covered_arr, "Kompressor", "Levert fra brønn(er)", "Spisslast", Plotting().GRASS_BLUE, Plotting().GRASS_GREEN, Plotting().SPRING_BLUE)
    with st.expander("Varighetskurve"):
        Plotting().hourly_triple_stack_plot(np.sort(energy_coverage.gshp_compressor_arr)[::-1], np.sort(energy_coverage.gshp_delivered_arr)[::-1], np.sort(energy_coverage.non_covered_arr)[::-1], "Kompressor", "Levert fra brønn(er)", "Spisslast", Plotting().GRASS_BLUE, Plotting().GRASS_GREEN, Plotting().SPRING_BLUE)
    st.subheader("Gjenstående elektrisk behov")
    df["S2 - Totalt elektrisk"] = electric_array + energy_coverage.non_covered_arr + energy_coverage.gshp_compressor_arr
    Plotting().hourly_plot(electric_array + energy_coverage.non_covered_arr + energy_coverage.gshp_compressor_arr, "Totalt elektrisk behov; uten solproduksjon", Plotting().GRASS_BLUE)
    with st.expander("Varighetskurve"):
        Plotting().hourly_plot(np.sort(electric_array + energy_coverage.non_covered_arr + energy_coverage.gshp_compressor_arr)[::-1], "Totalt elektrisk behov; uten solproduksjon", Plotting().GRASS_BLUE)
    df["S2 - Totalt elektrisk med solproduksjon"] = electric_array + energy_coverage.non_covered_arr + energy_coverage.gshp_compressor_arr - solar_array
    Plotting().hourly_negative_plot(electric_array + energy_coverage.non_covered_arr + energy_coverage.gshp_compressor_arr - solar_array, "Totalt elektrisk behov; med solproduksjon", Plotting().GRASS_BLUE)
    with st.expander("Varighetskurve"):
        Plotting().hourly_negative_plot(np.sort(electric_array + energy_coverage.non_covered_arr + energy_coverage.gshp_compressor_arr - solar_array)[::-1], "Totalt elektrisk behov; med solproduksjon", Plotting().GRASS_BLUE)
    with st.expander("Kostnader"):
        months = ["jan", "feb", "mar", "apr", "mai", "jun", "jul", "aug", "sep", "okt", "nov", "des"]
        cost_per_month_el = hour_to_month(ELPRICE*(electric_array + energy_coverage.non_covered_arr + energy_coverage.gshp_compressor_arr - solar_array))
        cost_per_month_districtheating = 0
        Plotting().xy_plot_bar_stacked(months, "Måneder i ett år", cost_per_month_el, cost_per_month_districtheating, f"Strøm: {int(round(np.sum(cost_per_month_el),0)):,} kr/år".replace(",", " "), f"Fjernvarme: {int(round(np.sum(cost_per_month_districtheating),0)):,} kr/år".replace(",", " "), 0, MAX_VALUE, "Kostnad [kr]", Plotting().GRASS_BLUE, Plotting().FOREST_GREEN)
        st.write(f"**Sum: {int(round(np.sum(cost_per_month_districtheating) + np.sum(cost_per_month_el),0)):,} kr**".replace(",", " "))
        df2 = pd.DataFrame({"Strøm" : cost_per_month_el, "Fjernvarme" : cost_per_month_districtheating})
    st.markdown("---")
    #np.savetxt('src/data/output/Kompressor.csv', energy_coverage.gshp_compressor_arr, delimiter=',')
    #--
    st.header("Alternativer for spisslast - Akkumuleringstank")
    selected_max_index = st.number_input("Velg maksindeks", value=8623, step = 10)
    max_effect_noncovered = max(energy_coverage.non_covered_arr)
    st.write("**Før akkumulering**")
    Plotting().hourly_plot(energy_coverage.non_covered_arr, "Spisslast", Plotting().SPRING_BLUE, 0, 1.1*max_effect_noncovered, max_effect_noncovered, winterweek=True, max_index=selected_max_index)
    Plotting().hourly_plot(energy_coverage.non_covered_arr, "Spisslast", Plotting().SPRING_BLUE, 0, 1.1*max_effect_noncovered, max_effect_noncovered, winterweek=0)
    with st.expander("Varighetskurve"):
        Plotting().hourly_plot(np.sort(energy_coverage.non_covered_arr)[::-1], "Spisslast", Plotting().SPRING_BLUE, 0, 1.1*max_effect_noncovered, max_effect_noncovered)
    st.write("**Etter akkumulering**")
    effect_reduction = st.number_input("Ønsket effektreduksjon [kW]", value=int(round(max_effect_noncovered/10,0)), step=10)
    if effect_reduction > max_effect_noncovered:
        st.warning("Effektreduksjon kan ikke være høyere enn effekttopp")
        st.stop()
    TO_TEMP = st.number_input("Turtemperatur [°C]", value = 60)
    FROM_TEMP = st.number_input("Returtemperatur [°C]", value = 40)
    peakshaving_arr, peakshaving_effect = peakshaving(energy_coverage.non_covered_arr, effect_reduction, TO_TEMP, FROM_TEMP)
    Plotting().hourly_plot(peakshaving_arr, "Spisslast", Plotting().SPRING_BLUE, 0, 1.1*max_effect_noncovered, peakshaving_effect, winterweek=True, max_index=selected_max_index)
    Plotting().hourly_plot(peakshaving_arr, "Spisslast", Plotting().SPRING_BLUE, 0, 1.1*max_effect_noncovered, peakshaving_effect, winterweek=0)
    with st.expander("Varighetskurve"):
        Plotting().hourly_plot(np.sort(peakshaving_arr)[::-1], "Spisslast", Plotting().SPRING_BLUE, 0, 1.1*max_effect_noncovered, peakshaving_effect)
    st.write("**Oppsummert**")
    Plotting().hourly_double_plot(energy_coverage.non_covered_arr, peakshaving_arr, "Spisslast (opprinnelig)", "Spisslast med akkumuleringstank", Plotting().SPRING_BLUE, Plotting().GRASS_BLUE, winterweek=True, max_index=selected_max_index)
    Plotting().hourly_double_plot(energy_coverage.non_covered_arr, peakshaving_arr, "Spisslast (opprinnelig)", "Spisslast med akkumuleringstank", Plotting().SPRING_BLUE, Plotting().GRASS_BLUE, winterweek=True, hours=100, max_index=selected_max_index)
    Plotting().hourly_double_plot(energy_coverage.non_covered_arr, peakshaving_arr, "Spisslast (opprinnelig)", "Spisslast med akkumuleringstank", Plotting().SPRING_BLUE, Plotting().GRASS_BLUE, winterweek=0)
    st.markdown("---")
    #--
    st.header("Fjernvarme/grunnvarme/solenergi")
    st.subheader("Dekningsgrad, grunnvarme/romoppvarming")
    energy_coverage = EnergyCoverage(space_heating_array)
    energy_coverage.COVERAGE = st.number_input("Velg energidekningsgrad for romoppvarming [%]", min_value=50, value=70, max_value=100, step=2, key="fjernvarme/grunnvarme/solenergi")    
    energy_coverage._coverage_calculation()
    df["S3 - Grunnvarmedekning"] = energy_coverage.covered_arr
    df["S3 - Spisslast"] = energy_coverage.non_covered_arr
    Plotting().hourly_stack_plot(energy_coverage.covered_arr, energy_coverage.non_covered_arr, "Grunnvarmedekning", "Spisslast", Plotting().FOREST_BROWN, Plotting().SPRING_BLUE)
    with st.expander("Varighetskurve"):
        Plotting().hourly_stack_plot(np.sort(energy_coverage.covered_arr)[::-1], np.sort(energy_coverage.non_covered_arr)[::-1], "Grunnvarmedekning", "Spisslast", Plotting().FOREST_BROWN, Plotting().SPRING_BLUE)
    st.subheader("Årsvarmefaktor, grunnvarme/romoppvarming")
    energy_coverage.COP = st.number_input("Velg COP", min_value=1.0, value=3.5, max_value=5.0, step=0.2, key="fjernvarme/grunnvarme/solenergi-cop")
    energy_coverage._geoenergy_cop_calculation()
    df["S3 - Kompressor"] = energy_coverage.gshp_compressor_arr
    df["S3 - Levert fra brønner"] = energy_coverage.gshp_delivered_arr
    Plotting().hourly_triple_stack_plot(energy_coverage.gshp_compressor_arr, energy_coverage.gshp_delivered_arr, energy_coverage.non_covered_arr, "Kompressor", "Levert fra brønn(er)", "Spisslast", Plotting().GRASS_BLUE, Plotting().GRASS_GREEN, Plotting().SPRING_BLUE)
    with st.expander("Varighetskurve"):
        Plotting().hourly_triple_stack_plot(np.sort(energy_coverage.gshp_compressor_arr)[::-1], np.sort(energy_coverage.gshp_delivered_arr)[::-1], np.sort(energy_coverage.non_covered_arr)[::-1], "Kompressor", "Levert fra brønn(er)", "Spisslast", Plotting().GRASS_BLUE, Plotting().GRASS_GREEN, Plotting().SPRING_BLUE)
    st.subheader("Konsept")
    Plotting().hourly_triple_stack_plot(dhw_array, energy_coverage.covered_arr, energy_coverage.non_covered_arr, "Tappevann(fjernvarme)", "Romoppvarming(grunnvarme)", "Romoppvarmingsspisslast(fjernvarme)", 
    Plotting().FOREST_PURPLE, Plotting().SPRING_GREEN, Plotting().SPRING_BLUE)
    Plotting().hourly_quad_stack_plot(dhw_array, energy_coverage.gshp_compressor_arr, energy_coverage.gshp_delivered_arr, energy_coverage.non_covered_arr, "Tappevann(fjernvarme)", "Kompressor(grunnvarme)", "Levert fra brønner(grunnvarme)", "Romoppvarmingspisslast(fjernvarme)", 
    Plotting().FOREST_PURPLE, Plotting().GRASS_BLUE, Plotting().GRASS_GREEN, Plotting().SPRING_BLUE)
    with st.expander("Varighetskurve"):
        Plotting().hourly_quad_stack_plot(np.sort(dhw_array)[::-1], np.sort(energy_coverage.gshp_compressor_arr)[::-1], np.sort(energy_coverage.gshp_delivered_arr)[::-1], np.sort(energy_coverage.non_covered_arr)[::-1], "Tappevann(fjernvarme)", "Kompressor(grunnvarme)", "Levert fra brønner(grunnvarme)", "Romoppvarmingspisslast(fjernvarme)", 
    Plotting().FOREST_PURPLE, Plotting().GRASS_BLUE, Plotting().GRASS_GREEN, Plotting().SPRING_BLUE)
    st.subheader("Gjenstående elektrisk behov")
    df["S3 - Totalt elektrisk"] = electric_array + energy_coverage.gshp_compressor_arr
    df["S3 - Totalt elektrisk med solproduksjon"] = electric_array + energy_coverage.gshp_compressor_arr - solar_array
    Plotting().hourly_plot(electric_array + energy_coverage.gshp_compressor_arr, "Totalt elektrisk behov; uten solproduksjon", Plotting().GRASS_BLUE)
    Plotting().hourly_negative_plot(electric_array + energy_coverage.gshp_compressor_arr - solar_array, "Totalt elektrisk behov; med solproduksjon", Plotting().GRASS_BLUE)
    with st.expander("Kostnader"):
        months = ["jan", "feb", "mar", "apr", "mai", "jun", "jul", "aug", "sep", "okt", "nov", "des"]
        cost_per_month_el = hour_to_month(ELPRICE*(electric_array + energy_coverage.gshp_compressor_arr - solar_array))
        cost_per_month_districtheating = hour_to_month(DISTRICTHEATING_PRICE*(energy_coverage.non_covered_arr + dhw_array))
        Plotting().xy_plot_bar_stacked(months, "Måneder i ett år", cost_per_month_el, cost_per_month_districtheating, f"Strøm: {int(round(np.sum(cost_per_month_el),0)):,} kr/år".replace(",", " "), f"Fjernvarme: {int(round(np.sum(cost_per_month_districtheating),0)):,} kr/år".replace(",", " "), 0, MAX_VALUE, "Kostnad [kr]", Plotting().GRASS_BLUE, Plotting().FOREST_GREEN)
        st.write(f"**Sum: {int(round(np.sum(cost_per_month_districtheating) + np.sum(cost_per_month_el),0)):,} kr**".replace(",", " "))
        df3 = pd.DataFrame({"Strøm" : cost_per_month_el, "Fjernvarme" : cost_per_month_districtheating})
    #np.savetxt('src/data/output/Fjernvarme_3.csv', (dhw_array + energy_coverage.non_covered_arr), delimiter=',')
    #np.savetxt('src/data/output/Kompressor_3.csv', (energy_coverage.gshp_compressor_arr), delimiter=',')
    df.to_csv("src/data/output/hei.csv", sep=";")

    # create fake dataframes
#    df1 = pd.DataFrame(np.random.rand(4, 5),
#                    index=["A", "B", "C", "D"],
#                    columns=["I", "J", "K", "L", "M"])
#    df2 = pd.DataFrame(np.random.rand(4, 5),
#                    index=["A", "B", "C", "D"],
#                    columns=["I", "J", "K", "L", "M"])
#    df3 = pd.DataFrame(np.random.rand(4, 5),
#                    index=["A", "B", "C", "D"], 
#                    columns=["I", "J", "K", "L", "M"])

    # Then, just call :
    Plotting().plot_clustered_stacked([df1, df2, df3],["Scenario 1", "Scenario 2", "Scenario 3"], color=[Plotting().GRASS_BLUE, Plotting().FOREST_GREEN])

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
    