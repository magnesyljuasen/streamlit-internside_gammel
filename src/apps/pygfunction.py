import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.constants import pi
from scipy.interpolate import interp1d
from scipy.signal import fftconvolve
import pygfunction as gt

from src.pygf.bore_field_thermal_resistance import bore_field_thermal_resistance_app
from src.pygf.comparison_gfunction_solvers import comparison_gfunction_solvers_app
from src.pygf.comparison_load_aggregation import comparison_load_aggregation_app
from src.pygf.custom_bore_field_from_file import custom_bore_field_from_file_app
from src.pygf.custom_bore_field import custom_bore_field_app
from src.pygf.custom_borehole import custom_borehole_app
from src.pygf.discretize_boreholes import discretize_boreholes_app
from src.pygf.equal_inlet_temperature import equal_inlet_temperature_app
from src.pygf.fluid_temperature_multiple_boreholes import fluid_temperature_multiple_boreholes_app
from src.pygf.fluid_temperature import fluid_temperature_app
from src.pygf.inclined_boreholes import inclined_boreholes_app
from src.pygf.load_aggregation import load_aggregation_app
from src.pygf.mixed_inlet_conditions import mixed_inlet_conditions_app
from src.pygf.multiple_independent_Utubes import multiple_independent_Utubes_app
from src.pygf.multipole_temperature import multipole_temperature_app
from src.pygf.regular_bore_field import regular_bore_field_app
from src.pygf.unequal_segments import unequal_segments_app
from src.pygf.uniform_heat_extraction_rate import uniform_heat_extraction_rate_app
from src.pygf.uniform_temperature import uniform_temperature_app

from src.pygf.simulation import simulation_app

def pygfunction_app():
    st.title("Beregning")
    simulation_app()
    st.markdown("---")
    st.title("Annet")
    if st.checkbox("Brønndesign og plassering"):
        custom_bore_field_from_file_app()
        st.markdown("---")
        custom_bore_field_app()
        st.markdown("---")
        custom_borehole_app()
        st.markdown("---")
        inclined_boreholes_app()
        st.markdown("---")
        regular_bore_field_app()
        st.markdown("---")
        multipole_temperature_app()

    if st.checkbox("Simuleringer"):
        fluid_temperature_multiple_boreholes_app()
        st.markdown("---")
        fluid_temperature_app()
        st.markdown("---")
        load_aggregation_app()
        st.markdown("---")
        #comparison_load_aggregation_app() #kjøretid

    if st.checkbox("Annet"):
        bore_field_thermal_resistance_app()
        st.markdown("---")
        comparison_gfunction_solvers_app()
        st.markdown("---")
        equal_inlet_temperature_app()
        st.markdown("---")
        mixed_inlet_conditions_app()
        st.markdown("---")
        multiple_independent_Utubes_app()
        st.markdown("---")
        unequal_segments_app()
        st.markdown("---")
        uniform_heat_extraction_rate_app()
        st.markdown("---")
        uniform_temperature_app()
        st.markdown("---")
        #discretize_boreholes_app() #kjøretid












def borehole_field():
    st.header("Brønndesign")
    D = st.number_input("Borehole buried depth (m)", value = 0) 
    H = st.number_input("Borehole length (m)", value = 300, step = 10) 
    r_b = st.number_input("Borehole radius (m)", 0.075) 
    pos = [
        (0,0),
        (15,0),
        #(30,0)
        ]
    field = [gt.boreholes.Borehole(H, D, r_b, x, y) for (x, y) in pos]
    st.pyplot(gt.boreholes.visualize_field(field))
    return field, D, H, r_b 

def load(x, YEARS):
    stacked_arr = []
    arr = pd.read_csv(r"src/data/behov.csv").to_numpy()
    for i in range(0, YEARS):
        stacked_arr.append(arr)
    stacked_arr = np.array(stacked_arr)
    arr = np.vstack([stacked_arr]).flatten()
    return arr

