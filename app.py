import streamlit as st

st.set_page_config(
    page_title="IndoEcon Data Explorer",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("IndoEcon Data Explorer")
st.write("""
Selamat datang di portal terpadu eksplorasi dan visualisasi data ekonomi, sosial, serta pembangunan Indonesia. 
Pilih sumber basis data yang ingin dieksplorasi melalui bilah sisi (**sidebar**) di sebelah kiri:

* **🌐 World Bank:** Indikator pembangunan lintas sektor, mencakup makroekonomi, kemiskinan, pendidikan, kesehatan, hingga lingkungan.
* **📈 FRED (Federal Reserve Bank of St. Louis):** Indikator moneter dan finansial frekuensi tinggi, seperti suku bunga acuan, kurs mata uang, inflasi, dan agregat likuiditas.
* **📊 BPS (Badan Pusat Statistik):** Statistik resmi terlengkap dengan cakupan berjenjang dari level **Nasional**, **Provinsi**, hingga **Kabupaten/Kota**.
* **🇮🇩 Satu Data Indonesia:** *(Segera hadir)*
""")

st.info(
    "👈 Pilih menu di **sidebar kiri** untuk mulai menjelajahi dan mengunduh"
    " data."
)
