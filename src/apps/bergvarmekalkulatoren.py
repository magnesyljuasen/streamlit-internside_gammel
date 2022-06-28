import streamlit as st
import src.innlogging.database as db

def bergvarmekalkulatoren_app():
    st.title("Bergvarmekalkulatoren") 
    
    st.subheader("[Kalkulatoren](%s)" % "https://magnesyljuasen-bergvarme-app-7fvbu7.streamlitapp.com/")
    list = db.fetch_all_data()
    st.subheader(f"Antall besøkende: {len(list)}")

    st.dataframe(list)

    key = st.text_input("Velg key", value = "Rådhusplassen 1, Oslo domkirkes sokn")

    with st.expander("Hent data"):
        my_dict = db.get_data(key)
        st.write(my_dict)










