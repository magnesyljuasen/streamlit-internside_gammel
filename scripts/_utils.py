import requests
import streamlit.components.v1 as components
import streamlit as st
import requests
from datetime import date
import numpy as np
import pandas as pd
import altair as alt
import base64

import matplotlib.pyplot as plt
import matplotlib as mpl
from cycler import cycler
import matplotlib.dates as mdates
plt.rcParams["figure.figsize"] = (10,5)

#  Hjelpefunksjon - Render SVG
def render_svg(svg):
    b64 = base64.b64encode(svg.encode('utf-8')).decode("utf-8")
    html = r'<img src="data:image/svg+xml;base64,%s"/>' % b64
    st.write(html, unsafe_allow_html=True)


#  Hjelpefunksjon - Fra timeserie til månedlig
def hour_to_month(hourly_array):
    monthly_array = []
    summed = 0
    for i in range(0, len(hourly_array)):
        verdi = hourly_array[i]
        if np.isnan(verdi):
            verdi = 0
        summed = verdi + summed
        if i == 744 or i == 1416 or i == 2160 or i == 2880 \
                or i == 3624 or i == 4344 or i == 5088 or i == 5832 \
                or i == 6552 or i == 7296 or i == 8016 or i == 8759:
            monthly_array.append(int(summed))
            summed = 0
    return monthly_array 


#  Hjelpefunksjon - Load Lottie
def load_lottie(url: str):
    r = requests.get(url)
    if r.status_code!= 200:
        return None
    return r.json()


#  Hjelpeklasse - Twitter
class Tweet(object):
    def __init__(self, s, embed_str=False):
        if not embed_str:
            # Use Twitter's oEmbed API
            # https://dev.twitter.com/web/embedded-tweets
            api = "https://publish.twitter.com/oembed?url={}".format(s)
            response = requests.get(api)
            self.text = response.json()["html"]
        else:
            self.text = s#

    def _repr_html_(self):
        return self.text

    def component(self):
        return components.html(self.text, height=400)


#  Hjelpefunksjon - dagens strømpris
def elspot_today():
    url = "https://norway-power.ffail.win/" 
    url = "https://playground-norway-power.ffail.win" #bruk denne for testing
    today = date.today()
    zones = ["NO1", "NO2", "NO3", "NO4", "NO5"]
    prize_zone_array = []
    for i, zone in enumerate(zones):
        r = requests.get(f"{url}/?zone={zone}&date={today}&key=b0235f2e-7ddc-4bf1-a054-5dffb4ec037a")
        if r.status_code == 200:
            price_array = []
            for i in range(0, 24):
                NOK_per_kWh = list(r.json().values())[i]["NOK_per_kWh"]
                price_array.append(NOK_per_kWh)
            prize_zone_array.append(price_array)
    options = ["NO1", "NO2", "NO3", "NO4", "NO5"]
    selected_region = st.selectbox("Velg strømregion", options)
    df = {
        "NO1" : 0,
        "NO2" : 1,
        "NO3" : 2,
        "NO4" : 3,
        "NO5" : 4
    }
    chart_data = pd.DataFrame({selected_region: prize_zone_array[df[selected_region]],}).to_numpy().flatten()
    Plotting().xy_plot(np.arange(0, len(chart_data), 1), 0, 24, f"Timer i ett døgn, {today}", chart_data, 0, max(chart_data), "Elspotpris [kr]", Plotting().FOREST_GREEN)
    st.metric(label = "Gjennomsnittlig strømpris", value = f"{round(np.mean(price_array), 2)} kr")


