import streamlit as st
import src.innlogging.database as db

def bergvarmekalkulatoren_app():
    st.title("Bergvarmekalkulatoren")
    
    list = db.fetch_all_data()
    st.subheader(f"Antall besøkende: {len(list)}")

    with st.expander("Vis data"):
        st.dataframe(list)

        key = st.text_input("Velg key", value = "Rådhusplassen 1, Oslo domkirkes sokn")
        my_dict = db.get_data(key)
        st.write(my_dict)










