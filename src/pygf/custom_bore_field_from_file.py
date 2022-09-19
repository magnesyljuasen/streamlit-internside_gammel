# -*- coding: utf-8 -*-
""" Example of definition of a bore field using custom borehole positions.

"""
import streamlit as st
import pygfunction as gt


def custom_bore_field_from_file_app():
    # -------------------------------------------------------------------------
    # Parameters
    # -------------------------------------------------------------------------

    # Filepath to bore field text file
    filename = 'src\pygf\data\custom_field_32_boreholes.txt'

    # -------------------------------------------------------------------------
    # Borehole field
    # -------------------------------------------------------------------------

    # Build list of boreholes
    field = gt.boreholes.field_from_file(filename)

    # -------------------------------------------------------------------------
    # Draw bore field
    # -------------------------------------------------------------------------

    st.pyplot(gt.boreholes.visualize_field(field))

    return