#  Hjelpklasse - Plotting
class Plotting:
    def __init__(self):
        self.GRASS_GREEN = "#48a23f"
        self.FOREST_GREEN = "#1d3c34"
        self.SUN_YELLOW = "#FFC358"
        self.GRASS_BLUE = "#3f48a2"
        self.GRASS_RED = "#a23f48"

    def xy_plot(self, x, xmin, xmax, xlabel, y, ymin, ymax, ylabel, COLOR):
        source = pd.DataFrame({"x": x, "y": y})
        c = alt.Chart(source).mark_line().encode(
            x=alt.X("x", scale=alt.Scale(domain=[xmin, xmax]), title=xlabel),
            y=alt.Y("y", scale=alt.Scale(domain=[ymin, ymax]), title=ylabel),
            color = alt.value(COLOR))
        st.altair_chart(c, use_container_width=True)

    def xy_bar_plot(self, x, xmin, xmax, xlabel, y, ymin, ymax, ylabel, COLOR):
        source = pd.DataFrame({"x": x, "y": y})
        c = alt.Chart(source).mark_bar(width=0.5).encode(
            x=alt.X("x", scale=alt.Scale(domain=[xmin, xmax]), title=xlabel),
            y=alt.Y("y", scale=alt.Scale(domain=[ymin, ymax]), title=ylabel),
            color = alt.value(COLOR))
        st.altair_chart(c, use_container_width=True)

    def xy_bar_thick_plot(self, x, xmin, xmax, xlabel, y, ymin, ymax, ylabel, COLOR):
        source = pd.DataFrame({"x": x, "y": y})
        c = alt.Chart(source).mark_bar().encode(
            x=alt.X("x", scale=alt.Scale(domain=[xmin, xmax]), title=xlabel),
            y=alt.Y("y", scale=alt.Scale(domain=[ymin, ymax]), title=ylabel),
            color = alt.value(COLOR))
        st.altair_chart(c, use_container_width=True)

