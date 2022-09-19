# -*- coding: utf-8 -*-
""" Example of simulation of a geothermal system with multiple boreholes.

    The g-function of a bore field is calculated for boundary condition of
    mixed inlet fluid temperature into the boreholes. Then, the borehole
    wall temperature variations resulting from a time-varying load profile
    are simulated using the aggregation method of Claesson and Javed (2012).
    Predicted outlet fluid temperatures of double U-tube borehole are
    evaluated.

"""
import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
from scipy.constants import pi
import pygfunction as gt
import pandas as pd

class Constants:
    def __init__(self):
        pass

    def shape(self):
        N_1 = st.number_input("Antall brønner (X)", value = 4, step = 1)
        N_2 = st.number_input("Antall brønner (Y)", value = 6, step = 1)
        N_b = N_1 * N_2
        return N_1, N_2, N_b

    def set_borehole_dimensions(self):
        st.header("Brønnplassering")
        D = 0
        r_b = st.number_input("Diameter", value = 150)/2000
        H = st.number_input("Dybde", value = 300, step = 10)
        B = st.number_input("Avstand mellom brønner", value = 15, step = 1)
        selected_field = st.selectbox("Konfigurasjon", options = ["Rektangulær", "Boks", "U", "L", "Sirkulær", "Linje", "Fra fil"])
                    
        if selected_field == "Rektangulær":
            N_1, N_2, N_b = self.shape() 
            field = gt.boreholes.rectangle_field(N_1, N_2, B, B, H, D, r_b)
        if selected_field == "Boks": 
            N_1, N_2, N_b = self.shape()
            field = gt.boreholes.box_shaped_field(N_1, N_2, B, B, H, D, r_b)
        if selected_field == "U":
            N_1, N_2, N_b = self.shape()
            field = gt.boreholes.U_shaped_field(N_1, N_2, B, B, H, D, r_b)
        if selected_field == "L":
            N_1, N_2, N_b = self.shape()
            field = gt.boreholes.L_shaped_field(N_1, N_2, B, B, H, D, r_b)
        if selected_field == "Sirkulær":
            N_b = st.number_input("Antall borehull", value = 10, step = 1)
            field = gt.boreholes.circle_field(N_b, B, H, D, r_b)
        st.pyplot(gt.boreholes.visualize_field(field))
        return D, H, r_b, B, N_b, field
        
    def borehole_dimensions(self):
        # Borehole dimensions
        D = 0.0             # Borehole buried depth (m)
        H = 300.0           # Borehole length (m)
        r_b = 0.075         # Borehole radius (m)
        B = 7.5             # Borehole spacing (m)

        # Rectangular field
        N_1 = 4             # Number of boreholes in the x-direction (columns)
        N_2 = 3             # Number of boreholes in the y-direction (rows)
        N_b = N_1 * N_2

        # Circular field
        N_b = 1     # Number of boreholes

        # -------------------------------------------------------------------------
        # Borehole fields
        # -------------------------------------------------------------------------

        # Rectangular field of 4 x 3 boreholes
        rectangularField = gt.boreholes.rectangle_field(N_1, N_2, B, B, H, D, r_b)

        # Box-shaped field of 4 x 3 boreholes
        boxField = gt.boreholes.box_shaped_field(N_1, N_2, B, B, H, D, r_b)

        # U-shaped field of 4 x 3 boreholes
        UField = gt.boreholes.U_shaped_field(N_1, N_2, B, B, H, D, r_b)

        # L-shaped field of 4 x 3 boreholes
        LField = gt.boreholes.L_shaped_field(N_1, N_2, B, B, H, D, r_b)

        # Circular field of 8 boreholes
        circleField = gt.boreholes.circle_field(N_b, B, H, D, r_b)

        # -------------------------------------------------------------------------
        # Draw bore fields
        # -------------------------------------------------------------------------
        for field in [rectangularField, boxField, UField, LField, circleField]:
            st.pyplot(gt.boreholes.visualize_field(field))
        return D, H, r_b, B, N_b, field

    def pipe_dimensions(self):
        r_out = 0.0211      # Pipe outer radius (m)
        r_in = 0.0147       # Pipe inner radius (m)
        D_s = 0.052         # Shank spacing (m)
        epsilon = 1.0e-6    # Pipe roughness (m)
        return r_out, r_in, D_s, epsilon

    def set_ground_properties(self):
        st.header("Grunnforhold")
        alpha = 1.0e-6      # Ground thermal diffusivity (m2/s)
        k_s = st.number_input("Effektiv varmeledningsevne (W/m.K)", value = 3.0, step = 0.2)           
        T_g = st.number_input("Uforstyrret temperatur (grader)", value = 8.0, step = 0.2)
        return alpha, k_s, T_g

    def ground_properties(self):
        alpha = 1.0e-6      # Ground thermal diffusivity (m2/s)
        k_s = 3.0           # Ground thermal conductivity (W/m.K)
        T_g = 8.0          # Undisturbed ground temperature (degC)
        return alpha, k_s, T_g

    def other_properties(self):
        k_g = 1.0           # Grout thermal conductivity (W/m.K)
        k_p = 0.4           # Pipe thermal conductivity (W/m.K)
        return k_g, k_p

