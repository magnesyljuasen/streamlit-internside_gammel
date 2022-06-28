import streamlit as st
from PIL import Image
import requests
import streamlit.components.v1 as components


def forside_app():
    col1, col2, col3 = st.columns(3)
    with col1:
        image = Image.open('src/bilder/logo.png')
        st.image(image)  
    with col2:
        st.title("Grunnvarme")
        st.write('Internside')

    st.header("Lenker")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("[GRANADA](%s)" % "https://geo.ngu.no/kart/granada_mobil/")
        st.subheader("[Løsmasser](%s)" % "https://geo.ngu.no/kart/losmasse_mobil/")
        st.subheader("[NADAG](%s)" % "https://geo.ngu.no/kart/nadag-avansert/")
    with c2:
        st.subheader("[Berggrunn](%s)" % "https://geo.ngu.no/kart/berggrunn_mobil/")
        st.subheader("[InSAR](%s)" % "https://insar.ngu.no/")
        st.subheader("[AV-kartet](%s)" % "https://kart.asplanviak.no/")
    st.markdown("""--""")
    #--
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("[Ebooks](%s)" % "https://asplanviak.sharepoint.com/sites/10333-03")
        st.subheader("[Gamle Ebooks](%s)" % "http://bikube/Oppdrag/8492/default.aspx")
        st.subheader("[GeoNorge](%s)" % "https://www.geonorge.no/")
    with c2:
        st.subheader("[UnderOslo](%s)" % "https://kart4.nois.no/underoslo/Content/login.aspx?standalone=true&onsuccess=restart&layout=underoslo&time=637883136354120798&vwr=asv")
        st.subheader("[Saksinnsyn](%s)" % "https://od2.pbe.oslo.kommune.no/kart/")
        st.subheader("[Nord Pool](%s)" % "https://www.nordpoolgroup.com/en/Market-data1/#/nordic/table")
        

    st.markdown(""" --- """)

    class Tweet(object):
        def __init__(self, s, embed_str=False):
            if not embed_str:
                # Use Twitter's oEmbed API
                # https://dev.twitter.com/web/embedded-tweets
                api = "https://publish.twitter.com/oembed?url={}".format(s)
                response = requests.get(api)
                self.text = response.json()["html"]
            else:
                self.text = s

        def _repr_html_(self):
            return self.text

        def component(self):
            return components.html(self.text, height=700)

    t = Tweet("https://twitter.com/SGehlin?ref_src=twsrc%5Etfw").component()
