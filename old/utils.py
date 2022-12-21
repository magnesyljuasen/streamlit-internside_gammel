import altair as alt
import numpy as np
import pandas as pd
import streamlit as st



class Plotting:
    def __init__(self):
        self.FOREST_GREEN = "#1d3c34"
        self.SUN_YELLOW = "#FFC358"

    
    def hourly_plot(self, y, COLOR, name):
        
        x = np.arange(8760)
        source = pd.DataFrame({"x": x, "y": y})

        c = alt.Chart(source).mark_bar(size=0.75, color= COLOR).encode(
            x=alt.X("x", scale=alt.Scale(domain=[0,8760]), title="Timer i ett år"),
            y=alt.Y("y", title="kW"),
            #y=alt.Y("y", scale=alt.Scale(domain=[0,800]), title="kW"),
            color=alt.Color(legend=alt.Legend(orient='top', direction='vertical', title=None))).configure_axis(
    grid=True
)
        st.altair_chart(c, use_container_width=True)

    def xy_plot(self, x, y, x_label, y_label, name, y_min, y_max):
        COLOR = self.FOREST_GREEN
        
        source = pd.DataFrame({"x": x, "y": y})

        c = alt.Chart(source).mark_line().encode(
            x=alt.X("x", scale=alt.Scale(domain=[0,len(x)]), title=x_label),
            y=alt.Y("y", scale=alt.Scale(domain=[y_min, y_max]), title=y_label),
            color = alt.value(COLOR)).properties(title=name)

        st.altair_chart(c, use_container_width=True)