class Fluid:
    def __init__(self) -> None:
        pass

    def flow_calculation(self, N):
        # Fluid properties
        m_flow_borehole = 0.50      # Total fluid mass flow rate per borehole (kg/s)
        m_flow_network = m_flow_borehole*N    # Total fluid mass flow rate (kg/s)
        # The fluid is propylene-glycol (20 %) at 20 degC
        fluid = gt.media.Fluid('MPG', 20.)
        cp_f = fluid.cp     # Fluid specific isobaric heat capacity (J/kg.K)
        rho_f = fluid.rho   # Fluid density (kg/m3)
        mu_f = fluid.mu     # Fluid dynamic viscosity (kg/m.s)
        k_f = fluid.k       # Fluid thermal conductivity (W/m.K)
        return cp_f, rho_f, mu_f, k_f, m_flow_network, m_flow_borehole

class Simulation:
    def __init__(self):
        self.years = 5

    def parameters(self):
        # Simulation parameters
        dt = 3600.                  # Time step (s)
        tmax = self.years * 8760. * 3600.     # Maximum time (s)
        Nt = int(np.ceil(tmax/dt))  # Number of time steps
        time = dt * np.arange(1, Nt+1)

        # Load aggregation scheme
        LoadAgg = gt.load_aggregation.ClaessonJaved(dt, tmax)

        # g-Function calculation options
        options = {'nSegments': 8, 'disp': True}
        return dt, tmax, Nt, time, LoadAgg, options

class Pipes:
    def __init__(self, D_s):
        self.D_s = D_s

    def double_pipe(self):
        # Pipe positions
        # Double U-tube [(x_in1, y_in1), (x_in2, y_in2), (x_out1, y_out1), (x_out2, y_out2)]
        pos_double = [(-self.D_s, 0.), (0., -self.D_s), (self.D_s, 0.), (0., self.D_s)]
        return pos_double

    def single_pipe(self):
        # Single U-tube [(x_in, y_in), (x_out, y_out)]
        pos_single = [(-self.D_s, 0.), (self.D_s, 0.)]
        return pos_single
        


