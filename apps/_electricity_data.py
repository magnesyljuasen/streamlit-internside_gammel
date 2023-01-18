import streamlit as st
import pandas as pd


def power_grid():
    st.button("Refresh")
    st.title("El-nett")
    st.header("Østmarka")
    df1 = pd.read_excel("src/data/input/el_nett_trondheim.xlsx", sheet_name=0)
    df2 = pd.read_excel("src/data/input/el_nett_trondheim.xlsx", sheet_name=1)
    #st.write(df1)
    #st.write(df2)