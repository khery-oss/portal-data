import streamlit as st

st.set_page_config(
    page_title="Indonesia Socio-Economic Data Hub",
    page_icon="📊",
    layout="wide"
)

st.title("🇮🇩 Indonesia Socio-Economic & Development Data Hub")
st.markdown(
    "Portal observasi data makroekonomi, ketenagakerjaan, sosial-pendidikan, dan pembangunan berkelanjutan "
    "Indonesia yang terintegrasi langsung dengan berbagai institusi resmi internasional dan nasional. "
    "Seluruh data ditarik secara **100% Live API** secara *real-time* tanpa penyimpanan data statis (*no hardcoding*)."
)

st.divider()

st.subheader("📚 Arsitektur Modul Data")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 🌐 1. World Bank (WDI)
    * **Cakupan:** Indikator makroekonomi jangka panjang, pertumbuhan PDB, neraca berjalan, keterbukaan perdagangan, dan utang nasional.
    * **Penyedia:** World Development Indicators (WDI) API.
    
    ### 📈 2. FRED (Federal Reserve Bank of St. Louis)
    * **Cakupan:** Suku bunga global/AS, perbandingan moneter, indeks harga produsen, dan harga komoditas global acuan.
    * **Penyedia:** Federal Reserve Economic Data REST API.
    
    ### 👷 3. ILO (International Labour Organization)
    * **Cakupan:** Pasar tenaga kerja, TPAK, pengangguran menurut jenjang pendidikan, pekerjaan rentan, dan struktur sektoral.
    * **Penyedia:** ILOSTAT Harmonized Modelled Estimates API.
    """)

with col2:
    st.markdown("""
    ### 🇺🇳 4. UN SDGs (United Nations)
    * **Cakupan:** Pilar target pembangunan berkelanjutan PBB, kemiskinan ekstrem, ketimpangan (*income share bottom 40%*), dan transisi energi.
    * **Penyedia:** United Nations Statistics Division (UNSD) SDG API.
    
    ### 🎓 5. UNESCO Institute for Statistics (UIS)
    * **Cakupan:** Angka Partisipasi Kasar/Murni (APK/APM), angka melek huruf (literasi), rasio murid-guru, dan belanja pendidikan publik.
    * **Penyedia:** UNESCO UIS Data Repository API.
    
    ### 📊 6. BPS (Badan Pusat Statistik RI)
    * **Cakupan:** Statistik resmi domestik nasional dan sub-nasional (provinsi/kabupaten), inflasi IHK, dan indikator kemiskinan daerah.
    * **Penyedia:** WebAPI Resmi Badan Pusat Statistik Indonesia.
    """)

st.divider()

st.subheader("⚙️ Prinsip & Standar Metodologi")
st.markdown("""
* **Live API Streaming:** Data ditarik saat tombol observasi ditekan langsung dari server basis data lembaga terkait.
* **Transparansi Metodologi:** Setiap indikator dilengkapi tautan dokumentasi resmi, kode seri, dan satuan pengukuran standar internasional.
* **Format Terbuka:** Seluruh hasil penarikan data dapat diunduh langsung dalam format CSV dan Excel (`.xlsx`).
""")

st.info("Pilih modul di bilah navigasi sebelah kiri untuk memulai eksplorasi data.")
