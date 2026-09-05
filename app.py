import io
import requests
import streamlit as st

st.set_page_config(
    page_title="IndoEcon Explorer",
    page_icon="📊",
    layout="wide"
)

st.title("🇮🇩 IndoEcon Explorer")
st.markdown(
    "Portal observasi data makroekonomi, ketenagakerjaan, sosial-pendidikan, kesehatan publik, dan pembangunan berkelanjutan "
    "Indonesia yang terintegrasi langsung dengan berbagai institusi resmi internasional dan nasional. "
    "Seluruh data ditarik secara **100% Live API** secara *real-time* tanpa penyimpanan data statis (*no hardcoding*)."
)

# =============================================================================
# CATATAN AKADEMIS & PENGGUNAAN RISET (DISCLAIMER)
# =============================================================================
st.info(
    "🎯 **Tujuan Platform & Pedoman Penggunaan Akademis:**\n\n"
    "Website ini dibuat untuk kebutuhan para **peneliti, akademisi, dosen, dan mahasiswa** "
    "dalam mengakses serta mengeksplorasi data resmi Indonesia secara cepat, transparan, dan terbuka.\n\n"
    "* **Rekomendasi Cross-check:** Pengguna sangat disarankan untuk tetap melakukan *cross-check* kembali "
    "ke website utama sumber data resmi seperti yang tercantum pada masing-masing modul.\n"
    "* **Standar Sitasi & Penulisan Sumber:** Dalam penulisan karya ilmiah, skripsi, tesis, jurnal, maupun laporan riset, "
    "penulisan sumber **tetap menggunakan sumber asli** tempat data diterbitkan "
    "(seperti *World Bank, FRED (Federal Reserve Bank of St. Louis), ILO (International Labour Organization), "
    "UN SDGs (United Nations), UNESCO Institute for Statistics, atau WHO (World Health Organization)*).\n"
    "* **Koreksi & Masukan:** Apabila terdapat kekeliruan, kesalahan data, atau *error* pada penarikan API, "
    "bisa langsung diberitahukan ke email tim pengembang melalui formulir kontak di bawah."
)

st.divider()

