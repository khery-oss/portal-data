import streamlit as st
import requests

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

st.info("💡 Pilih modul di bilah navigasi sebelah kiri untuk memulai eksplorasi data.")

st.divider()

# =============================================================================
# KOTAK SARAN & PERMINTAAN DATA (LANGSUNG KE EMAIL)
# =============================================================================
st.subheader("📬 Kotak Saran & Permintaan Data Baru")
st.markdown(
    "Punya masukan, kritik, atau butuh indikator ekonomi/sosial lain yang ingin ditambahkan ke dashboard? "
    "Kirimkan pesanmu langsung ke tim pengembang melalui formulir di bawah ini."
)

# GANTI DENGAN EMAIL KAMU DI SINI:
TARGET_EMAIL = "indoecon.project@gmail.com"

with st.form("feedback_form", clear_on_submit=True):
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        nama_pengirim = st.text_input("Nama Lengkap / Instansi*", placeholder="Contoh: Budi Santoso (Universitas Indonesia)")
    with col_f2:
        email_pengirim = st.text_input("Email Kamu*", placeholder="nama@email.com")
        
    tipe_pesan = st.selectbox(
        "Kategori Pesan:",
        ["Permintaan Indikator / Dataset Baru", "Laporan Masalah / Bug", "Kritik & Saran", "Lainnya"]
    )
    
    isi_pesan = st.textarea(
        "Pesan / Detail Permintaan Data*",
        placeholder="Tuliskan nama indikator, sumber lembaga (misal BI, OJK, Kemendag), atau masukan perbaikan yang kamu harapkan...",
        height=120
    )
    
    submitted = st.form_submit_button("📩 Kirim ke Pengembang", type="primary")

    if submitted:
        if not nama_pengirim.strip() or not email_pengirim.strip() or not isi_pesan.strip():
            st.error("Mohon lengkapi Nama, Email, dan Isi Pesan sebelum mengirim.")
        elif "@" not in email_pengirim or "." not in email_pengirim:
            st.error("Format email tidak valid. Mohon periksa kembali.")
        else:
            with st.spinner("Mengirimkan pesan ke email pengembang..."):
                endpoint = f"https://formsubmit.co/{TARGET_EMAIL}"
                payload = {
                    "name": nama_pengirim,
                    "email": email_pengirim,
                    "category": tipe_pesan,
                    "message": isi_pesan,
                    "_subject": f"[{tipe_pesan}] Pesan Baru dari IndoEcon Explorer",
                    "_captcha": "false"  # Matikan captcha agar mulus via Streamlit
                }
                headers = {"User-Agent": "Mozilla/5.0"}
                
                try:
                    res = requests.post(endpoint, data=payload, headers=headers, timeout=15)
                    if res.status_code in [200, 302]:
                        st.success("🎉 Terima kasih! Masukan/permintaan data kamu telah berhasil dikirimkan ke email pengembang.")
                    else:
                        st.error(f"Gagal mengirim pesan (Kode status: {res.status_code}). Silakan coba lagi.")
                except Exception as e:
                    st.error(f"Terjadi kesalahan saat menghubungkan ke layanan pengiriman: {e}")
