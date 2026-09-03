import streamlit as st

st.set_page_config(
    page_title="IndoEcon Data Explore",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("IndoEcon Data Explore")
st.write("""
Selamat datang di repositori eksplorasi data Indonesia, khususnya ekonomi, pembangunan, dan finansial.
Pilih sumber data yang ingin diakses melalui menu navigasi di bilah sisi (**sidebar**) sebelah kiri:

* **🏛️ World Bank:** Data indikator pembangunan lintas sektor (makro, sosial, kemiskinan, lingkungan).
* **📈 FRED:** Data makro-finansial frekuensi tinggi dari Federal Reserve Bank of St. Louis.
* **📊 BPS & Satu Data:** *(Segera hadir)*
""")

st.info("👈 Buka sidebar di kiri atas untuk berpindah halaman sumber data.")
