import streamlit as st


def geoteknikk_app():
    st.title("Energibrønner og geoteknikk")

    st.header("Sjekkliste")
    st.subheader("Kartstudier")
    st.write("- *Dybde til fjell* | NADAG, GRANADA")
    st.write("- *Type løsmasser* | Løsmassedatabasen")
    st.write("- *Over/under marin grense* | Marin grense")
    st.write("- *Dypforvitring* | Aktsomhetskart for tunnelplanlegging")
    st.write("- *Terrengprofil* | Kartverket")
    st.write("- *Nærhet til hendelser vi vet om*")
    
    st.subheader("f2")
    
    st.subheader("Risiko")
    st.write("- Setningsskader eller skred?")
    st.write("- Type anlegg (åpent/lukket)")
    st.write("- Størrelse på anlegg (antall brønner) og temperaturnivåer")
    st.write("- Løsmassemektighet og utstrekning") 
    
    st.subheader("Konsekvens")
    st.write("- Fundamentering bygg inkl. omkringliggende bygg (bunnledninger, gulv, pilarer, peler)") 
    st.write("- Varierende dybder til fjell (skjevsetninger)")
    st.write("- Store dybder til fjell (stort setningspotensiale)")


    st.subheader("Tiltak")
    st.write("- Utstøping")
    st.write("- Poretrykksivå")

    