st.subheader("📚 Arsitektur Modul Data")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 🌐 1. World Bank (WDI)
    * **Cakupan:** Indikator makroekonomi jangka panjang, pertumbuhan PDB riil/nominal, neraca transaksi berjalan, perdagangan internasional, dan utang.
    * **Penyedia:** World Development Indicators (WDI) API.
    
    ### 📈 2. FRED (Federal Reserve Bank of St. Louis)
    * **Cakupan:** Suku bunga global/AS, perbandingan kebijakan moneter, inflasi produsen, dan harga komoditas strategis global.
    * **Penyedia:** Federal Reserve Economic Data REST API.
    
    ### 👷 3. ILO (International Labour Organization)
    * **Cakupan:** Pasar tenaga kerja, TPAK, pengangguran terbuka & menurut tingkat pendidikan, pekerja rentan, serta transformasi sektoral.
    * **Penyedia:** ILOSTAT Harmonized Modelled Estimates API.
    """)

with col2:
    st.markdown("""
    ### 🇺🇳 4. UN SDGs (United Nations)
    * **Cakupan:** Indikator tujuan pembangunan berkelanjutan global, kemiskinan ekstrem, ketimpangan (*income share bottom 40%*), dan transisi energi bersih.
    * **Penyedia:** United Nations Statistics Division (UNSD) SDG API.
    
    ### 🎓 5. UNESCO Institute for Statistics (UIS)
    * **Cakupan:** Angka Partisipasi Kasar/Murni (APK/APM), angka melek aksara (literasi), rasio murid-guru, dan pembiayaan belanja pendidikan publik.
    * **Penyedia:** UNESCO UIS Data Repository API.
    
    ### 🏥 6. WHO (World Health Organization)
    * **Cakupan:** Indikator kesehatan publik, angka harapan hidup, stunting & gizi balita, tenaga medis, jaminan kesehatan semesta (*UHC*), dan modal manusia (*human capital*).
    * **Penyedia:** WHO Global Health Observatory (GHO) OData API.
    """)

st.divider()

st.subheader("⚙️ Prinsip Integritas Data")
st.markdown("""
* **100% Live API Streaming:** Data ditarik *on-the-fly* pada saat pengguna menekan tombol penarikan data langsung ke server resmi.
* **Bebas Manipulasi:** Tidak ada data buatan, tiruan, atau berkas lokal tersembunyi di dalam skrip sistem (*zero hardcoding*).
* **Ekspor Terbuka:** Seluruh data yang berhasil ditarik dapat diunduh seketika dalam format CSV dan Excel (`.xlsx`) untuk analisis ekonometrika lebih lanjut di R, Stata, Python, maupun SPSS.
""")

st.info("💡 Pilih modul di bilah navigasi sebelah kiri untuk memulai penarikan dan eksplorasi data.")

st.divider()

# =============================================================================
# KOTAK SARAN, LAPORAN EROR & PERMINTAAN DATA BARU
# =============================================================================
st.subheader("📬 Kotak Saran, Laporan Kendala & Permintaan Data")
st.markdown(
    "Menemukan kekeliruan data, *error* pada API, atau membutuhkan seri indikator baru untuk riset Anda? "
    "Kirimkan masukan langsung ke email kami melalui formulir di bawah ini."
)

TARGET_EMAIL = "indoecon.project@gmail.com"

with st.form("feedback_form", clear_on_submit=True):
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        nama_pengirim = st.text_input("Nama Lengkap / Instansi Akademik*", placeholder="Contoh: Budi Santoso (Universitas Indonesia)")
    with col_f2:
        email_pengirim = st.text_input("Alamat Email Pengirim*", placeholder="nama@email.com")
        
    tipe_pesan = st.selectbox(
        "Kategori Pesan:",
        [
            "Laporan Kesalahan Data / API Error",
            "Permintaan Indikator / Dataset Tambahan",
            "Kritik, Saran & Masukan Metodologi",
            "Lainnya"
        ]
    )
    
    isi_pesan = st.text_area(
        "Detail Laporan / Pesan*",
        placeholder="Jelaskan secara spesifik indikator mana yang mengalami kendala/eror, atau sebutkan dataset yang ingin ditambahkan beserta sumber resminya...",
        height=130
    )
    
    submitted = st.form_submit_button("📩 Kirim Pesan ke Pengembang", type="primary")

    if submitted:
        if not nama_pengirim.strip() or not email_pengirim.strip() or not isi_pesan.strip():
            st.error("Mohon lengkapi Nama, Email, dan Detail Pesan sebelum mengirim.")
        elif "@" not in email_pengirim or "." not in email_pengirim:
            st.error("Format alamat email tidak valid. Mohon periksa kembali.")
        else:
            with st.spinner("Mengirimkan pesan ke email pengembang..."):
                endpoint = f"https://formsubmit.co/{TARGET_EMAIL}"
                payload = {
                    "name": nama_pengirim,
                    "email": email_pengirim,
                    "category": tipe_pesan,
                    "message": isi_pesan,
                    "_subject": f"[{tipe_pesan}] Pesan dari IndoEcon Explorer",
                    "_captcha": "false"
                }
                headers = {"User-Agent": "Mozilla/5.0"}
                
                try:
                    res = requests.post(endpoint, data=payload, headers=headers, timeout=15)
                    if res.status_code in [200, 302]:
                        st.success("🎉 Terima kasih! Laporan/masukan Anda telah berhasil dikirimkan ke email pengembang.")
                    else:
                        st.error(f"Gagal mengirim pesan (Status HTTP: {res.status_code}). Silakan coba lagi.")
                except Exception as e:
                    st.error(f"Terjadi kendala saat menghubungi server pengiriman: {e}")