def simulation_app():
    # -------------------------------------------------------------------------
    # Simulation parameters
    # -------------------------------------------------------------------------
    constants = Constants()
    r_out, r_in, D_s, epsilon = constants.pipe_dimensions()
    alpha, k_s, T_g = constants.set_ground_properties()
    k_g, k_p = constants.other_properties()
    D, H, r_b, B, N_b, field = constants.set_borehole_dimensions()

    fluid = Fluid()
    cp_f, rho_f, mu_f, k_f, m_flow_network, m_flow_borehole = fluid.flow_calculation(N_b)

    simulation = Simulation()
    dt, tmax, Nt, time, LoadAgg, options = simulation.parameters()

    pipes = Pipes(D_s)
    pos_double = pipes.double_pipe()

    # -------------------------------------------------------------------------
    # Initialize bore field and pipe models
    # -------------------------------------------------------------------------

    # Pipe thermal resistance
    R_p = gt.pipes.conduction_thermal_resistance_circular_pipe(r_in, r_out, k_p)

    # Fluid to inner pipe wall thermal resistance (Double U-tube in parallel)
    m_flow_pipe = m_flow_borehole/2
    h_f = gt.pipes.convective_heat_transfer_coefficient_circular_pipe(m_flow_pipe, r_in, mu_f, rho_f, k_f, cp_f, epsilon)
    R_f = 1.0/(h_f*2*pi*r_in)

    st.header("Borehullsmotstand")
    st.subheader(f"* Pipe: {round(R_p, 3)}")
    st.subheader(f"* Fluid-Pipe: {round(R_f, 3)} ")

    # Double U-tube (parallel), same for all boreholes in the bore field
    UTubes = []
    for borehole in field:
        UTube = gt.pipes.MultipleUTube(pos_double, r_in, r_out, borehole, k_s, k_g, R_f + R_p, nPipes=2, config='parallel')
        UTubes.append(UTube)
    # Build a network object from the list of UTubes
    network = gt.networks.Network(field, UTubes, m_flow_network=m_flow_network, cp_f=cp_f)

    if st.button("Start beregning"):
        st.markdown("---")
        st.header("Simulering")
        # -------------------------------------------------------------------------
        # Calculate g-function
        # -------------------------------------------------------------------------

        # Get time values needed for g-function evaluation
        time_req = LoadAgg.get_times_for_simulation()
        # Calculate g-function
        my_bar = st.progress(0)
        gFunc = gt.gfunction.gFunction(network, alpha, time=time_req, boundary_condition='MIFT', options=options)
        # Initialize load aggregation scheme
        LoadAgg.initialize(gFunc.gFunc/(2*pi*k_s))
        my_bar.progress(33)

        # -------------------------------------------------------------------------
        # Simulation
        # -------------------------------------------------------------------------

        # Evaluate heat extraction rate
        #Q_tot = nBoreholes*synthetic_load(time/3600.)
        #Q_tot = nBoreholes*load(time/3600., simulation.years)
        Q_tot = load(time/3600., simulation.years)

        T_b = np.zeros(Nt)
        T_f_in = np.zeros(Nt)
        T_f_out = np.zeros(Nt)
        for i, (t, Q_i) in enumerate(zip(time, Q_tot)):
            # Increment time step by (1)
            LoadAgg.next_time_step(t)

            # Apply current load (in watts per meter of borehole)
            Q_b = Q_i/N_b
            LoadAgg.set_current_load(Q_b/H)

            # Evaluate borehole wall temperature
            deltaT_b = LoadAgg.temporal_superposition()
            T_b[i] = T_g - deltaT_b

            # Evaluate inlet fluid temperature (all boreholes are the same)
            T_f_in[i] = network.get_network_inlet_temperature(Q_tot[i], T_b[i], m_flow_network, cp_f, nSegments=1)

            # Evaluate outlet fluid temperature
            T_f_out[i] = network.get_network_outlet_temperature(T_f_in[i], T_b[i], m_flow_network, cp_f, nSegments=1)

        # -------------------------------------------------------------------------
        # Plot hourly heat extraction rates and temperatures
        # -------------------------------------------------------------------------
        my_bar.progress(66)

        # Configure figure and axes
        fig = gt.utilities._initialize_figure()

        ax1 = fig.add_subplot(211)
        # Axis labels
        ax1.set_xlabel(r'Time [hours]')
        ax1.set_ylabel(r'Total heat extraction rate [W]')
        gt.utilities._format_axes(ax1)

        # Plot heat extraction rates
        hours = np.arange(1, Nt+1) * dt / 3600.
        ax1.plot(hours, Q_tot)

        ax2 = fig.add_subplot(212)
        # Axis labels
        ax2.set_xlabel(r'Time [hours]')
        ax2.set_ylabel(r'Temperature [degC]')
        gt.utilities._format_axes(ax2)

        # Plot temperatures
        ax2.plot(hours, T_b, label='Borehole wall')
        ax2.plot(hours, T_f_out, '-.', label='Outlet, double U-tube (parallel)')
        ax2.legend()

        # Adjust to plot window
        plt.tight_layout()
        st.pyplot(plt)
        my_bar.progress(100)


        # -------------------------------------------------------------------------
        # Plot fluid temperature profiles
        # -------------------------------------------------------------------------

        # Evaluate temperatures at nz evenly spaced depths along the borehole
        # at the (it+1)-th time step
        nz = 20
        it = 8724
        z = np.linspace(0., H, num=nz)
        T_f = UTubes[0].get_temperature(z, T_f_in[it], T_b[it], m_flow_borehole, cp_f)


        # Configure figure and axes
        fig = gt.utilities._initialize_figure()

        ax3 = fig.add_subplot(111)
        # Axis labels
        ax3.set_xlabel(r'Temperature [degC]')
        ax3.set_ylabel(r'Depth from borehole head [m]')
        gt.utilities._format_axes(ax3)

        # Plot temperatures
        pltFlu = ax3.plot(T_f, z, 'b-', label='Fluid')
        pltWal = ax3.plot(np.array([T_b[it], T_b[it]]), np.array([0., H]), 'k--', label='Borehole wall')
        ax3.legend(handles=[pltFlu[0]]+pltWal)

        # Reverse y-axes
        ax3.set_ylim(ax3.get_ylim()[::-1])
        # Adjust to plot window
        plt.tight_layout()
        st.pyplot(plt)

        return


def synthetic_load(x):
    """
    Synthetic load profile of Bernier et al. (2004).

    Returns load y (in watts) at time x (in hours).
    """
    A = 2000.0
    B = 2190.0
    C = 80.0
    D = 2.0
    E = 0.01
    F = 0.0
    G = 0.95

    func = (168.0-C)/168.0
    for i in [1, 2, 3]:
        func += 1.0/(i*pi)*(np.cos(C*pi*i/84.0)-1.0) \
                          *(np.sin(pi*i/84.0*(x-B)))
    func = func*A*np.sin(pi/12.0*(x-B)) \
           *np.sin(pi/4380.0*(x-B))

    y = func + (-1.0)**np.floor(D/8760.0*(x-B))*abs(func) \
      + E*(-1.0)**np.floor(D/8760.0*(x-B))/np.sign(np.cos(D*pi/4380.0*(x-F))+G)
    return -y

def load(x, YEARS):
    stacked_arr = []
    arr = pd.read_csv(r"src/data/behov.csv").to_numpy()
    for i in range(0, YEARS):
        stacked_arr.append(arr)
    stacked_arr = np.array(stacked_arr)
    arr = np.vstack([stacked_arr]).flatten()
    return arr