#    def hourly_plot(self, y, COLOR, name):
#        x = np.arange(8760)
#        source = pd.DataFrame({"x": x, "y": y})
#
#        c = alt.Chart(source).mark_bar(size=0.75, color= COLOR).encode(
#            x=alt.X("x", scale=alt.Scale(domain=[0,8760]), title="Timer i ett år"),
#            y=alt.Y("y", title="kW"),
#            #y=alt.Y("y", scale=alt.Scale(domain=[0,800]), title="kW"),
#            color=alt.Color(legend=alt.Legend(orient='top', direction='vertical', title=None))).configure_axis(grid=True)
#        st.altair_chart(c, use_container_width=True)

    def hourly_stack_plot(self, y1 , y2, y1label, y2label, y1color, y2color):
        date_1, date_2 = np.datetime64("2021-01-01T00"), np.datetime64("2022-01-01T00")
        x = np.arange(date_1, date_2, dtype='datetime64')
        mpl.rcParams['axes.prop_cycle'] = cycler(color=[y1color, y2color])
        plt.stackplot(x, y1, y2, labels=[f'{y1label}: {int(np.sum(y1)):,} kWh | {int(max(y1)):,} kW'.replace(',', ' '),f'{y2label}: {int(np.sum(y2)):,} kWh | {int(max(y2)):,} kW'.replace(',', ' ')])
        plt.legend(loc='best')
        myFmt = mdates.DateFormatter('%d.%m')
        plt.gca().xaxis.set_major_formatter(myFmt)
        plt.xlabel("Timer i ett år")
        plt.ylabel("Effekt [kW]")
        plt.grid(color='black', linestyle='--', linewidth=0.1)
        plt.xlim([date_1, date_2])
        st.pyplot(plt)
        plt.close()

    def hourly_triple_stack_plot(self, y1 , y2, y3, y1label, y2label, y3label, y1color, y2color, y3color):
        date_1, date_2 = np.datetime64("2021-01-01T00"), np.datetime64("2022-01-01T00")
        x = np.arange(date_1, date_2, dtype='datetime64')
        mpl.rcParams['axes.prop_cycle'] = cycler(color=[y1color, y2color, y3color])
        plt.stackplot(x, y1, y2, y3, labels=[
        f'{y1label}: {int(np.sum(y1)):,} kWh | {int(max(y1)):,} kW'.replace(',', ' '),
        f'{y2label}: {int(np.sum(y2)):,} kWh | {int(max(y2)):,} kW'.replace(',', ' '),
        f'{y3label}: {int(np.sum(y3)):,} kWh | {int(max(y3)):,} kW'.replace(',', ' ')])
        plt.legend(loc='best')
        myFmt = mdates.DateFormatter('%d.%m')
        plt.gca().xaxis.set_major_formatter(myFmt)
        plt.xlabel("Timer i ett år")
        plt.ylabel("Effekt [kW]")
        plt.grid(color='black', linestyle='--', linewidth=0.1)
        plt.xlim([date_1, date_2])
        st.pyplot(plt)
        plt.close()

    def hourly_plot(self, y1, y1label, y1color, ymin = None, ymax = None, hline_value=0, winterweek = False):
        date_1, date_2 = np.datetime64("2021-01-01T00"), np.datetime64("2022-01-01T00")
        x = np.arange(date_1, date_2, dtype='datetime64')
        if winterweek == True:
            y_new = []
            date_1 = np.datetime64("2021-01-02T00")
            date_2 = np.datetime64("2021-01-08T00")
            x = np.arange(date_1, date_2, dtype='datetime64').flatten()
            #for i in range(0, len(y1)):
            #    state = x[i] > date_1 and x[i] < date_2
            #    if bool(state) == bool(1):
            #        y_new.append(y1[i])
            #y1 = y_new
        mpl.rcParams['axes.prop_cycle'] = cycler(color=[y1color])
        plt.stackplot(x, y1, labels=[f'{y1label}: {int(np.sum(y1)):,} kWh | {int(max(y1)):,} kW'.replace(',', ' ')])
        plt.legend(loc='best')
        myFmt = mdates.DateFormatter('%d.%m')
        plt.gca().xaxis.set_major_formatter(myFmt)
        plt.xlabel("Timer i ett år")
        plt.ylabel("Effekt [kW]")
        plt.ylim((ymin, ymax))
        plt.axhline(y = hline_value, color = 'black', linestyle = '-.', linewidth=0.5)        
        plt.grid(color='black', linestyle='--', linewidth=0.1)
        plt.xlim([date_1, date_2])
        st.pyplot(plt)
        plt.close()

    def xy_plot(self, x, xmin, xmax, x_label, y, ymin, ymax, y_label, COLOR):
        fig, ax = plt.subplots()
        mpl.rcParams['axes.prop_cycle'] = cycler(color=[COLOR])
        ax.plot(x, y, linewidth=2.0)
        ax.grid(color='black', linestyle='--', linewidth=0.1)
        ax.set(xlim=(xmin, xmax), ylim=(ymin, ymax), xlabel=(x_label), ylabel=(y_label))
        st.pyplot(plt)
        plt.close()

    def xy_plot_bar(self, x, x_label, y, ymin, ymax, y_label, COLOR, hline_value=0):
        fig, ax = plt.subplots()
        mpl.rcParams['axes.prop_cycle'] = cycler(color=[COLOR])
        ax.bar(x, y)
        ax.grid(color='black', linestyle='--', linewidth=0.1)
        ax.set(ylim=(ymin, ymax), xlabel=(x_label), ylabel=(y_label))
        if hline_value != 0:
            ax.axhline(y = hline_value, color = 'black', linestyle = '--', linewidth=0.3)
        st.pyplot(plt)
        plt.close()

    def xy_simulation_plot(self, x, xmin, xmax, x_label, y1, y2, ymin, ymax, y_label, y_legend1, y_legend2, COLOR1, COLOR2):
        fig, ax = plt.subplots()
        x = x/12
        ax.plot(x, y1, linewidth=2.0, color=COLOR1, label=y_legend1)
        ax.plot(x, y2, linewidth=2.0, color=COLOR2, label=y_legend2)
        ax.axhline(y = 1, color = 'black', linestyle = '--', linewidth=0.3)
        ax.axhline(y = 0, color = 'black', linestyle = '-.', linewidth=0.3)        
        ax.legend()
        ax.grid(color='black', linestyle='--', linewidth=0.1)
        ax.set(xlim=(xmin, xmax), xlabel=(x_label), ylabel=(y_label), yticks=(np.arange(ymin, ymax, 1)))
        st.pyplot(plt)