def constants():
    st.header("Parametere")
    YEARS = st.number_input("Simuleringsperiode", value = 20, step = 1) #Period 
    K_S = st.number_input("Effektiv varmeledningsevne (W/m.K)", value = 3.0, step = 0.1) #Ground thermal conductivity (W/m.K)
    T_G = st.number_input("Uforstyrret temperatur (degC)", value = 6.0, step = 0.2) #Ground thermal conductivity (W/m.K)
    ALPHA = 1.0e-6 #Ground thermal diffusivity (m2/s)
    return YEARS, ALPHA, K_S, T_G

def calculation(YEARS, ALPHA, K_S, T_G):
    options = {'nSegments': 8,'disp': True} #g-Function calculation options

    #Simulation parameters
    dt = 3600. #Time step (s)
    tmax = YEARS *8760. * 3600. #Maximum time (s)
    Nt = int(np.ceil(tmax/dt)) #Number of time steps
    time = dt * np.arange(1, Nt+1)

    Q_b = load(time/3600., YEARS) #Evaluate heat extraction rate
    LoadAgg = gt.load_aggregation.ClaessonJaved(dt, tmax) #Load aggregation scheme

    #Calculate g-function
    boreField, D, H, r_b = borehole_field() #Initialize borehole field
    time_req = LoadAgg.get_times_for_simulation() #Get time values needed for g-function evaluation
    gFunc = gt.gfunction.gFunction(boreField, ALPHA, time=time_req, options=options) #Calculate g-function
    LoadAgg.initialize(gFunc.gFunc/(2*pi*K_S)) #Initialize load aggregation scheme

    #Simulation
    T_b = np.zeros(Nt)
    for i, (t, Q_b_i) in enumerate(zip(time, Q_b)):
        LoadAgg.next_time_step(t) #Increment time step by (1)
        LoadAgg.set_current_load(Q_b_i/H) #Apply current load
        deltaT_b = LoadAgg.temporal_superposition() #Evaluate borehole wall temeprature
        T_b[i] = T_G - deltaT_b

    #Calculate exact solution from convolution in the Fourier domain
    dQ = np.zeros(Nt) #Heat extraction rate increment
    dQ[0] = Q_b[0] #Heat extraction rate increment
    dQ[1:] = Q_b[1:] - Q_b[:-1] #Heat extraction rate increment
    g = interp1d(time_req, gFunc.gFunc)(time) #Interpolated g-function
    T_b_exact = T_G - fftconvolve(dQ, g/(2.0*pi*K_S*H), mode='full')[0:Nt] #Convolution in Fourier domain

    #Plot results
    st.header("Resultater")
    fig = gt.utilities._initialize_figure() #Configure figure and axes
 
    ax1 = fig.add_subplot(311)
    ax1.set_xlabel(r'$t$ [hours]')
    ax1.set_ylabel(r'$Q_b$ [W]')
    gt.utilities._format_axes(ax1)
    hours = np.arange(1, Nt+1) * dt / 3600.
    ax1.plot(hours, Q_b)

    ax2 = fig.add_subplot(312)
    ax2.set_xlabel(r'$t$ [hours]')
    ax2.set_ylabel(r'$T_b$ [degC]')
    gt.utilities._format_axes(ax2)
    ax2.plot(hours, T_b)
    ax2.plot(hours, T_b_exact, 'k.')

    ax3 = fig.add_subplot(313)
    ax3.set_xlabel(r'$t$ [hours]')
    ax3.set_ylabel(r'Error [degC]')
    gt.utilities._format_axes(ax3)
    ax3.plot(hours, T_b - T_b_exact)

    plt.tight_layout()
    st.pyplot(plt)

#def pygfunction_app():
    #st.title("Beregning")
    #YEARS, ALPHA, K_S, T_G = constants()
    #calculation(YEARS, ALPHA, K_S, T_G)
    
    return